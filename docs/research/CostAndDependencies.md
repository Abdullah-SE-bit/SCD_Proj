# Cost, dependencies and external services

| Service | Purpose | Credential | Cost expectation | Status |
|---|---|---|---|---|
| GitHub + Actions | code, CI | gh login | free for a public repository | in use |
| GHCR | images | token in Jenkins | free for public images | not set up |
| Hacker News API | source 1 | none | free | not used yet |
| GitHub REST API | source 2 | token recommended | free, rate limited | not used yet |
| Product Hunt API | source 3 (proposed) | developer token | free; **terms unreviewed** | needs human |
| Hosted LLM | labels, agents, fallback, comparison | API key | free tier possible; limits change | needs human (D-12) |
| Colab / Kaggle | training | account | free GPU with limits | needs human |
| Hugging Face | base model download | none for proposed models | free | not used yet |

No paid service is authorised. A Claude subscription is development tooling, not application runtime.
Dependencies on websites are limited by keeping a card snapshot (ETH-006).
