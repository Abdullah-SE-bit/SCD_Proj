# Phase 0 handoff: review brief

- Repository: https://github.com/Abdullah-SE-bit/SCD_Proj
- Branches: `chore/phase-0-bootstrap` → `dev` → `main`
- Author: `Abdullah-SE-bit` (clone `SCD_Proj`). Reviewer: `Demidoga` (clone `SCD_Proj_demidoga`).
- Scope: Phase 0 only. **Do not start application implementation.**
- Sources: `docs/source/*.pdf` in your clone (checksums in `docs/source/CHECKSUMS.sha256`).
- Registry: `docs/requirements/requirements.json`. Documents: `docs/README.md`.
- PR numbers and CI results: in the promotion PR description.

## Review
1. `python harness/verification/scd.py identity` must report `Demidoga`.
2. `git fetch origin`; read `git diff origin/main...origin/dev`.
3. Audit both PDFs page by page against the registry (agent `scd-requirements-auditor` may help).
4. Review architecture, contracts, plan, structure, skills, agents, hooks, permissions, workflow.
5. Check protection: `python harness/verification/scd.py gh -- api repos/Abdullah-SE-bit/SCD_Proj/branches/main/protection`.
6. Confirm no application code and no secrets.
7. `uv run --no-project --python 3.12 --with-requirements requirements-dev.txt python harness/verification/scd.py all`.
8. Post a comment review with findings. Do **not** approve because you were asked. Show Asad the findings;
   submit approve or request-changes only on Asad's decision, saying Claude assisted. Merge only after approval
   and green checks.

Known limitations: `docs/handoff/KnownLimitations.md`.
