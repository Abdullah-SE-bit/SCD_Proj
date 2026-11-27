# Environment verification report (2026-11-28)

| Item | Result |
|---|---|
| OS | Windows 11 Pro 10.0.26200; Claude Code native on Windows (shells: PowerShell, Git Bash); WSL2 Ubuntu-24.04 present |
| Hardware | i5-1335U, 12 threads, 15.6 GB RAM, no NVIDIA GPU, 220 GB free |
| Tools | Claude Code 2.1.332, Git 2.55.0, gh 2.98.0, Node 24.18.0, Python 3.14.6, uv 0.13.7, kubectl 1.36.1, kind, minikube, trivy, kubeconform, Java 17 |
| Missing locally | helm, k3d, gitleaks, actionlint, hadolint, Jenkins |
| Docker | Desktop installed; daemon stopped at inspection |
| GitHub accounts | Abdullah-SE-bit and Demidoga in `gh` keyring; shared active account = Abdullah-SE-bit |
| Clones | `SCD_Proj`, `SCD_Proj_demidoga` (sibling folders; lower-case `demidoga`) |
| Git identities | separate local user.name and user.email per clone |
| Push identity | before Phase 0 both clones pushed with the shared active account; fixed with a per-clone credential helper; verified: each helper's token resolves to its own login |
| Repository | public; main and dev; collaborators Abdullah-SE-bit (admin), Demidoga (write); no prior protection, rulesets, workflows, issues or PRs |
| Repository security | secret scanning and push protection enabled |
| Hooks before Phase 0 | user plugins only; no project hooks |
| Cross-session | desktop session start and messaging available; verification result in the Phase 0 report |
