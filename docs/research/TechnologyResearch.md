# Technology research

Date: 2026-11-28. Versions from PyPI, npm, GitHub releases and the Hugging Face API on that date. All choices
are **proposed** (decision D-03). Estimates are labelled; nothing here was benchmarked.

## Criteria
Compatibility with both documents, effort, reliability, CPU and RAM (the build machine has 15.6 GB, no NVIDIA
GPU), cost, licence, testability, Kubernetes fit, learning value.

## Choices
| Area | Primary | Alternative | Fallback | Reason |
|---|---|---|---|---|
| Frontend | React 19 + TypeScript + Vite 8 | Next.js 16 | server-rendered templates | static bundle behind a small web server; runtime API URL; Next adds a server we do not need |
| Frontend tests | Vitest + Testing Library; Playwright for e2e | Jest | - | native to Vite |
| Backend | Python 3.12 + FastAPI + Pydantic v2 | Flask | - | guide examples use 3.12, uvicorn, pytest; schema validation built in |
| API schemas | JSON Schema + OpenAPI in `contracts/` | Pydantic-only export | - | guide 2: define each schema once |
| Orchestration | explicit Python state machine with asyncio | LangGraph 1.2 (MIT) | - | testable, no framework lock-in; adopt LangGraph only if persistence or interrupts get costly |
| Database | PostgreSQL + SQLAlchemy 2.1 + Alembic | psycopg + SQL files | - | migrations required |
| Cache | Redis | Valkey | in-process (tests only) | guide names Redis; check Redis licence terms for the chosen version |
| Vector store | Qdrant (Apache-2.0 client) | pgvector + Postgres full text | Chroma | dense + sparse hybrid with payload filters; guide shows a separate vector-store volume |
| Embeddings | BAAI/bge-small-en-v1.5 (MIT, 33M params) on CPU | e5-small | hosted | small enough for CPU |
| Reranker | cross-encoder MiniLM (check licence at adoption) | BAAI/bge-reranker-base (MIT, 278M params) | none (not compliant) | CPU latency |
| Clustering | scikit-learn HDBSCAN or KMeans | BERTopic | keyword niches | fewer dependencies |
| Trends | monthly counts and slope in SQL/Python | forecasting library | - | requirement is rising/flat/saturated |
| Connectors | httpx via M5; HN Firebase API, GitHub REST | HN Algolia search | snapshot | official APIs first |
| Hosted LLM | OpenAI-compatible client; Gemini or Groq free tier | OpenRouter free models | paid key | provider swappable; free limits change often and may use prompts for training |
| Base model | Qwen/Qwen2.5-1.5B-Instruct (Apache-2.0, 1.54B) | Qwen/Qwen3-1.7B (Apache-2.0, 2.03B) | SmolLM2-1.7B-Instruct (Apache-2.0) | in the 1B-3B range, ungated; Llama 3.2 and Gemma are gated |
| Training | Unsloth + TRL QLoRA on Colab or Kaggle GPU | PEFT + TRL | - | guide 6.2 |
| Serving | merged GGUF on llama.cpp behind FastAPI | Ollama | transformers CPU | CPU serving, exact `/score` contract |
| Cluster | kind + Calico | minikube `--cni=calico` | k3d + Calico | enforced NetworkPolicy; kindnet now documents enforcement, but Calico is what the guide names |
| Registry | GHCR | local registry | `kind load` | free for public images |
| Monitoring | dashboard page reading `/metrics` | Prometheus + Grafana | - | guide allows it and it saves RAM |
| Evaluation | pytest + small harness | Ragas | - | metrics are specified |
| Security | gitleaks, Trivy 0.76.2 (digest-pinned), pip-audit, bandit | Semgrep | - | free, scriptable |
| Infra validation | kubeconform, actionlint | kubeval | - | maintained |

## Source findings that change the plan
- Trivy supply chain was compromised in March 2026 (GHSA-69fq-xp46-6x23: trivy 0.69.4, trivy-action < 0.35.0).
  We run a digest-pinned 0.76.2 image and no Trivy action.
- Reddit API access now needs prior approval and is being migrated (third-party reports; verify on Reddit).
  Do not depend on Reddit.
- YC `robots.txt` (fetched today) disallows `/companies?*`; YC offers no official public API. `yc-oss/api` is an
  unofficial mirror with no declared licence.
- HN website `robots.txt` sets `Crawl-delay: 30`; use the official API instead of pages.
- A paid Claude plan does not include API usage for an application (some plans include limited API credits:
  check current terms). Budget a separate provider.

## References
- https://github.com/aquasecurity/trivy/security/advisories/GHSA-69fq-xp46-6x23
- https://kindnet.sigs.k8s.io/docs/user/network-policies/
- https://docs.tigera.io/calico/latest/getting-started/kubernetes/kind
- https://www.ycombinator.com/robots.txt · https://github.com/yc-oss/api
- https://www.producthunt.com/v2/docs (terms: https://www.producthunt.com/terms-of-service, not yet reviewed)
- https://support.claude.com/en/articles/9876003
- https://unsloth.ai/docs/get-started/unsloth-notebooks
- https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct
