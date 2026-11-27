# Human annotation plan

AI must not produce any label below. Templates and schemas only.

| Set | Size | Who | Schema | Task |
|---|---|---|---|---|
| Retrieval queries with relevant cards | 20+ | both, split evenly | retrieval-query | P04.05 |
| Checked training labels (evaluation set) | 60+ | 30+ each, 10 shared to measure agreement | training-example plus checked_by | P06.01 |
| Verdict labels | team's choice; propose 40+ with at least 8 of each case type | both independently, then resolve | verdict-label | P09.01 |

Procedure: write guidelines from the rubrics; label without seeing the system output or the other person's
label; record annotator and date; discuss disagreements; keep both original labels and the resolution; report
agreement. Case types: clear GO, clear NO-GO, borderline, thin evidence. Sizes beyond the documented minima are
proposals.
