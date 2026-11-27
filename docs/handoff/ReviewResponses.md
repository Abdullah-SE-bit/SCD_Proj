# Responses to the independent review of #8

[Findings](https://github.com/Abdullah-SE-bit/SCD_Proj/pull/8#pullrequestreview-6093185832). Fixes: #12 (H5, M9), #13 (M3, M4, M5, M10),
#14 (H7, M1, M2, M6, M7), #15 (H1-H4, M8, H6 mechanism), and this pull request (H6 statuses).

## Answered but not fully closed
| Item | Remaining |
|---|---|
| H3, H4, M8 | text-matching hooks cannot stop interpreters or `git apply` writing files; a subcommand built from a variable can avoid the prompt; bypass-permissions mode may skip prompts |
| M9 | ConfigMap and replica changes are not rolled back, including verdict rules (belongs to P01.05) |
| M8 | a command containing commit text in a heredoc can be denied; copying from a protected file is denied |

## Low findings
| Finding | State |
|---|---|
| `AMB-04` cites "p2/p7" | fixed here |
| Phase 0 code scope misses `scripts/*.py`, other languages and folders | open |
| requirement `verification` and `category` not frozen | open |
| deny rules in settings cover `Bash` only | open (the hook covers PowerShell) |
| `SCH-006` says "tokens"; "reachable" sentence unregistered; `DBS-001/002` do not list fields | open |
| source checksum cannot be verified in CI; `main` has no policy until promotion | accepted: PDFs are not public |
| unsalted email hashes in a public repository | open, needs a human decision with D-02 |
| `critic.json` response description; verdict request lacks gate facts; no ingress rules yet | open (P03.01, P01.01) |
| `P05.03` does not depend on `P05.06` | open: `tasks.json` change needs the human label |
| comment review chained with short flags asks | accepted: fails safe |
| authorization label persists after new pushes (primary session observation) | open: humans must recheck after a push |
