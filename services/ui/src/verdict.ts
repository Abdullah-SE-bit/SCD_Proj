// The parts of contracts/schemas/verdict.schema.json that the UI shows. The UI displays them; it never
// computes a verdict.
export type Dimension = "demand_pain" | "competition" | "differentiation" | "feasibility" | "risk" | "learning";

export type Verdict = {
  verdict: "GO" | "PIVOT" | "NO-GO" | "INSUFFICIENT_EVIDENCE";
  stability: "STABLE" | "BORDERLINE";
  score: number;
  confidence: number;
  gates: Record<"evidence" | "feasibility" | "risk" | "duplicate", "pass" | "fail">;
  weights: Record<Dimension, number>;
  thresholds: { T_go: number; T_no: number; floor: number };
  scores: { dimension: Dimension; score: number; confidence: number; evidence_ids: string[]; reason: string }[];
  weakest_dimension: Dimension | null;
  what_would_make_go: { change: string; new_score: number; new_verdict: string }[];
  sensitivity: { runs: number; flipped: number };
};
