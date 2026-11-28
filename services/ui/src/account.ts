// Accounts, profile and history calls. The shapes are what the gateway returns; nothing is computed here.
import type { Dimension, Verdict } from "./verdict";

export type Profile = {
  skills: string[];
  hours_per_week: number;
  weeks_available: number;
  team_size: number;
  compute: "laptop" | "free_gpu" | "paid";
  goal: "startup" | "portfolio" | "course_project";
  interests: string[];
  version?: number;
  user_id?: string;
};
export type Summary = Pick<Verdict, "verdict" | "score"> | null;
export type Idea = { idea_id: string; title: string; versions: number; latest_version: number; verdict: Summary };
export type Version = { version: number; text: string; verdict: Summary };
export type Comparison = {
  dimensions: Dimension[];
  ideas: { idea_id: string; title: string; version: number; verdict: Summary; dimensions: Record<Dimension, number | null> }[];
};

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

export async function call<T>(path: string, options: { token?: string; method?: string; body?: unknown } = {}): Promise<T> {
  const headers: Record<string, string> = {};
  if (options.token) headers.Authorization = `Bearer ${options.token}`;
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  const response = await fetch(`/api${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  }).catch(() => {
    throw new ApiError("The API could not be reached.", 0);
  });
  const body = await response.json().catch(() => null);
  if (!response.ok || !body) {
    const wait = body?.retry_after ? ` Wait ${body.retry_after} seconds.` : "";
    throw new ApiError(`${body?.error ?? `The API answered ${response.status}`}.${wait}`, response.status);
  }
  return body as T;
}
