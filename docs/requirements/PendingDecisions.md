# Pending decisions (one checkpoint)

Nothing here is approved. Proposed defaults are in force for planning only.

| ID | Decision | Recommended | Affects | Needed before |
|---|---|---|---|---|
| D-01 | Commit the course PDFs? The repository is public | Keep them local; or make the repository private and commit them | docs/source | any time |
| D-02 | Repository visibility (markers must be able to open it) | Private with the instructor invited, once their account is known; public keeps free protection and Actions | M14, SUB-002 | submission |
| D-03 | Technology stack | [TechStack](../research/TechStack.md) primary column | all | P01 |
| D-04 | Owner of the Learning score (AMB-01, 02) | Feasibility scorer | M9 | P03.03 |
| D-05 | Image per module (AMB-03) | 15 images | M14 | P01.02 |
| D-06 | Hosted model path (AMB-04) | Through an M5 `/llm` endpoint | M5, M10 | P04.01 |
| D-07 | Verdict interpretations (AMB-05, 08, 09, 10, 13, 19, 24, 26) | As recommended in Ambiguities | M11 | P03.01 |
| D-08 | Work split between contributors | [TaskOwnership](../planning/TaskOwnership.md) | all | P01 |
| D-09 | Third data source and API tokens (AMB-18) | Product Hunt official API | M4 | P04.02 |
| D-10 | Provide "Assignment 1" | Share the document | M2 | P02.01 |
| D-11 | **Decided (A-06):** no approval on task PRs into dev | - | branches | done |
| D-12 | Hosted LLM provider and key (a Claude subscription does not include API usage) | A free tier (Gemini or Groq), checked for data-use terms | M5, M10, M10t | P05 |
| D-13 | Where Jenkins, cluster and model run (15.6 GB RAM) | Local, one heavy workload at a time; GPU only on Colab/Kaggle | M14, M10t | P01 |
| D-14 | Instructor questions (AMB-01, 03, 04, 05, 09, 24, 26) | Send one combined message | M9, M11, M14 | P03 |

Academic inputs only students can give: names and roll numbers, hand-written retrieval queries, hand-checked
training labels, human verdict labels, signatures.
