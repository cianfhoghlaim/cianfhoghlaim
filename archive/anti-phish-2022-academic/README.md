# anti-phish (2022 academic)

> **Moved to `archive/anti-phish-2022-academic/` on 2026-06-24.**
> This is a 2022 personal research project, NOT a production Cianfhoghlaim HuggingFace Space.

The 6 Colab notebooks + the academic README are preserved here
for personal archival purposes. The original `spaces/anti-phish/`
directory was deleted from the public monorepo because:

1. **Inappropriate public content** — the README contains deeply
   personal 2026 reflection (mentions validated disability + MSc
   in AI in September + grandmother dying + Assisted Dying) that
   does not belong in a public KCG Space.
2. **Stale technology** — the 6 Colab notebooks use pre-2022
   classical ML / PyTorch / HuggingFace Transformers / Flower
   federated learning patterns that have since been superseded
   by the KCG canonical stack (celtic-language-ai + irish-llm-on-device
   + unsloth + peft).
3. **Not a Space** — the directory has 6 .ipynb files and no
   `app.py`; it was never a deployable HF Space.

The 6 notebooks are:

1. `1_Data_Extraction.ipynb`
2. `2_Classical_Machine_Learning_Models.ipynb`
3. `3_PyTorch_Deep_Learning_Models.ipynb`
4. `4_Huggingface_Transformers.ipynb`
5. `5_Flower_Federated_Learning.ipynb`
6. `6_Gradio_Front_End.ipynb`

The original README is preserved verbatim at
`README.md` (this archive).

If you want to re-publish this work as a public HF Space, the
recommended path is to create a new `spaces/anti-phish-2026/`
directory that:
- Uses the KCG canonical stack (LiteLLM gateway + BAML + ccc +
  Cognee)
- Does NOT include the personal reflection
- Is a deployable Gradio app (not a set of Colab notebooks)
- Has an openspec change (`modernize-anti-phish-space`)
