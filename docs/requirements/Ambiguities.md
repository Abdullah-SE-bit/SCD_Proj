# Ambiguities and contradictions

Source wording is never rewritten; these are interpretations. Status of every entry: **open** until the matching decision is made; entries marked 'No' for approval are proposed defaults that apply unless changed.

| ID | Issue | Instructor clarification advisable | Human approval |
|---|---|---|---|
| AMB-01 | Six dimensions, four scorers | Yes | Yes (D-04) |
| AMB-02 | Owner of Learning and portfolio value | Yes | Yes (D-04) |
| AMB-03 | Deployable units and image count | Yes | Yes (D-05) |
| AMB-04 | Hosted model versus single internet exit | Yes | Yes (D-06) |
| AMB-05 | Weakest versus least-confident score in sensitivity | Yes | Yes (D-07) |
| AMB-06 | Floor breach and threshold precedence | No | No (low impact, follows source) |
| AMB-07 | BORDERLINE: verdict or stability, and for which verdicts | No | No |
| AMB-08 | Challenge adjustments, order and caps | Yes | Yes (D-07) |
| AMB-09 | Abstaining scorers | Yes | Yes (D-07) |
| AMB-10 | Independence of evidence sources | Yes | Yes (D-07) |
| AMB-11 | Cache invalidation | No | No |
| AMB-12 | Which clarifying questions to ask | Yes | No (revisit in P05) |
| AMB-13 | Smallest what-if change | Yes | Yes (D-07) |
| AMB-14 | Fine-tuning counts and splits | No | No |
| AMB-15 | Evaluation thresholds and baselines | No | No |
| AMB-16 | Resource limits | No | No |
| AMB-17 | Unspecified algorithms and infrastructure | No | No |
| AMB-18 | Third data source | Yes | Yes (D-09) |
| AMB-19 | Available hours and build effort | Yes | Yes (D-07) |
| AMB-20 | Assignment 1 reference | No | Yes (D-10) |
| AMB-21 | Score and verdict data flow | No | No |
| AMB-22 | Duplicate gate detection | No | No |
| AMB-23 | Rounding and boundary comparisons | No | No |
| AMB-24 | Worked example sensitivity and `flipped: 3` | Yes | Yes (D-07) |
| AMB-25 | Branch model | No | Yes (D-11) |
| AMB-26 | Which dimensions the score floor applies to | Yes | Yes (D-07) |

## AMB-01 Six dimensions, four scorers
- **Sources:** D p3 M9: four scorers (Demand and Pain; Competition and Differentiation; Feasibility; Risk). D p4 5.1: six dimensions. D p2 U6: six scores.
- **Why unclear:** Four scorers name only five dimensions.
- **Interpretations:** (a) Feasibility scorer also emits learning; (b) a fifth component emits learning; (c) computed in code from profile interests.
- **Consequences:** (b) breaks 'four scorers'; (c) breaks 'computed features plus model judgment'.
- **Recommendation:** Keep four scorers; the Competition scorer emits two scores and the Feasibility scorer emits feasibility and learning, each with its own rubric.
- **Support:** Feasibility is the only profile-aware scorer; the Competition scorer already emits two.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-04).
- **Status:** open.

## AMB-02 Owner of Learning and portfolio value
- **Sources:** D p4 5.1; D p3 M9.
- **Why unclear:** No module is assigned. Risk-free evidence for 'teaches skills' is also hard to cite as card ids.
- **Interpretations:** Same as AMB-01; evidence may be cards showing the stack, or profile interests.
- **Consequences:** Evidence gate and abstention affect this dimension most.
- **Recommendation:** Feasibility scorer; evidence = cards showing the technologies involved; abstain if none.
- **Support:** D p3: every score cites evidence ids.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-04).
- **Status:** open.

## AMB-03 Deployable units and image count
- **Sources:** D p1: one container per module. G p3: each module its own Dockerfile; 'at least 6 distinct images'. G p3 layout lists no `profile` service. G p6 9.1 lists no Deployment for M2, M4, M6i, M10t and groups 'M8 and M9'.
- **Why unclear:** Minimum count, per-module rule and the object list differ.
- **Interpretations:** (a) 6 grouped images; (b) one image per module.
- **Consequences:** (a) saves RAM but conflicts with D p1 and p4 M14.
- **Recommendation:** One image per runtime module (ui, gateway, profile, orchestrator, scouts, tools, kb, ingestion, analyst, ideation, validators, scorer, verdict, critic, agentops); M10t and evaluation are job images.
- **Support:** Description is explicit; 15 images satisfy 'at least 6'.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-05).
- **Status:** open.

## AMB-04 Hosted model versus single internet exit
- **Sources:** D p3 M10 hosted fallback; G p4 hosted labelling and comparison; D p2/p7 only M5 reaches the internet.
- **Why unclear:** Calling a hosted model needs egress from M3/M8/M10.
- **Interpretations:** (a) route model calls through M5; (b) allow egress for a second, model-gateway pod; (c) M5 exposes a dedicated proxy endpoint.
- **Consequences:** (b) contradicts 'only M5'.
- **Recommendation:** (c): M5 adds `POST /llm` with its own allow-list, budget and no sanitising of prompts; the key lives only in M5.
- **Support:** Keeps NetworkPolicy rule literal.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-06).
- **Status:** open.

## AMB-05 Weakest versus least-confident score in sensitivity
- **Sources:** D p5 5.3: 'least confident score moved by one point'. D p5 Fig.4: 'weakest score +/- 1'.
- **Why unclear:** Different dimensions may be perturbed.
- **Interpretations:** (a) least confident; (b) weakest; (c) both.
- **Consequences:** (c) changes the run count from 14.
- **Recommendation:** (a) least confident (ties: lower score, then fixed dimension order).
- **Support:** Prose is the detailed rule and G p2 example has 14 runs = 12 weight + 2 score.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-07).
- **Status:** open.

## AMB-06 Floor breach and threshold precedence
- **Sources:** D p5 5.3: floor breach gives PIVOT; below T_no is NO-GO. Fig.4: failing 'score >= T_go and floor' tests score >= T_no.
- **Why unclear:** A breach with score below T_no matches two sentences.
- **Interpretations:** NO-GO or PIVOT.
- **Consequences:** Affects tuning.
- **Recommendation:** Follow Fig.4: below T_no is NO-GO even with a floor breach.
- **Support:** Figure resolves the order explicitly.
- **Instructor clarification:** No. **Human approval:** No (low impact, follows source).
- **Status:** open.

## AMB-07 BORDERLINE: verdict or stability, and for which verdicts
- **Sources:** Fig.4 shows BORDERLINE as an outcome reached only from GO. D p5: any flipping run marks the card BORDERLINE. D p6: 'GO, BORDERLINE'. G p2: verdict enum without BORDERLINE; stability STABLE or BORDERLINE.
- **Why unclear:** Outcome versus attribute; scope.
- **Interpretations:** Attribute on every scored verdict, or only on GO.
- **Consequences:** API shape and UI.
- **Recommendation:** `stability` attribute; computed for every verdict that reached scoring.
- **Support:** Schema and worked example agree.
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-08 Challenge adjustments, order and caps
- **Sources:** D p3 Fig.3: verdict (5) → challenge (6) → stability (7). D p5: each accepted objection −0.5 (at most 1.0) and confidence −0.1.
- **Why unclear:** Whether the verdict is recomputed; whether the cap is per dimension or total; whether confidence is capped; whether gates re-run.
- **Interpretations:** Per-dimension cap with confidence capped at −0.2, or uncapped confidence.
- **Consequences:** Changes results.
- **Recommendation:** M11 recomputes gates and score after adjustments; cap per dimension; confidence reduced only for counted objections (max −0.2); clamp to ranges; pre-challenge result kept in the trace.
- **Support:** 'lowers the matching score by 0.5 (at most 1.0) and its confidence by 0.1'.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-07).
- **Status:** open.

## AMB-09 Abstaining scorers
- **Sources:** D p3 M9: no evidence ids → abstain. D p5: weighted sum and mean confidence over dimensions.
- **Why unclear:** Value of an abstained dimension is undefined.
- **Interpretations:** (a) count as 0; (b) renormalise weights; (c) INSUFFICIENT EVIDENCE if any abstains; (d) renormalise but confidence counts 0.
- **Consequences:** (a) guesses a score; (b) alone hides missing data.
- **Recommendation:** (d), and INSUFFICIENT EVIDENCE if a floor dimension abstains; card names it (U10). Risk or differentiation abstention cannot pass their gate by default.
- **Support:** U10 'does not guess'.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-07).
- **Status:** open.

## AMB-10 Independence of evidence sources
- **Sources:** D p5: '3 independent sources on at least 2 platforms'; confidence uses min(1, sources/5).
- **Why unclear:** Source may mean card, URL, domain or author; scope per idea or per dimension.
- **Interpretations:** Distinct canonical URL domains+items; distinct cards after dedupe.
- **Consequences:** Gate strictness.
- **Recommendation:** A source is a deduplicated card with a distinct canonical URL; platform is the card's `source`; counted over all evidence cited for the idea.
- **Support:** G p1 card_sources has platform and url.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-07).
- **Status:** open.

## AMB-11 Cache invalidation
- **Sources:** D p3 M2 and G p8: keys include profile and rubric versions.
- **Why unclear:** Engine, config, model and knowledge-base changes also change answers.
- **Interpretations:** Minimum or extended key.
- **Consequences:** Stale verdicts.
- **Recommendation:** Key = idea version, profile version, rubric versions, engine and config version, model id, KB snapshot id; TTL as backstop.
- **Support:** 'Minimums: you may add' (G p1).
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-12 Which clarifying questions to ask
- **Sources:** D p2 U5: only questions that change the result.
- **Why unclear:** No method given.
- **Interpretations:** (a) ask when a gate or verdict differs across plausible answers (simulate with M11); (b) model decides.
- **Consequences:** (b) is untestable.
- **Recommendation:** (a) using a small fixed question set tied to engine inputs.
- **Support:** Testable with the deterministic engine.
- **Instructor clarification:** Yes. **Human approval:** No (revisit in P05).
- **Status:** open.

## AMB-13 Smallest what-if change
- **Sources:** D p5: 'smallest change that changes the verdict'; heading 'make this GO'; U7 version 2; applying re-runs scorers.
- **Why unclear:** Metric of 'smallest'; target verdict; numeric change versus textual change.
- **Interpretations:** Minimum total score delta to reach GO in 0.5 steps; ties by weight.
- **Consequences:** Re-scored result may differ from the numeric prediction.
- **Recommendation:** Search score deltas (single, then pairs) to reach GO and be stable; present as a suggested change; after apply, show the re-scored result honestly.
- **Support:** U7 and the worked example target GO.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-07).
- **Status:** open.

## AMB-14 Fine-tuning counts and splits
- **Sources:** D p4: at least 300 training examples, 60 checked. G p4: collect at least 300 examples; use checked ones for evaluation; split by idea.
- **Why unclear:** Whether the 60 are inside the 300.
- **Interpretations:** 300 total (240 train) or 300 train plus 60 evaluation.
- **Consequences:** Compliance risk.
- **Recommendation:** At least 300 training rows plus at least 60 hand-checked evaluation rows from disjoint ideas (360+).
- **Support:** Satisfies both readings.
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-15 Evaluation thresholds and baselines
- **Sources:** G p5: retrieval gate fails below baseline; Jenkins compares with stored baseline.
- **Why unclear:** Metric, tolerance and how baselines update are unspecified.
- **Interpretations:** recall@5 and MRR with tolerance.
- **Consequences:** Flaky or toothless gates.
- **Recommendation:** recall@5 primary, MRR secondary; baseline committed by reviewed PR; no tolerance for retrieval (deterministic); nightly tolerance decided from measured variance.
- **Support:** G p8 example uses recall at 5.
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-16 Resource limits
- **Sources:** G p6: requests and limits from measurements.
- **Why unclear:** No values before measurement.
- **Interpretations:** Measure then set.
- **Consequences:** Guessing violates the rule.
- **Recommendation:** Set only after `kubectl top` measurement (P10.01); record the data.
- **Support:** Explicit rule.
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-17 Unspecified algorithms and infrastructure
- **Sources:** Both documents.
- **Why unclear:** Clustering, trend classification, effort estimation, duplicate detection, rate limits, vector store, frameworks.
- **Interpretations:** See TechnologyResearch.
- **Consequences:** Design effort.
- **Recommendation:** Record each as a decision record when made.
- **Support:** Guide allows free choice.
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-18 Third data source
- **Sources:** D p1 YC directory, HN, GitHub, Product Hunt or Reddit; at least 3 (M4). Fig.1 marks PH/Reddit optional.
- **Why unclear:** YC has no official API; its robots.txt disallows `/companies?*`. Reddit access needs approval. Product Hunt needs a token and its terms need checking.
- **Interpretations:** HN + GitHub + (Product Hunt | YC permitted pages | yc-oss mirror).
- **Consequences:** Ethics rule D p1.
- **Recommendation:** HN and GitHub plus Product Hunt official API; fallback needs instructor agreement.
- **Support:** Guide 5 'official APIs first'.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-09).
- **Status:** open.

## AMB-19 Available hours and build effort
- **Sources:** D p5 Feasibility gate; G p2 profile has hours_per_week, weeks_available, team_size.
- **Why unclear:** Whether team size multiplies; who estimates effort.
- **Interpretations:** hours×weeks×team; per person.
- **Consequences:** Gate outcome.
- **Recommendation:** Available = hours_per_week × weeks_available × team_size; effort estimate = scorer feature with evidence, shown on card.
- **Support:** D p2 '200 free hours' for a team.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-07).
- **Status:** open.

## AMB-20 Assignment 1 reference
- **Sources:** D p3 M2.
- **Why unclear:** Layering rules are in a document not supplied.
- **Interpretations:** Use routes/services/repositories as stated.
- **Consequences:** Marking detail may be missed.
- **Recommendation:** Follow the parenthesis; ask the user for Assignment 1.
- **Support:** Only information available.
- **Instructor clarification:** No. **Human approval:** Yes (D-10).
- **Status:** open.

## AMB-21 Score and verdict data flow
- **Sources:** Fig.1 M9→M10 'scores', M10→M11, M11→M12 'verdict'; G p2 M9 scores using M10; G p3 M11 POST /verdict takes six scores.
- **Why unclear:** Arrows read as direct calls; the API tables suggest orchestrated calls.
- **Interpretations:** Orchestrator-mediated or direct chain.
- **Consequences:** Service coupling.
- **Recommendation:** M9 calls M10; M3 calls M11 and M12. The deviation is stated in the report.
- **Support:** M3 is the supervisor.
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-22 Duplicate gate detection
- **Sources:** D p5: same core features for same user unless Differentiation ≥ 3.
- **Why unclear:** How 'same' is judged; whether pre- or post-challenge differentiation.
- **Interpretations:** Feature overlap computed from KB matches.
- **Consequences:** False NO-GO.
- **Recommendation:** Scorer reports the matched card and overlap as features; M11 applies the rule to the post-challenge score.
- **Support:** M11 must stay model-free.
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-23 Rounding and boundary comparisons
- **Sources:** D p5, p6: >= thresholds; example rounds to one decimal.
- **Why unclear:** Compare raw or rounded values.
- **Interpretations:** Raw.
- **Consequences:** Edge flips.
- **Recommendation:** Compare unrounded values with `>=`; round only for display.
- **Support:** Determinism (M11).
- **Instructor clarification:** No. **Human approval:** No.
- **Status:** open.

## AMB-24 Worked example sensitivity and `flipped: 3`
- **Sources:** D p6 example; G p2 `sensitivity: {runs: 14, flipped: 3}`.
- **Why unclear:** Recomputed: exactly 3 of the 12 weight runs flip 70.5 (competition +20%, feasibility −20%, learning −20%), but the least-confident score −1 also drops any dimension below 70, which would make 4. D p6 calls 73.5 'stable' after testing one weight change; −1 on feasibility (68.5) or learning (69.5) would still flip it.
- **Interpretations:** The example is illustrative, or score runs are excluded from `flipped`.
- **Consequences:** Unit tests must not assert numbers the rules contradict.
- **Recommendation:** Implement the prose rules; assert 70.5, 69.9, 73.5, 73.1 and the three weight flips; do not assert `flipped: 3` for 14 runs. Ask the instructor.
- **Support:** Arithmetic.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-07).
- **Status:** open.

## AMB-25 Branch model
- **Sources:** G p3, p5: feature branch → PR → main with one review. Project instruction adds `dev` between them.
- **Why unclear:** Task PRs into dev need no approval under the instruction, while D p1 requires mutual review.
- **Interpretations:** Review on dev too, or only on promotion.
- **Consequences:** Review evidence.
- **Recommendation:** Keep dev; require a peer review comment on every task PR as policy, one approval enforced on main.
- **Support:** Satisfies both.
- **Instructor clarification:** No. **Human approval:** Yes (D-11).
- **Status:** open.

## AMB-26 Which dimensions the score floor applies to
- **Sources:** D p5 Fig.4: "Score >= T_go and no dimension below floor?". D p5 5.3: "no score below the floor on the first five dimensions".
- **Why unclear:** the figure covers all six; the text excludes learning and portfolio value.
- **Interpretations:** (a) first five (text); (b) all six (figure).
- **Consequences:** under (b) a low learning score turns a GO into PIVOT.
- **Recommendation:** (a), as in `config/verdict.defaults.json`.
- **Support:** the text is the detailed rule and names the dimensions.
- **Instructor clarification:** Yes. **Human approval:** Yes (D-07).
- **Status:** open.
