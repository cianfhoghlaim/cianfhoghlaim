## Why

`spaces/anti-phish/` was a 2022 personal academic project, NOT a
production Cianfhoghlaim HuggingFace Space. The directory has
6 Colab notebooks + a README, not an `app.py`. The README
contains a 2026 personal reflection that mentions validated
disability + MSc in AI in September + grandmother dying + Assisted
Dying — deeply personal content that does not belong in a public
KCG Space.

The 6 Colab notebooks use pre-2022 classical ML / PyTorch /
HuggingFace Transformers / Flower federated learning patterns
that have since been superseded by the KCG canonical stack
(`celtic-language-ai` + `irish-llm-on-device` + `unsloth` + `peft`).

This change moves the 6 notebooks + the original README to
`archive/anti-phish-2022-academic/` (private, not pushed to
HF) and replaces the public README with a 1-paragraph "moved
to private archive" notice pointing at the future path for
re-publication (a `spaces/anti-phish-2026/` directory that uses
the KCG canonical stack).

## What changes

- `spaces/anti-phish/` → `archive/anti-phish-2022-academic/`
  (git mv; preserves history)
- `archive/anti-phish-2022-academic/README.md` (the new 1-paragraph
  "moved to private archive" notice; the original README is at
  `archive/anti-phish-2022-academic/README.md.bak`)
- 1 ADDED Requirement to the `infrastructure-stacks` spec

## Out of scope

- Re-publishing the work as a public HF Space. That requires a
  new openspec change (`modernize-anti-phish-space`) that
  rebuilds the directory with the KCG canonical stack.
- The 6 Colab notebooks remain in the private archive; they
  are NOT deleted.
