# KCG_SUMMARY: IRLBench — Irish-English Bilingual LLM Benchmark

## What It Is
IRLBench is a multi-modal, culturally grounded, parallel Irish-English benchmark for evaluating Large Language Model (LLM) reasoning in low-resource languages. Based on 12 subjects from the 2024 Irish Leaving Certificate examinations, it provides open-ended (long-form) evaluation rather than multiple-choice, using the official marking scheme for assessing both correctness and language fidelity. The benchmark reveals that even the best models answer correctly only 55.8% of the time in Irish versus 76.2% in English, and produce valid Irish responses less than 80% of the time.

## Why This Matters for Kings' College Galway
IRLBench is the first standardised benchmark for Irish-language LLM evaluation and is directly aligned with the Irish secondary school curriculum — the very Leaving Certificate exams that Kings' College Galway students are preparing for. For the **teanga** platform, this benchmark provides: (1) an evaluation framework to measure how well AI tutors perform in Irish across subjects, (2) a dataset of real exam questions for building subject-specific Irish-language QA systems, (3) evidence for the persistent Irish-English performance gap that the school's AI tools must address, and (4) a methodology for culturally grounded evaluation that avoids the cultural bias in standard LLM benchmarks.

## Key Patterns Preserved
- `readme.md` — Full benchmark description, 12-subject structure, evaluation methodology (LLM-as-judge with marking scheme), directory layout, and usage instructions for extraction, response generation, judgement, and result analysis

## Source Files
Full source code was removed on 2026-06-06. The dataset is available at huggingface.co/datasets/ReliableAI/IRLBench. The evaluation codebase is at the original repository. This skeleton preserves the benchmark methodology and evaluation framework description.

## What Was Removed
- Python scripts (extraction, response generation, judgement, analysis, visualisation)
- Dataset files (exam questions in Irish and English)
- LLM response and judgement data
- Visualisation outputs
- Environment configuration files
