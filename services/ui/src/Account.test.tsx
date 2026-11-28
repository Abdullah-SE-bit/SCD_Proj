import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { App } from "./App";

const reply = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const profile = {
  user_id: "u_1",
  skills: ["python"],
  hours_per_week: 10,
  weeks_available: 12,
  team_size: 2,
  compute: "laptop",
  goal: "portfolio",
  interests: ["education"],
  version: 3,
};

// answers by "METHOD path"; anything else is a 404
function api(routes: Record<string, () => Response>) {
  const fetch = vi.fn(async (path: string, init?: RequestInit) => {
    const route = routes[`${init?.method ?? "GET"} ${path}`];
    return route ? route() : reply({ error: "unknown" }, 404);
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

const press = (name: string) => fireEvent.click(screen.getByRole("button", { name }));
const type = (label: string, value: string) => fireEvent.change(screen.getByLabelText(label), { target: { value } });

async function signIn() {
  render(<App />);
  press("Profile");
  type("Email", "student@example.org");
  type("Password", "correct horse");
  press("Sign in");
}

afterEach(() => {
  cleanup();
  sessionStorage.clear();
  vi.unstubAllGlobals();
});

test("asks to sign in before showing the profile or history", () => {
  api({});
  render(<App />);
  for (const tab of ["Profile", "History"]) {
    press(tab);
    expect(screen.getByRole("button", { name: "Sign in" })).toBeTruthy();
  }
});

test("shows why sign-in was refused, also when there were too many tries", async () => {
  const answers = [reply({ error: "wrong email or password" }, 401), reply({ error: "too many requests", retry_after: 40 }, 429)];
  api({ "POST /api/auth/login": () => answers.shift() as Response });
  await signIn();
  expect((await screen.findByRole("alert")).textContent).toContain("wrong email or password");
  press("Sign in");
  await vi.waitFor(() => expect(screen.getByRole("alert").textContent).toContain("Wait 40 seconds"));
});

test("creates an account and signs in with it", async () => {
  const fetch = api({
    "POST /api/auth/register": () => reply({ user_id: "u_1" }, 201),
    "POST /api/auth/login": () => reply({ token: "t0" }),
    "GET /api/profile": () => reply({ error: "no profile saved" }, 404),
  });
  render(<App />);
  press("Profile");
  type("Email", "student@example.org");
  type("Password", "correct horse");
  press("Create account");
  expect(await screen.findByText("No profile saved yet.")).toBeTruthy();
  expect(fetch.mock.calls.map((c) => c[0])).toEqual(["/api/auth/register", "/api/auth/login", "/api/profile"]);
  expect(fetch.mock.calls[2][1]?.headers).toEqual({ Authorization: "Bearer t0" });
});

test("shows the saved profile, marks changes as unsaved and saves them", async () => {
  const fetch = api({
    "POST /api/auth/login": () => reply({ token: "t0" }),
    "GET /api/profile": () => reply(profile),
    "PUT /api/profile": () => reply({ ...profile, hours_per_week: 4, version: 4 }),
  });
  await signIn();
  expect(await screen.findByText("Saved, version 3.")).toBeTruthy();
  type("Hours per week", "4");
  expect(screen.getByText("Unsaved changes.")).toBeTruthy();
  press("Save profile");
  expect(await screen.findByText("Saved, version 4.")).toBeTruthy();
  const sent = JSON.parse(fetch.mock.calls.at(-1)?.[1]?.body as string);
  expect(sent).toEqual({ ...profile, user_id: undefined, version: undefined, hours_per_week: 4 });
});

test("keeps the input and says what is wrong when a save is rejected", async () => {
  api({
    "POST /api/auth/login": () => reply({ token: "t0" }),
    "GET /api/profile": () => reply(profile),
    "PUT /api/profile": () => reply({ error: "invalid value: team_size" }, 400),
  });
  await signIn();
  await screen.findByText("Saved, version 3.");
  type("Team size", "0");
  press("Save profile");
  expect((await screen.findByRole("alert")).textContent).toContain("invalid value: team_size");
  expect((screen.getByLabelText("Team size") as HTMLInputElement).value).toBe("0");
});

test("returns to sign-in when the token is no longer accepted", async () => {
  api({ "POST /api/auth/login": () => reply({ token: "old" }), "GET /api/profile": () => reply({ error: "log in first" }, 401) });
  await signIn();
  expect(await screen.findByText("Your sign-in ended. Sign in again.")).toBeTruthy();
});

const idea = (id: string, title: string, verdict: object | null) => ({
  idea_id: id,
  title,
  source: "own",
  versions: 2,
  latest_version: 2,
  verdict,
});
const go = { verdict: "GO", score: 70.5, confidence: 0.7, stability: "STABLE", weakest_dimension: "competition" };

async function history(routes: Record<string, () => Response>) {
  const fetch = api({ "POST /api/auth/login": () => reply({ token: "t0" }), "GET /api/profile": () => reply(profile), ...routes });
  await signIn();
  await screen.findByText("Saved, version 3.");
  press("History");
  return fetch;
}

test("says so when there is no history", async () => {
  await history({ "GET /api/ideas": () => reply({ ideas: [] }) });
  expect(await screen.findByText("No ideas saved yet.")).toBeTruthy();
});

test("lists ideas and shows the versions of one", async () => {
  await history({
    "GET /api/ideas": () => reply({ ideas: [idea("idea_a", "Link checker", go), idea("idea_b", "Timer", null)] }),
    "GET /api/ideas/idea_a/versions": () =>
      reply({
        idea_id: "idea_a",
        title: "Link checker",
        versions: [{ version: 1, version_id: "v1", text: "Checks links", created_at: "2026-11-01", verdict: null }],
      }),
  });
  expect(await screen.findByText("GO, score 70.5, version 2")).toBeTruthy();
  expect(screen.getByText("Not judged yet, version 2")).toBeTruthy();
  press("Versions of Link checker");
  expect(await screen.findByText("Version 1: Checks links (not judged)")).toBeTruthy();
});

test("compares exactly two ideas on all six dimensions, leaving missing scores empty", async () => {
  const scores = { demand_pain: 3.5, competition: 2, differentiation: 3, feasibility: 4, risk: 3.5, learning: 4.5 };
  const blank = Object.fromEntries(Object.keys(scores).map((k) => [k, null]));
  const fetch = await history({
    "GET /api/ideas": () => reply({ ideas: [idea("idea_a", "Link checker", go), idea("idea_b", "Timer", null)] }),
    "GET /api/compare?a=idea_a&b=idea_b": () =>
      reply({
        dimensions: Object.keys(scores),
        ideas: [
          { idea_id: "idea_a", title: "Link checker", version: 2, verdict: go, dimensions: scores },
          { idea_id: "idea_b", title: "Timer", version: 2, verdict: null, dimensions: blank },
        ],
      }),
  });
  await screen.findByText("GO, score 70.5, version 2");
  const compare = screen.getByRole("button", { name: "Compare the two selected" });
  expect(compare).toHaveProperty("disabled", true);
  fireEvent.click(screen.getByLabelText("Select Link checker"));
  fireEvent.click(screen.getByLabelText("Select Timer"));
  fireEvent.click(compare);
  const table = await screen.findByRole("table");
  expect(within(table).getAllByRole("row")).toHaveLength(8); // header, verdict, six dimensions
  expect(within(table).getByRole("row", { name: /^Feasibility/ }).textContent).toBe("Feasibility4No score");
  expect(fetch.mock.calls.at(-1)?.[0]).toBe("/api/compare?a=idea_a&b=idea_b");
});

test("reports a history that cannot be loaded", async () => {
  await history({ "GET /api/ideas": () => reply({ error: "accounts are unavailable" }, 503) });
  expect((await screen.findByRole("alert")).textContent).toContain("accounts are unavailable");
});
