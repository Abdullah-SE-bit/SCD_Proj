# Hardware feasibility

Measured 2026-11-28: Windows 11 Pro 10.0.26200; Intel i5-1335U (10 cores, 12 threads); 15.6 GB RAM (4.2 GB free
at inspection); Intel Iris Xe graphics, no NVIDIA GPU; 220 GB free on C:. Docker Desktop installed (daemon was
stopped); WSL2 Ubuntu-24.04 running; kind, minikube, kubectl, trivy, kubeconform present; no local Jenkins.

| Workload | Estimate (not measured) | Verdict |
|---|---|---|
| kind + Calico, one node | 2-3 GB | fits |
| Postgres, Redis, Qdrant | 1-1.5 GB | fits |
| ~11 small Python services, 1 replica | 1.5-2.5 GB | fits |
| Embeddings + reranker on CPU | 0.5-1.5 GB | fits, slow reranking possible |
| 1.5B model, Q4 GGUF | 1.5-2.5 GB | fits, seconds per score on CPU |
| Jenkins | 1-2 GB | fits only if idle apps are scaled down |
| Everything at once | 8-13 GB | tight: close other applications; give Docker about 10 GB |
| Fine-tuning | GPU required | Colab or Kaggle free GPU |

Replace estimates with `kubectl top` measurements in P10.01 before setting limits.
