# Federated Learning — KCG Summary

## What It Is
Two complementary projects for privacy-preserving federated machine learning. `syft-flwr` is an open-source framework combining Flower's federated learning with OpenMined's SyftBox protocol for trustless cross-silo training. `flwr` (fantastic-enigma) is a companion repo demonstrating federated supervised fine-tuning of LLMs (Llama 3.2 1B, Pythia 70M) using the Flower AI framework.

## Why This Matters for Kings' College Galway
Federated learning enables training Celtic language models on student data distributed across schools without centralising sensitive educational records — critical for GDPR compliance in Irish classrooms. The FedRAG notebook demonstrates privacy-preserving RAG across distributed document sources, directly applicable to Leaving Certificate curriculum materials held by different schools. The FL diabetes prediction pattern translates to distributed educational assessment models (predicting student performance from private gradebooks). SyftBox's trustless protocol is ideal for inter-institutional collaboration between Irish-language schools (Gaelscoileanna) where no single party should hold all data.

## Key Patterns Preserved
- `syft-flwr/README.md` — Main framework overview: Flower + SyftBox integration for federated learning
- `syft-flwr/RELEASE.md` — Release process documentation for syft-flwr
- `syft-flwr/docs/message_flow.md` — Architecture: how messages flow between Flower and SyftBox nodes
- `syft-flwr/notebooks/fl-diabetes-prediction/README.md` — Multi-round federated model training walkthrough
- `syft-flwr/notebooks/federated-analytics-diabetes/README.md` — Privacy-preserving statistical queries across distributed datasets
- `syft-flwr/notebooks/fedrag/README.md` — Federated RAG with remote data science workflow
- `flwr/README.md` — Federated LLM finetuning playground with Flower

## Source Files
Full source removed (2026-06-06). Available at:
- syft-flwr: https://github.com/OpenMined/syft-flwr
- flwr: https://github.com/adap/flower

## What Was Removed
Python source code, Jupyter notebook .ipynb files, model checkpoints, package dependencies (pyproject.toml, uv.lock), Dockerfiles, CI/CD configs, training data, images/gifs, Git metadata.
