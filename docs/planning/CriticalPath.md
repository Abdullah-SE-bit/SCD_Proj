# Critical path and parallel work

Generated. Longest dependency chain by effort points (S=1, M=3, L=5):

`P00.01 → P00.04 → P00.05 → P00.06 → P00 → P01.02 → P01.04 → P01.05 → P01 → P04.01 → P04.02 → P04.03 → P04.04 → P04.05 → P04 → P05.02 → P05.04 → P05 → P07.02 → P07.03 → P07 → P08 → P09.02 → P09 → P10.01 → P10.03 → P10.04 → P10`

Total: 88 points.

## Tasks that can start together within a phase

| Phase | Parallel starters |
|---|---|
| P01 | P01.01, P01.02, P01.03 |
| P02 | P02.01 |
| P03 | P03.01, P03.03 |
| P04 | P04.01 |
| P05 | P05.01, P05.02, P05.03 |
| P06 | P06.01 |
| P07 | P07.01 |
| P08 | P08.01, P08.03 |
| P09 | P09.01 |
| P10 | P10.01, P10.02 |

## Tasks needing a human, credentials or a GPU

| Task | Needs | Title |
|---|---|---|
| P00.06 | human | Independent review of foundation |
| P00 | human | Phase 0 gate |
| P01.05 | human, credentials | Jenkins delivery of skeleton |
| P03.01 | human | Gates, score, thresholds and confidence |
| P03.03 | human | Rubrics for six dimensions |
| P04.02 | credentials | Scouts for three sources |
| P04.05 | human | Retrieval evaluation and CI gate |
| P05.01 | credentials | Feature computation and four scorers |
| P06.01 | human, credentials | Build and hand-check dataset |
| P06.02 | human, gpu | Train, merge and quantise |
| P06.03 | credentials | Serve model with fallback |
| P06.04 | credentials | Model comparison |
| P07.02 | credentials | Idea generator debate |
| P09.01 | human | Human labelled verdict set |
| P09.02 | human | Baseline, tuning and final matrices |
| P10.02 | human | Merge-conflict exercise |
| P10.03 | human | Report, screenshots and decision records |
| P10.04 | human | Contribution table, access check and viva |
| P10 | human | Phase 10 gate |
