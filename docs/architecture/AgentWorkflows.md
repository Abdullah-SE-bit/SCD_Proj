# Agent workflows

Proposed state machines (Description Figures 2 and 3).

## Discover
```mermaid
stateDiagram-v2
  [*] --> Request
  Request --> Niches : M7+M6
  Niches --> Ideator
  Ideator --> GapAnalyst
  GapAnalyst --> Skeptic
  Skeptic --> Critic : objections with evidence
  Critic --> Ideator : another round (max 3)
  Critic --> Validate : survivors
  Validate --> Result : ranked cards
  Result --> [*]
```

## Validate
```mermaid
stateDiagram-v2
  [*] --> Intake
  Intake --> Clarify : answer would change result
  Clarify --> Intake
  Intake --> Evidence
  Evidence --> AwaitApproval : deep search over budget
  AwaitApproval --> Evidence : approved or declined
  Evidence --> Scorers : 4 in parallel
  Scorers --> Features
  Features --> Verdict : M11
  Verdict --> Challenge : Skeptic and critic
  Challenge --> Stability : M11 recompute, sensitivity, what-if
  Stability --> Card
  Card --> [*]
```

Rules: the model scores, only M11 decides; bounded retries and timeouts; budgets on tokens, pages, steps and
cost; re-run only what changed; every transition traced; behaviour tests replay recorded responses.

## AgenticOps
```mermaid
flowchart LR
  A[Agents and tools] -->|trace records| T[M13]
  T --> J[(traces jsonl)] & I[(traces_index)] & Me[/metrics/] --> D[Dashboard]
  J --> R[Replay with recorded tool results]
  Ing[Ingestion run] --> Dr[Drift report]
  L[(Labelled ideas)] --> H[Evaluation harness Job + nightly] --> Res[(eval/results)] --> B{Below baseline?}
  Reg[Prompt and rubric registry] -->|version recorded| T
```
