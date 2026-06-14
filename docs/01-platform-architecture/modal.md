---
title: 'Modal — Serverless GPU Cloud'
domain: 'architecture'
status: 'stable'
description: 'Modal is a serverless cloud platform for running Python code on GPUs. It provides on-demand access to A100, H100, and L40S GPUs with per-second billing, containerised execution, and a Python-native API. No Kubernetes, no cluster management — just decorate a function and it runs i'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/modal.md
ccc_query_hints:
  - modal — serverless gpu cloud
truth: partial

---

# Modal — Serverless GPU Cloud

## Overview

Modal is a serverless cloud platform for running Python code on GPUs. It provides on-demand access to A100, H100, and L40S GPUs with per-second billing, containerised execution, and a Python-native API. No Kubernetes, no cluster management — just decorate a function and it runs in the cloud.

## Why This Matters for Kings' College Galway

The MacBook M4 handles daily fine-tuning, but large-scale experiments — full-parameter fine-tuning of 13B+ models, multi-GPU training, or processing the complete multi-nation curriculum corpus at scale — benefit from cloud GPU acceleration. Modal provides on-demand H100 GPUs for these burst workloads without maintaining a permanent GPU cluster. The per-second billing model means a 2-hour fine-tuning run costs exactly 2 hours of GPU time, not a monthly reservation.

## Key Features

- **On-demand GPUs** — A100, H100, L40S with per-second billing
- **Python-native** — `@app.function(gpu="H100")` decorator
- **Serverless** — No cluster management or provisioning
- **Containerised** — Each function runs in an isolated container
- **Volume storage** — Persistent storage for datasets and model weights

## Installation

```bash
uv add modal
```

## Integration with Our Stack

Modal is used for large-scale training runs that exceed the MacBook M4's capacity. Training scripts are adapted from Unsloth/TRL workflows with Modal's function decorator. Results (models, metrics) are synced back to Garage S3 for local serving via llama-swap.

## Upstream

- **Repository**: <https://github.com/modal-labs/modal-client>
- **Documentation**: <https://modal.com/docs>
- **Latest**: H100 GPU availability, improved cold start times, Python 3.12 support

## Screenshot

Modal's web dashboard at `modal.com` shows function invocations with execution time, GPU utilisation, and logs. The CLI (`modal deploy`, `modal run`) provides deployment and invocation commands. Function output appears in terminal with streaming logs.
