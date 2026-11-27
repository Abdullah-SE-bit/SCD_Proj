# Evaluation strategy

No evaluation has been run. No numbers exist yet; never write estimated ones into results.

| Evaluation | Data (human-made) | Metrics | Output |
|---|---|---|---|
| Retrieval | `eval/retrieval/queries.jsonl`, 20+ hand-written | recall@5, MRR | results JSON + baseline |
| Model | 60+ hand-checked examples, ideas disjoint from training | MAE, share within 1 point, valid-JSON rate, real-evidence-id share, latency, cost; base vs tuned vs hosted; one failure case | comparison table |
| Verdict | `eval/verdict/labels.jsonl` | agreement, confusion matrix before/after, GO-on-human-NO-GO rate separately | report matrices |
| Behaviour | recorded responses | tools used, evidence cited, budget kept, injection resisted | CI + harness |
| Operations | traces | cost per verdict, latency per agent, cache hits, fallbacks | dashboard |

Separation rules: verdict-labelled ideas never enter training; split by idea; tuning must keep a held-out part
or use leave-some-out so thresholds are not fitted to the whole set (state the method in the report).
Baselines change only by reviewed PR.
