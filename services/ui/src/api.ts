// The browser calls only its own origin; the server forwards /api to the gateway (see nginx/).
import type { Verdict } from "./verdict";

export type Run = { run_id: string; status: string; label?: string; verdict: Verdict };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init).catch(() => {
    throw new Error("The API could not be reached.");
  });
  const body = await response.json().catch(() => null);
  if (!response.ok || !body) throw new Error(body?.error ?? `The API answered ${response.status} without a result.`);
  return body as T;
}

export async function checkIdea(idea: string): Promise<Run> {
  const { run_id } = await request<{ run_id: string }>("/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ idea }),
  });
  const run = await request<Run>(`/runs/${encodeURIComponent(run_id)}`);
  if (!run.verdict) throw new Error("The API returned a run without a verdict.");
  return run;
}
