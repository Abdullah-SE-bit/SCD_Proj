# Technology stack

Status: **proposed, not locked** (D-03). No application dependency is committed.

| Layer | Proposed |
|---|---|
| UI | React, TypeScript, Vite, Vitest, Playwright |
| Services | Python 3.12, FastAPI, Pydantic v2, httpx, pytest, ruff, mypy |
| Data | PostgreSQL, SQLAlchemy, Alembic, Redis, Qdrant |
| Retrieval | bge-small embeddings, cross-encoder reranker |
| Model | Qwen2.5-1.5B-Instruct, Unsloth/TRL QLoRA, GGUF on llama.cpp |
| Platform | Docker, kind + Calico, GHCR, GitHub Actions, Jenkins |
| Ops and security | JSON-lines traces, `/metrics`, Trivy, gitleaks, pip-audit, bandit, kubeconform |

Locked today (harness only): Python 3.12 in CI and the versions in `requirements-dev.txt`.
