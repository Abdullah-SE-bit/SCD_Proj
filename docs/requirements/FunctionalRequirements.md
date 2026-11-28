# Functional, agent, data, model and evaluation requirements

Generated from `docs/requirements/requirements.json`. Do not edit by hand. 130 requirements.

## M1

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| USR-003 | Desc p2 §2 U3 | mandatory | U3: Watch the agents work live. Done when the screen shows the running agent, its tool calls and its spend as they happen. | Live stream shows agent, tool calls, spend during a run. | e2e | unimplemented |
| USR-006 | Desc p2 §2 U6 | mandatory | U6: Read a verdict card showing verdict, gates, six scores with evidence links, weights, confidence and stability. | Card renders every listed element. | component | unimplemented |
| USR-010 | Desc p2 §2 U10 | mandatory | U10: See why a verdict is INSUFFICIENT EVIDENCE; the card says what was missing and does not guess. | Card names missing evidence and shows no guessed verdict. | e2e | unimplemented |
| M01-004 | Desc p3 §4 | mandatory | M1 has component tests. | UI component tests run in CI. | ci | implemented |
| API-003 | Guide p2 §3 | mandatory | Public: POST /auth/register, /auth/login; GET, PUT /profile. | Endpoints exist. | contract | unimplemented |
| API-004 | Guide p2 §3 | mandatory | Public: POST /discover, /validate return a run id; GET /runs/{id} and live /runs/{id}/events (SSE or WebSocket). | Endpoints exist; stream works. | contract | unimplemented |
| API-005 | Guide p2 §3 | mandatory | Public: POST /runs/{id}/answer, /approve; POST /ideas/{id}/challenge, /whatif. | Endpoints exist. | contract | unimplemented |
| API-006 | Guide p2 §3 | mandatory | Public: GET /ideas, /ideas/{id}/versions, /compare; GET /metrics (Prometheus-style or JSON). | Endpoints exist. | contract | unimplemented |

## M2

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| USR-001 | Desc p2 §2 U1 | mandatory | U1: Sign up, log in and save a profile. Done when the profile is stored, editable, and changes later recommendations. | Register, login, edit profile; a later recommendation differs accordingly. | e2e | unimplemented |
| USR-009 | Desc p2 §2 U9 | mandatory | U9: Compare ideas and see history; past ideas and versions listed and two ideas compare on all six dimensions. | History, versions and six-dimension comparison shown. | e2e | unimplemented |
| M02-001 | Desc p3 §4 | mandatory | Postgres stores users, profiles, ideas, versions and runs; Redis caches verdicts and retrieval. | Data persisted in Postgres; cache in Redis. | integration | unimplemented |
| M02-002 | Desc p3 §4 | mandatory | Database migrations exist. | Fresh database migrates to head. | integration | unimplemented |
| M02-003 | Desc p3 §4 | mandatory | Cache keys include profile and rubric versions. | Changing either version misses cache. | unit | unimplemented |
| DBS-001 | Guide p1 §2 Fig.1 | mandatory | Application records: users, profiles, ideas, idea_versions, verdicts, dimension_scores, approvals, traces_index, conversations with listed fields. | Migrations include listed entities and fields. | integration | unimplemented |
| SCH-002 | Guide p2 §2.1 | mandatory | Student profile schema with user_id, skills, hours_per_week, weeks_available, team_size, compute (laptop, free_gpu, paid), goal (startup, portfolio, course_project), interests. | Schema contains all fields and enums. | contract | unimplemented |
| CMN-002 | Guide p8 §12 | mandatory | Cache verdicts with profile and rubric version in the key. | Same as M02-003. | unit | unimplemented |

## M3

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| USR-004 | Desc p2 §2 U4 | mandatory | U4: Approve or decline an expensive deep search. Done when the system states the cost and waits before going over budget. | Run pauses with stated cost; approve and decline both work. | e2e | unimplemented |
| USR-005 | Desc p2 §2 U5 | mandatory | U5: Submit own idea (Validate) and answer clarifying questions. Done when only questions that change the result are asked, then a verdict card is shown. | Only result-changing questions are asked; card appears. | e2e | unimplemented |
| DSC-004 | Desc p3 §3.1 Fig.2 | mandatory | Survivors go through the Validate workflow (M9 to M11); result is ranked ideas with verdict cards. | Each ranked idea has a card produced by Validate. | e2e | unimplemented |
| VAL-001 | Desc p3 §3.2 Fig.3 | mandatory | Validate intake takes idea plus profile and clarifies if needed. | Intake asks only when needed. | test | unimplemented |
| VAL-002 | Desc p3 §3.2 Fig.3 | mandatory | Evidence step retrieves cards and scouts on demand (M6, M4, M5). | Thin evidence triggers on-demand scouting within budget. | test | unimplemented |
| VAL-005 | Desc p3 §3.2 Fig.3 | mandatory | Order: verdict, then challenge (Skeptic objects, critic checks claims), then stability (sensitivity and what-would-make-GO), then card with trace and cost recorded. | Trace shows the order and cost. | test | unimplemented |
| M03-001 | Desc p3 §4 | mandatory | Supervisor runs Discover and Validate as testable state machines. | State transitions unit-tested. | unit | unimplemented |
| M03-003 | Desc p3 §4 | mandatory | Stop at budget and ask the user. | Budget exhaustion pauses and asks. | test | unimplemented |

## M4

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M04-001 | Desc p3 §4 | mandatory | Scouts bring in new data from at least 3 sources. | Three connectors produce cards. | integration | unimplemented |

## M5

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| DAT-001 | Desc p1 §1.3 | mandatory | Collect data only through official APIs or pages that allow it; respect robots.txt and rate limits. | Every source has a recorded permission basis; robots.txt and rate limits enforced by M5. | test | implemented |
| API-007 | Guide p2 §3 | mandatory | M5 POST /fetch applies allow-list, rate limit, robots.txt, cache, sanitiser. | Behaviour tested. | test | implemented |
| ETH-001 | Guide p4 §5 | mandatory | Official APIs first (HN Firebase, GitHub REST, Reddit and Product Hunt with keys); avoid scraping HTML where an API exists; read terms and robots.txt. | Source register with basis. | inspection | implemented |

## M6

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M06-001 | Desc p3 §4 | mandatory | Knowledge base is the searchable memory and the source of every piece of evidence. | Every evidence id resolves to a card. | test | unimplemented |
| M06-002 | Desc p3 §4 | mandatory | Hybrid search with reranking. | Hybrid plus rerank pipeline evaluated. | eval | unimplemented |
| M06-003 | Desc p3 §4 | mandatory | Filters by date, source and niche. | Each filter tested. | test | unimplemented |
| M06-004 | Desc p3 §4 | mandatory | Card ids for citations. | Results carry card ids. | test | unimplemented |
| M06-005 | Desc p3 §4 | mandatory | Freshness and coverage tracking. | Freshness and coverage reported. | test | unimplemented |
| M06-006 | Desc p3 §4 | mandatory | Retrieval quality measured on at least 20 hand-written queries. | >=20 human-written queries with results. | eval | unimplemented |
| DBS-002 | Guide p1 §2 Fig.1 | mandatory | Knowledge records: cards, card_sources, niches, vector store chunks, niche_stats, ingestion_runs; cards link to niches, chunks to cards, claims to card ids. | Schema includes entities and links. | integration | unimplemented |
| SCH-001 | Guide p2 §2.1 | mandatory | Idea card schema with id, name, summary, problem, customer, niche_tags, stage, funding_usd, source, url, published_at, fetched_at, text. | Schema contains all fields. | contract | unimplemented |
| SCH-003 | Guide p2 §2.2 | mandatory | Evidence item schema with evidence_id, card_id, quote, source, url, retrieved_at. | Schema contains all fields. | contract | unimplemented |
| API-008 | Guide p3 §3 | mandatory | M6 POST /search with filters returns ranked evidence items with ids. | Contract test. | contract | unimplemented |
| ETH-004 | Guide p4 §5 | mandatory | Every card keeps source and URL and the verdict card links to them. | Links present. | e2e | unimplemented |
| CIC-003 | Guide p5 §8.1 | mandatory | Retrieval quality gate fails if the score drops below the baseline. | Seeded regression fails the job. | ci | unimplemented |
| CMN-006 | Guide p8 §12 | mandatory | Test retrieval by metrics, not by eye; keep card id when splitting text. | Eval and chunk tests. | test | unimplemented |

## M6i

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M6I-001 | Desc p4 §4 | mandatory | Ingestion turns fetched pages into idea cards: dedupe, chunk, embed, index. | Pipeline stages tested. | integration | unimplemented |
| M6I-002 | Desc p4 §4 | mandatory | Ingestion is repeatable without duplicates. | Re-run adds zero duplicates. | test | unimplemented |
| M6I-003 | Desc p4 §4 | mandatory | At least 1,500 cards from at least 3 sources. | Counted card total >=1500 across >=3 sources. | measurement | unimplemented |
| ETH-006 | Guide p4 §5 | mandatory | Keep a snapshot of card data so the system does not depend on a website being up. | Restore from snapshot works offline. | test | unimplemented |

## M7

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| GEN-001 | Desc p1 §1.1 | mandatory | The system collects startup ideas, products and niches from public sources (YC directory, Hacker News, GitHub, Product Hunt or Reddit) and organises them into a map of niches and trends. | Niche map with trend series is built from collected public-source cards. | e2e | unimplemented |
| VAL-004 | Desc p3 §3.2 Fig.3 | mandatory | Features are numbers computed in code from the evidence. | Features are deterministic functions of retrieved data. | unit | unimplemented |
| M07-001 | Desc p4 §4 | mandatory | Cluster cards into niches and find rising, flat and saturated niches and gaps. | Niches labelled rising/flat/saturated with gaps. | test | unimplemented |
| M07-002 | Desc p4 §4 | mandatory | Named niches, monthly time series, and a list of gaps that feeds M8 and M9. | Outputs consumed by M8 and M9. | integration | unimplemented |

## M8

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| GEN-002 | Desc p1 §1.1 | mandatory | Discover: from a student profile (skills, hours, team size, compute, goal) the system proposes fitting ideas and niches, including new ideas built from gaps found in the data. | A Discover run returns profile-fitting ideas including at least one gap-derived idea with cited gap evidence. | e2e | unimplemented |
| USR-002 | Desc p2 §2 U2 | mandatory | U2: Ask for ideas in a niche or in general (Discover). Done when a ranked list of ideas is returned, each with a verdict and a short reason. | Ranked list with verdict and reason per idea. | e2e | unimplemented |
| DSC-001 | Desc p3 §3.1 Fig.2 | mandatory | Discover steps: request, niches (M7+M6), Ideator proposes ideas citing gap evidence, Gap Analyst adds complaints and missing features (M8+M6). | State machine test covers steps 1-4. | test | unimplemented |
| DSC-002 | Desc p3 §3.1 Fig.2 | mandatory | Skeptic argues against each idea with evidence; Critic keeps only objections backed by evidence. | Unsupported objections are dropped in tests. | test | unimplemented |
| DSC-003 | Desc p3 §3.1 Fig.2 | mandatory | Debate steps 3 to 6 repeat up to 3 rounds; ideas the Skeptic defeats with evidence are dropped. | Never exceeds 3 rounds; defeated ideas absent. | test | unimplemented |
| M08-001 | Desc p4 §4 | mandatory | Ideator, Gap Analyst and Skeptic debate to propose ideas that fit the profile. | Three roles participate; ideas fit profile. | test | unimplemented |
| M08-002 | Desc p4 §4 | mandatory | Limited debate rounds; every idea cites its gap evidence; ideas defeated with evidence are dropped. | Round cap, citations and drops tested. | test | unimplemented |

## M9

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| VAL-003 | Desc p3 §3.2 Fig.3 | mandatory | Four scorers run in parallel, each with its own rubric. | Trace shows overlapping scorer execution. | test | unimplemented |
| M09-001 | Desc p4 §4 | mandatory | Four scorers in parallel: Demand and Pain; Competition and Differentiation; Feasibility for this student; Risk. | Four scorers exist and run concurrently. | test | unimplemented |
| M09-002 | Desc p4 §4 | mandatory | Each scorer has its own rubric, tools and output schema. | Separate rubric, tool list and schema each. | inspection | unimplemented |
| M09-003 | Desc p4 §4 | mandatory | Scores combine computed features with model judgment. | Score records include features. | test | unimplemented |
| M09-004 | Desc p4 §4 | mandatory | Every score cites evidence ids, otherwise the scorer abstains. | Score without evidence is rejected as abstention. | unit | unimplemented |
| VER-002 | Desc p4 §5 | mandatory | Every score carries evidence ids and uses a versioned rubric. | Schema requires both. | contract | in_progress |
| DIM-001 | Desc p4 §5.1 | mandatory | Each of six dimensions is scored 0 to 5 (higher is better for the student) with confidence 0 to 1 and evidence ids. | Schema bounds enforced. | contract | in_progress |
| DIM-002 | Desc p4 §5.1 | mandatory | The six dimensions and what a score of 5 means: demand and pain: many independent sources show the same strong, recurring problem; competition: few or weak direct competitors, so there is room to enter; differentiation: a clear gap that existing products do not address; feasibility for this student: fits the student's hours, skills and compute with margin; risk: no legal, privacy, safety or platform-dependency concern; learning and portfolio value: teaches skills the student wants and shows well on a CV. | All six produced; each rubric's anchor 5 matches the stated meaning. | inspection | in_progress |
| DIM-003 | Desc p4 §5.1 | mandatory | Each score combines computed features with the fine-tuned model's judgment under a versioned rubric. | Score record has features, model and rubric version. | test | unimplemented |
| SCH-004 | Guide p2 §2.2 | mandatory | Dimension score schema with dimension, score, confidence, evidence_ids, features, reason, rubric_version, model. | Schema contains all fields. | contract | unimplemented |

## M10

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M10-001 | Desc p4 §4 | mandatory | Fine-tuned 1B to 3B model (LoRA or QLoRA) in its own container applies the rubrics. | Model size in range; served by own container. | inspection | unimplemented |
| M10-002 | Desc p4 §4 | mandatory | At least 300 training examples. | Training set count >=300. | measurement | unimplemented |
| M10-003 | Desc p4 §4 | mandatory | At least 60 examples checked by hand. | >=60 marked human-checked with annotator. | measurement | unimplemented |
| M10-005 | Desc p4 §4 | mandatory | Comparison of base, fine-tuned and hosted models. | Comparison table from real runs. | eval | unimplemented |
| API-009 | Guide p3 §3 | mandatory | M10 POST /score takes rubric, idea, evidence and returns dimension score JSON. | Contract test. | contract | unimplemented |
| FT-006 | Guide p4 §6.2 | mandatory | Merge adapter into base model (optionally quantise to GGUF). | Merged artefact produced. | inspection | unimplemented |

## M10t

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M10T-001 | Desc p4 §4 | mandatory | Offline pipeline with data, scripts and documented commands in the repository. | A new person can rerun from documented commands. | inspection | unimplemented |
| FT-001 | Guide p4 §6.1 | mandatory | At least 300 (idea, evidence, dimension) examples from the knowledge base covering all six dimensions and all score levels. | Coverage matrix complete. | measurement | unimplemented |
| FT-002 | Guide p4 §6.1 | mandatory | Hosted model drafts labels with the rubric; at least 60 checked by hand and fixed, marked, and used for evaluation. | Checked flag and evaluation use recorded. | inspection | unimplemented |
| FT-003 | Guide p4 §6.1 | mandatory | Split by idea, not by row (e.g. 80/20); never train on ideas from the labelled verdict set. | Leakage test passes. | test | unimplemented |
| FT-004 | Guide p4 §6.1 | mandatory | One JSON object per line with system, user and assistant messages. | Dataset validates. | contract | unimplemented |
| FT-005 | Guide p4 §6.2 | mandatory | Train on a free GPU with LoRA or QLoRA using PEFT and TRL or Unsloth; watch validation loss; record rank, learning rate, epochs, batch size in repo. | Settings and loss recorded. | inspection | unimplemented |
| FT-009 | Guide p4 §6.3 | mandatory | Run base, fine-tuned and hosted on hand-checked test examples; report MAE and share within 1 point, valid-JSON rate, real-evidence-id share, latency and cost per score. | Table with real measurements. | eval | unimplemented |
| FT-010 | Guide p4 §6.3 | mandatory | Include one example where fine-tuning did not help and explain why. | Example documented. | inspection | unimplemented |

## M11

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| GEN-003 | Desc p1 §1.1 | mandatory | Validate: for a brought or proposed idea the system returns GO, PIVOT, NO-GO or INSUFFICIENT EVIDENCE with evidence, what would change it, and how stable it is. | Verdict card shows verdict, evidence, what-would-change and stability. | e2e | unimplemented |
| USR-007 | Desc p2 §2 U7 | mandatory | U7: Ask what would make this GO; concrete changes are proposed and one can be applied, giving version 2 computed by the engine. | Apply a change and receive version 2. | e2e | unimplemented |
| USR-011 | Desc p2 §2 | mandatory | The same idea can get different verdicts for different students (profile-dependent). | Test with two profiles yields differing verdicts for a large idea. | test | unimplemented |
| M11-004 | Desc p4 §4 | mandatory | Unit tests for every gate, threshold edge, sensitivity check and what-if. | Tests enumerate each case and pass. | ci | unimplemented |
| GAT-001 | Desc p5 §5.2 | mandatory | Hard gates are checked first; a failed gate decides the verdict whatever the score. | Gate precedence tests. | unit | implemented |
| GAT-002 | Desc p5 §5.2 | mandatory | Evidence gate: at least 3 independent sources on at least 2 platforms, else INSUFFICIENT EVIDENCE. | Edge tests 2/3 sources and 1/2 platforms. | unit | implemented |
| GAT-003 | Desc p5 §5.2 | mandatory | Feasibility gate: estimated build effort fits available hours, else NO-GO with hours gap stated. | Edge test; gap stated. | unit | implemented |
| GAT-004 | Desc p5 §5.2 | mandatory | Risk gate: no legal or safety blocker, else NO-GO with blocker named. | Blocker named. | unit | implemented |
| GAT-005 | Desc p5 §5.2 | mandatory | Duplicate gate: no existing product with same core features for the same user unless Differentiation is 3 or more, else NO-GO with product named. | Edge tests at differentiation 3. | unit | implemented |
| FLW-001 | Desc p5 §5.2 Fig.4 | mandatory | Decision order: evidence, feasibility, risk, duplicate gates; weighted score; confidence check; threshold and floor check; T_no split; sensitivity check. | Order covered by tests. | unit | in_progress |
| SCR-001 | Desc p5 §5.3 | mandatory | Weighted score is sum of weight x score scaled to 0-100; weights come from the goal and add to 100. | Worked example reproduces 70.5. | unit | implemented |
| SCR-002 | Desc p5 §5.3 | mandatory | Starting weight presets for Startup, Portfolio and Course project (changes must be justified). | ConfigMap holds presets; changes have a decision record. | inspection | implemented |
| SCR-003 | Desc p5 §5.3 | mandatory | GO needs score >= T_go and no score below the floor on the first five dimensions. | Floor and threshold edge tests. | unit | implemented |
| SCR-004 | Desc p5 §5.3 | mandatory | Score between T_no and T_go, or a floor breach, gives PIVOT naming the weakest dimension; below T_no is NO-GO. | Edge tests at T_no and T_go. | unit | implemented |
| SCR-005 | Desc p5 §5.3 | mandatory | Starting values T_go 70, T_no 50, floor 1.5, to be tuned. | Defaults in config. | unit | implemented |
| SCR-006 | Desc p5 §5.3 | mandatory | Confidence = 0.7 x mean dimension confidence + 0.3 x min(1, sources/5); below 0.5 gives INSUFFICIENT EVIDENCE (abstain). | Formula and 0.5 edge tested. | unit | implemented |
| SCR-007 | Desc p5 §5.3 | mandatory | Challenge: each accepted evidence-backed objection lowers the matching score by 0.5 (at most 1.0) and its confidence by 0.1; unsupported objections discarded. | Adjustment and cap tests. | unit | unimplemented |
| SCR-008 | Desc p5 §5.3 | mandatory | Sensitivity: recompute the verdict with each weight moved up and down by 20 percent (the difference shared among the others; the worked example shares it in proportion) and the least confident score moved by one point. | Run enumeration tested. | unit | unimplemented |
| SCR-009 | Desc p5 §5.3 | mandatory | If any sensitivity run changes the verdict, the card says BORDERLINE and shows what flips it. | Flip listed on card. | unit | unimplemented |
| SCR-010 | Desc p5 §5.3 | mandatory | What would make this GO: find the smallest change that changes the verdict; applying it re-runs scorers and engine and creates a new version. | New version created after apply. | e2e | unimplemented |
| SCR-011 | Desc p6 §5.4 | mandatory | Worked example: Portfolio weights 15/15/15/25/10/20 with scores Demand 3.5, Competition 2.0, Differentiation 3.0, Feasibility 4.0, Risk 3.5, Learning 4.5 and all gates passing give 352.5/5 = 70.5 (GO); lowering the Feasibility weight from 25 to 20, sharing 5 points in proportion, gives about 69.9, so the verdict flips to PIVOT and the card says GO, BORDERLINE; raising Competition from 2.0 to 3.0 gives 73.5, and about 73.1 under the same weight change, which the document calls a stable GO (see AMB-24). | Fixtures with the stated inputs reproduce the four numbers and the stated flip. | unit | in_progress |
| SCH-005 | Guide p2 §2.3 | mandatory | Verdict schema with idea_id, version, run_id, verdict, stability, score, confidence, gates, weights, thresholds, scores, weakest_dimension, what_would_make_go, sensitivity, versions. | Schema contains all fields. | contract | implemented |
| API-010 | Guide p3 §3 | mandatory | M11 POST /verdict and /whatif take six scores, profile, config and return verdict JSON. | Contract test. | contract | in_progress |
| TUN-001 | Guide p7 §10 | mandatory | Human labelled set of ideas with profiles and human verdicts incl. clear GO, clear NO-GO, borderline and thin-evidence cases; note who labelled what (ideally independently then resolved). | Dataset with annotators exists. | inspection | unimplemented |
| TUN-002 | Guide p7 §10 | mandatory | Labelled set used only for tuning and measuring, never for training the scoring model. | Leakage test passes. | test | unimplemented |
| TUN-003 | Guide p7 §10 | mandatory | Run system on every labelled idea and build a confusion matrix against human verdicts. | Matrix from real runs. | eval | unimplemented |
| TUN-004 | Guide p7 §10 | mandatory | Tune T_go, T_no, floors and weights; report GO-on-human-NO-GO error separately. | Separate error reported. | eval | unimplemented |
| TUN-005 | Guide p7 §10 | mandatory | Final values in ConfigMap; before and after matrices in report; avoid overfitting. | Both matrices; generalisation check described. | inspection | unimplemented |

## M12

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| USR-008 | Desc p2 §2 U8 | mandatory | U8: Press Challenge on a claim; the critic re-checks it against its evidence and defends or removes it. | Challenged claim is defended or removed with reason. | e2e | unimplemented |
| M12-001 | Desc p4 §4 | mandatory | M12 stops unsupported claims and manipulation with claim check against evidence. | Unsupported claim rejected. | test | unimplemented |
| M12-004 | Desc p4 §4 | mandatory | Approval required above budget. | Over-budget action waits for approval. | test | unimplemented |
| API-011 | Guide p3 §3 | mandatory | M12 POST /check takes claims with evidence ids and returns, per claim, whether it is supported. | Contract test. | contract | unimplemented |

## M13

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| M13-001 | Desc p4 §4 | mandatory | Tracing per run. | Run trace retrievable by id. | test | unimplemented |
| M13-002 | Desc p4 §4 | mandatory | Budgets. | Budget limits enforced. | test | unimplemented |
| M13-003 | Desc p4 §4 | mandatory | Prompt and rubric registry. | Versions recorded per verdict. | test | unimplemented |
| M13-004 | Desc p4 §4 | mandatory | Evaluation harness. | Harness runs and stores results. | eval | unimplemented |
| M13-005 | Desc p4 §4 | mandatory | Drift reports. | Report generated after ingestion. | test | unimplemented |
| M13-006 | Desc p4 §4 | mandatory | Dashboard. | Dashboard shows required metrics. | demo | unimplemented |
| DBS-003 | Guide p1 §2 Fig.1 | mandatory | Files on volumes: traces/*.jsonl, prompts/ and rubrics/ versioned in git, eval/results/*.json; Redis only holds cache entries with TTL. | Layout implemented; Redis TTL set. | inspection | unimplemented |
| SCH-006 | Guide p2 §2.3 | mandatory | Trace record per step with run_id, step_id, parent_step, agent, kind, tool, input, output, tokens, cost_usd, latency_ms, retries, model, cache_hit, error, ts. | Schema contains all fields. | contract | unimplemented |
| API-012 | Guide p3 §3 | mandatory | M13 POST /trace and GET /runs/{id}/trace write and read traces. | Contract test. | contract | unimplemented |
| OPS-001 | Guide p4 §7 | mandatory | Every agent step, tool call and model call writes a trace record under one run id. | Completeness test. | test | unimplemented |
| OPS-002 | Guide p4 §7 | mandatory | A replay command re-runs a stored run using recorded tool results. | Replay reproduces decisions. | test | unimplemented |
| OPS-003 | Guide p4 §7 | mandatory | Caps on tokens, pages, steps and cost per run enforced in orchestrator and tool layer; over budget stops or asks. | Each cap tested. | test | unimplemented |
| OPS-004 | Guide p5 §7 | mandatory | Prompts and rubrics are versioned files; each verdict records versions; a change means a new version and a new evaluation. | Version bump triggers evaluation. | ci | unimplemented |
| OPS-005 | Guide p5 §7 | mandatory | Evaluation harness scores verdicts on labelled ideas (agreement, confusion matrix) and checks tools used, evidence cited, budget kept, injection resisted. | Report includes all checks. | eval | unimplemented |
| OPS-007 | Guide p5 §7 | mandatory | After each ingestion report data freshness, niche coverage and verdict distribution shift. | Drift report generated. | test | unimplemented |
| OPS-008 | Guide p5 §7 | mandatory | Dashboard: cost per verdict, latency per agent, cache hit rate, fallbacks, approvals, blocked injections. | All six metrics visible. | demo | unimplemented |
| OPS-009 | Guide p5 §7 | mandatory | Behaviour tests replay recorded model responses; cover invalid scorer JSON, tool timeout, empty source and poisoned page. | Four cases pass without a live model. | ci | unimplemented |

## M14

| ID | Source | Level | Requirement | Acceptance | Verify by | Status |
|---|---|---|---|---|---|---|
| NET-003 | Guide p7 §9.3 | mandatory | Show external access failing from a non-M5 pod and working from M5. | Recorded test. | evidence | implemented |
