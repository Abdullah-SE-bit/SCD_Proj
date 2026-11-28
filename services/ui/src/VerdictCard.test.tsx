import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import example from "../../../contracts/schemas/examples/verdict.valid.json";
import { VerdictCard } from "./VerdictCard";
import type { Verdict } from "./verdict";

const verdict = example as Verdict;
const title = () => screen.getByRole("heading", { level: 2 });

afterEach(cleanup);

test("labels fixture data ahead of the verdict", () => {
  render(<VerdictCard verdict={verdict} label="FIXTURE DATA" />);
  const note = screen.getByRole("note");
  expect(note.textContent).toBe("FIXTURE DATA. These are sample values; your idea was not evaluated.");
  expect(note.compareDocumentPosition(title()) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
});

test("adds no fixture label to other results", () => {
  render(<VerdictCard verdict={verdict} />);
  expect(screen.queryByRole("note")).toBeNull();
});

test("shows the verdict, its stability, the score against both thresholds and the confidence", () => {
  render(<VerdictCard verdict={verdict} />);
  expect(title().textContent).toBe("GO");
  expect(screen.getByText("Borderline: 3 of 14 sensitivity checks changed the verdict.")).toBeTruthy();
  expect(screen.getByRole("img", { name: "Score 70.5 of 100. Lower threshold 50, GO threshold 70." })).toBeTruthy();
  expect(screen.getByText("Confidence: 74%")).toBeTruthy();
});

test("lists the four gates and six dimension scores with weight, reason and evidence", () => {
  render(<VerdictCard verdict={verdict} />);
  const gates = within(screen.getByRole("list", { name: "Gates" })).getAllByRole("listitem");
  expect(gates.map((gate) => gate.textContent)).toEqual([
    "Evidence: pass",
    "Feasibility: pass",
    "Risk: pass",
    "Duplicate: pass",
  ]);
  expect(screen.getAllByRole("row")).toHaveLength(7); // header and six dimensions
  const row = screen.getByRole("row", { name: /^Feasibility/ });
  for (const text of ["4 of 5", "25%", "Short explanation that cites the ids above", "card_8f21#c2"]) {
    expect(row.textContent).toContain(text);
  }
  expect(screen.getByText("Weakest dimension: Competition. Score floor: 1.5.")).toBeTruthy();
});

test("says what would make it GO", () => {
  render(<VerdictCard verdict={verdict} />);
  expect(screen.getByText("Narrow to X segment: score 73.5, GO")).toBeTruthy();
});

test("abstains without showing a score", () => {
  render(<VerdictCard verdict={{ ...verdict, verdict: "INSUFFICIENT_EVIDENCE", scores: [], weakest_dimension: null }} />);
  expect(title().textContent).toBe("Insufficient evidence");
  expect(screen.getByText("There was not enough evidence to give a score.")).toBeTruthy();
  expect(screen.queryByRole("img")).toBeNull();
  expect(screen.queryByRole("table")).toBeNull();
});
