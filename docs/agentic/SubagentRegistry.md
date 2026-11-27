# Subagent registry

Reusable roles, started only when needed.

| Agent | Tools | Responsibility | Delivers |
|---|---|---|---|
| scd-requirements-auditor | Read, Grep, Glob | audits the registry against both PDFs | missed, reworded or mis-cited requirements with page numbers |
| scd-software-architect | Read, Grep, Glob | reviews boundaries, data ownership and contracts | design findings and decision-record drafts as text |
| scd-backend-engineer | Read, Grep, Glob, Edit, Write, Bash | implements Python services within one claimed task | code and tests |
| scd-frontend-engineer | Read, Grep, Glob, Edit, Write, Bash | implements UI within one claimed task | components, component tests |
| scd-database-engineer | Read, Grep, Glob, Edit, Write, Bash | writes migrations and repositories | migrations and tests |
| scd-rag-engineer | Read, Grep, Glob, Edit, Write, Bash | builds retrieval and reranking | search code and measured metrics |
| scd-data-ingestion-engineer | Read, Grep, Glob, Edit, Write, Bash | builds connectors, sanitiser and ingestion | pipeline code, counts |
| scd-agent-workflow-engineer | Read, Grep, Glob, Edit, Write, Bash | builds state machines, debate, critic and tracing | code and replay tests |
| scd-ml-engineer | Read, Grep, Glob, Edit, Write, Bash | prepares datasets, training and serving | scripts and measured results |
| scd-devops-engineer | Read, Grep, Glob, Edit, Write, Bash | builds images, manifests and pipelines | manifests, scripts, run logs |
| scd-security-auditor | Read, Grep, Glob | audits injection, egress, secrets and supply chain | findings with file and line |
| scd-qa-engineer | Read, Grep, Glob, Bash | runs tests and looks for missing cases | reproducible failures and coverage gaps |
| scd-evaluation-engineer | Read, Grep, Glob, Edit, Write, Bash | builds evaluation harnesses (never labels) | harness code and raw results |
| scd-code-reviewer | Read, Grep, Glob | reviews a diff against requirements and contracts | severity-ranked findings |
| scd-documentation-engineer | Read, Grep, Glob, Edit, Write | keeps documents truthful and current | document updates |
| scd-release-verifier | Read, Grep, Glob, Bash | verifies a phase gate or submission | pass/fail table with evidence |
