import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { App } from "./App";

const reply = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const run = { run_id: "fixture-run", status: "completed", label: "FIXTURE DATA", verdict: { verdict: "GO" } };

function submit(idea: string) {
  render(<App />);
  fireEvent.change(screen.getByLabelText("Your project idea"), { target: { value: idea } });
  fireEvent.click(screen.getByRole("button", { name: "Check this idea" }));
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

test("starts empty and cannot send a blank idea", () => {
  render(<App />);
  expect(screen.getByText("No result yet.")).toBeTruthy();
  expect(screen.getByRole("button", { name: "Check this idea" })).toHaveProperty("disabled", true);
});

test("calls only the API on its own origin and shows the run", async () => {
  const fetch = vi.fn().mockResolvedValueOnce(reply({ run_id: "fixture-run" })).mockResolvedValueOnce(reply(run));
  vi.stubGlobal("fetch", fetch);
  submit("A study planner");
  expect(screen.getByRole("status").textContent).toBe("Checking your idea...");
  expect(await screen.findByText("FIXTURE DATA")).toBeTruthy();
  expect(fetch.mock.calls.map((call) => call[0])).toEqual(["/api/validate", "/api/runs/fixture-run"]);
  expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ idea: "A study planner" });
});

test("shows the API's reason when it refuses", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(reply({ error: "idea must be text" }, 400)));
  submit("x");
  expect((await screen.findByRole("alert")).textContent).toContain("idea must be text");
});

test("says so when the API cannot be reached", async () => {
  vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));
  submit("x");
  expect((await screen.findByRole("alert")).textContent).toContain("could not be reached");
});

test("reports a gateway error page instead of failing silently", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("<html>Bad Gateway</html>", { status: 502 })));
  submit("x");
  expect((await screen.findByRole("alert")).textContent).toContain("502");
});
