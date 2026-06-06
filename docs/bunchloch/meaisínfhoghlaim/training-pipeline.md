# training pipeline

> Auto-merged from subdirectory .md files on 2026-06-06

---


## File: docs/meaisínfhoghlaim/training/KCG_SUMMARY.md

# Training — KCG Summary

## What It Is
Three resources for LLM training and deployment. `open-instruct` (Allen AI) is the reference codebase for post-training open language models — used to build the Tülu 3 suite via SFT, DPO, and RLVR (reinforcement learning with verifiable rewards). `phone/` contains research notes on deploying fine-tuned LLMs and VLMs on iOS/Android devices. `utils/` holds auxiliary training utilities.

## Why This Matters for Kings' College Galway
Open-instruct is the blueprint for fine-tuning Irish-language models: the SFT → DPO → RLVR pipeline maps directly to curriculum-tuned LLMs that can generate Leaving Certificate answers with structured reasoning. The Tülu 3 recipe for mixing general + specialised data informs how to blend Irish educational content with general English capability. Phone deployment research supports the "Irish LLM on iPhone" vision — models accessible to every Irish secondary student without cloud dependency. The multi-node training scripts provide patterns for scaling from single-GPU Unsloth fine-tuning to distributed training on the M4 MacBook cluster.

## Key Patterns Preserved
- `open-instruct/README.md` — Project overview: Tülu 3 pipeline, available models, setup
- `open-instruct/AGENTS.md` — AI agent instructions for working with open-instruct
- `open-instruct/CLAUDE.md` — Claude-specific coding guidelines
- `open-instruct/docs/index.md` — Documentation index
- `open-instruct/docs/algorithms/finetune.md` — SFT training recipe and configuration
- `open-instruct/docs/algorithms/dpo.md` — Direct Preference Optimisation pipeline
- `open-instruct/docs/algorithms/grpo.md` — Group Relative Policy Optimisation (RLVR)
- `open-instruct/docs/algorithms/online_dpo.md` — Online DPO variant
- `open-instruct/docs/algorithms/ppo.md` — Proximal Policy Optimisation
- `open-instruct/docs/algorithms/rejection_sampling.md` — Rejection sampling for synthetic data
- `open-instruct/docs/algorithms/reward_modeling.md` — Reward model training
- `open-instruct/docs/algorithms/synthetic_preference_dataset.md` — Synthetic preference data generation
- `open-instruct/docs/algorithms/trained_model_location.md` — Where to find trained checkpoints
- `open-instruct/docs/data/preference-data.md` — Preference dataset format and sources
- `open-instruct/docs/get_started/installation.md` — Installation with uv
- `open-instruct/docs/get_started/ai2_internal_setup.md` — Allen AI internal infrastructure
- `open-instruct/docs/olmo2.md` — OLMo 2 model training specifics
- `open-instruct/docs/tulu1_tulu2.md` — Tülu 1 and 2 history
- `open-instruct/docs/tulu3.md` — Tülu 3 details and results
- `open-instruct/docs/safety.md` — Safety evaluation approach
- `open-instruct/docs/safety-eval/safety.md` — Safety evaluation methodology
- `open-instruct/docs/ai2_internal.md` — Internal infrastructure notes
- `open-instruct/docs/dataset_transformation.md` — Dataset transformation pipeline
- `open-instruct/human_eval/README.md` — Human evaluation setup
- `open-instruct/scripts/README.md` — Scripts overview
- `open-instruct/scripts/train/olmo3/README.md` — OLMo 3 training configuration
- `open-instruct/scripts/data/azure_batch/README.md` — Azure batch processing
- `open-instruct/scripts/data/filtering_and_updates/README.md` — Data filtering and deduplication
- `open-instruct/scripts/data/filtering_and_updates/TEST_README.md` — Testing for filtering scripts
- `open-instruct/scripts/persona_driven_data_gen/README.md` — Persona-driven synthetic data
- `open-instruct/scripts/synth_pref/README.md` — Synthetic preference data generation
- `open-instruct/decontamination/README.md` — Training set decontamination
- `phone/docs/Federated AI Marketplace on iPhone.md` — Federated learning on iOS research
- `phone/docs/Fine-tuning VLMs for iOS HTR.md` — Vision-language models for handwriting recognition on iPhone
- `phone/docs/How to Run and Deploy LLMs on your iOS or Android Phone _ Unsloth Documentation.md` — Mobile LLM deployment guide
- `phone/docs/Irish LLM for iPhone Development.md` — Irish-specific mobile LLM strategy

## Source Files
Full source removed (2026-06-06). Available at:
- open-instruct: https://github.com/allenai/open-instruct

## What Was Removed
Python source code, Jupyter notebooks (.ipynb), shell scripts (.sh), Dockerfiles, CI/CD configs, Python package files (pyproject.toml, setup.py), JSON data files, CSV datasets, model configs, training logs, Git metadata, images.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/AGENTS.md

# Bash commands
- `uv run pytest`: Run the tests.
- `make style && make quality` run the linter + formatter.
- `uv run mkdocs serve`: View the documentation locally at http://127.0.0.1:8000/
- `uv run mkdocs build`: Build the documentation to the `site/` directory.

# Workflow
- Always run the linter and make sure the tests pass before finishing a task.
- Prefer running single tests, not the whole suite, when developing.
- To run the `./scripts/train/build_image_and_launch.sh` script, you must commit the current changes.
- Launch tool use experiments by running `./scripts/train/build_image_and_launch.sh scripts/train/debug/tool_grpo_fast.sh`.
- Launch multi-node non-tool experiments by running `./scripts/train/build_image_and_launch.sh scripts/train/debug/large_test_script.sh`.

# Documentation
To verify that documentation changes don't alter the generated output:
1. Build docs on your branch: `uv run mkdocs build && cp -r site site-branch`
2. Switch to main branch and build: `cd /path/to/main && uv run mkdocs build`
3. Compare the builds: `diff -rq site-branch /path/to/main/site`
4. If no output, the docs are identical. If differences exist, review with: `diff -r site-branch /path/to/main/site`

---


## File: docs/meaisínfhoghlaim/training/open-instruct/CLAUDE.md

# Bash commands
- `uv run pytest`: Run the tests.
- `make style && make quality` run the linter + formatter.
- `uv run mkdocs serve`: View the documentation locally at http://127.0.0.1:8000/
- `uv run mkdocs build`: Build the documentation to the `site/` directory.

# Workflow
- Always run the linter and make sure the tests pass before finishing a task.
- Prefer running single tests, not the whole suite, when developing.
- To run the `./scripts/train/build_image_and_launch.sh` script, you must commit the current changes.
- Launch tool use experiments by running `./scripts/train/build_image_and_launch.sh scripts/train/debug/tool_grpo_fast.sh`.
- Launch multi-node non-tool experiments by running `./scripts/train/build_image_and_launch.sh scripts/train/debug/large_test_script.sh`.

# Documentation
To verify that documentation changes don't alter the generated output:
1. Build docs on your branch: `uv run mkdocs build && cp -r site site-branch`
2. Switch to main branch and build: `cd /path/to/main && uv run mkdocs build`
3. Compare the builds: `diff -rq site-branch /path/to/main/site`
4. If no output, the docs are identical. If differences exist, review with: `diff -r site-branch /path/to/main/site`

---


## File: docs/meaisínfhoghlaim/training/open-instruct/decontamination/README.md

# Scripts for computing overlap between train and test sets

These scripts are for creating Elasticsearch indices over training datasets, particularly instruction tuning datasets, and querying them with test sets to compute overlap. They can be used for quantifying and analyzing training dataset contamination.

## Running Elasticsearch

Elasticsearch needs to up and running for creating and querying indices. You can run it locally by following the steps [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/run-elasticsearch-locally.html). Make sure to keep track of the password and save it as an environment variable, `ELASTIC_PASSWORD`, e.g.:

```bash
export ELASTIC_PASSWORD=[password]
```

## Indexing

You can index the training sets either as text or as dense vectors. The indexing script assumes that the training dataset is a Huggingface dataset, and has a field that contains prompt-response pairs in a conversational format, e.g. a `messages` field that looks like

```json
[
    {
        "role": "user",
        "content": "Write me a poem."
    },
    {
        "role": "assistant",
        "content": "Sorry, I cannot help you with that."
    }
]
```

The script indexes each turn as a separate Elasticsearch document, and importantly only indexes the messages of one specific role. The assumption is that you would want to index only the prompts for quantifying contamination. You can control this behavior using the `--messages_field`, `--query_filter`, and `--query_field` options as follows:

```bash
python index.py --messages_field messages --query_filter role:user --query_field content
```

The setting above looks for the `messages` field in the dataset, finds messages where the `role` is `user` and indexes their `content`.

### Indexing multiple datasets

You can index one dataset at a time as follows

```bash
python index.py --dataset HF_DATASET_NAME
```

Alternatively, you can pass a training configuration yaml with a `dataset_mixer` field to index all the datasets in the mix.

```bash
python index.py --dataset_mixer_config config.yaml
```

### Indexing vector representations

By default, the indexing script indexes the text in the datasets. If you want to perform soft matching, you can change `--index_type`, and specify an embedding model (defaults to [NV-Embed-v2](https://huggingface.co/nvidia/NV-Embed-v2)).

```bash
python index.py --index_type vector --model nvidia/NV-Embed-v2
```

The script assumes you are running this on GPUs and uses all the available devices. You can adjust `--max_batch_tokens` to a suitable value if you run into OOM errors or if you want to use your GPUs more effectively.

## Searching

The searching script lets you query one or more `text` or a `vector` indices with a test set. When querying a `text` index, you can perform an ngram match, a full text match, or an embedding-based match of a specified field(s) in the test set. The basic usage looks like

```bash
python search.py --train_dataset_names allenai/tulu-2-sft-mixture allenai/wildchat-1m --dataset tatsu-lab/alpaca_eval --split eval --field instruction --output_dir /path/to/output
```

The command above queries the indices corresponding to the two training sets, `allenai/tulu-2-sft-mixture` and `allenai/wildchat-1m` (assuming these were indexed earlier) with the AlpacaEval dataset, particularly the `instruction` field in the `eval` split.

The script will create in the output directory one `jsonl` file per each pair of index and evaluation dataset with instance-level information about the matches, and a TSV file called `contamination_report.tsv` with a table of contamination scores for all the pairs.

Like with the indexing script, a dataset mixer configuration can be passed with the `--dataset_mixer_config` option instead of `--train_dataset_names`.

### Checking for contamination against the Tulu 3 evaluation suite

If no evaluation dataset is specified using the `--dataset` option, the entire Tulu 3 evaluation suite will be used to query the specified indices.

### Matching ngrams

Text indexes can be queried for ngram matches instead of full field matches (default) as follows

```bash
python search.py --train_dataset_names TRAIN_DATASET_NAME --ngram_size SIZE [--match_threshold THRESHOLD]
```

Matching scores are then computed as follows:
- For each token in the test instance, all matching training documents are retrieved. A training document is considered a match for a token if it is part of an ngram of the specified `SIZE` in the test instance, that also occurs in the training document.
- The single training document that covers the most number of tokens in the test instance is considered the largest match.
- If no threshold is specified, the match score for the test instance is the proportion of the matched tokens. If a threshold is specified, the score is `0` or `1` depending on the threshold.
- The evaluation dataset level match (or contamination) score is the average of instance level match scores.

### Embedding-based matching

If the index is created using `--index_type vector`, the same option needs to be specified for searching as well, along with the same `--model MODEL_NAME`. The searching script also assumes you are running this on GPUs.

You can specify a `--match_threshold` here as well, and the behavior is similar to that in ngram matching, except that the match scores here come from embedding similarity.

### Decontamination

If you need to remove instances from the training sets that match any of the test instances, just pass a `--decontaminate` option to `search.py`. The output directory will contain one decontaminated `jsonl` file per training dataset. If you pass a `--match_treshold`, only those train instances that have a matching score greater than the threshold with *any* of the test instances will be removed.

Note that elasticsearch retrieves a limited number of hits each time you search. You can increase this by requesting a larger number of results by passing a different value to `--search_size` (default is 100). Setting this to a larger number (e.g. 10000) is a good idea if you are decontaminating datasets. Since elasticsearch does not necessarily retrieve all the documents that match, it is not guaranteed that decontamination removes all the matching training instances. You can always check for contamination after decontaminating a dataset to see how effective it was.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/ai2_internal.md

Deprecated. Check out [get_started/ai2_internal_setup.md](get_started/ai2_internal_setup.md) instead.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/dataset_transformation.md

# Dataset Transformations

Dataset transformations are a key part of the training process. Typically, we are given some text dataset, and we tokenize and filter it to be used for training.

Open Instruct includes a `dataset_transformation.py` utility which

* handles dataset mixing
* handles different tokenization functions
* **caches** the tokenized dataset so we don't have to re-tokenize every time
    * This is especially important when we have 405B SFT models: 32 nodes are just spending like
    5 minutes to tokenize the dataset. This translates to 32 * 5 * 8 = 1280 minutes = 21 hours of
    wasted H100 time.
    * Sometimes we also launch on places that don't have a shared cache, so we would
    download individual datasets 32 times, and wait for concatenation and tokenization (actually
    twice because the `with accelerator.main_process_first()` function assumes a shared cache)
    * Using a cache like this also minimizes the time to get first training output, making debug
    cycles faster.


## SFT Dataset Format

We expect the dataset to have a `messages` key, which is a list of dictionaries with `role` and `content` keys. For example,

* [allenai/tulu-3-sft-personas-instruction-following](https://huggingface.co/datasets/allenai/tulu-3-sft-personas-instruction-following)
* [allenai/tulu-3-sft-personas-code](https://huggingface.co/datasets/allenai/tulu-3-sft-personas-code)

Below is a minimal example of how `dataset_transformation.py` was used in the `finetune.py` script to mix, tokenize, and filter a dataset for SFT.

You can run `python scripts/data/finetune_dataset_transformation.py` to see the output.


```python title="scripts/data/finetune_dataset_transformation.py" linenums="1"
--8<-- "scripts/data/finetune_dataset_transformation.py"
```

![dataset](dataset/sft.png)


You can also use a different `chat_template_name`. For example,

```python
tc = TokenizerConfig(
    # ...
    chat_template_name="simple_chat",
)
#...
```

would give us


![dataset](dataset/sft2.png)

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/dpo.md

# Direct Preference Optimization (DPO)

We support Direct Preference Optimization (DPO) training on a variety of datasets.

## Implemented Variants

- `dpo_tune_cache.py` is the DPO implementation that directly optimizes model outputs based on human preferences.

## `dpo_tune_cache.py`

This implementation has the following key features:

- Auto save the trained checkpoint to HuggingFace Hub
- Supports LigerKernel for optimized training with fused operations
- Implements the DPO algorithm for direct preference optimization


There are several relevant implementation details:

1. To save memory, we 1) cache the logprobs of the reference model on the dataset, 2) remove the reference model from the memory after the logprobs are computed. This means that you won't see the initial training losses for a while until the logprobs are computed.
2. We use the `dpo_norm` loss type by default, which is a length-normalized loss. See the [SimPO](https://arxiv.org/abs/2405.14734) paper for more details.




### Debug (Single GPU)

You can run the script in a single GPU mode to debug the training process.

```bash
bash scripts/train/debug/dpo.sh
```



### Reproduce `allenai/Llama-3.1-Tulu-3-8B-DPO` (4 Nodes)

You can reproduce our `allenai/Llama-3.1-Tulu-3-8B-DPO` model by running the following command:

```bash
bash scripts/train/tulu3/dpo_8b.sh
```

![dpo_plot](dpo/tulu3_8b_dpo.png)
![dpo_plot](dpo/tulu3_8b_dpo-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/Tulu3-8B-DPO--VmlldzoxMTg3NjY4Nw" style="width:100%; height:500px" title="Tulu3-8B-DPO"></iframe>


???+ info


    Based on our internal evaluation, the DPO model is roughly on par with the original `allenai/Llama-3.1-Tulu-3-8B-DPO` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![dpo_plot](dpo/tulu3_8b_dpo_eval.png)

    For example, DROP is lower than the reference, but DROP can be quite brittle due to parsing issues (see below).

    ![dpo_plot](dpo/tulu3_8b_dpo_eval_drop.png)


???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!



### Reproduce `allenai/OLMo-2-1124-7B-DPO` (4 Nodes)

You can reproduce our `allenai/OLMo-2-1124-7B-DPO` model by running the following command:

```bash
bash scripts/train/olmo2/dpo_7b.sh
```

???+ info

    If you are an external user, `mason.py` will print out the actual command being executed on our internal server, so you can modify the command as needed.

![dpo_plot](dpo/olmo2_7b_dpo.png)
![dpo_plot](dpo/olmo2_7b_dpo-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-7B-DPO--VmlldzoxMTkyNzUyOA" style="width:100%; height:500px" title="OLMo2-7B-DPO"></iframe>

???+ info

    Based on our internal evaluation, the DPO model is roughly on par with the original `allenai/OLMo-2-1124-7B-DPO` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![dpo_plot](dpo/olmo2_7b_dpo_eval.png)

???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!




### Reproduce `allenai/OLMo-2-1124-13B-DPO` (4 Nodes)

You can reproduce our `allenai/OLMo-2-1124-13B-DPO` model by running the following command:

```bash
bash scripts/train/olmo2/dpo_13b.sh
```

![dpo_plot](dpo/olmo2_13b_dpo.png)
![dpo_plot](dpo/olmo2_13b_dpo-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-13B-DPO--VmlldzoxMTg3NjcyMQ" style="width:100%; height:500px" title="OLMo2-13B-DPO"></iframe>


???+ info

    Based on our internal evaluation, the DPO model is roughly on par with the original `allenai/OLMo-2-1124-13B-DPO` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![dpo_plot](dpo/olmo2_13b_dpo_eval.png)


???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!


### Training Metrics

During training, the following metrics are logged:

- `training_step`: Current training step
- `learning_rate`: The current learning rate from the learning rate scheduler
- `epoch`: Current epoch (as a fraction of total dataset)
- `train_loss`: The average training loss over the logged steps
- `logps/chosen`: Average log probabilities for chosen responses
- `logps/rejected`: Average log probabilities for rejected responses

For DPO and DPO-norm loss types, additional metrics are logged:

- `rewards/chosen`: Average rewards for chosen responses
- `rewards/rejected`: Average rewards for rejected responses
- `rewards/average`: Average of chosen and rejected rewards
- `rewards/accuracy`: Accuracy of preference prediction
- `rewards/margin`: Margin between chosen and rejected rewards

When using load balancing loss (for OLMoE), the following metric is also logged:

- `aux_loss`: Auxiliary loss for load balancing

The metrics are logged every `logging_steps` steps (if specified) and provide insights into:

- Training progress (loss, learning rate, epoch)
- Model behavior (log probabilities, rewards)
- Preference learning (accuracy, margin)
- Resource utilization (auxiliary losses)

## Acknowledgements

We would like to thank the following projects for general infrastructure:

- [DeepSpeedAI/DeepSpeed](https://github.com/deepspeedai/DeepSpeed)
- [HuggingFace/Transformers](https://github.com/huggingface/transformers)

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/finetune.md

# Supervised finetuning (SFT)

We support Supervised finetuning (SFT) on a variety of datasets.






## Implemented Variants

- `finetune.py` is the original SFT implementation.


## `finetune.py`


This implementation has the following key features:

- Auto save the trained checkpoint to HuggingFace Hub
- Supports LigerKernel for optimized training with fused operations



### Debug (Single GPU)

You can run the script in a single GPU mode to debug the training process.

```bash
bash scripts/train/debug/finetune.sh
```

![finetune](finetune/finetune_debug.png)


### Reproduce `allenai/Llama-3.1-Tulu-3-8B-SFT` (8 Nodes)

You can reproduce our `allenai/Llama-3.1-Tulu-3-8B-SFT` model by running the following command:

```bash
bash scripts/train/tulu3/finetune_8b.sh
```

???+ info

    If you are an external user, `mason.py` will print out the actual command being executed on our internal server, so you can modify the command as needed.

    ![tulu3_8b](finetune/tulu3_8b.png)



![finetune_plot](finetune/tulu3_8b_sft.png)
![finetune_plot](finetune/tulu3_8b_sft-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/Tulu3-8B-SFT--VmlldzoxMTk0OTY4MA" style="width:100%; height:500px" title="Tulu3-8B-SFT"></iframe>


???+ info


    Based on our internal evaluation, the SFT model is roughly on par with the original `allenai/Llama-3.1-Tulu-3-8B` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![finetune_plot](finetune/tulu3_8b_eval.png)

???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!




### Reproduce `allenai/OLMo-2-1124-7B-SFT` (8 Nodes)

You can reproduce our `allenai/OLMo-2-1124-7B-SFT` model by running the following command:

```bash
bash scripts/train/olmo2/finetune_7b.sh
```

![finetune_plot](finetune/olmo2_7b_sft.png)
![finetune_plot](finetune/olmo2_7b_sft-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-1124-7B-SFT--VmlldzoxMTg1NzIxMw" style="width:100%; height:500px" title="OLMo2-1124-7B-SFT"></iframe>

???+ info

    Based on our internal evaluation, the SFT model is roughly on par with the original `allenai/OLMo-2-1124-7B` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![finetune_plot](finetune/olmo2_7b_sft_eval.png)

???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!


### Reproduce `allenai/OLMo-2-1124-13B-SFT` (8 Nodes)

You can reproduce our `allenai/OLMo-2-1124-13B-SFT` model by running the following command:

```bash
bash scripts/train/olmo2/finetune_13b.sh
```

![finetune_plot](finetune/olmo2_13b_sft.png)
![finetune_plot](finetune/olmo2_13b_sft-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-13B-SFT--VmlldzoxMjA0MjUyNg" style="width:100%; height:500px" title="OLMo2-1124-7B-SFT"></iframe>

???+ info

    Based on our internal evaluation, the SFT model is roughly on par with the original `allenai/OLMo-2-1124-7B` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![finetune_plot](finetune/olmo2_13b_sft_eval.png)

???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!


### Reproduce `allenai/OLMo-2-1124-32B-SFT` (8 Nodes)

You can reproduce our `allenai/OLMo-2-1124-32B-SFT` model by running the following command:

```bash
bash scripts/train/olmo2/finetune_32b.sh
```

![finetune_plot](finetune/olmo2_32b_sft.png)
![finetune_plot](finetune/olmo2_32b_sft-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-32B-SFT--VmlldzoxMjA0MjUxOQ" style="width:100%; height:500px" title="OLMo2-1124-7B-SFT"></iframe>

???+ info

    Based on our internal evaluation, the SFT model is roughly on par with the original `allenai/OLMo-2-1124-7B` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![finetune_plot](finetune/olmo2_32b_sft_eval.png)

???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!




### Training Metrics

During training, the following metrics are logged:

- `learning_rate`: The current learning rate from the learning rate scheduler
- `train_loss`: The average training loss over the logged steps
- `total_tokens`: Total number of tokens processed (excluding padding)
- `per_device_tps`: Tokens per second processed per device (excluding padding)
- `total_tokens_including_padding`: Total number of tokens including padding tokens
- `per_device_tps_including_padding`: Tokens per second processed per device (including padding)

The metrics are logged every `logging_steps` steps (if specified) and provide insights into:
- Training progress (loss, learning rate)
- Training efficiency (tokens per second)
- Resource utilization (padding vs non-padding tokens)

## Acknowledgements

We would like to thank the following projects for general infrastructure:

- [DeepSpeedAI/DeepSpeed](https://github.com/deepspeedai/DeepSpeed)
- [HuggingFace/Transformers](https://github.com/huggingface/transformers)

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/grpo.md

# Grouped Relative Policy Optimization (GRPO)

GRPO is an online RL method used in [DeepSeek R1 paper](https://arxiv.org/abs/2501.12948) and its first appearance is in [DeepSeekMath](https://arxiv.org/abs/2402.03300)



## Implemented Variants

- `grpo_fast.py` is a faster variant using [packing techniques](https://huggingface.co/blog/sirluk/llm-sequence-packing).
- `grpo_vllm_thread_ray_gtrl.py` is a more vanilla GRPO implementation, using vLLM and Ray.



## `grpo_fast.py`

This implementation has the following features:

- Uses packing techniques to speed up the training process, inspired by [Open-Reasoner-Zero/Open-Reasoner-Zero](https://github.com/Open-Reasoner-Zero/Open-Reasoner-Zero)
- Uses a thread-based approach to parallelize the training and inference processes, based on [Asynchronous RLHF](https://arxiv.org/abs/2410.18252).
- Uses a data preparation thread to prepare the data for the training process.

In simpler tasks, we see 2x faster training, and even 10x faster for more complex tasks. With `grpo_fast.py`, we can run crank up `number_samples_per_prompt` and train on really large batch sizes.

It implements additional optimizations:

* `grpo_fast.py` also implements an optimization to skip zero gradient batches. If we solve a prompt 100% correct or 0% correct, the std of the group is 0. So `adv = (score - score.mean()) / (score.std + 1e-5) = 0 / 1e-5 = 0`, causing 0 gradients. `grpo_fast.py` will skip these batches before packing the sequences.

![](grpo/grpo_fast_gradient.png)

Figure taken from [this discord thread by @the_real_jrb](https://discord.com/channels/1179127597926469703/1208183216843005962/1357712190957682839)

* `grpo_fast.py` only applies the verification reward if the format reward is enabled (via `--additive_format_reward False` by default). See ([allenai/open-instruct/pull/659](https://github.com/allenai/open-instruct/pull/659)). A direct additive format reward is undesirable. In GRPO, the scale of the rewards is not relevant due to group normalization. For example, a group of [0, 0, 0, 0, 10], [0, 0, 0, 0, 11], [0, 0, 0, 0, 1] reward will have the same advantage.

Now imagine there are cases where the model generates a really long response (8k) gen length, but only get the format reward right, GRPO will push up the probs for this long response even though the response is not really correct. As a result, when using the format reward directly, we see the response length of unsolved prompts to fluctuate significantly, causing stability issues.

![](grpo/additive_format_reward.png)

### Debug (Single GPU)

You can run the script in a single GPU mode to debug the training process.

```bash
# single GPU
bash scripts/train/debug/grpo_fast.sh
# 3 GPU: 2 for training, 1 for inference (a more realistic setting for async training)
bash scripts/train/debug/grpo_fast_3_gpu.sh
```

### Reproduce `allenai/Llama-3.1-Tulu-3.1-8B` (1 Nodes)

You can reproduce our `allenai/Llama-3.1-Tulu-3.1-8B` model by running the following command:

```bash
bash scripts/train/tulu3/grpo_fast_8b_single_node.sh
```

???+ info

    Here the `grpo_fast.py` actually use 6 GPUs for training and 2 GPUs for inference, so it's using less hardware but runs faster than `grpo_vllm_thread_ray_gtrl.py` which uses 2 nodes (12 GPUs for training and 4 GPUs for inference).


![grpo_tulu3_8b](grpo/tulu3.1_8b_grpo_fast.png)
![grpo_tulu3_8b_time](grpo/tulu3.1_8b_grpo_fast-time.png)

??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/Tulu3-1-8B-GRPO-Fast--VmlldzoxMTk0NzcwOA" style="width:100%; height:500px" title="Tulu3-8B-GRPO-Fast"></iframe>

???+ info

    Below are some learning curves for the evaluation metrics during training. Basically, ifeval, gsm8k, and math:flex all go up.

    ![grpo_plot](grpo/tulu3.1_8b_grpo_fast_eval_curve.png)

???+ info

    Based on our internal evaluation, the GRPO model is roughly on par with the original `allenai/Llama-3.1-Tulu-3.1-8B` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![grpo_plot](grpo/tulu3.1_8b_grpo_fast_eval.png)


???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!


### (🧪 Experimental) Qwen 2.5 7B GRPO Fast Zero-style

We have

```bash
bash scripts/train/qwen/grpo_fast_7b.sh
```


![grpo_qwen2.5_7B_works](grpo/qwen2.5_7b_grpo_fast_zero.png)
![grpo_qwen2.5_7B_works_time](grpo/qwen2.5_7b_grpo_fast_zero-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/Qwen2-5-7B-GRPO-Fast-Zero--VmlldzoxMjA2NDExMA" style="width:100%; height:500px" title="Qwen2.5-7B-GRPO-Fast-Zero"></iframe>


???+ info

    Below are some learning curves for the evaluation metrics during training. Basically, ifeval, gsm8k, and math:flex all go up.

    ![grpo_plot](grpo/qwen2.5_7b_grpo_fast_zero_eval_curve.png)

???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!




### (🧪 Experimental) Olmo2 7B GRPO Fast Zero-style

We have

```bash
bash scripts/train/olmo2/grpo_fast_7b_zero.sh
```


![grpo_olmo2_7b_zero](grpo/olmo2_7b_grpo_fast_zero.png)
![grpo_olmo2_7b_zero_time](grpo/olmo2_7b_grpo_fast_zero-time.png)

??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-7B-GRPO-Fast-Zero--VmlldzoxMjA0MjU4MQ" style="width:100%; height:500px" title="OLMo2-7B-GRPO-Fast-Zero"></iframe>

???+ info

    Below are some learning curves for the evaluation metrics during training. Basically, ifeval, gsm8k, and math:flex all go up.

    ![grpo_plot](grpo/olmo2_7b_grpo_fast_zero_eval_curve.png)


???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!


### (🧪 Experimental) Olmo2 13B GRPO Fast Zero-style

We have

```bash
bash scripts/train/olmo2/grpo_fast_13b_zero.sh
```


![grpo_olmo2_13b_zero](grpo/olmo2_13b_grpo_fast_zero.png)
![grpo_olmo2_13b_zero_time](grpo/olmo2_13b_grpo_fast_zero-time.png)

??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-13B-GRPO-Fast-Zero--VmlldzoxMjA0MjU4Mw" style="width:100%; height:500px" title="OLMo2-13B-GRPO-Fast-Zero"></iframe>

???+ info

    Below are some learning curves for the evaluation metrics during training. Basically, ifeval, gsm8k, and math:flex all go up.

    ![grpo_plot](grpo/olmo2_13b_grpo_fast_zero_eval_curve.png)


???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!




### Training Metrics

See the Training Metrics for `grpo_vllm_thread_ray_gtrl.py` below for general metrics. `grpo_fast.py` includes the following additional metrics:


* `other/real_batch_size_ratio`: In GRPO, as we train we actually get smaller and smaller batch sizes. This is because if we solve a prompt 100% correct or 0% correct, the std of the group is 0. So `adv = (score - score.mean()) / (score.std + 1e-5) = 0 / 1e-5 = 0`, causing 0 gradients. This metric is the ratio of the samples that have gradients vs the total number of samples,
* `other/packed_ratio`: The ratio of the packed sequences vs the total number of sequences. The lower the ratio, the more efficiently we have packed the sequences. E.g., if we have 100 sequences and the ratio is 0.1, it means we only have to do 10% of the forward passes than if we didn't pack.


## `grpo_vllm_thread_ray_gtrl.py`


This implementation has the following features:

- Uses a thread-based approach to parallelize the training and inference processes, based on [Asynchronous RLHF](https://arxiv.org/abs/2410.18252).
- Uses vLLM and Ray to parallelize the training process, based on how [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF) does it


### Debug (Single GPU)

You can run the script in a single GPU mode to debug the training process.

```bash
bash scripts/train/debug/grpo.sh
```



### Reproduce `allenai/Llama-3.1-Tulu-3.1-8B` (2 Nodes)

You can reproduce our `allenai/Llama-3.1-Tulu-3.1-8B` model by running the following command:

```bash
bash scripts/train/tulu3/grpo_8b.sh
```

![grpo_tulu3_8b](grpo/tulu3.1_8b_grpo.png)
![grpo_tulu3_8b_time](grpo/tulu3.1_8b_grpo-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/Tulu3-1-8B-GRPO--VmlldzoxMTkyNzc2MA" style="width:100%; height:500px" title="Tulu3-8B-GRPO"></iframe>


???+ info

    Below are some learning curves for the evaluation metrics during training. Basically, ifeval, gsm8k, and math:flex all go up.

    ![grpo_plot](grpo/tulu3.1_8b_grpo_eval_curve.png)


???+ info

    Based on our internal evaluation, the GRPO model is roughly on par with the original `allenai/Llama-3.1-Tulu-3.1-8B` model, though there are some slight differences. Note that your results may vary slightly due to the random seeds used in the training.

    ![grpo_plot](grpo/tulu3.1_8b_grpo_eval.png)


### Reproduce `allenai/OLMo-2-1124-7B-Instruct` but better (2 Nodes)

You can reproduce our `allenai/OLMo-2-1124-7B-Instruct` model by running the following command:

```bash
bash scripts/train/olmo2/grpo_7b.sh
```

![grpo_olmo2_7b](grpo/olmo2_7b_grpo.png)
![grpo_olmo2_7b_time](grpo/olmo2_7b_grpo-time.png)

??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/OLMo-2-7B-GRPO--VmlldzoxMTkyNzc1OA" style="width:100%; height:500px" title="OLMo2-7B-GRPO"></iframe>

???+ info

    Below are some learning curves for the evaluation metrics during training. Basically, ifeval, gsm8k, and math:flex all go up.

    ![grpo_plot](grpo/olmo2_7b_grpo_eval_curve.png)


???+ info

    Based on our internal evaluation, the GRPO model actually outperforms the original `allenai/OLMo-2-1124-7B-Instruct` model. This is mostly because the original `allenai/OLMo-2-1124-7B-Instruct` was trained with PPO, which may suffer from not using a outcome reward model to initialize the value model (since it uses a genreal RM to initialize the value model). Note that your results may vary slightly due to the random seeds used in the training.

    ![grpo_plot](grpo/olmo2_7b_grpo_eval.png)




### (🧪 Experimental) Qwen 2.5 7B Zero-style

Here is a command to run GRPO on the `Qwen/Qwen2.5-7B` on [ai2-adapt-dev/math_ground_truth_zs](https://huggingface.co/datasets/ai2-adapt-dev/math_ground_truth_zs), which is simply a zero-shot version of the RLVR MATH dataset. The training is done starting from a base model, similar to how [DeepSeek R1](https://arxiv.org/abs/2501.12948) does it.

```bash
bash scripts/train/qwen/grpo_7b.sh
```

![grpo_qwen2.5_7B_works](grpo/qwen2.5_7b_grpo_zero.png)
![grpo_qwen2.5_7B_works_time](grpo/qwen2.5_7b_grpo_zero-time.png)


??? note "👉 Tracked WandB Experiments (Click to expand)"

    <iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/Qwen2-5-7B-GRPO-Zero--VmlldzoxMjA0MjY5OA" style="width:100%; height:500px" title="Qwen2.5-7B-GRPO-Zero"></iframe>

???+ info

    Below are some learning curves for the evaluation metrics during training. Basically, ifeval, gsm8k, and math:flex all go up.

    ![grpo_plot](grpo/qwen2.5_7b_grpo_zero_eval_curve.png)


???+ info

    We haven't quite figured out how to make our internal evaluation toolchains more open yet. Stay tuned!


### Training Metrics

During training, the following metrics are logged:


* `episode`: the global episode number training has gone through (e.g., `3000` means we have trained on 3000 data points already -- in the case of RLVR that is prompts, which can repeat)
* `lr`: the current learning rate
* `epoch`: the fraction or multiple of the epoch (e.g., `2.7` means we have trained on the dataset for 2 epochs and 70% of the third epoch)
* `objective/kl`: the KL divergence between the current policy and the reference policy (sum of the KL divergence of each response token)
* `objective/scores`: the scores of the current response, rated by a combination of reward model and other rewards (e.g., R1 style format reward, verifiable reward, etc.)
* `objective/rlhf_reward`: the RLHF reward, which is `objective/scores` - `beta` * `objective/kl`
* `objective/non_score_reward`: `beta` * `objective/kl`
* `objective/entropy`: the entropy of the current policy
* `objective/loss`: the GRPO loss
* `objective/kl2`: the second variant of KL divergence used in the training process, calculated similarly to `objective/kl`
* `objective/kl3`: the third variant of KL divergence used in the training process, providing additional insights into policy divergence
* `objective/scores_mean`: the mean of the scores of the current response, providing an average measure of response quality
* `objective/reward_std`: the standard deviation of the rewards, indicating the variability in the reward distribution
* `objective/verifiable_correct_rate`: the rate at which responses are verifiably correct, providing a measure of response accuracy
* `loss/policy_avg`: the average policy loss, indicating the mean loss incurred during policy updates
* `policy/approxkl_avg`: the average approximate KL divergence, used to monitor policy stability
* `policy/clipfrac_avg`: the average fraction of updates where the policy was clipped, indicating how often clipping occurs
* `policy/entropy_avg`: the average entropy of the policy, providing a measure of policy randomness
* `time/from_scratch`: the time taken to train the model from scratch
* `time/training`: the time taken to do one training step
* `val/sequence_lengths`: the length of the sequences in the generated responses
* `val/num_stop_token_ids`: the number of stop tokens in the generated responses
* `val/ratio`: the mean ratio of the new policy to the old policy, used to assess policy updates
* `val/ratio_var`: the variance of the ratio of the new policy to the old policy, indicating the variability in policy updates
* `val/stop_token_rate`: the rate at which stop tokens appear in the responses, providing a measure of response termination
* `val/format_scores`: the mean format scores, indicating the quality of response formatting (only logged if `add_r1_style_format_reward` is enabled)
* `other/real_batch_size_ratio`: In GRPO, as we train we actually get smaller and smaller batch sizes. This is because if we solve a prompt 100% correct or 0% correct, the std of the group is 0. So `adv = (score - score.mean()) / (score.std + 1e-5) = 0 / 1e-5 = 0`, causing 0 gradients. This metric is the ratio of the samples that have gradients vs the total number of samples,
* `other/packed_ratio`: The ratio of the packed sequences vs the total number of sequences. The lower the ratio, the more efficiently we have packed the sequences. E.g., if we have 100 sequences and the ratio is 0.1, it means we only have to do 10% of the forward passes than if we didn't pack.





## Acknowledgements

We would like to thank the following resources for GRPO theory:

- [DeepSeek R1](https://arxiv.org/abs/2501.12948)
- [DeepSeekMath](https://arxiv.org/abs/2402.03300)
- [Asynchronous RLHF](https://arxiv.org/abs/2410.18252)

We would like to thank the following resources for GRPO implementation and Ray usage:

- [Packing Techniques](https://huggingface.co/blog/sirluk/llm-sequence-packing)
- [OpenRLHF/OpenRLHF](https://github.com/OpenRLHF/OpenRLHF)
- [Open-Reasoner-Zero/Open-Reasoner-Zero](https://github.com/Open-Reasoner-Zero/Open-Reasoner-Zero)


We would like to thank the following projects for general infrastructure:

- [vLLM](https://github.com/vllm-project/vllm)
- [Ray](https://github.com/ray-project/ray)
- [DeepSpeedAI/DeepSpeed](https://github.com/deepspeedai/DeepSpeed)
- [HuggingFace/Transformers](https://github.com/huggingface/transformers)

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/online_dpo.md

# Reward model training

`open_instruct/online_dpo.py` contains the script for training online DPO models.


## Get started

In the sections below, we will include some examples on how to train models and demonstrating different features. A couple of notes:

* You should adjust your `per_device_train_batch_size` and `gradient_accumulation_steps` accordingly to maximize throughput on a particular GPU type.
* If you set `take_top_bottom_generation`, you can use a `num_generation_per_prompt` larger than 2 -- it just takes the top and bottom scoring generations for each prompt.
* For the examples below, we use `mason.py` to invoke experiment orchastration on Ai2's cluster. For external users, you can copy the command after the `--` and run it on your system or debug locally. For example: the documentation will have commands like the following, but you can just run `$YOUR_COMMAND` on your system and make sure it matches `$NUM_GPUS`.
    * You can you `--image costah/open_instruct_onlinedpo2` to specify a custom image or if you don't specify any it's going to use the default image.
    * If you installed your python on NFS you can run a debug mode by **not toggling** `--pure_docker_mode` and it will mount your python environment on the docker container.

```bash
python mason.py \
    --cluster ai2/jupiter \
    --image costah/open_instruct_onlinedpo2 --pure_docker_mode \
    --priority preemptible \
    --budget ai2/jupiter \
    --gpus $NUM_GPUS -- $YOUR_COMMAND
```

**WARNING: This script is not battle-tested. There may be bugs and issues -- please report them! Use at your own risk.**


### Level 0: single GPU; quick debug. Should take less than 10 minutes to finish

```bash
python open_instruct/online_dpo_vllm_thread.py \
    --dataset_mixer_list trl-internal-testing/tldr-preference-sft-trl-style 1.0 \
    --dataset_mixer_eval_list trl-internal-testing/tldr-preference-sft-trl-style 1.0 \
    --dataset_mixer_list_splits train \
    --dataset_mixer_eval_list_splits validation \
    --max_token_length 1024 \
    --max_prompt_token_length 512 \
    --model_name_or_path cleanrl/EleutherAI_pythia-1b-deduped__sft__tldr \
    --reward_model_path cleanrl/EleutherAI_pythia-1b-deduped__reward__tldr \
    --non_stop_penalty \
    --stop_token eos \
    --chat_template simple_concat_with_space \
    --learning_rate 3e-6 \
    --total_episodes 3000 \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps 64 \
    --max_token_length 1024 \
    --max_prompt_token_length 512 \
    --beta 0.1 \
    --output_dir models/rm/rm_sentiment_1b \
    --single_gpu_mode \
    --hf_metadata_dataset "" \
    --no_try_launch_beaker_eval_jobs \
    --gradient_checkpointing \
    --with_tracking \
    --push_to_hub \
    --vllm_gpu_memory_utilization 0.5 \
    --actor_num_gpus_per_node 1 \
    --local_mini_batch_size 32 \
    --num_mini_batches 1 \
    --vllm_sync_backend gloo

# LEVEL 0.1: two GPU; quick debug; using 1 GPU for training and 1 GPU for vllm generation via --vllm_device cuda:1
python open_instruct/online_dpo_vllm_thread.py \
    --dataset_mixer_list trl-internal-testing/tldr-preference-sft-trl-style 1.0 \
    --dataset_mixer_eval_list trl-internal-testing/tldr-preference-sft-trl-style 1.0 \
    --dataset_mixer_list_splits train \
    --dataset_mixer_eval_list_splits validation \
    --max_token_length 1024 \
    --max_prompt_token_length 512 \
    --model_name_or_path cleanrl/EleutherAI_pythia-1b-deduped__sft__tldr \
    --reward_model_path cleanrl/EleutherAI_pythia-1b-deduped__reward__tldr \
    --non_stop_penalty \
    --stop_token eos \
    --chat_template simple_concat_with_space \
    --learning_rate 3e-6 \
    --total_episodes 3000 \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 2 \
    --gradient_accumulation_steps 64 \
    --max_token_length 1024 \
    --max_prompt_token_length 512 \
    --num_train_epochs 1 \
    --beta 0.1 \
    --output_dir models/rm/rm_sentiment_1b \
    --single_gpu_mode \
    --vllm_gpu_memory_utilization 0.5 \
    --actor_num_gpus_per_node 1 \
    --local_mini_batch_size 32 \
    --num_mini_batches 1 \
    --vllm_sync_backend gloo
    --no_try_launch_beaker_eval_jobs \
    --gradient_checkpointing \
    --with_tracking \
    --push_to_hub
```

## Old examples

These examples use the older form of the script available at https://github.com/allenai/open-instruct/blob/efa36849bd65db7614e6729344df94ace83b7228/open_instruct/online_dpo_vllm_thread.py. These require older package versions, use at your own risk.


### LEVEL 1: 8 GPU; TL;DR summarization

Here we are using --vllm_device cuda:7 to say we want to launch the vllm generation engine on the 8th GPU (or GPU_7 using 0 index)
```bash
# for running TL;DR you can likely use GPUs with less memory
python mason.py \
    --image nathanl/open_instruct_auto --pure_docker_mode \
    --cluster ai2/jupiter \
    --priority normal \
    --resumable \
    --preemptible \
    --budget ai2/jupiter \
    --gpus 8 -- accelerate launch --num_processes 7 --config_file configs/ds_configs/deepspeed_zero3.yaml \
     open_instruct/online_dpo_vllm_thread.py \
    --dataset_mixer '{"trl-internal-testing/tldr-preference-sft-trl-style": 1.0}' \
    --dataset_train_splits train \
    --dataset_eval_mixer '{"trl-internal-testing/tldr-preference-sft-trl-style": 1.0}' \
    --dataset_eval_splits validation \
    --max_token_length 1024 \
    --max_prompt_token_length 512 \
    --learning_rate 3e-6 \
    --output_dir models/minimal/online_dpo_vllm_thread_tldr \
    --per_device_train_batch_size 16 \
    --local_rollout_forward_batch_size 32 \
    --gradient_accumulation_steps 4 \
    --num_epochs 1 \
    --num_mini_batches 1 \
    --total_episodes 1000000 \
    --model_name_or_path cleanrl/EleutherAI_pythia-1b-deduped__sft__tldr  \
    --reward_model_path cleanrl/EleutherAI_pythia-1b-deduped__reward__tldr \
    --non_stop_penalty \
    --stop_token eos \
    --beta 0.1 \
    --response_length 53 \
    --with_tracking \
    --push_to_hub \
    --hf_metadata_dataset '""' \
    --no_try_launch_beaker_eval_jobs \
    --single_gpu_mode
```

* Tracked experiment: https://wandb.ai/ai2-llm/open_instruct_internal/runs/fub45jhm
* Trained model: https://huggingface.co/vwxyzjn/online_dpo_vllm_thread__cleanrl_EleutherAI_pythia-1b-deduped__sft__tldr/tree/online_dpo_vllm_thread__1__1726080959


### LEVEL 2: 8 GPU; Huggingface no robot

```bash
# for running chat based models you should use an 8xH100 node.
python mason.py \
    --cluster ai2/jupiter \
    --image nathanl/open_instruct_auto --pure_docker_mode \
    --workspace ai2/tulu-3-dev \
    --priority high \
    --preemptible \
    --budget ai2/jupiter \
    --gpus 8 -- accelerate launch --num_processes 7 --config_file configs/ds_configs/deepspeed_zero3.yaml \
    open_instruct/online_dpo_vllm_thread.py \
    --exp_name "online_dpo_vllm_thread_beta_0.03" \
    --dataset_mixer '{"HuggingFaceH4/no_robots": 1.0}' \
    --dataset_train_splits train \
    --dataset_eval_mixer '{"HuggingFaceH4/no_robots": 1.0}' \
    --dataset_eval_splits test \
    --max_token_length 1024 \
    --max_prompt_token_length 512 \
    --learning_rate 8e-7 \
    --output_dir /output/ \
    --chat_template tulu \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 32 \
    --local_rollout_forward_batch_size 1 \
    --vllm_device cuda:7 \
    --num_epochs 1 \
    --num_mini_batches 1 \
    --total_episodes 100000 \
    --model_name_or_path allenai/open_instruct_dev  \
    --model_revision costa_finetune_tulu3_8b_norobot__meta-llama_Meta-Llama-3.1-8B__42__1725559869 \
    --reward_model_path vwxyzjn/reward_modeling__allenai_open_instruct_dev \
    --reward_model_revision reward_modeling__1__1725760619 \
    --non_stop_penalty \
    --stop_token eos \
    --penalty_reward_value -10.0 \
    --beta 0.03 \
    --num_evals 3 \
    --seed 3 \
    --response_length 1024 \
    --gradient_checkpointing \
    --with_tracking \
    --push_to_hub
```

* Tracked experiment: https://wandb.ai/ai2-llm/open_instruct_internal/runs/do4nuqhh
* Trained model: https://huggingface.co/vwxyzjn/online_dpo_vllm_thread_beta_0.03__allenai_open_instruct_dev/tree/online_dpo_vllm_thread_beta_0.03__3__1726200312


### LEVEL 3: 8 GPU; Training on ultrafeedback RM

```bash
# for running chat based models you should use an 8xH100 node.
python mason.py \
    --cluster ai2/jupiter \
    --image nathanl/open_instruct_auto --pure_docker_mode \
    --workspace ai2/tulu-3-dev \
    --priority high \
    --preemptible \
    --budget ai2/jupiter \
    --gpus 8 -- accelerate launch --num_processes 7 --config_file configs/ds_configs/deepspeed_zero3.yaml \
    open_instruct/online_dpo_vllm_thread.py \
    --exp_name "online_dpo_vllm_thread_beta_0.03" \
    --dataset_mixer '{"allenai/ultrafeedback_binarized_cleaned": 1.0}' \
    --sft_messages_key chosen \
    --dataset_train_splits train_prefs \
    --dataset_eval_mixer '{"allenai/ultrafeedback_binarized_cleaned": 1.0}' \
    --dataset_eval_splits test_prefs \
    --max_token_length 1024 \
    --max_prompt_token_length 512 \
    --learning_rate 8e-7 \
    --output_dir /output/ \
    --chat_template tulu \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 32 \
    --local_rollout_forward_batch_size 1 \
    --vllm_device cuda:7 \
    --num_epochs 1 \
    --num_mini_batches 1 \
    --total_episodes 300000 \
    --model_name_or_path allenai/open_instruct_dev  \
    --model_revision finetune__meta-llama_Meta-Llama-3.1-8B__42__1725751338 \
    --reward_model_path vwxyzjn/reward_modeling__allenai_llama-3-tulu-2-8b \
    --reward_model_revision reward_modeling__1__1726175049 \
    --non_stop_penalty \
    --stop_token eos \
    --penalty_reward_value -10.0 \
    --beta 0.03 \
    --num_evals 3 \
    --response_length 1024 \
    --gradient_checkpointing \
    --with_tracking \
    --push_to_hub
```

* Tracked experiment: https://wandb.ai/ai2-llm/open_instruct_internal/runs/le8luk2u
* Trained model: https://huggingface.co/vwxyzjn/online_dpo_vllm_thread_beta_0.03__allenai_open_instruct_dev/tree/online_dpo_vllm_thread_beta_0.03__1__1726282895

### If you want to use beaker datasets

If you want to use beaker datasets, you need to mount your datasets using --beaker_datasets.
An example command with beaker datasets models:

```
python mason.py \
    --cluster ai2/jupiter \
    --image nathanl/open_instruct_auto \
    --pure_docker_mode \
    --workspace ai2/tulu-3-dev \
    --priority high \
    --preemptible \
    --budget ai2/jupiter \
    --beaker_datasets /model:01J6DC8YQ291QA3QEYQTM3CBHE /reward_model:01J834TT3SB6PTB3QYPH33YJ6M \
    --gpus 8 -- accelerate launch --num_processes 7 --config_file configs/ds_configs/deepspeed_zero3.yaml \
    open_instruct/online_dpo_vllm_thread.py \
    --exp_name "online_dpo_vllm_thread_beta_0.03" \
    --dataset_mixer '{"allenai/ultrafeedback_binarized_cleaned": 1.0}' \
    --sft_messages_key chosen \
    --dataset_train_splits train_prefs \
    --dataset_eval_mixer '{"allenai/ultrafeedback_binarized_cleaned": 1.0}' \
    --dataset_eval_splits test_prefs \
    --max_token_length 1024 \
    --max_prompt_token_length 512 \
    --learning_rate 8e-7 \
    --output_dir /output/ \
    --chat_template tulu \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 32 \
    --local_rollout_forward_batch_size 1 \
    --vllm_device cuda:7 \
    --num_epochs 1 \
    --num_mini_batches 1 \
    --total_episodes 300000 \
    --model_name_or_path /model \
    --reward_model_path /reward_model \
    --non_stop_penalty \
    --stop_token eos \
    --penalty_reward_value -10.0 \
    --beta 0.03 \
    --num_evals 3 \
    --response_length 1024 \
    --gradient_checkpointing \
    --with_tracking \
    --push_to_hub
```


### Quality of life tools


Note that when running with `--push_to_hub` and `--with_tracking`, the HF repo is automatically tracked to wandb, so we link the tracked run and the trained model.

![reward modeling tracked hf repo](reward_modeling_hf_repo.png)


Furthermore, we also track the dataset length visualization in wandb (see detail in [here](#dataset-processing))


![token length visualization in wandb](reward_modeling_token_wandb.png)


Finally, we also include samples

![reward modeling preference sample texts](reward_modeling_preference_sample_texts.png)


## Explanation of the logged metrics


* `episode`: the global episode number training has gone through (e.g., `3000` means we have trained on 3000 data points already)
* `lr`: the current learning rate
* `epoch`: the fraction or multiple of the epoch (e.g., `2.7` means we have trained on the dataset for 2 epochs and 70% of the third epoch)
* `objective/kl`: the KL divergence between the current policy and the reference policy (sum of the KL divergence of each response token)
* `objective/scores`: the scores of the current response, rated by a reward model
* `objective/rlhf_reward`: the RLHF reward, which is `objective/scores` - `beta` * `objective/kl`
* `objective/non_score_reward`: `beta` * `objective/kl`
* `objective/entropy`: the entropy of the current policy
* `objective/scores_margin`: the difference between the chosen response scores and the rejected response scores. We pick the chosen response to be the response with higher scores, and the rejected response to be the response with lower scores
* `objective/loss`: the DPO loss
* `logps/chosen`: the log probability of the chosen response
* `logps/rejected`: the log probability of the rejected response
* `reward/chosen`: the implicit DPO reward of the chosen response
* `reward/rejected`: the implicit DPO reward of the rejected response
* `reward_margin`: the difference between the implicit PDO chosen reward and the implicit rejected reward
* `time/from_scratch`: the time taken to train the model from scratch
* `time/training`: the time taken to do one training step
* `val/sequence_lengths`: the length of the sequences in the generated responses
* `val/num_stop_token_ids`: the number of stop tokens in the generated responses




## Implementation details

These are relevant implementation details on reward modeling:

1. The tokenizer pads from the left, so it's straightforward to do generations.
1. Disable dropout in the model: this is an implementation detail in PPO training (see p.3. in https://arxiv.org/pdf/1909.08593).
1. Layer initialization: we initialize the score's weight according to `std=1 / np.sqrt(model.config.hidden_size + 1)` (see p. 11 in https://arxiv.org/abs/2009.01325)
1. Vocab size for RM and Policy: we use the same vocab size for the reward model and the policy model. This is to ensure that the reward model can score all the tokens in the policy model. We added a `ValueError` for situations when `policy.config.vocab_size != reward_model.config.vocab_size`.
1. Retrain on the same prompts: say we only have 10k prompts but we specified `--episodes 100k`, we will shuffle the prompts at every 10k episodes and retrain on them.
1. Truncate responses at the stop token: we truncate the responses at the `--stop_token eos` to ensure the generation is stopped at the stop token.
1. Non-stop penalty: we use a non-stop penalty to the reward model to penalize the model for not stopping at the stop token. For example, if the model does not end at the stop token, we penalize the model by `-10.0` (see `--penalty_reward_value -10.0`).
1. Async training and generation: we follow the architecture in https://arxiv.org/abs/2310.00036 to do rollout and training asynchronously. This is to ensure that the training is not bottlenecked by the generation.
1. We also optimizes online DPO runtime by re-using the model training logprob to save an additional forward pass; notice that this does impact KL calculation and causes some numerical issues. See https://github.com/allenai/open-instruct/pull/364 for more detail.


```python
import queue
import threading
import time

class Agent():
    def __init__(self):
        self.param = 1

    def learn(self, data):
        self.param += 1

def query_generator_fn():
    for i in range(1, 100):
        yield i


ITER = 7
batch_size = 32
agent = Agent()
data_Q = queue.Queue(maxsize=1)
param_and_query_Q = queue.Queue(maxsize=1)
def actor():
    for i in range(1, ITER + 1):
        params, query = param_and_query_Q.get()
        data = params
        print(f"[actor] generating data π_{params} -> p_{query} D_π_{data}")
        time.sleep(1) # simulate data generation
        data_Q.put((query, data))

actor_thread = threading.Thread(target=actor)
actor_thread.start()

# initial param put
generator = query_generator_fn()
next_queries = next(generator)
param_and_query_Q.put((agent.param, next_queries))

# cleanba style stuff
async_mode = True
start_time = time.time()
for g in range(1, ITER + 1):
    queries = next_queries
    if async_mode:
        if g != 1:
            next_queries = next(generator)
        param_and_query_Q.put((agent.param, queries))
    else:
        if g != 1:
            next_queries = next(generator)
            param_and_query_Q.put((agent.param, next_queries)) # note the indent here is different
    _, data = data_Q.get()
    old_param = agent.param
    agent.learn(data)
    time.sleep(1) # simulate training
    print(f"--[leaner] get π_{old_param} ->  p_{queries} D_π_{data} -> π_{agent.param}, time: {time.time() - start_time}")
actor_thread.join()
```
```
[actor] generating data π_1 -> p_1 D_π_1
[actor] generating data π_1 -> p_1 D_π_1
--[leaner] get π_1 ->  p_1 D_π_1 -> π_2, time: 2.0022709369659424
[actor] generating data π_2 -> p_1 D_π_2
--[leaner] get π_2 ->  p_1 D_π_1 -> π_3, time: 3.003502607345581
[actor] generating data π_3 -> p_2 D_π_3
--[leaner] get π_3 ->  p_2 D_π_2 -> π_4, time: 4.004725933074951
[actor] generating data π_4 -> p_3 D_π_4
--[leaner] get π_4 ->  p_3 D_π_3 -> π_5, time: 5.005916118621826
[actor] generating data π_5 -> p_4 D_π_5
--[leaner] get π_5 ->  p_4 D_π_4 -> π_6, time: 6.007085800170898
[actor] generating data π_6 -> p_5 D_π_6
--[leaner] get π_6 ->  p_5 D_π_5 -> π_7, time: 7.007669448852539
--[leaner] get π_7 ->  p_6 D_π_6 -> π_8, time: 8.009439706802368
```

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/ppo.md

# Proximal Policy Optimization (PPO)



## Implemented Variants

- `open_instruct/grpo_vllm_thread_ray_gtrl.py` contains the script for training PPO models.



## `ppo_vllm_thread_ray_gtrl.py`


This implementation has the following features:

- Uses a thread-based approach to parallelize the training and inference processes, based on [Asynchronous RLHF](https://arxiv.org/abs/2410.18252).
- Uses vLLM and Ray to parallelize the training process, based on how [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF) does it



### Debug (Single GPU)

You can run the script in a single GPU mode to debug the training process.

```bash
bash scripts/train/debug/ppo.sh
```



### Reproduce `allenai/Llama-3.1-Tulu-3.1-8B` (2 Nodes)

You can reproduce our `allenai/Llama-3.1-Tulu-3-8B` model by running the following command:

```bash
bash scripts/train/tulu3/ppo_8b.sh
```

### Quality of life tools


Note that when running with `--push_to_hub` and `--with_tracking`, the HF repo is automatically tracked to wandb, so we link the tracked run and the trained model.

![reward modeling tracked hf repo](reward_modeling_hf_repo.png)


Furthermore, we also track the dataset length visualization in wandb (see detail in [here](#dataset-processing))


![token length visualization in wandb](reward_modeling_token_wandb.png)


Finally, we also include samples

![reward modeling preference sample texts](reward_modeling_preference_sample_texts.png)


### Training Metrics

During training, the following metrics are logged:


* `episode`: the global episode number training has gone through (e.g., `3000` means we have trained on 3000 data points already -- in the case of RLVR that is prompts, which can repeat)
* `lr`: the current learning rate
* `epoch`: the fraction or multiple of the epoch (e.g., `2.7` means we have trained on the dataset for 2 epochs and 70% of the third epoch)
* `objective/kl`: the KL divergence between the current policy and the reference policy (sum of the KL divergence of each response token)
* `objective/scores`: the scores of the current response, rated by a combination of reward model and other rewards (e.g., R1 style format reward, verifiable reward, etc.)
* `objective/rlhf_reward`: the RLHF reward, which is `objective/scores` - `beta` * `objective/kl`
* `objective/non_score_reward`: `beta` * `objective/kl`
* `objective/entropy`: the entropy of the current policy
* `objective/loss`: the PPO loss
* `objective/verifiable_correct_rate`: the rate at which responses are verifiably correct, providing a measure of response accuracy
* `loss/policy_avg`: the average policy loss, indicating the mean loss incurred during policy updates
* `policy/approxkl_avg`: the average approximate KL divergence, used to monitor policy stability
* `policy/clipfrac_avg`: the average fraction of updates where the policy was clipped, indicating how often clipping occurs
* `policy/entropy_avg`: the average entropy of the policy, providing a measure of policy randomness
* `time/from_scratch`: the time taken to train the model from scratch
* `time/training`: the time taken to do one training step
* `val/sequence_lengths`: the length of the sequences in the generated responses
* `val/num_stop_token_ids`: the number of stop tokens in the generated responses




## Implementation details

These are relevant implementation details on reward modeling:

1. The tokenizer pads from the left, so it's straightforward to do generations.
1. Disable dropout in the model: this is an implementation detail in PPO training (see p.3. in https://arxiv.org/pdf/1909.08593).
1. Layer initialization: we initialize the score's weight according to `std=1 / np.sqrt(model.config.hidden_size + 1)` (see p. 11 in https://arxiv.org/abs/2009.01325)
1. Vocab size for RM and Policy: we use the same vocab size for the reward model and the policy model. This is to ensure that the reward model can score all the tokens in the policy model. We added a `ValueError` for situations when `policy.config.vocab_size != reward_model.config.vocab_size`.
1. Retrain on the same prompts: say we only have 10k prompts but we specified `--episodes 100k`, we will shuffle the prompts at every 10k episodes and retrain on them.
1. Truncate responses at the stop token: we truncate the responses at the `--stop_token eos` to ensure the generation is stopped at the stop token.
1. Non-stop penalty: we use a non-stop penalty to the reward model to penalize the model for not stopping at the stop token. For example, if the model does not end at the stop token, we penalize the model by `-10.0` (see `--penalty_reward_value -10.0`).
1. Async training and generation: we follow the architecture in https://arxiv.org/abs/2310.00036 to do rollout and training asynchronously. This is to ensure that the training is not bottlenecked by the generation.

```python
import queue
import threading
import time

class Agent():
    def __init__(self):
        self.param = 1

    def learn(self, data):
        self.param += 1

def query_generator_fn():
    for i in range(1, 100):
        yield i


ITER = 7
batch_size = 32
agent = Agent()
data_Q = queue.Queue(maxsize=1)
param_and_query_Q = queue.Queue(maxsize=1)
def actor():
    for i in range(1, ITER + 1):
        params, query = param_and_query_Q.get()
        data = params
        print(f"[actor] generating data π_{params} -> p_{query} D_π_{data}")
        time.sleep(1) # simulate data generation
        data_Q.put((query, data))

actor_thread = threading.Thread(target=actor)
actor_thread.start()

# initial param put
generator = query_generator_fn()
next_queries = next(generator)
param_and_query_Q.put((agent.param, next_queries))

# cleanba style stuff
async_mode = True
start_time = time.time()
for g in range(1, ITER + 1):
    queries = next_queries
    if async_mode:
        if g != 1:
            next_queries = next(generator)
        param_and_query_Q.put((agent.param, next_queries))
    else:
        if g != 1:
            next_queries = next(generator)
            param_and_query_Q.put((agent.param, next_queries)) # note the indent here is different
            queries = next_queries
    _, data = data_Q.get()
    old_param = agent.param
    agent.learn(data)
    time.sleep(1) # simulate training
    print(f"--[leaner] get π_{old_param} ->  p_{queries} D_π_{data} -> π_{agent.param}, time: {time.time() - start_time}")
actor_thread.join()
```
```
# async_mode = True
[actor] generating data π_1 -> p_1 D_π_1
[actor] generating data π_1 -> p_1 D_π_1
--[leaner] get π_1 ->  p_1 D_π_1 -> π_2, time: 2.0003671646118164
[actor] generating data π_2 -> p_2 D_π_2
--[leaner] get π_2 ->  p_1 D_π_1 -> π_3, time: 3.0012056827545166
[actor] generating data π_3 -> p_3 D_π_3
--[leaner] get π_3 ->  p_2 D_π_2 -> π_4, time: 4.001934766769409
[actor] generating data π_4 -> p_4 D_π_4
--[leaner] get π_4 ->  p_3 D_π_3 -> π_5, time: 5.002779722213745
[actor] generating data π_5 -> p_5 D_π_5
--[leaner] get π_5 ->  p_4 D_π_4 -> π_6, time: 6.003664970397949
[actor] generating data π_6 -> p_6 D_π_6
--[leaner] get π_6 ->  p_5 D_π_5 -> π_7, time: 7.004390716552734
--[leaner] get π_7 ->  p_6 D_π_6 -> π_8, time: 8.00534439086914

# async_mode = False
[actor] generating data π_1 -> p_1 D_π_1
--[leaner] get π_1 ->  p_1 D_π_1 -> π_2, time: 2.000866174697876
[actor] generating data π_2 -> p_2 D_π_2
--[leaner] get π_2 ->  p_2 D_π_2 -> π_3, time: 4.002583980560303
[actor] generating data π_3 -> p_3 D_π_3
--[leaner] get π_3 ->  p_3 D_π_3 -> π_4, time: 6.003793239593506
[actor] generating data π_4 -> p_4 D_π_4
--[leaner] get π_4 ->  p_4 D_π_4 -> π_5, time: 8.005346775054932
[actor] generating data π_5 -> p_5 D_π_5
--[leaner] get π_5 ->  p_5 D_π_5 -> π_6, time: 10.00696587562561
[actor] generating data π_6 -> p_6 D_π_6
--[leaner] get π_6 ->  p_6 D_π_6 -> π_7, time: 12.00776195526123
[actor] generating data π_7 -> p_7 D_π_7
--[leaner] get π_7 ->  p_7 D_π_7 -> π_8, time: 14.009297132492065
```



## Acknowledgements

We would like to thank the following resources for PPO theory:

- [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)
- [The N+ Implementation Details of RLHF with PPO: A Case Study on TL;DR Summarization](https://arxiv.org/abs/2403.17031)
- [Asynchronous RLHF](https://arxiv.org/abs/2410.18252)

We would like to thank the following resources for distributed Ray usage:

- [OpenRLHF/OpenRLHF](https://github.com/OpenRLHF/OpenRLHF)


We would like to thank the following projects for general infrastructure:

- [vLLM](https://github.com/vllm-project/vllm)
- [Ray](https://github.com/ray-project/ray)
- [DeepSpeedAI/DeepSpeed](https://github.com/deepspeedai/DeepSpeed)
- [HuggingFace/Transformers](https://github.com/huggingface/transformers)

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/rejection_sampling.md

# Rejection sampling

This is a technique used in the Llama 3 paper. The basic idea is to sample `n` (typically between 10 and 30) outputs from the latest chat model policy (usually
the best performing checkpoint of some kind) and use a reward model to select the best candidate. In the following script, we can vary the `--num_completions` to generate
different number of completions per prompt.


# Debug run (use an interactive session)

This code supports HF models, local models and also API-based models (e.g., `gpt-4`). For generating completions, the code now accepts one model at a time, but we're working on adding an ensemble of models. Stay tuned.

```bash
# 1. first sample a bunch of completions given prompts
# Here is an example created dataset: https://huggingface.co/datasets/vwxyzjn/generation_1727879425
python open_instruct/rejection_sampling/generation.py \
    --dataset_mixer_list allenai/tulu-v2-sft-mixture 100 \
    --dataset_splits train \
    --model_name_or_path allenai/llama-3-tulu-2-8b \
    --num_completions 3 \
    --save_filename output/completions.jsonl \
    --push_to_hub
```

### Scoring completions
You can use either a single RM to score responses or a list of RMs. In the latter case, we will take the majority vote to compute the final score. The RMs can be models explicitly trained as RMs, HF LMs, or API-based models.

Note that by default we include the reference completion in the list of completions to perform rejection sampling. This can be disabled by setting `--no_include_reference_completion_for_rejection_sampling`

```bash
# 2.1 tokenize them and run a reward model to filter them
# Here is an example created dataset: https://huggingface.co/datasets/vwxyzjn/rejection_sampling_1727887719
# Here is an example created dataset for raw scores: https://huggingface.co/datasets/vwxyzjn/rejection_sampling_scores_1727887719/
python open_instruct/rejection_sampling/rejection_sampling.py \
    --input_filename output/completions.jsonl \
    --model_names_or_paths allenai/llama-3-tulu-2-8b-uf-mean-rm \
    --save_filename_scores output/completions_scores.jsonl \
    --save_filename output/rejection_sampled_completions.jsonl \
    --num_completions 3 \
    --push_to_hub \
    --num_gpus 1 \

# 2.1.2 without reference completion in rejection sampling
# Here is an example created dataset: https://huggingface.co/datasets/vwxyzjn/rejection_sampling_1727887719
# Here is an example created dataset for raw scores: https://huggingface.co/datasets/vwxyzjn/rejection_sampling_scores_1727887719/
python open_instruct/rejection_sampling/rejection_sampling.py \
    --input_filename output/completions.jsonl \
    --model_names_or_paths allenai/llama-3-tulu-2-8b-uf-mean-rm \
    --save_filename_scores output/completions_scores.jsonl \
    --save_filename output/rejection_sampled_completions.jsonl \
    --no_include_reference_completion_for_rejection_sampling \
    --num_completions 3 \
    --push_to_hub \
    --num_gpus 1 \

# 2.2 tokenize them and run llm as a judge
# Note then when using LLM as a judge, it's possible that llm api failed to produce a score in our expected
# format, so score extraction failed and we simply mark the score -1.
# Here is an example created dataset: https://huggingface.co/datasets/vwxyzjn/rejection_sampling_1727889563
# Here is an example created dataset for raw scores: https://huggingface.co/datasets/vwxyzjn/rejection_sampling_scores_1727889563
python open_instruct/rejection_sampling/rejection_sampling.py \
    --input_filename output/completions.jsonl \
    --model_names_or_paths gpt-4o-mini  \
    --save_filename_scores output/completions_scores.jsonl \
    --save_filename output/rejection_sampled_completions.jsonl \
    --num_completions 3 \
    --push_to_hub \
    --num_gpus 1 \

# 2.3 tokenize them and run a combination of reward models / llm as a judge
# Here is an example created dataset: https://huggingface.co/datasets/vwxyzjn/rejection_sampling_1724273702
# Here is an example created dataset for raw scores: https://huggingface.co/datasets/vwxyzjn/rejection_sampling_scores_1724273702
python open_instruct/rejection_sampling/rejection_sampling.py \
    --input_filename output/completions.jsonl \
    --model_names_or_paths allenai/llama-3-tulu-2-8b-uf-mean-rm gpt-4o-mini gpt-4-turbo \
    --save_filename_scores output/completions_scores.jsonl \
    --save_filename output/rejection_sampled_completions.jsonl \
    --num_completions 3 \
    --push_to_hub \
    --num_gpus 1 \
 ```



# Run through the entire dataset run

To run through the entire dataset you would need a lot more GPUs to finish the generation more quickly.


```bash
# NOTE: the scripts below only generate 400 prompts, so it's for demonstration purposes only. The scripts are highly scalable, and you could modify its `num_prompts=400` to something else like 300000 for the tulu dataset.

# you need to make sure your default beaker workspace has WANDB_API_KEY and HF_TOKEN secrets in them
beaker secret write HF_TOKEN xxxxxxxxxxxx
beaker secret write WANDB_API_KEY xxxxxxxxxxx

# You can use docker to do the job submission
bash scripts/rejection_sampling_tulu_docker.bash

# if you are using mason you can debug with the following command(s), the
# rejection sampling shards should appear in your local foldeer
bash scripts/rejection_sampling_tulu.bash
```

You can see a demo [here](https://drive.google.com/file/d/1dq3KG15ajpOv8tFYEZGS4tlW7G55oOYP/view?usp=sharing)

<img width="1327" alt="image" src="https://github.com/user-attachments/assets/71a15671-e054-4eab-a571-715881958e74">


# Implementation details

Note that it is possible to generate identical completions per prompt, which is not going to be that useful, so we filter them out via

```py
if len(set([item.text for item in output.outputs])) == 1:
    continue
```



## Debug commands

```bash
# debug job submission; you should install your python on NFS and
# make sure `which python` returns the python environment you are using
python mason.py \
    --cluster ai2/jupiter \
    --priority low \
    --budget ai2/jupiter \
    --gpus 1 -- which python
# sometimes we run into permission issues; need to run the following
python mason.py \
    --cluster ai2/jupiter \
    --priority low \
    --budget ai2/jupiter \
    --gpus 1 -- chmod -R 777 /net/nfs.cirrascale/allennlp/.cache/
```

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/reward_modeling.md

# Reward Modeling (RM)

We support training reward models, mostly based on [Learning to summarize from human feedback](https://arxiv.org/abs/2009.01325).



## Implemented Variants

- `reward_modeling.py` contains the script for training reward models.


## `reward_modeling.py`


This implementation has the following key features:

- Auto save the trained checkpoint to HuggingFace Hub
- Supports LigerKernel for optimized training with fused operations

There are several relevant implementation details:

1. The tokenizer pads from the right: when the length of the data points differ, the tokenizer pads from the right
1. Disable dropout in the model: this is actually an implementation detail in PPO training, but for consistency we also disable dropout in the reward model training (see p.3. in https://arxiv.org/pdf/1909.08593)
1. Layer initialization: we initialize the score's weight according to `std=1 / np.sqrt(model.config.hidden_size + 1)` (see p. 11 in https://arxiv.org/abs/2009.01325)



### Debug (Single GPU)

You can run the script in a single GPU mode to debug the training process.

```bash
bash scripts/train/debug/reward_modeling.sh
```


### Reproduce `allenai/Llama-3.1-Tulu-3-8B-RM` (8 Nodes)

You can reproduce our `allenai/Llama-3.1-Tulu-3-8B-RM` model by running the following command:

```bash
bash scripts/train/tulu3/reward_modeling_8b.sh
```


![finetune_plot](reward_modeling/tulu3_8b_rm.png)
![finetune_plot](reward_modeling/tulu3_8b_rm-time.png)


<iframe loading="lazy" src="https://wandb.ai/ai2-llm/open_instruct_public/reports/Tulu3-8B-RM--VmlldzoxMTkwOTgyNw" style="width:100%; height:500px" title="Tulu3-8B-RM"></iframe>


### Training Metrics

During training, the following metrics are logged:

* `episode`: the global episode number training has gone through (e.g., `3000` means we have trained on 3000 data points already)
* `epoch`: the fraction or multiple of the epoch (e.g., `2.7` means we have trained on the dataset for 2 epochs and 70% of the third epoch)
* `train/rm/accuracy`: the training accuracy of the training batch
* `train/rm/loss`: the logsigmoid loss of the reward modeling of the training batch
* `train/rm/chosen_rewards`: the reward of the chosen responses of the training batch
* `train/rm/rejected_rewards`: the reward of the rejected responses of the training batch
* `train/rm/reward_margin`: the reward margin (chosen_reward - rejected_reward) of the training batch
* `train/rm/lr`: the training learning rate


We also have `eval/rm/accuracy`, `eval/rm/loss`, `eval/rm/chosen_rewards`, `eval/rm/rejected_rewards`, `eval/rm/reward_margin` for the evalation dataset.



## Acknowledgements

We would like to thank the following projects for general infrastructure:

- [DeepSpeedAI/DeepSpeed](https://github.com/deepspeedai/DeepSpeed)
- [HuggingFace/Transformers](https://github.com/huggingface/transformers)

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/synthetic_preference_dataset.md

# Synthetic preference dataset

This section focuses explicitly on creating synthetic preference datasets.

# Debug run (use an interactive session)

This code supports HF models, local models and also API-based models (e.g., `gpt-4`). For generating completions, the code now accepts one model at a time, but we're working on adding an ensemble of models. Stay tuned.

```bash
# 1. first sample a bunch of completions given prompts
# Here is an example created dataset: https://huggingface.co/datasets/vwxyzjn/generation_1725567768
python open_instruct/rejection_sampling/generation.py \
    --dataset_mixer_list HuggingFaceH4/no_robots 100 \
    --dataset_splits train \
    --model_name_or_path allenai/llama-3-tulu-2-8b \
    --num_completions 3 \
    --save_filename output/completions.jsonl \
    --sanity_check \
    --push_to_hub
```

### Create preference pairs

```bash
# 2.1 do LLM as a judge to create synthetic preference dataset
# Here is an example created dataset: https://huggingface.co/datasets/vwxyzjn/synthetic_preference_dataset_1725567862
python open_instruct/rejection_sampling/synthetic_preference_dataset.py \
    --input_filename output/completions.jsonl \
    --model gpt-4o-2024-08-06 \
    --save_filename output/synthetic_preferences.jsonl \
    --num_completions 3 \
    --push_to_hub \
```


You can visualize the dataset via

```bash
python -m costa_utils.hf_viz \
    --sft vwxyzjn/synthetic_preference_dataset_1725567862 \
    --split train \
    --sft_messages_column_name whole_conversation

python -m costa_utils.hf_viz \
    --preference vwxyzjn/synthetic_preference_dataset_1725567862 \
    --split train \
    --preference_chosen_column_name chosen \
    --preference_rejected_column_name rejected
```

![synthetic_preference_dataset](synthetic_preference_dataset.png)

# Run through the entire dataset run

To run through the entire dataset you would need a lot more GPUs to finish the generation more quickly.


```bash
# NOTE: the scripts below only generate 400 prompts, so it's for demonstration purposes only. The scripts are highly scalable, and you could modify its `num_prompts=400` to something else like 300000 for the tulu dataset.

# you need to make sure your default beaker workspace has WANDB_API_KEY and HF_TOKEN secrets in them
beaker secret write HF_TOKEN xxxxxxxxxxxx
beaker secret write WANDB_API_KEY xxxxxxxxxxx

# Docker mode: using caches from WEKA
deploy_mode="docker_weka" bash scripts/synthetic_preference_dataset.bash

# Docker mode: using caches from NFS
deploy_mode="docker_nfs" bash scripts/synthetic_preference_dataset.bash

# Docker mode: do not use caches
deploy_mode="docker" bash scripts/synthetic_preference_dataset.bash

# If you have environment setup with NFS and want to launch debug mode:
deploy_mode="nfs" bash scripts/synthetic_preference_dataset.bash
```

You can see a demo [here](https://drive.google.com/file/d/1dq3KG15ajpOv8tFYEZGS4tlW7G55oOYP/view?usp=sharing)

<img width="1327" alt="image" src="https://github.com/user-attachments/assets/71a15671-e054-4eab-a571-715881958e74">

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/trained_model_location.md

# Trained Model Location

When running our training scripts, the model will get uploaded to several places when applicable for redundancy, depending on the cluster environment:

* Hugging Face
* Google Cloud Storage
* Ai2's internal beaker dataset
* Local storage



## Hugging Face

Let's use [https://wandb.ai/ai2-llm/open_instruct_public/runs/tyfe1095](https://wandb.ai/ai2-llm/open_instruct_public/runs/tyfe1095) as an example. If you go to its wandb's Overview page -> config -> search for `hf`, then you can find this `hf_repo_url`.

![](trained_model_location/hf.png)
![](trained_model_location/hf2.png)

To download, notice the `run_name` for this run is `tulu3_8b_dpo__1__1742613782`. So you can use the following command to download the model:

```bash
exp_name=tulu3_8b_dpo__1__1742613782
# first download the model
huggingface-cli download --revision $exp_name allenai/open_instruct_dev
# get the cache directory
exp_cache_dir=$(huggingface-cli download --revision $exp_name allenai/open_instruct_dev)
ls $exp_cache_dir
```
```
Downloading 'config.json' to '/weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/c0ed34722856586c3fa9ccb27bd52fb8e1d759a1.incomplete'
config.json: 100%|████████████████████████████████████████████████████████████| 984/984 [00:00<00:00, 5.84MB/s]
Download complete. Moving file to /weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/c0ed34722856586c3fa9ccb27bd52fb8e1d759a1
Downloading 'pytorch_model-00001-of-00004.bin' to '/weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/9da6b1637575b207617b84e84a5a974e8ee2a9fab55bd7e0343d6edf2a9f9f28.incomplete'
pytorch_model-00001-of-00004.bin: 100%|███████████████████████████████████▉| 4.98G/4.98G [00:07<00:00, 662MB/s]
Download complete. Moving file to /weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/9da6b1637575b207617b84e84a5a974e8ee2a9fab55bd7e0343d6edf2a9f9f28
Downloading 'pytorch_model-00002-of-00004.bin' to '/weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/667937dac38f3df4ffe7f5be637b54bed58c40b78c39550b639d12f6d57461b7.incomplete'
pytorch_model-00002-of-00004.bin: 100%|███████████████████████████████████▉| 5.00G/5.00G [00:07<00:00, 657MB/s]
Download complete. Moving file to /weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/667937dac38f3df4ffe7f5be637b54bed58c40b78c39550b639d12f6d57461b7
Downloading 'pytorch_model-00003-of-00004.bin' to '/weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/7d0471f489239e21a2063568974d4b118f294b5d1a381f306fe165729b6e88d3.incomplete'
pytorch_model-00003-of-00004.bin: 100%|███████████████████████████████████▉| 4.92G/4.92G [00:07<00:00, 678MB/s]
Download complete. Moving file to /weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/7d0471f489239e21a2063568974d4b118f294b5d1a381f306fe165729b6e88d3
Downloading 'pytorch_model-00004-of-00004.bin' to '/weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/ff53f644b12798a5e81c6c8072169a29b6a318a251d7d939687e2af333efe51e.incomplete'
pytorch_model-00004-of-00004.bin: 100%|███████████████████████████████████▉| 1.17G/1.17G [00:03<00:00, 337MB/s]
Download complete. Moving file to /weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/blobs/ff53f644b12798a5e81c6c8072169a29b6a318a251d7d939687e2af333efe51e
/weka/oe-adapt-default/allennlp/.cache/hub/models--allenai--open_instruct_dev/snapshots/40227c36fb1b5b714a71f9d635ead5a79c23507f
root@phobos-cs-aus-452:/weka/oe-adapt-default/costah/oi2/docs/algorithms/trained_model_location# # get the cache directory
root@phobos-cs-aus-452:/weka/oe-adapt-default/costah/oi2/docs/algorithms/trained_model_location# exp_cache_dir=$(huggingface-cli download --revision $exp_name allenai/open_instruct_dev)
root@phobos-cs-aus-452:/weka/oe-adapt-default/costah/oi2/docs/algorithms/trained_model_location# ls $exp_cache_dir
config.json                       pytorch_model-00003-of-00004.bin  special_tokens_map.json
generation_config.json            pytorch_model-00004-of-00004.bin  tokenizer_config.json
pytorch_model-00001-of-00004.bin  pytorch_model.bin.index.json      tokenizer.json
pytorch_model-00002-of-00004.bin  README.md
```

## Google Cloud Storage

Let's use [https://wandb.ai/ai2-llm/open_instruct_public/runs/tyfe1095](https://wandb.ai/ai2-llm/open_instruct_public/runs/tyfe1095) as an example. Because this run was conducted on the `ai2/augusta`, `mason.py` automatically appends `--gs_bucket_path gs://ai2-llm/post-training/` to the training args (for external users you can try doing the same append). Then, the model was automatically uploaded to

```
gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782
```

![](trained_model_location/gcs.png)

To download, you can run the following command:

```
gsutil -o "GSUtil:parallel_composite_upload_threshold=150M" \
    -o "GSUtil:parallel_thread_count=1" \
    -m \
    cp -r gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782 .
ls tulu3_8b_dpo__1__1742613782
```
```
root@phobos-cs-aus-452:/weka/oe-adapt-default/costah/oi2/tulu3_8b_dpo__1__1742613782# gsutil -o "GSUtil:parallel_composite_upload_threshold=150M" \
>     -o "GSUtil:parallel_thread_count=1" \
>     -m \
>     cp -r gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782 .
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/config.json...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/generation_config.json...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/pytorch_model-00001-of-00004.bin...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/pytorch_model-00002-of-00004.bin...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/pytorch_model-00003-of-00004.bin...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/pytorch_model-00004-of-00004.bin...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/pytorch_model.bin.index.json...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/special_tokens_map.json...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/tokenizer.json...
Copying gs://ai2-llm/post-training//costah/output/tulu3_8b_dpo__1__1742613782/tokenizer_config.json...
Resuming download for ./tulu3_8b_dpo__1__1742613782/pytorch_model-00003-of-00004.bin component 0
Resuming download for ./tulu3_8b_dpo__1__1742613782/pytorch_model-00003-of-00004.bin component 1
Resuming download for ./tulu3_8b_dpo__1__1742613782/pytorch_model-00003-of-00004.bin component 2
Resuming download for ./tulu3_8b_dpo__1__1742613782/pytorch_model-00003-of-00004.bin component 3
| [10/10 files][ 15.0 GiB/ 15.0 GiB] 100% Done  52.1 MiB/s ETA 00:00:00
Operation completed over 10 objects/15.0 GiB.
root@phobos-cs-aus-452:/weka/oe-adapt-default/costah/oi2/tulu3_8b_dpo__1__1742613782# ls
tulu3_8b_dpo__1__1742613782
root@phobos-cs-aus-452:/weka/oe-adapt-default/costah/oi2/tulu3_8b_dpo__1__1742613782# ls tulu3_8b_dpo__1__1742613782
config.json                       pytorch_model-00003-of-00004.bin  tokenizer_config.json
generation_config.json            pytorch_model-00004-of-00004.bin  tokenizer.json
pytorch_model-00001-of-00004.bin  pytorch_model.bin.index.json
pytorch_model-00002-of-00004.bin  special_tokens_map.json
```



## Local storage / NFS

The local storage is quite ephemeral. Sometimes we try to assign an `output_dir` to a particular directory. For example, when launching with `mason.py`, we automatically overwrite the `output_dir` to be `/weka/oe-adapt-default/allennlp/deletable_checkpoint/$beaker_user/`. You can find the model in the following directory:


![](trained_model_location/local.png)


```
ls "/weka/oe-adapt-default/allennlp/deletable_checkpoint/valpy/tulu3_8b_sft_no_IF__8__1745534652"
config.json                       pytorch_model-00003-of-00004.bin  tokenizer_config.json
generation_config.json            pytorch_model-00004-of-00004.bin  tokenizer.json
pytorch_model-00001-of-00004.bin  pytorch_model.bin.index.json
pytorch_model-00002-of-00004.bin  special_tokens_map.json
```


## Beaker Dataset (Ai2's internal storage)

When possible, we try to upload the model to beaker dataset. You can find the model in corresponding beaker experiment by looking up `beaker_experiment_url` in the tracked wandb run.


![](trained_model_location/beaker_dataset.gif)

You can download the model by running the following command:

```bash
exp_name=tulu3_8b_dpo__1__1742613782
dataset_id=01JPXXXKZPACGK5AZ1XSD5V54F
mkdir $exp_name
beaker dataset fetch "$dataset_id" -o $exp_name --concurrency 64
```
```
Downloading dataset 01JPXXXKZPACGK5AZ1XSD5V54F to tulu3_8b_dpo__1__1742613782
Files: 6          4 in progress ⠸
Bytes: 16.49 MiB  14.96 GiB in progress ⠸
```

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/data/preference-data.md

# Current preference datasets

To build all the datasets at once (use this carefully), run:
```
sh scripts/data/preferences/prepare_all.sh
```

## Chat

### Maintained here

First, older popular datasets. Build these datasets (a subset only) with:
```
python scripts/data/preferences/webgpt.py --push_to_hub --hf_entity=ai2-adapt-dev
python scripts/data/preferences/hh-harmless.py --push_to_hub --hf_entity=ai2-adapt-dev
python scripts/data/preferences/hh-helpful.py --push_to_hub --hf_entity=ai2-adapt-dev
```
* [ai2-adapt-dev/webgpt-binarized](https://huggingface.co/datasets/ai2-adapt-dev/webgpt-binarized)
* [ai2-adapt-dev/hh-rlhf-harmless](https://huggingface.co/datasets/ai2-adapt-dev/hh-rlhf-harmless)
* [ai2-adapt-dev/hh-rlhf-helpful](https://huggingface.co/datasets/ai2-adapt-dev/hh-rlhf-helpful)

Next, Nvidia's recent HelpSteer 2.
They are created with:
```
python scripts/data/preferences/helpsteer2.py --push_to_hub --min_score 2.5 --hf_entity=ai2-adapt-dev
python scripts/data/preferences/helpsteer2.py --push_to_hub --min_score 2 --hf_entity=ai2-adapt-dev
python scripts/data/preferences/helpsteer2.py --push_to_hub --min_score 2 --hf_entity=ai2-adapt-dev --aspects_to_ignore verbosity
python scripts/data/preferences/helpsteer2.py --push_to_hub --hf_entity=ai2-adapt-dev --aspects_to_ignore verbosity
```
The binarization weighting that Nvidia recommends can be used with:
```
python scripts/data/preferences/helpsteer2_nvidia.py --push_to_hub --hf_entity ai2-adapt-dev
```
Some examples include:
* [ai2-adapt-dev/helpsteer-2-binarized-above-2.0-margin-0.5-ignore-verbosity](https://huggingface.co/datasets/ai2-adapt-dev/helpsteer-2-binarized-above-2.0-margin-0.5-ignore-verbosity)
* [ai2-adapt-dev/helpsteer-2-binarized-ignore-verbosity](https://huggingface.co/datasets/ai2-adapt-dev/helpsteer-2-binarized-ignore-verbosity): This ignores verbosity aspect, which is unclear in the paper.
* [ai2-adapt-dev/helpsteer2-binarized-nvidia-spec](https://huggingface.co/datasets/ai2-adapt-dev/helpsteer2-binarized-nvidia-spec): This uses the specific weighting that Nvidia converged on in their HelpSteer2 paper training multiple types of reward models.

Also, specific splits of Nectar (randomly binarized from top 3 completions and a bottom completion) are included with:
```
python scripts/data/preferences/nectar.py --push_to_hub --hf_entity ai2-adapt-dev
python scripts/data/preferences/nectar.py --push_to_hub --subset anthropic-hh --hf_entity ai2-adapt-dev
python scripts/data/preferences/nectar.py --push_to_hub --deduplication --hf_entity ai2-adapt-dev
```
The default split is `lmsys-chat-1m`.
The last example is called "deduplication" due to potential overlap with UltraFeedback, given they source from the same underlying dataset. Basic tests showed they did not use the same prompts, but slight modifications could've occured.
* [ai2-adapt-dev/nectar_binarized-anthropic-hh](https://huggingface.co/datasets/ai2-adapt-dev/nectar_binarized-anthropic-hh)
* [ai2-adapt-dev/nectar_binarized-lmsys-chat-1m](https://huggingface.co/datasets/ai2-adapt-dev/nectar_binarized-lmsys-chat-1m)
* [ai2-adapt-dev/nectar_binarized-dedup-ultrafeedback](https://huggingface.co/datasets/ai2-adapt-dev/nectar_binarized-dedup-ultrafeedb)ack

### Stored on HF
* [allenai/ultrafeedback_binarized_cleaned_train](https://huggingface.co/datasets/allenai/ultrafeedback_binarized_cleaned_train)
* [ai2-adapt-dev/summarize_from_feedback](https://huggingface.co/datasets/ai2-adapt-dev/summarize_from_feedback)
* [ai2-adapt-dev/DaringAnteater-prefs](https://huggingface.co/datasets/ai2-adapt-dev/DaringAnteater-prefs)
* [ai2-adapt-dev/DaringAnteater-prefs-RM-filter](https://huggingface.co/datasets/ai2-adapt-dev/DaringAnteater-prefs-RM-filter)
* [ai2-adapt-dev/WildChat-prefs-280824](https://huggingface.co/datasets/ai2-adapt-dev/WildChat-prefs-280824)
* [ai2-adapt-dev/helpsteer2-binarized-mean-aspects](https://huggingface.co/datasets/ai2-adapt-dev/helpsteer2-binarized-mean-aspects): Similar to our other HelpSteer splits, less processing.
* [ai2-adapt-dev/Skywork-Magpie](https://huggingface.co/datasets/ai2-adapt-dev/Skywork-Magpie): Subset of the [Skywork Preference Dataset](https://huggingface.co/datasets/Skywork/Skywork-Reward-Preference-80K-v0.1) for only the [Magpie](https://arxiv.org/abs/2406.08464) splits.

### UltraFeedback Replication

**The current replications have fewer prompts than the original. These are built by splitting the original and recreating completions. We are working on merging them.**

Build these datasets with:
```
python scripts/data/preferences/ultrafeedback.py --push_to_hub --hf_entity=ai2-adapt-dev
```
The master version of the UltraFeedback pipeline replication can be found here:
[ai2-adapt-dev/ultrafeedback-pipeline-replication](https://huggingface.co/datasets/ai2-adapt-dev/ultrafeedback-pipeline-replication)

UltraFeedback variants explore different combinations of prompt sources, model diversity, sampling methods, and prompt templates:

- Setup 0: Replication of original UltraFeedback
- Setup 1-2: Custom prompts with UltraFeedback methodology
- Setup 3-4: Custom prompts with varied model diversity and principle sampling
- Setup 5: Custom prompts with UltraFeedback template
- Setup 6: Increased model diversity

- [ai2-adapt-dev/ultrafeedback-replication-p0](https://huggingface.co/datasets/ai2-adapt-dev/ultrafeedback-replication-p0)
- [ai2-adapt-dev/ultrafeedback-replication-p1](https://huggingface.co/datasets/ai2-adapt-dev/ultrafeedback-replication-p1)
- [ai2-adapt-dev/ultrafeedback-replication-p2](https://huggingface.co/datasets/ai2-adapt-dev/ultrafeedback-replication-p2)
- [ai2-adapt-dev/ultrafeedback-replication-p3](https://huggingface.co/datasets/ai2-adapt-dev/ultrafeedback-replication-p3)
- [ai2-adapt-dev/ultrafeedback-replication-p4](https://huggingface.co/datasets/ai2-adapt-dev/ultrafeedback-replication-p4)
- [ai2-adapt-dev/ultrafeedback-replication-p5](https://huggingface.co/datasets/ai2-adapt-dev/ultrafeedback-replication-p5)
- [ai2-adapt-dev/ultrafeedback-replication-p6](https://huggingface.co/datasets/ai2-adapt-dev/ultrafeedback-replication-p6)

## UltraInteract Variants
Build these datasets with:
```
python scripts/data/preferences/ultrainteract.py --push_to_hub --hf_entity=ai2-adapt-dev
```
Split by category and by selecting the longest conversations per prompt or a random length per prompt.
From [UltraInteract_pair](https://huggingface.co/datasets/openbmb/UltraInteract_pair).

* [ai2-adapt-dev/UltraInteract_pair_maxlen_Coding](https://huggingface.co/datasets/ai2-adapt-dev/UltraInteract_pair_maxlen_Coding)
* [ai2-adapt-dev/UltraInteract_pair_randomlen_Coding](https://huggingface.co/datasets/ai2-adapt-dev/UltraInteract_pair_randomlen_Coding)
* [ai2-adapt-dev/UltraInteract_pair_maxlen_Math_CoT](https://huggingface.co/datasets/ai2-adapt-dev/UltraInteract_pair_maxlen_Math_CoT)
* [ai2-adapt-dev/UltraInteract_pair_randomlen_Math_CoT](https://huggingface.co/datasets/ai2-adapt-dev/UltraInteract_pair_randomlen_Math_CoT)
* [ai2-adapt-dev/UltraInteract_pair_maxlen_Math_PoT](https://huggingface.co/datasets/ai2-adapt-dev/UltraInteract_pair_maxlen_Math_PoT)
* [ai2-adapt-dev/UltraInteract_pair_randomlen_Math_PoT](https://huggingface.co/datasets/ai2-adapt-dev/UltraInteract_pair_randomlen_Math_PoT)
* [ai2-adapt-dev/UltraInteract_pair_maxlen_Logic](https://huggingface.co/datasets/ai2-adapt-dev/UltraInteract_pair_maxlen_Logic)
* [ai2-adapt-dev/UltraInteract_pair_randomlen_Logic](https://huggingface.co/datasets/ai2-adapt-dev/UltraInteract_pair_randomlen_Logic)

## Tulu 2.5 Data
Build these datasets with:
```
python scripts/data/preferences/split_tulu2.5_prefs.py --push_to_hub --hf_entity=ai2-adapt-dev

```
Split from [this dataset](https://huggingface.co/datasets/allenai/tulu-2.5-preference-data) for easier mixing:
* [ai2-adapt-dev/tulu-2.5-prefs-alpaca_farm_gpt4_pref](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-alpaca_farm_gpt4_pref)
* [ai2-adapt-dev/tulu-2.5-prefs-alpaca_farm_human_pref](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-alpaca_farm_human_pref)
* [ai2-adapt-dev/tulu-2.5-prefs-argilla_dpo_mix](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-argilla_dpo_mix)
* [ai2-adapt-dev/tulu-2.5-prefs-capybara](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-capybara)
* [ai2-adapt-dev/tulu-2.5-prefs-chatbot_arena_2023](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-chatbot_arena_2023)
* [ai2-adapt-dev/tulu-2.5-prefs-chatbot_arena_2024](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-chatbot_arena_2024)
* [ai2-adapt-dev/tulu-2.5-prefs-helpsteer](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-helpsteer)
* [ai2-adapt-dev/tulu-2.5-prefs-hh_rlhf](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-hh_rlhf)
* [ai2-adapt-dev/tulu-2.5-prefs-hh_rlhf_60k](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-hh_rlhf_60k)
* [ai2-adapt-dev/tulu-2.5-prefs-nectar](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-nectar)
* [ai2-adapt-dev/tulu-2.5-prefs-nectar_60k](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-nectar_60k)
* [ai2-adapt-dev/tulu-2.5-prefs-orca_dpo_pairs](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-orca_dpo_pairs)
* [ai2-adapt-dev/tulu-2.5-prefs-preference_big_mixture](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-preference_big_mixture)
* [ai2-adapt-dev/tulu-2.5-prefs-prm800k_pairs_phase2](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-prm800k_pairs_phase2)
* [ai2-adapt-dev/tulu-2.5-prefs-shp_2](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-shp_2)
* [ai2-adapt-dev/tulu-2.5-prefs-stack_exchange_60k](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-stack_exchange_60k)
* [ai2-adapt-dev/tulu-2.5-prefs-stack_exchange_paired](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-stack_exchange_paired)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_evol_instruct](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_evol_instruct)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_false_qa](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_false_qa)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_flan_v2](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_flan_v2)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_lower_10k](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_lower_10k)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_mean_aspects](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_mean_aspects)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_middle_10k](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_middle_10k)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_overall](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_overall)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_sharegpt](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_sharegpt)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_top_10k](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_top_10k)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_truthful_qa](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_truthful_qa)
* [ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_ultrachat](https://huggingface.co/datasets/ai2-adapt-dev/tulu-2.5-prefs-ultrafeedback_ultrachat)

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/get_started/ai2_internal_setup.md

# Ai2 Internal Setup

This document details some best practices when working with our cluster.

## (One-time setup) VScode + Weka setup

You should join the `#vscode-weka-dev-workflow` slack channel to setup your VScode to work with weka.

After following the instructions there, you should end up with a VScode / Cursor setup that looks like this:

- Your terminal has direct access to the weka filesystem.
- You can run `beaker` commands from the terminal.
- You can edit files in the weka filesystem.
- You can run python scripts with the pyenv / uv environment.

![VScode setup](./vscode.png)


## (One-time setup) Setup API keys

You need to first obtain API key or tokens from the following website:

* `BEAKER_TOKEN`: [https://beaker.org/user](https://beaker.org/user)
* `WANDB_API_KEY`: [https://wandb.ai/authorize](https://wandb.ai/authorize)
* `HF_TOKEN`: [https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

Then you need to write them in beaker secret as follows (replace the `xxxx` with your own API key or token)
```bash
beaker_whoami=$(beaker account whoami --format json | jq -r '.[0].name')
beaker secret write -w ai2/tulu-2-improvements "${beaker_whoami}_BEAKER_TOKEN" xxxx
beaker secret write -w ai2/tulu-2-improvements "${beaker_whoami}_WANDB_API_KEY" xxxx
beaker secret write -w ai2/tulu-2-improvements "${beaker_whoami}_HF_TOKEN" xxxx
beaker secret write -w ai2/tulu-3-dev "${beaker_whoami}_BEAKER_TOKEN" xxxx
beaker secret write -w ai2/tulu-3-dev "${beaker_whoami}_WANDB_API_KEY" xxxx
beaker secret write -w ai2/tulu-3-dev "${beaker_whoami}_HF_TOKEN" xxxx
```


## mason.py (for job submission)

`mason.py` is our job submission script. It basically takes your command and runs it in the specified clusters.

For example, let's say you have a training job like this:

```bash
python open_instruct/finetune.py \
    --model_name_or_path EleutherAI/pythia-14m \
    --tokenizer_name EleutherAI/pythia-14m \
    --dataset_mixer_list allenai/tulu-3-sft-personas-algebra 100 \
    --use_flash_attn False \
    --with_tracking --report_to wandb
```

You can take your command above and run it on the weka cluster with the following command (use `--` to separate the mason command from the python command):

```bash
python mason.py \
    --cluster ai2/jupiter ai2/saturn ai2/neptune \
    --workspace ai2/tulu-3-dev \
    --image nathanl/open_instruct_auto --pure_docker_mode \
    --priority normal \
    --budget ai2/oe-adapt \
    --gpus 0 -- python open_instruct/finetune.py \
    --model_name_or_path EleutherAI/pythia-14m \
    --tokenizer_name EleutherAI/pythia-14m \
    --dataset_mixer_list allenai/tulu-3-sft-personas-algebra 100 \
    --use_flash_attn False \
    --with_tracking --report_to wandb
```


![mason.py](./mason.png)

![mason_job.py](./mason_job.png)



`mason.py` does a few things:

**Auto set HF cache environment variables:**

During the job submission, it automatically tries to setup a shared Hugging Face cache with environment variables. For example, it sets

* `HF_HOME=/weka/oe-adapt-default/allennlp/.cache/huggingface`.
* `HF_DATASETS_CACHE=/weka/oe-adapt-default/allennlp/.cache/huggingface`
* `HF_HUB_CACHE=/weka/oe-adapt-default/allennlp/.cache/hub`

**Auto set `--hf_entity` and `--wandb_entity` arguments:**

so during runtime we issue fewer HF API calls, which sometimes could fail due to rate limiting.

**Auto caching datasets:**

mason.py will auto call `--cache_dataset_only` for you, so you do the tokenization locally instead of in the jobs, which saves idle GPU time in the actual jobs.


**Auto upload to Google Cloud Storage:**

When submitting to the `ai2/augusta` cluster, mason will try to read your model and upload it to Google Cloud Storage and download it to the job (since the cluster does not have a reliable shared filesystem).



## update_command_args.py (for sweep, benchmark, etc.)

The [/scripts/train](/scripts/train) directory contains many examples on how to launch jobs with mason.py. Sometimes the commands can get long and hard to manage, so we wrote a script called [update_command_args.py](/update_command_args.py) that can be used to add or update arguments in a shell script. For example,

```bash
python update_command_args.py scripts/train/tulu3/grpo_fast_8b.sh \
    --cluster ai2/augusta \
    --priority normal \
    --image costah/open_instruct_dev0320_11  --non_stop_penalty False | uv run bash
```

This will update the `--cluster`, `--priority`, `--image`, and `--non_stop_penalty` arguments in the script with the ones specified, making it easier to launch jobs with different configurations.


As another example, you can run something like this for a learning rate search:

```bash
for lr in 1e-6 1e-5 1e-4; do
    python update_command_args.py scripts/train/tulu3/grpo_fast_8b.sh \
        --exp_name grpo_fast_8b_lr_${lr} \
        --learning_rate $lr \
        --image costah/open_instruct_dev0320_11 --non_stop_penalty False | uv run bash
done
```

We also have a script called [scripts/train/benchmark.sh](/scripts/train/benchmark.sh) that keeps track of all the commands used to launch jobs in our public [wandb project `ai2-llm/open_instruct_public`](https://wandb.ai/ai2-llm/open_instruct_public).




## Ai2 Internal Evaluation

We provide a script integrated with beaker for use internally at Ai2. There are couple of use cases.

*1.* Run evals against a public Hugging Face model. Basically you need to prefix the model name with `hf-` and provide the location as the HF path (e.g. `meta-llama/Meta-Llama-3-8B-Instruct`).

```bash
for model in allenai/OLMoE-1B-7B-0125-Instruct allenai/OLMoE-1B-7B-0125-DPO allenai/OLMoE-1B-7B-0125-SFT allenai/OLMoE-1B-7B-0924-SFT allenai/OLMoE-1B-7B-0924-Instruct; do
python scripts/submit_eval_jobs.py \
    --model_name hf-$model \
    --cluster ai2/jupiter ai2/neptune ai2/saturn ai2/ceres  \
    --priority high \
    --location $model \
    --is_tuned \
    --workspace "tulu-3-results" \
    --priority high \
    --preemptible \
    --use_hf_tokenizer_template \
    --run_oe_eval_experiments \
    --evaluate_on_weka \
    --skip_oi_evals
done
```


*2.* Run evals against a model hosted on Beaker dataset. If it's a training run, you should try matching the `exp_name` and `run_id` with the training run.


```bash
model_name=0222_32B_dpo_lr_8.5e-7__allenai_open_instruct_dev__42__1741225304
url=https://wandb.ai/ai2-llm/open_instruct_internal/runs/7afq8x28
location=01JNMHSM8DDSFB3GJDBM5MP6J8
python scripts/submit_eval_jobs.py \
    --model_name $model_name \
    --cluster ai2/jupiter ai2/neptune ai2/saturn ai2/ceres  \
    --priority high \
    --location $location \
    --is_tuned \
    --workspace "tulu-3-results" \
    --preemptible \
    --use_hf_tokenizer_template \
    --run_oe_eval_experiments \
    --skip_oi_evals \
    --run_id $url
```

This will later show up in the [internal leaderboard](https://huggingface.co/spaces/allenai/oe-eval-leaderboard).

![internal leaderboard](./internal_leaderboard.png)


*3.* Run evals against a model hosted on weka.

```bash
python scripts/submit_eval_jobs.py \
    --model_name test_no_hf_upload \
    --location /weka/oe-adapt-default/costah/models/0129_grpo_math_kl_fix_zs_0.0_16_half-m_461_checkpoints/step_640 \
    --cluster ai2/saturn ai2/neptune \
    --is_tuned \
    --workspace "tulu-3-results" \
    --priority high \
    --preemptible \
    --use_hf_tokenizer_template \
    --beaker_image "nathanl/open_instruct_auto" \
    --run_oe_eval_experiments \
    --evaluate_on_weka \
    --oe_eval_tasks gsm8k::tulu,minerva_math::tulu \
    --run_id https://wandb.ai/ai2-llm/open_instruct_internal/runs/swf79vby \
    --skip_oi_evals \
    --oe_eval_max_length 8096
```


*4.* Run evals against a model on Google Cloud Storage.

```bash
python scripts/submit_eval_jobs.py \
    --model_name test_gs_location \
    --location gs://ai2-llm/post-training/allenai/Llama-3.1-Tulu-3.1-8B \
    --cluster ai2/augusta \
    --is_tuned \
    --workspace tulu-3-results \
    --preemptible \
    --use_hf_tokenizer_template \
    --beaker_image nathanl/open_instruct_auto \
    --oe_eval_tasks gsm8k::tulu \
    --skip_oi_evals \
    --gpu_multiplier 2 \
    --run_oe_eval_experiments
```


## Running with gantry

You can also run with gantry, if you want to test changes.
**Important**: Before you run any command with gantry, make sure you *commit and push*, since gantry will attempt to clone the repo with your local latest commit hash.

See the "One-Time Setup" section below before running commands. To test your setup, run the following command -- if this job succeeds, then you're ready to run evaluations with gantry.

```bash
gantry run --workspace {workspace} --budget ai2/oe-adapt --beaker-image kavelr/oe-safety --venv base --cluster ai2/jupiter --env-secret OPENAI_API_KEY=openai_api_key --env-secret HF_TOKEN=hf_token -- python -c 'print("Hello world")'
```

You can freely add any additional arguments to give to Beaker, such as a `--priority` tag which can be set to preemptible, normal, high, or urgent. AI2 policies may restrict the priorities that are available to users on certain clusters.

In the examples below, text within {} tags should be replaced with your own values.

As a convenience, you can use the `evaluation/gantry_run.sh` script which includes some necessary arguments. You can use it the same way as `gantry run`, but excluding these boilerplate arguments (take a look at the script to see what it includes). Example usage:

```bash
PYTHONPATH=safety-eval ./evaluation/gantry_run.sh --workspace {workspace} --cluster {cluster} --gpus {n_gpus} \
    --priority {priority} -- python evaluation/run_all_generation_benchmarks.py \
    --model_name_or_path allenai/tulu-2-dpo-7b \
    --model_input_template_path_or_name tulu2 \
    --report_output_path /results/metrics.json
```

### Extra Beaker Commands
Here is an example using the full `gantry run` command. Use the beaker image `seungjuh/oe-safety-support-olmo17`

**Important**: Please include all the beaker arguments exactly as in the examples unless intentionally modifying some configuration. Many of them are necessary to avoid job failures, such as `--beaker-image`, `--venv`, and `--env-secret`. Note that `openai_api_key` and `hf_token` are Beaker workspace secret names, so should *not* be replaced with actual values (see One-Time Setup).

Note that the `--` divides the gantry command from the evaluation command - you can edit the second part to run whatever eval suite you want from the `eval.py` script. Any additional Beaker arguments such as a dataset mount to use a model from a Beaker dataset or adding a priority tag can be added before the `--`.

You can also run all generator evaluations parallelized across the GPUs allocated to your batch job, like so:
```bash
gantry run --workspace {your_workspace} --cluster {cluster} --gpus {n_gpus} \
    --name {beaker_experiment_name} --task-name {beaker_task_name} --beaker-image seungjuh/oe-safety-support-olmo17 --venv base \
    --env-secret OPENAI_API_KEY=openai_api_key \
    --env-secret HF_TOKEN=hf_token \
    --budget {budget} -- python evaluation/run_all_generation_benchmarks.py \
    --model_name_or_path allenai/tulu-2-dpo-7b \
    --model_input_template_path_or_name tulu2 \
    --report_output_path /results/metrics.json --save_individual_results_path /results/all.json
```

Because the `--report_output_path` argument is set to `/results/metrics.json`, the output will automatically get logged to Beaker metrics in the experiment page ([example](https://beaker.org/ex/01HW8NKZ458MA1PSB1X4YQTH94/tasks/01HW8NKZ4DTDA8FEFDGWA7Q8XX/job/01HW8NM2QR5AYB53PYP32J2VAA)).


### Common Gotchas

If you're experiencing job failures, here are some things to check:

- Make sure your local changes are committed,  pushed, and up to date with the remote
- Make sure you have `--beaker-image seungjuh/oe-safety-support-olmo17` and `--venv base` in your `gantry run` command
- Check your GitHub personal access token is authorized to access the allenai organization
- Make sure the openai_api_key and hf_token secrets exist in your Beaker workspace

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/get_started/installation.md


# Installation

Our setup mostly follows our [Dockerfile](./Dockerfile), which uses Python 3.10. *Note that Open Instruct is a research codebase and does not guarantee backward compatibility.* We offer two installation strategies:

* **Local installation**: This is the recommended way to install Open Instruct. You can install the dependencies by running the following commands:
```bash
pip install --upgrade pip "setuptools<70.0.0" wheel
# TODO, unpin setuptools when this issue in flash attention is resolved
pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
pip install packaging
pip install flash-attn==2.7.2.post1 --no-build-isolation
pip install -r requirements.txt
pip install -e .
python -m nltk.downloader punkt
```

* **Local installation with uv (preview)**: We are experimenting with using [uv](https://docs.astral.sh/uv/). You can install via
```bash
uv sync
uv sync --extra compile # to install flash attention
```


* **Docker installation**: You can also use the Dockerfile to build a Docker image. You can build the image with the following command:

```bash
docker build . -t open_instruct_dev
# if you are interally at AI2, you can create an image like this:
beaker_user=$(beaker account whoami --format json | jq -r '.[0].name')
beaker image delete $beaker_user/open_instruct_dev
beaker image create open_instruct_dev -n open_instruct_dev -w ai2/$beaker_user
```

Optionally you can build the base image with the following command:

```bash
docker build --build-arg CUDA=12.1.0 --build-arg TARGET=cudnn8-devel --build-arg DIST=ubuntu20.04 -f  Dockerfile.base . -t cuda-no-conda:12.1-cudnn8-dev-ubuntu20.04
```

* **Docker with uv**: You can also use the Dockerfile to build a Docker image with uv. You can build the image with the following command:

```bash
docker build -f Dockerfile.uv --build-arg UV_CACHE_DIR=$UV_CACHE_DIR -t open_instruct_dev_uv .
# if you are interally at AI2, you can create an image like this:
beaker_user=$(beaker account whoami --format json | jq -r '.[0].name')
beaker image delete $beaker_user/open_instruct_dev_uv
beaker image create open_instruct_dev_uv -n open_instruct_dev_uv -w ai2/$beaker_user
```

If you are internally at AI2, you may launch experiments using our always-up-to-date auto-built image `nathanl/open_instruct_auto`.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/index.md

# Welcome to Open Instruct

This repo serves as an open effort on instruction-tuning and post-training popular pretrained language models on publicly available datasets. We release this repo and will keep updating it with:

1. Code for finetuning language models with latest techniques and instruction datasets in a unified format.
2. Code for DPO, preference finetuning and reinforcement learning with verifiable rewards (RLVR).
3. Checkpoints or other useful artifacts that we build in our exploration.


We also support some evaluations natively in the codebase, but these are now unmaintained and instead we suggest using [OLMES](https://github.com/allenai/olmes), which we used for TÜLU 3. Below are some of our papers:

* [TÜLU 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124)
    * Latest research on open post-training techniques and methodologies
    * Comprehensive details on our most recent model training approaches

* [How Far Can Camels Go? Exploring the State of Instruction Tuning on Open Resources](https://arxiv.org/abs/2306.04751)
    * Our first paper introducing the project's foundation and vision
    * Presents initial findings and exploration of instruction tuning with open resources

* [Camels in a Changing Climate: Enhancing LM Adaptation with Tulu 2](https://arxiv.org/abs/2311.10702)
    * Second paper focusing on Llama-2 model adaptations
    * Details our work with direct preference optimization (DPO) techniques

* [Unpacking DPO and PPO: Disentangling Best Practices for Learning from Preference Feedback](https://arxiv.org/abs/2406.09279)
    * Most recent research comparing reinforcement learning approaches
    * Analyzes best practices for both DPO and PPO methodologies

<p align="center" width="100%">
      <img src="assets/images/tulu_logo.png" alt="Tülu (a hybrid camel) represents a suite of LLaMa models that we built by fully-finetuning them on a strong mix of datasets." style="width: 20%; min-width: 200px; display: block; margin: auto;">
</p>

Try some of the models we train with Open Instruct. There is a [free demo](https://playground.allenai.org/) or download them from HuggingFace:

| **Stage**           | **Llama 3.1 8B**                                                                                          | **Llama 3.1 70B**                                                                                         | **OLMo-2 7B**                                                                                          | **OLMo-2 13B**                                                                                         |
|----------------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| **Base Model**       | [meta-llama/Llama-3.1-8B](https://huggingface.co/meta-llama/Llama-3.1-8B)                                | [meta-llama/Llama-3.1-70B](https://huggingface.co/meta-llama/Llama-3.1-70B)                              | [allenai/OLMo2-7B-1124](https://huggingface.co/allenai/OLMo2-7B-1124)                                | [allenai/OLMo-2-13B-1124](https://huggingface.co/allenai/OLMo-2-13B-1124)                             |
| **SFT**              | [allenai/Llama-3.1-Tulu-3-8B-SFT](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-SFT)                | [allenai/Llama-3.1-Tulu-3-70B-SFT](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-SFT)              | [allenai/OLMo-2-1124-7B-SFT](https://huggingface.co/allenai/OLMo-2-1124-7B-SFT)                | [allenai/OLMo-2-1124-13B-SFT](https://huggingface.co/allenai/OLMo-2-1124-13B-SFT)              |
| **DPO**              | [allenai/Llama-3.1-Tulu-3-8B-DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-DPO)                | [allenai/Llama-3.1-Tulu-3-70B-DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-DPO)              | [allenai/OLMo-2-1124-7B-DPO](https://huggingface.co/allenai/OLMo-2-1124-7B-DPO)                | [allenai/OLMo-2-1124-13B-DPO](https://huggingface.co/allenai/OLMo-2-1124-13B-DPO)              |
| **Final Models (RLVR)** | [allenai/Llama-3.1-Tulu-3-8B](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B)                        | [allenai/Llama-3.1-Tulu-3-70B](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B)                      | [allenai/OLMo-2-1124-7B-Instruct](https://huggingface.co/allenai/OLMo-2-1124-7B-Instruct)                        | [allenai/OLMo-2-1124-13B-Instruct](https://huggingface.co/allenai/OLMo-2-1124-13B-Instruct)                      |
| **Final Models (RLVR)** | (🔥 New, trained with GRPO) [allenai/Llama-3.1-Tulu-3.1-8B](https://huggingface.co/allenai/Llama-3.1-Tulu-3.1-8B)                        |          |                       |                      |
| **Reward Model (RM)**| [allenai/Llama-3.1-Tulu-3-8B-RM](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-RM)                                                     | (Same as 8B)                                                     | [allenai/OLMo-2-1124-7B-RM](https://huggingface.co/allenai/OLMo-2-1124-7B-RM)                                                     | (Same as 7B)                                                     |

## News

- [2025-11-20] We released [Olmo 3](https://allenai.org/blog/olmo3)!
- [2025-02-12] We released the [`allenai/Llama-3.1-Tulu-3.1-8B` model](https://huggingface.co/allenai/Llama-3.1-Tulu-3.1-8B), which is trained with our GRPO recipe and outperforms the old [`allenai/Llama-3.1-Tulu-3-8B` model](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B) in almost all of our evals.
- [2024-11-22] We released [TÜLU 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124) and updated our entire stack of open post-training recipes with both Llama 3.1 and OLMo 2.
- [2024-07-01] We released [Unpacking DPO and PPO: Disentangling Best Practices for Learning from Preference Feedback](https://arxiv.org/abs/2406.09279) and have majorly updated our codebase to support new models and package versions.
- [2023-11-27] We released [Camels in a Changing Climate: Enhancing LM Adaptation with Tulu 2](https://arxiv.org/abs/2311.10702). Check out our models [here](https://huggingface.co/collections/allenai/tulu-v2-suite-6551b56e743e6349aab45101). We have added a DPO finetuning script for replicating our results.
- [2023-09-26] We switched to use the official [alpaca-eval](https://github.com/tatsu-lab/alpaca_eval) library to run AlpacaFarm evaluation but use regenerated longer reference outputs. This will change our numbers reported in the paper. We will update the paper soon.
- [2023-09-25] Supported using [vLLM](https://github.com/vllm-project/vllm/) for our evaluations, which speeds up the evaluation by 10x.
- [2023-09-17] Supported [LoRA](https://arxiv.org/abs/2106.09685) and [QLoRA](https://arxiv.org/abs/2305.14314) finetuning. See [here](#parameter-efficient-finetuning) for more details.
- [2023-08-18] Added support for [ToxiGen](https://github.com/microsoft/TOXIGEN)/[TruthfulQA](https://github.com/sylinrl/TruthfulQA) evaluation. Check our `scripts/eval/` for examples of running them.
- [2023-08-08] Supported several new instruction dataset, including [LIMA](https://huggingface.co/datasets/GAIR/lima) / [WizardLM](https://github.com/nlpxucan/WizardLM) / [Open-Orca](https://huggingface.co/datasets/Open-Orca/OpenOrca). See the [preparation script](./scripts/data/prepare_train_data.sh) for details. Performance hasn't been evaluated yet.
- [2023-08-06] Supported LLaMa 2 finetuning and FlashAttention-2 by bumping the version of transformers and many other dependencies.
- [2023-06-29] Added [licensing info](#licensing) for our released models.
- [2023-06-09] Released Tülu (a suite of LLaMa models fully-finetuned on a strong mix of datasets) and many other checkpoints on HuggingFace [[Links]](#released-checkpoints).
- [2023-06-09] Initial release of the codebase containing the training and evaluation code for our [arxiv paper](https://arxiv.org/abs/2306.04751).



## Citation

If you used this repository or our models, please cite our work:

Tulu 1:
```bibtex
@misc{wang2023far,
   title={How Far Can Camels Go? Exploring the State of Instruction Tuning on Open Resources},
   author={Yizhong Wang and Hamish Ivison and Pradeep Dasigi and Jack Hessel and Tushar Khot and Khyathi Raghavi Chandu and David Wadden and Kelsey MacMillan and Noah A. Smith and Iz Beltagy and Hannaneh Hajishirzi},
   year={2023},
   eprint={2306.04751},
   archivePrefix={arXiv},
   primaryClass={cs.CL}
}
```

Tulu 2:
```bibtex
@misc{ivison2023camels,
      title={Camels in a Changing Climate: Enhancing LM Adaptation with Tulu 2},
      author={Hamish Ivison and Yizhong Wang and Valentina Pyatkin and Nathan Lambert and Matthew Peters and Pradeep Dasigi and Joel Jang and David Wadden and Noah A. Smith and Iz Beltagy and Hannaneh Hajishirzi},
      year={2023},
      eprint={2311.10702},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

Tulu 2.5:
```bibtex
@misc{ivison2024unpacking,
      title={Unpacking DPO and PPO: Disentangling Best Practices for Learning from Preference Feedback},
      author={Hamish Ivison and Yizhong Wang and Jiacheng Liu and Zeqiu Wu and Valentina Pyatkin and Nathan Lambert and Noah A. Smith and Yejin Choi and Hannaneh Hajishirzi},
      year={2024},
      eprint={2406.09279},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
}
```

Tulu 3:
```bibtex
@article{lambert2024tulu3,
  title = {Tülu 3: Pushing Frontiers in Open Language Model Post-Training},
  author = {
    Nathan Lambert and Jacob Morrison and Valentina Pyatkin and Shengyi Huang and Hamish Ivison and Faeze Brahman and Lester James V. Miranda and Alisa Liu and Nouha Dziri and Shane Lyu and Yuling Gu and Saumya Malik and Victoria Graf and Jena D. Hwang and Jiangjiang Yang and Ronan Le Bras and Oyvind Tafjord and Chris Wilhelm and Luca Soldaini and Noah A. Smith and Yizhong Wang and Pradeep Dasigi and Hannaneh Hajishirzi
  },
  year = {2024},
  email = {tulu@allenai.org}
}
```

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/olmo2.md

# OLMo 2 Commands

Here we'll add commands and references to the training runs of OLMo 2.
We'll prioritize the smaller models where more people are hoping to study and reproduce them.

Core to training OLMo models (version 1 and 2) at least are to include the following flags: `--add_bos` and `--use_slow_tokenizer False` because of the tokenizer used.

For more details on how to convert these to standard launch commands (without ai2 `mason.py`) see the `tulu3.md` docs.

## Insturction Finetuning

### 1B

We ran training for the 1B model in SFT on 1 node of 8 NVIDIA H100 GPUs.

The command used internally is:
```
python mason.py \
    --cluster ai2/augusta \
    --workspace ai2/olmo-instruct \
    --priority high \
    --image nathanl/open_instruct_auto --pure_docker_mode \
    --preemptible \
    --num_nodes 1 \
    --budget ai2/oe-adapt \
    --gpus 8 -- accelerate launch \
    --mixed_precision bf16 \
    --num_processes 8 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage3_no_offloading_accelerate.conf \
    --deepspeed_multinode_launcher standard \
    open_instruct/finetune.py \
    --exp_name olmo2_1b_sft \
    --model_name_or_path allenai/OLMo-2-0425-1B \
    --model_revision main \
    --tokenizer_name allenai/OLMo-2-1124-7B \
    --tokenizer_revision main \
    --use_slow_tokenizer False \
    --add_bos \
    --dataset_mixer_list allenai/tulu-3-sft-olmo-2-mixture-0225 1.0 \
    --use_flash_attn \
    --max_seq_length 4096 \
    --per_device_train_batch_size 2 \
    --gradient_accumulation_steps 8 \
    --learning_rate 3e-5 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.03 \
    --weight_decay 0.0 \
    --num_train_epochs 2 \
    --report_to wandb \
    --with_tracking \
    --logging_steps 1 \
    --seed 1
```
Which reduces to roughly:
```
accelerate launch \
    --mixed_precision bf16 \
    --num_processes 8 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage3_no_offloading_accelerate.conf \
    --deepspeed_multinode_launcher standard \
    open_instruct/finetune.py \
    --exp_name olmo2_1b_v2_sft_lr3e-5_seed1  \
    --model_name_or_path allenai/OLMo-2-0425-1B \
    --model_revision main \
    --tokenizer_name allenai/OLMo-2-1124-7B \
    --tokenizer_revision main \
    --use_slow_tokenizer False \
    --add_bos \
    --dataset_mixer_list allenai/tulu-3-sft-olmo-2-mixture-0225 1.0 \
    --use_flash_attn \
    --max_seq_length 4096 \
    --per_device_train_batch_size 2 \
    --gradient_accumulation_steps 8 \
    --learning_rate 3e-5 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.03 \
    --weight_decay 0.0 \
    --num_train_epochs 2 \
    --report_to wandb \
    --with_tracking \
    --logging_steps 1 \
    --seed 1
```
For those internal to Ai2, see the [wandb logs](https://wandb.ai/ai2-llm/open_instruct_internal/runs/532v35jn/overview) or the [beaker job](https://beaker.allen.ai/orgs/ai2/workspaces/olmo-instruct/work/01JS4Q5QYDVAJE6XKKR4FGVQZ5?taskId=01JS4Q5QYJFHBKH3X47MPNB7P4&jobId=01JS4Q5R38CRQV0WK4J6494Q4Q).

## Preference Tuning (DPO)

### 1B

We ran training for the 1B model in DPO on 1 node of 8 NVIDIA H100 GPUs.
The command reduces to:
```
accelerate launch \
    --mixed_precision bf16 \
    --num_processes 8 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage2_accelerate.conf \
    --deepspeed_multinode_launcher standard \
    open_instruct/dpo_tune_cache.py \
    --exp_name 0424_1B_dpo_onpol_lr_2.5e-6_seed_111 \
    --learning_rate 2.5e-6 \
    --seed 111 \
    --model_name_or_path allenai/OLMo-2-0425-1B-SFT \
    --model_revision main \
    --use_flash_attn \
    --tokenizer_name_or_path allenai/OLMo-2-1124-13B \
    --tokenizer_revision main \
    --max_seq_length 2048 \
    --per_device_train_batch_size 8 \
    --gradient_accumulation_steps 2 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.1 \
    --weight_decay 0.0 \
    --num_train_epochs 1 \
    --output_dir /output \
    --with_tracking \
    --report_to wandb \
    --logging_steps 1 \
    --gradient_checkpointing \
    --dataset_mixer_list allenai/olmo-2-0425-1b-preference-mix \
    --use_slow_tokenizer False \
    --add_bos \
    --use_lora False \
    --dpo_loss_type dpo_norm \
    --dpo_beta 5
```

For those internal to Ai2, see the [wandb logs](https://wandb.ai/ai2-llm/open_instruct_internal/runs/bcu4arvs/overview) or the [beaker job](https://beaker.allen.ai/orgs/ai2/workspaces/olmo-instruct/work/01JSMRC1TR1Q4MV7NY8WFSR4SA?).


Example with DeepSpeed Stage 2:
```
python mason.py \
    --cluster ai2/augusta \
    --workspace ai2/olmo-instruct \
    --priority urgent \
    --image nathanl/open_instruct_auto --pure_docker_mode \
    --preemptible \
    --num_nodes 1 \
    --budget ai2/oe-adapt \
    --gpus 8 -- accelerate launch \
    --mixed_precision bf16 \
    --num_processes 8 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage2_accelerate.conf \
    --deepspeed_multinode_launcher standard \
    open_instruct/dpo_tune_cache.py \
    --exp_name "0424_1B_dpo_onpol_lr_2.5e-6_seed_111" \
    --learning_rate 2.5e-6 \
    --seed 111 \
    --model_name_or_path allenai/open_instruct_dev \
    --model_revision "olmo2_1b_v2_sft_lr3e-5_seed1__1__1744989064" \
    --use_flash_attn \
    --tokenizer_name_or_path allenai/OLMo-2-1124-13B \
    --tokenizer_revision main \
    --max_seq_length 2048 \
    --per_device_train_batch_size 8 \
    --gradient_accumulation_steps 2 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.1 \
    --weight_decay 0.0 \
    --num_train_epochs 1 \
    --output_dir /output \
    --with_tracking \
    --report_to wandb \
    --logging_steps 1 \
    --gradient_checkpointing \
    --dataset_mixer_list \
        allenai/olmo-2-1b-pref-mix-v0 1.0 \
    --use_slow_tokenizer False \
    --add_bos \
    --use_lora False \
    --dpo_loss_type dpo_norm \
    --dpo_beta 5
```

Example run with DeepSpeed Stage 3 (slower than stage 2):
```
for lr in 2e-6; do
python mason.py \
    --cluster ai2/jupiter \
    --workspace ai2/olmo-instruct \
    --priority high \
    --image nathanl/open_instruct_auto --pure_docker_mode \
    --preemptible \
    --num_nodes 1 \
    --budget ai2/oe-adapt \
    --gpus 8 -- accelerate launch \
    --mixed_precision bf16 \
    --num_processes 8 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage3_no_offloading_accelerate.conf \
    --deepspeed_multinode_launcher standard \
    open_instruct/dpo_tune_cache.py \
    --exp_name "0421_1B_dpo_lr_${lr}" \
    --learning_rate $lr \
    --model_name_or_path allenai/open_instruct_dev \
    --model_revision "olmo2_1b_v2_sft_lr3e-5_seed1__1__1744989064" \
    --use_flash_attn \
    --tokenizer_name_or_path allenai/OLMo-2-1124-13B \
    --tokenizer_revision main \
    --max_seq_length 2048 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.1 \
    --weight_decay 0.0 \
    --num_train_epochs 1 \
    --output_dir /output \
    --with_tracking \
    --report_to wandb \
    --logging_steps 1 \
    --gradient_checkpointing \
    --dataset_mixer_list \
        allenai/olmo-2-32b-pref-mix-v0-filter-datecutoff 1.0 \
    --use_slow_tokenizer False \
    --add_bos \
    --use_lora False \
    --dpo_loss_type dpo_norm \
    --dpo_beta 5 \
    --add_bos \
    --use_slow_tokenizer False
done
```

## RLVR

### 1B

The 1B OLMo 2 model has two RL stages run in sequence. The first is on MATH, GSM8K, and IF constraints:
```
python open_instruct/grpo_vllm_thread_ray_gtrl.py \
    --exp_name 0423_grpo_seed_1_lr_7e-7 \
    --beta 0.01 \
    --local_mini_batch_size 32 \
    --number_samples_per_prompt 16 \
    --local_rollout_batch_size 4 \
    --kl_estimator kl3 \
    --learning_rate 5e-7 \
    --dataset_mixer_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 1.0 \
    --dataset_mixer_list_splits train \
    --dataset_mixer_eval_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 16 \
    --dataset_mixer_eval_list_splits train \
    --max_token_length 2048 \
    --max_prompt_token_length 2048 \
    --response_length 2048 \
    --model_name_or_path allenai/OLMo-2-0425-1B-DPO \
    --model_revision main \
    --tokenizer_name allenai/OLMo-2-1124-7B-DPO \
    --tokenizer_revision main \
    --use_slow_tokenizer False \
    --add_bos \
    --non_stop_penalty \
    --stop_token eos \
    --temperature 1.0 \
    --ground_truths_key ground_truth \
    --chat_template_name tulu \
    --sft_messages_key messages \
    --total_episodes 2000000 \
    --penalty_reward_value 0.0 \
    --deepspeed_stage 2 \
    --per_device_train_batch_size 1 \
    --local_rollout_forward_batch_size 2 \
    --actor_num_gpus_per_node 4 8 \
    --num_epochs 1 \
    --vllm_tensor_parallel_size 4 \
    --lr_scheduler_type constant \
    --apply_verifiable_reward true \
    --seed 1 \
    --num_evals 100 \
    --save_freq 200 \
    --reward_model_multiplier 0.0 \
    --no_try_launch_beaker_eval_jobs \
    --try_launch_beaker_eval_jobs_on_weka \
    --gradient_checkpointing \
    --with_tracking \
    --tokenizer_name_or_path allenai/OLMo-2-1124-7B-DPO
```
For those internal to Ai2, see the [wandb logs](https://wandb.ai/ai2-llm/open_instruct_internal/runs/80rvltbs/overview) or the [beaker job](https://beaker.allen.ai/orgs/ai2/workspaces/olmo-instruct/work/01JSPEYF1PGPNYGQ4NBEZPJA4W?taskId=01JSPEYF1S9EJHBG1ZS6ZXMPRA&jobId=01JSPEYF6JFZHCZRBCZSZSEM8T).

Next, on MATH only:
```
python open_instruct/grpo_vllm_thread_ray_gtrl.py \
--exp_name 0427_grpo_seed_1_lr_9e-7 \
--beta 0.01 \
--local_mini_batch_size 32 \
--number_samples_per_prompt 16 \
--local_rollout_batch_size 4 \
--kl_estimator kl3 \
--learning_rate 5e-7 \
--dataset_mixer_list allenai/RLVR-MATH 1.0 \
--dataset_mixer_list_splits train \
--dataset_mixer_eval_list allenai/RLVR-MATH 16 \
--dataset_mixer_eval_list_splits train \
--max_token_length 2048 \
--max_prompt_token_length 2048 \
--response_length 2048 \
--model_name_or_path allenai/OLMo-2-0425-1B-RLVR1 \
--model_revision main \
--use_slow_tokenizer False \
--add_bos \
--non_stop_penalty \
--stop_token eos \
--temperature 1.0 \
--ground_truths_key ground_truth \
--chat_template_name tulu \
--sft_messages_key messages \
--total_episodes 2000000 \
--penalty_reward_value 0.0 \
--deepspeed_stage 2 \
--per_device_train_batch_size 1 \
--local_rollout_forward_batch_size 2 \
--actor_num_gpus_per_node 4 8 \
--num_epochs 1 \
--vllm_tensor_parallel_size 4 \
--lr_scheduler_type constant \
--apply_verifiable_reward true \
--seed 1 \
--num_evals 100 \
--save_freq 200 \
--reward_model_multiplier 0.0 \
--no_try_launch_beaker_eval_jobs \
--try_launch_beaker_eval_jobs_on_weka \
--gradient_checkpointing \
--with_tracking \
--tokenizer_name_or_path allenai/OLMo-2-1124-7B-DPO \
--tokenizer_revision main
```
For those internal to Ai2, see the [wandb logs](https://wandb.ai/ai2-llm/open_instruct_internal/runs/25yfin0f?nw=nwusernatolambert) or the [beaker job](https://beaker.allen.ai/orgs/ai2/workspaces/olmo-instruct/work/01JSWFCG62FC4NEDEW8YZDECXV?taskId=01JSWFCG64DSXNJDV7N23A92HG&jobId=01JSWFCGBFAQ288RSMAQF0TYS7).

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/safety-eval/safety.md

# Safety Evaluations

We are using the Ai2 Safety Evaluation suite for safety evals. This contains a bunch of sub-evals, and you can learn more by looking at [the eval-safety fork](https://github.com/nouhadziri/safety-eval-fork).

## Running at Ai2

This should be the most relevant thing for internal Ai2 users of open-instruct. To run evals, use the task suite `SAFETY_EVAL` or `SAFETY_EVAL_REASONING` when calling `submit_eval_jobs.py`. This will create a job that uploads and runs the safety evaluations (and uploads to the leaderboard if the appropriate flag is set).

An example command on a reasoning model would be:
```bash
python scripts/submit_eval_jobs.py \
    --model_name <model name> \
      --location <beaker id> \
      --is_tuned --workspace tulu-3-results \
      --preemptible \
      --use_hf_tokenizer_template \
      --beaker_image nathanl/open_instruct_auto \
      --upload_to_hf allenai/tulu-3-evals \
      --run_oe_eval_experiments \
      --oe_eval_task_suite "SAFETY_EVAL_REASONING"
```

An example command on a non-reasoning model would be:
```bash
python scripts/submit_eval_jobs.py \
    --model_name <model name> \
      --location <beaker id> \
      --is_tuned --workspace tulu-3-results \
      --preemptible \
      --use_hf_tokenizer_template \
      --beaker_image nathanl/open_instruct_auto \
      --upload_to_hf allenai/tulu-3-evals \
      --run_oe_eval_experiments \
      --oe_eval_task_suite "SAFETY_EVAL"
```

## Running on an interactive session

Clone [the fork](https://github.com/nouhadziri/safety-eval-fork) and run from that location.

### Safety benchmarks

For all benchmarks requiring safety evaluation unless noted otherwise, as a default, we use the [WildGuard](https://github.com/allenai/wildguard) classifier to evaluate the safety of model outputs.

- [WildGuardTest](https://arxiv.org/abs/2406.18495)
- [Harmbench](https://arxiv.org/abs/2402.04249)
- [ToxiGen](https://arxiv.org/abs/2203.09509)
- [XSTest](https://arxiv.org/abs/2308.01263)
- [JailbreakTrigger (in TrustLLM)](https://arxiv.org/abs/2401.05561)
- [Do-anything-now](https://arxiv.org/abs/2308.03825)
- [WildJailbreak](https://arxiv.org/abs/2406.18510) (both harmful and benign contrast sets)

```commandline
PYTHONPATH=safety-eval python evaluation/run_all_generation_benchmarks.py    \
 --model_name_or_path allenai/tulu-2-dpo-7b     --model_input_template_path_or_name tulu2    \
  --report_output_path ./generation_results/metrics.json     --save_individual_results_path ./generation_results/all.json \
  --hf_upload_name {HF upload name} --upload_to_hf {HF repo ID} --min_gpus_per_task {num. GPUs available}
```

**Changing classifiers for safety benchmarks**:

You can change the safety classifier used for evaluation by specifying the `classifier_model_name` in the yaml file.
For example, when you want to use the HarmBench's classifiers for evaluation on HarmBench, you can use `HarmbenchClassifier` as the `classifier_model_name`. Please check out the `evaluation/tasks/generation/harmbench/default.yaml` and `evaluation/tasks/classification/harmbench/harmbench_classsifier.yaml` to see the classifier's specification.




## Running with gantry

You can also run with gantry, if you want to test changes.
**Important**: Before you run any command with gantry, make sure you *commit and push*, since gantry will attempt to clone the repo with your local latest commit hash.

See the "One-Time Setup" section below before running commands. To test your setup, run the following command -- if this job succeeds, then you're ready to run evaluations with gantry.

```bash
gantry run --workspace {workspace} --budget ai2/oe-adapt --beaker-image kavelr/oe-safety --venv base --cluster ai2/jupiter --env-secret OPENAI_API_KEY=openai_api_key --env-secret HF_TOKEN=hf_token -- python -c 'print("Hello world")'
```

You can freely add any additional arguments to give to Beaker, such as a `--priority` tag which can be set to preemptible, normal, high, or urgent. AI2 policies may restrict the priorities that are available to users on certain clusters.

In the examples below, text within {} tags should be replaced with your own values.

As a convenience, you can use the `evaluation/gantry_run.sh` script which includes some necessary arguments. You can use it the same way as `gantry run`, but excluding these boilerplate arguments (take a look at the script to see what it includes). Example usage:

```bash
PYTHONPATH=safety-eval ./evaluation/gantry_run.sh --workspace {workspace} --cluster {cluster} --gpus {n_gpus} \
    --priority {priority} -- python evaluation/run_all_generation_benchmarks.py \
    --model_name_or_path allenai/tulu-2-dpo-7b \
    --model_input_template_path_or_name tulu2 \
    --report_output_path /results/metrics.json
```

### Extra Beaker Commands
Here is an example using the full `gantry run` command. Use the beaker image `seungjuh/oe-safety-support-olmo17`

**Important**: Please include all the beaker arguments exactly as in the examples unless intentionally modifying some configuration. Many of them are necessary to avoid job failures, such as `--beaker-image`, `--venv`, and `--env-secret`. Note that `openai_api_key` and `hf_token` are Beaker workspace secret names, so should *not* be replaced with actual values (see One-Time Setup).

Note that the `--` divides the gantry command from the evaluation command - you can edit the second part to run whatever eval suite you want from the `eval.py` script. Any additional Beaker arguments such as a dataset mount to use a model from a Beaker dataset or adding a priority tag can be added before the `--`.

You can also run all generator evaluations parallelized across the GPUs allocated to your batch job, like so:
```bash
gantry run --workspace {your_workspace} --cluster {cluster} --gpus {n_gpus} \
    --name {beaker_experiment_name} --task-name {beaker_task_name} --beaker-image seungjuh/oe-safety-support-olmo17 --venv base \
    --env-secret OPENAI_API_KEY=openai_api_key \
    --env-secret HF_TOKEN=hf_token \
    --budget {budget} -- python evaluation/run_all_generation_benchmarks.py \
    --model_name_or_path allenai/tulu-2-dpo-7b \
    --model_input_template_path_or_name tulu2 \
    --report_output_path /results/metrics.json --save_individual_results_path /results/all.json
```

Because the `--report_output_path` argument is set to `/results/metrics.json`, the output will automatically get logged to Beaker metrics in the experiment page ([example](https://beaker.org/ex/01HW8NKZ458MA1PSB1X4YQTH94/tasks/01HW8NKZ4DTDA8FEFDGWA7Q8XX/job/01HW8NM2QR5AYB53PYP32J2VAA)).

### Gantry One-Time Setup

Before you can use gantry, there are a couple of things to set up. For the workspace you use, ensure it is owned by the `ai2` organization, or gantry won't be able to create the experiments.

1. Run `pip install beaker-gantry beaker-py`
2. Create a [GitHub personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) with "repo" scope
3. Go to https://github.com/settings/tokens and authorize your token to configure SSO access to the allenai organization
4. Run `gantry config set-gh-token` and paste the token created above when prompted
5. Create a [HuggingFace access token](https://huggingface.co/settings/tokens) with "read" scope (this is used to authenticate for using restricted models like Llama series)
6. Run `beaker secret write --workspace {your_workspace} hf_token {your_token}`
7. Obtain an OpenAI API key and run `beaker secret write --workspace {your_workspace} openai_api_key {your_api_key}

Doing these steps once will set up your workspace to use gantry.


### Common Gotchas

If you're experiencing job failures, here are some things to check:

- Make sure your local changes are committed,  pushed, and up to date with the remote
- Make sure you have `--beaker-image seungjuh/oe-safety-support-olmo17` and `--venv base` in your `gantry run` command
- Check your GitHub personal access token is authorized to access the allenai organization
- Make sure the openai_api_key and hf_token secrets exist in your Beaker workspace

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/safety.md

# Safety Evaluations

We are using the Ai2 Safety Evaluation suite for safety evals. This contains a bunch of sub-evals, and you can learn more by looking at [the eval-safety fork](https://github.com/nouhadziri/safety-eval-fork).

## Running at Ai2

This should be the most relevant thing for internal Ai2 users of open-instruct. To run evals, use the task suite `SAFETY_EVAL` or `SAFETY_EVAL_REASONING` when calling `submit_eval_jobs.py`. This will create a job that uploads and runs the safety evaluations (and uploads to the leaderboard if the appropriate flag is set).

An example command on a reasoning model would be:
```bash
python scripts/submit_eval_jobs.py \
    --model_name <model name> \
      --location <beaker id> \
      --is_tuned --workspace tulu-3-results \
      --preemptible \
      --use_hf_tokenizer_template \
      --beaker_image nathanl/open_instruct_auto \
      --upload_to_hf allenai/tulu-3-evals \
      --run_oe_eval_experiments \
      --oe_eval_task_suite "SAFETY_EVAL_REASONING"
```

An example command on a non-reasoning model would be:
```bash
python scripts/submit_eval_jobs.py \
    --model_name <model name> \
      --location <beaker id> \
      --is_tuned --workspace tulu-3-results \
      --preemptible \
      --use_hf_tokenizer_template \
      --beaker_image nathanl/open_instruct_auto \
      --upload_to_hf allenai/tulu-3-evals \
      --run_oe_eval_experiments \
      --oe_eval_task_suite "SAFETY_EVAL"
```


## Running on an interactive session

Clone [the fork](https://github.com/nouhadziri/safety-eval-fork) and run from that location.

### Safety benchmarks

For all benchmarks requiring safety evaluation unless noted otherwise, as a default, we use the [WildGuard](https://github.com/allenai/wildguard) classifier to evaluate the safety of model outputs.

- [WildGuardTest](https://arxiv.org/abs/2406.18495)
- [Harmbench](https://arxiv.org/abs/2402.04249)
- [ToxiGen](https://arxiv.org/abs/2203.09509)
- [XSTest](https://arxiv.org/abs/2308.01263)
- [JailbreakTrigger (in TrustLLM)](https://arxiv.org/abs/2401.05561)
- [Do-anything-now](https://arxiv.org/abs/2308.03825)
- [WildJailbreak](https://arxiv.org/abs/2406.18510) (both harmful and benign contrast sets)

```commandline
PYTHONPATH=safety-eval python evaluation/run_all_generation_benchmarks.py    \
 --model_name_or_path allenai/tulu-2-dpo-7b     --model_input_template_path_or_name tulu2    \
  --report_output_path ./generation_results/metrics.json     --save_individual_results_path ./generation_results/all.json \
  --hf_upload_name {HF upload name} --upload_to_hf {HF repo ID} --min_gpus_per_task {num. GPUs available}
```

**Changing classifiers for safety benchmarks**:

You can change the safety classifier used for evaluation by specifying the `classifier_model_name` in the yaml file.
For example, when you want to use the HarmBench's classifiers for evaluation on HarmBench, you can use `HarmbenchClassifier` as the `classifier_model_name`. Please check out the `evaluation/tasks/generation/harmbench/default.yaml` and `evaluation/tasks/classification/harmbench/harmbench_classsifier.yaml` to see the classifier's specification.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/tulu1_tulu2.md

## Tulu 1 and Tulu 2 Documentation


Note Tulu 1/2 results used an ealier version of Open Instruct with a pinned version of Transformers. If you are looking to replicate these results, refer to [this commit or older](https://github.com/allenai/open-instruct/commit/f3424591638ed63b31d5869abd867932c359c1ed).


## Released Checkpoints

Our checkpoints can be found:

- [Here](https://huggingface.co/collections/hamishivi/tulu-v1-suite-655138c3743e6349aaa07d7d) for all Tulu v1 models.
- [Here](https://huggingface.co/collections/allenai/tulu-v2-suite-6551b56e743e6349aab45101) for all Tulu v2 models.
- [OLMo 7B SFT](https://huggingface.co/allenai/OLMo-7B-SFT) and [Instruct](https://huggingface.co/allenai/OLMo-7B-Instruct), along with a [2048 sequence length version of Tulu 2](https://huggingface.co/datasets/allenai/tulu-v2-sft-mixture-olmo-2048).


### Weight diff script

Our Tulu V1 models were released as weight diffs (due to LLaMa 1 license). We use a slightly modified form of the [Alpaca weight diff script](https://github.com/tatsu-lab/stanford_alpaca/blob/main/weight_diff.py), which runs the same.

To merge a model:
1. Download the relevant LLaMa model and convert it to Hugging Face format (see above).
2. Download our repository and install the right dependencies (see above).
3. Download the model diff you want.
4. Run the command below:

```bash
python scripts/weights/weight_diff.py recover --path_raw ${hf_llama_path} --path_tuned ${output_path} --path_diff ${diff_location}
```

## Evaluation

### Benchmark-based eval

We provide the scripts for running evaluation of Huggingface/OpenAI models on a list of standard benchmarks targeting for the core capabilities of large language models. These benchmakrs include:

- [MMLU](https://github.com/hendrycks/test)
- [Grade School Math (GSM)](https://github.com/openai/grade-school-math)
- [MATH](https://github.com/hendrycks/math)
- [Big-Bench Hard (BBH)](https://github.com/suzgunmirac/BIG-Bench-Hard/tree/main)
- [TydiQA](https://github.com/google-research-datasets/tydiqa)
- [Codex HumanEval](https://github.com/openai/human-eval/tree/master)
- [HumanEval+ and MBPP+](https://github.com/evalplus/evalplus)
- [IFEval](https://github.com/google-research/google-research/tree/master/instruction_following_eval)
- [ToxiGen](https://github.com/microsoft/TOXIGEN)
- [XSTest](https://github.com/paul-rottger/exaggerated-safety/)
- [TruthfulQA](https://github.com/sylinrl/TruthfulQA)
- [AlpacaEval 1 and 2](https://github.com/tatsu-lab/alpaca_eval)

We are working on including more promising benchmarks into this list. Please stay tuned!

You can use the following script to download all the evaluation data:

```bash
./scripts/data/prepare_eval_data.sh
```

Evaluation scripts for different datasets are put under `./scripts`. For example, you can use the following command to run the MMLU evaluation script:

```bash
./scripts/eval/mmlu.sh
```


### Human evaluation

We release our human evaluation interface and collected annotations in the `./human_eval` folder. Please see the corresponding [README](./human_eval/README.md) for more details.


## Training

### Dataset preparation

We include a collection of representative instruction datasets in our exploration and are adding new ones to our list. We unify them into the same chatting format. To download and prepare these datasets, simply run the following command:

```bash
./scripts/data/prepare_train_data.sh
```

Please check these datasets for licenses and restrictions around their use!

You can also find the processed [Tulu v1](https://huggingface.co/datasets/allenai/tulu-v1-sft-mixture) and [Tulu v2](https://huggingface.co/datasets/allenai/tulu-v2-sft-mixture) SFT datasets on HuggingFace. Note that the train data preparation script will not precisely recreate the Tulu v2 mixture due to randomness in the generation and shifts in data availability - see [this PR](https://github.com/allenai/open-instruct/pull/156) for some details. If you need exactly yhe training data used, the HuggingFace mixture is exactly this - the exact same data used during model training.

### Model preparation

Generally, most huggingface-compatible causal language models should work fine with our codebase, potentially with some adjusting for different tokenizers etc. Some models may require addtional requests to download. E.g., for LLaMa 1 and 2, please consult [the Hugging Face documentation](https://huggingface.co/docs/transformers/model_doc/llama) for requesting access and converting them to a huggingface-compatible format.

### Finetuning

You can use the following command to run instruction tuning (finetuning a pretrained model to follow instructions):

```bash
./scripts/finetune_with_accelerate.sh
```

Make sure to adjust `model_name_or_path`, `tokenizer_name`, `train_file`, and `output_dir` to your models / data / setting. By default, this uses `deepspeed` with `accelerate`.

### Parameter-Efficient Finetuning

We support [LoRA](https://arxiv.org/abs/2106.09685) finetuning, wherein only a small number of parameters are updated, resulting in faster and cheaper training. For even more efficiency, we also support [QLoRA](https://arxiv.org/abs/2305.14314) finetuning, wherein the non-trained (underlying) model parameters are quantised during 4-bit training. This means you can train a 70b Llama model on a single 80GB A100! Please refer to the respective papers for more details.

Please also note you cannot currently run QLoRA with model parallelism - only data-parallel training is supported, so you cannot train a model that does not fit on one GPU. For LoRA, you can use deepspeed + zero-3 to achieve model parallelism (and FSDP is not currently supported).

Please see `./scripts/finetune_lora_with_accelerate.sh` and `./scripts/finetune_qlora_with_accelerate.sh` for example hyperparameters. We found a larger rank (e.g. 256) and higher learning rate (e.g. 2e-4) worked best. Additionally, we found that QLoRA tended to always achieve similar results to LoRA, while LoRA itself sometimes fell behind full-finetuning, especially in long, complex generation tasks. However, for most purposes, LoRA training essentially matches full-finetuning performance. We recommend merging modules learnt with QLoRA into a dequantised model (run our merge script with the `--qlora` flag).

## DPO Finetuning

For an example of how to fully finetune a model with DPO, see `scripts/dpo_train_with_accelerate.sh`. Note you will require at least 8 80GB A100s to be able to train a 7b size model, and will require more compute for anything larger. We have not tested multi-node training with this script, but it should work.

Our script also supports PEFT training with QLoRA. See `scripts/dpo_train_with_qlora.sh` for an example. We have not trained models with this, so it may require additional hyperparameter tuning to achieve reasonable results.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/docs/tulu3.md

# Tulu3 Reproduction

This document details the commands and configs to reproduce the tulu3 models.

## Finetuning


### Llama-3.1-Tulu-3-8B-SFT Reproduction

Below is (almost) the exact command which produced [Llama-3.1-Tulu-3-8B-SFT](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-SFT). We deployed the command across 8 machines, each equipped with 8 NVIDIA H100 GPUs, for a total of 64 GPUs in the our setup.

```bash
# modify the following `MACHINE_RANK`, `MAIN_PROCESS_IP`,
# `NUM_MACHINES`, `NUM_PROCESSES`, `PER_DEVICE_TRAIN_BATCH_SIZE`,
# `GRADIENT_ACCUMULATION_STEPS` according to your setup
MACHINE_RANK=0
MAIN_PROCESS_IP=localhost
NUM_MACHINES=8
NUM_PROCESSES=64
PER_DEVICE_TRAIN_BATCH_SIZE=1
GRADIENT_ACCUMULATION_STEPS=2
accelerate launch \
    --mixed_precision bf16 \
    --num_machines 8 \
    --num_processes 64 \
    --machine_rank $MACHINE_RANK \
    --main_process_ip $MAIN_PROCESS_IP \
    --main_process_port 29400 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage3_no_offloading_accelerate.conf \
    --deepspeed_multinode_launcher standard open_instruct/finetune.py \
    --model_name_or_path meta-llama/Llama-3.1-8B \
    --tokenizer_name meta-llama/Llama-3.1-8B \
    --use_slow_tokenizer \
    --use_flash_attn \
    --max_seq_length 4096 \
    --preprocessing_num_workers 128 \
    --per_device_train_batch_size $PER_DEVICE_TRAIN_BATCH_SIZE \
    --gradient_accumulation_steps $GRADIENT_ACCUMULATION_STEPS \
    --learning_rate 5e-06 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.03 \
    --weight_decay 0.0 \
    --num_train_epochs 2 \
    --output_dir output/sft_8b \
    --with_tracking \
    --report_to wandb \
    --logging_steps 1 \
    --model_revision main \
    --dataset_mixer_list allenai/tulu-3-sft-mixture 1.0 \
    --checkpointing_steps epoch \
    --dataset_mix_dir output/sft_8b \
    --exp_name tulu-3-8b-sft \
    --seed 123
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JBNTPW8TKG09B2XR832YB5S8
```

> [!NOTE]
> If you have different number of GPUs, please adjust the `NUM_MACHINES`, `NUM_PROCESSES`, `PER_DEVICE_TRAIN_BATCH_SIZE`, and `GRADIENT_ACCUMULATION_STEPS` accordingly to reproduce the same effective batch size.
> The effective batch size is calculated by multiplying:
> - Number of GPUs / processes (NUM_PROCESSES)
> - Train batch size per GPU (PER_DEVICE_TRAIN_BATCH_SIZE)
> - Gradient accumulation steps (GRADIENT_ACCUMULATION_STEPS)
> so we have
> ```
> 64 GPUs: 64 * 1 * 2 = 128 # from the example above
> 8 GPUs:   8 * 1 * 16 = 128 # if you only
> ```
> You can achieve the same effective batch size with fewer GPUs by increasing gradient accumulation steps proportionally (e.g., `NUM_PROCESSES=8, PER_DEVICE_TRAIN_BATCH_SIZE=1, and GRADIENT_ACCUMULATION_STEPS=16`)

### Llama-3.1-Tulu-3-70B-SFT Reproduction

This is (almost) the exact command which produced [allenai/Llama-3.1-Tulu-3-70B-SFT](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-SFT)


```bash
# modify the following `MACHINE_RANK`, `MAIN_PROCESS_IP`,
# `NUM_MACHINES`, `NUM_PROCESSES`, `PER_DEVICE_TRAIN_BATCH_SIZE`,
# `GRADIENT_ACCUMULATION_STEPS` according to your setup
MACHINE_RANK=0
MAIN_PROCESS_IP=localhost
NUM_MACHINES=8
NUM_PROCESSES=64
PER_DEVICE_TRAIN_BATCH_SIZE=1
GRADIENT_ACCUMULATION_STEPS=2
accelerate launch \
    --mixed_precision bf16 \
    --num_machines $NUM_MACHINES \
    --num_processes $NUM_PROCESSES \
    --machine_rank $MACHINE_RANK \
    --main_process_ip $MAIN_PROCESS_IP \
    --main_process_port 29400 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage3_no_offloading_accelerate.conf \
    --deepspeed_multinode_launcher standard open_instruct/finetune.py \
    --model_name_or_path meta-llama/Llama-3.1-70B \
    --tokenizer_name meta-llama/Llama-3.1-70B \
    --use_slow_tokenizer \
    --use_flash_attn \
    --max_seq_length 4096 \
    --preprocessing_num_workers 128 \
    --per_device_train_batch_size $PER_DEVICE_TRAIN_BATCH_SIZE \
    --gradient_accumulation_steps $GRADIENT_ACCUMULATION_STEPS \
    --learning_rate 2e-06 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.03 \
    --weight_decay 0.0 \
    --num_train_epochs 2 \
    --output_dir output/sft_70B \
    --with_tracking \
    --report_to wandb \
    --logging_steps 1 \
    --model_revision main \
    --dataset_mixer_list allenai/tulu-3-sft-mixture 1.0 \
    --dataset_mix_dir output/sft_70B \
    --checkpointing_steps 1000 \
    --keep_last_n_checkpoints 20 \
    --gradient_checkpointing \
    --exp_name tulu-3-70b-sft \
    --seed 456
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JC5J4R80M18XQTDH47JSFRJY/
```


## Preference Tuning


### Llama-3.1-Tulu-3-8B-DPO Reproduction

This is (almost) the exact command which produced [allenai/Llama-3.1-Tulu-3-8B-DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-DPO)


```bash
accelerate launch \
    --mixed_precision bf16 \
    --num_machines 1 \
    --num_processes 8 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage3_no_offloading_accelerate.conf open_instruct/dpo_tune.py \
    --model_name_or_path allenai/Llama-3.1-Tulu-3-8B-SFT \
    --use_flash_attn \
    --tokenizer_name allenai/Llama-3.1-Tulu-3-8B-SFT \
    --max_seq_length 2048 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --learning_rate 5e-07 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.1 \
    --weight_decay 0.0 \
    --num_train_epochs 1 \
    --output_dir output/dpo_8b \
    --with_tracking \
    --report_to wandb \
    --logging_steps 1 \
    --model_revision main \
    --gradient_checkpointing \
    --dataset_mixer_list allenai/llama-3.1-tulu-3-8b-preference-mixture 1.0 \
    --use_slow_tokenizer \
    --use_lora False \
    --dpo_loss_type dpo_norm \
    --dpo_beta 5 \
    --checkpointing_steps 1000 \
    --exp_name tulu-3-8b-dpo
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JCRXP0AR5312S8MD3XGCN0J7/
```



### Llama-3.1-Tulu-3-70B-DPO Reproduction

This is (almost) the exact command which produced [allenai/Llama-3.1-Tulu-3-70B-DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-DPO)


```bash
# modify the following `MACHINE_RANK`, `MAIN_PROCESS_IP`,
# `NUM_MACHINES`, `NUM_PROCESSES`, `PER_DEVICE_TRAIN_BATCH_SIZE`,
# `GRADIENT_ACCUMULATION_STEPS` according to your setup
MACHINE_RANK=0
MAIN_PROCESS_IP=localhost
NUM_MACHINES=8
NUM_PROCESSES=64
PER_DEVICE_TRAIN_BATCH_SIZE=1
GRADIENT_ACCUMULATION_STEPS=2
accelerate launch \
    --mixed_precision bf16 \
    --num_machines $NUM_MACHINES \
    --num_processes $NUM_PROCESSES \
    --machine_rank $MACHINE_RANK \
    --main_process_ip $MAIN_PROCESS_IP \
    --main_process_port 29400 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage3_offloading_accelerate.conf \
    --deepspeed_multinode_launcher standard open_instruct/dpo_tune_cache.py \
    --model_name_or_path allenai/Llama-3.1-Tulu-3-70B-SFT \
    --tokenizer_name allenai/Llama-3.1-Tulu-3-70B-SFT \
    --use_flash_attn \
    --max_seq_length 2048 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size $PER_DEVICE_TRAIN_BATCH_SIZE \
    --gradient_accumulation_steps $GRADIENT_ACCUMULATION_STEPS \
    --learning_rate 2e-07 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.1 \
    --weight_decay 0.0 \
    --num_train_epochs 1 \
    --output_dir output/dpo_70b \
    --with_tracking \
    --report_to wandb \
    --logging_steps 1 \
    --model_revision main \
    --gradient_checkpointing \
    --dataset_mixer_list allenai/llama-3.1-tulu-3-70b-preference-mixture \
    --use_slow_tokenizer \
    --use_lora False \
    --dpo_loss_type dpo_norm \
    --dpo_beta 5 \
    --checkpointing_steps epoch \
    --exp_name tulu-3-70b-dpo
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JCSAYYHQYF9QDQDCV6KJ53M9/
```

### Llama-3.1-Tulu-3-405B-DPO Reproduction

This is (almost) the exact command which produced [allenai/Llama-3.1-Tulu-3-405B-DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-405B-DPO)


```bash
# modify the following `MACHINE_RANK`, `MAIN_PROCESS_IP`,
# `NUM_MACHINES`, `NUM_PROCESSES`, `PER_DEVICE_TRAIN_BATCH_SIZE`,
# `GRADIENT_ACCUMULATION_STEPS` according to your setup
MACHINE_RANK=0
MAIN_PROCESS_IP=localhost
NUM_MACHINES=8
NUM_PROCESSES=64
PER_DEVICE_TRAIN_BATCH_SIZE=1
GRADIENT_ACCUMULATION_STEPS=2
accelerate launch --mixed_precision bf16 \
    --num_machines 32 \
    --num_processes 256 \
    --machine_rank $BEAKER_REPLICA_RANK \
    --main_process_ip $BEAKER_LEADER_REPLICA_HOSTNAME \
    --main_process_port 29400 \
    --use_deepspeed \
    --deepspeed_config_file configs/ds_configs/stage3_no_offloading_accelerate.conf \
    --deepspeed_multinode_launcher standard open_instruct/dpo_tune_cache.py \
    --model_name_or_path allenai/Llama-3.1-Tulu-3-405B-SFT \
    --tokenizer_name allenai/Llama-3.1-Tulu-3-70B-SFT \
    --use_flash_attn \
    --max_seq_length 2048 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size 1 \
    --gradient_accumulation_steps 1 \
    --learning_rate 2e-07 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.1 \
    --weight_decay 0.0 \
    --num_train_epochs 1 \
    --output_dir output_405b \
    --with_tracking \
    --report_to wandb \
    --logging_steps 1 \
    --model_revision main \
    --gradient_checkpointing \
    --dataset_mixer_list ai2-adapt-dev/405b_preference_mix 1.0 \
    --use_slow_tokenizer \
    --use_lora False \
    --dpo_loss_type dpo_norm \
    --dpo_beta 5 \
    --checkpointing_steps 1000
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JJ4QRZ31SH79AHVM6WWDVJB4/
```


## RLVR

### RLVR for IF Note:
We have since updated the RLVR verifier functions and judge for precise IF. If you want to reproduce Tulu3 results,
please use the IFEvalVerifierOld class in ground_truth_utils.py. The new IFEvalVerifier class is not compatible with
the old data format, so please use the new IF data format for the new verifier. The new verifier and the new data will
give better results.

### Llama-3.1-Tulu-3-8B-RM Reproduction

This is (almost) the exact command which produced [allenai/Llama-3.1-Tulu-3-8B-RM](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-RM)


```bash
accelerate launch \
    --config_file configs/ds_configs/deepspeed_zero3.yaml open_instruct/reward_modeling.py \
    --dataset_mixer '{"allenai/llama-3.1-tulu-3-8b-preference-mixture": 1.0}' \
    --dataset_train_splits train \
    --dataset_eval_mixer '{"allenai/ultrafeedback_binarized_cleaned": 1.0}' \
    --dataset_eval_splits test_prefs \
    --model_name_or_path allenai/Llama-3.1-Tulu-3-8B-SFT \
    --chat_template tulu \
    --learning_rate 3e-6 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 32 \
    --max_token_length 2048 \
    --max_prompt_token_length 2048 \
    --num_train_epochs 1 \
    --output_dir output/rm_8b \
    --gradient_checkpointing \
    --push_to_hub \
    --with_tracking
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JCS01RFBQGFE5F1W3W96FFVM/
```

### Llama-3.1-Tulu-3-8B Reproduction

This is (almost) the exact command which produced [allenai/Llama-3.1-Tulu-3-8B](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B)


```bash
python open_instruct/ppo_vllm_thread_ray_gtrl.py \
    --exp_name tulu-3-8b-rlvr \
    --dataset_mixer_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 1.0 \
    --dataset_mixer_list_splits train \
    --dataset_mixer_eval_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 16 \
    --dataset_mixer_eval_list_splits train \
    --max_token_length 2048 \
    --max_prompt_token_length 2048 \
    --response_length 2048 \
    --model_name_or_path allenai/Llama-3.1-Tulu-3-8B-DPO \
    --reward_model_path allenai/Llama-3.1-Tulu-3-8B-RM \
    --non_stop_penalty \
    --stop_token eos \
    --temperature 1.0 \
    --chat_template_name tulu \
    --learning_rate 3e-7 \
    --total_episodes 10000000 \
    --penalty_reward_value -10.0 \
    --deepspeed_stage 3 \
    --per_device_train_batch_size 2 \
    --local_rollout_forward_batch_size 2 \
    --local_mini_batch_size 32 \
    --local_rollout_batch_size 32 \
    --actor_num_gpus_per_node 7 \
    --vllm_tensor_parallel_size 1 \
    --beta 0.05 \
    --apply_verifiable_reward true \
    --output_dir output/rlvr_8b \
    --seed 3 \
    --num_evals 3 \
    --save_freq 100 \
    --reward_model_multiplier 0.0 \
    --gradient_checkpointing \
    --with_tracking
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JCVTA10BQDVGGQKFYWEZ6KCQ/
```



### Llama-3.1-Tulu-3-70B Reproduction

This is (almost) the exact command which produced [allenai/Llama-3.1-Tulu-3-70B](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B)

Couple of notes:
* Make sure to modify `configs/beaker_configs/ray_node_setup.sh` in our own cluster setup. The idea is to have the replicas join the main machines via `ray`.
* We had to use `--vllm_tensor_parallel_size 4` because `--vllm_tensor_parallel_size 8` errors out for some strange reason. This is a temporary workaround.
* Here the effective batch size is `sum(actor_num_gpus_per_node) * local_mini_batch_size = 40 * 16 = 640`. If you have less GPUs, you can adjust `actor_num_gpus_per_node` and `local_mini_batch_size` accordingly.

```bash
source configs/beaker_configs/ray_node_setup.sh && python open_instruct/ppo_vllm_thread_ray_gtrl.py \
    --dataset_mixer_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 1.0 \
    --dataset_mixer_list_splits train \
    --dataset_mixer_eval_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 16 \
    --dataset_mixer_eval_list_splits train \
    --max_token_length 2048 \
    --max_prompt_token_length 2048 \
    --response_length 2048 \
    --model_name_or_path allenai/Llama-3.1-Tulu-3-70B-DPO \
    --exp_name tulu-3-70b-rlvr \
    --reward_model_path allenai/Llama-3.1-Tulu-3-8B-RM \
    --beta 0.07 \
    --warmup_ratio 0.1 \
    --seed 8 \
    --output_dir output/rlvr_70b \
    --non_stop_penalty \
    --stop_token eos \
    --temperature 1.0 \
    --chat_template_name tulu \
    --learning_rate 1e-7 \
    --total_episodes 400000 \
    --penalty_reward_value -10.0 \
    --deepspeed_stage 3 \
    --per_device_train_batch_size 1 \
    --local_rollout_forward_batch_size 1 \
    --local_mini_batch_size 16 \
    --local_rollout_batch_size 16 \
    --actor_num_gpus_per_node 8 8 8 8 8 \
    --vllm_num_engines 1 \
    --vllm_tensor_parallel_size 4 \
    --apply_verifiable_reward true \
    --reward_model_multiplier 0.0 \
    --no_gather_whole_model \
    --num_evals 3 \
    --save_freq 40 \
    --gradient_checkpointing \
    --with_tracking
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JD3YEM4XGH2F2H10Y49GK441/
```

### Llama-3.1-Tulu-3-405B Reproduction

This is (almost) the exact command which produced [allenai/Llama-3.1-Tulu-3-405B](https://huggingface.co/allenai/Llama-3.1-Tulu-3-405B)

Couple of notes:
* We had to set `TORCH_NCCL_ENABLE_MONITORING=0` to turn off NCCL heartbeat monitoring and avoid timeouts. Feel free to remove this.
* Make sure to modify `configs/beaker_configs/ray_node_setup.sh` in our own cluster setup. The idea is to have the replicas join the main machines via `ray`.
* Here the effective batch size is `sum(actor_num_gpus_per_node) * local_mini_batch_size = 40 * 16 = 640`. If you have less GPUs, you can adjust `actor_num_gpus_per_node` and `local_mini_batch_size` accordingly.

```bash
TORCH_NCCL_ENABLE_MONITORING=0 python mason.py \
    --cluster ai2/jupiter --pure_docker_mode \
    --workspace ai2/tulu-3-dev \
    --priority urgent \
    --preemptible \
    --num_nodes 32 \
    --image nathanl/open_instruct_auto \
    --budget ai2/oe-adapt \
    --gpus 8 -- source configs/beaker_configs/ray_node_setup.sh \&\& TORCH_DISTRIBUTED_DEBUG=DETAIL python open_instruct/ppo_vllm_thread_ray_gtrl.py \
    --dataset_mixer_list allenai/RLVR-MATH 1.0 \
    --dataset_mixer_list_splits train \
    --dataset_mixer_eval_list allenai/RLVR-MATH 128 \
    --dataset_mixer_eval_list_splits train \
    --max_token_length 2048 \
    --max_prompt_token_length 2048 \
    --response_length 1024 \
    --model_name_or_path /weka/oe-adapt-default/hamishi/405b_dpo_v4 \
    --exp_name "405b_rlvr_math_only_8b_valu_on_v4" \
    --reward_model_path allenai/Llama-3.1-Tulu-3-8B-RM \
    --beta 0.05 \
    --output_dir "/weka/oe-adapt-default/hamishi/405b_rlvr_math_only_8b_valu_on_v4" \
    --non_stop_penalty \
    --stop_token eos \
    --temperature 1.0 \
    --chat_template tulu \
    --learning_rate 1e-7 \
    --total_episodes 400000 \
    --num_epochs 4 \
    --penalty_reward_value -10.0 \
    --deepspeed_stage 3 \
    --per_device_train_batch_size 1 \
    --local_rollout_forward_batch_size 1 \
    --local_mini_batch_size 8 \
    --local_rollout_batch_size 8 \
    --actor_num_gpus_per_node 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 8 \
    --vllm_num_engines 1 \
    --vllm_tensor_parallel_size 16 \
    --vllm_enforce_eager true \
    --apply_verifiable_reward true \
    --reward_model_multiplier 0.0 \
    --no_gather_whole_model \
    --seed 3 \
    --num_evals 3 \
    --no_try_launch_beaker_eval_jobs \
    --save_freq 25 \
    --try_launch_beaker_eval_jobs_on_weka \
    --gradient_checkpointing \
    --with_tracking
# For Ai2 internal members, this was the experiment URL: https://beaker.org/ex/01JJA31S20XAFR82YPFKSMMYZV/
```


### (NEW) Llama-3.1-Tulu-3.1-8B Reproduction

This is the exact command which produced [allenai/Llama-3.1-Tulu-3.1-8B](https://huggingface.co/allenai/Llama-3.1-Tulu-3.1-8B), which uses 2 nodes (16 GPUs)


```bash
for learning_rate in 5e-7; do
for beta in 0.01; do
for nspp in 16; do
for m in half-m ; do
for kl_estimator in kl3; do
local_rollout_batch_size=4
if [ $m == "half-m" ]; then
    local_mini_batch_size=$(($local_rollout_batch_size * $nspp / 2))
else
    local_mini_batch_size=$(($local_rollout_batch_size * $nspp))
fi
exp_name="0204_lr_scan_grpo_math_lr_${learning_rate}_${kl_estimator}_${beta}_${nspp}_${m}_${RANDOM}"
full_bsz=$(($local_rollout_batch_size * nspp * (7) * 2))
echo $exp_name:
echo --- local_mini_batch_size=$local_mini_batch_size
echo --- full_bsz=$full_bsz
echo --- num_gradient_updates=$(($local_rollout_batch_size * $nspp / $local_mini_batch_size))
python mason.py \
    --cluster ai2/jupiter \
    --workspace ai2/tulu-3-dev \
    --priority high \
    --preemptible \
    --num_nodes 2 \
    --max_retries 1 \
    --budget ai2/oe-adapt \
    --gpus 8 -- source configs/beaker_configs/ray_node_setup.sh \&\& uv run python open_instruct/grpo_vllm_thread_ray_gtrl.py \
    --exp_name $exp_name \
    --beta $beta \
    --local_mini_batch_size $local_mini_batch_size \
    --number_samples_per_prompt $nspp \
    --output_dir /weka/oe-adapt-default/costah/models/$exp_name \
    --local_rollout_batch_size $local_rollout_batch_size \
    --kl_estimator $kl_estimator \
    --learning_rate $learning_rate \
    --dataset_mixer_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 1.0 \
    --dataset_mixer_list_splits train \
    --dataset_mixer_eval_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 16 \
    --dataset_mixer_eval_list_splits train \
    --max_token_length 2048 \
    --max_prompt_token_length 2048 \
    --response_length 2048 \
    --model_name_or_path allenai/Llama-3.1-Tulu-3-8B-DPO \
    --non_stop_penalty \
    --stop_token eos \
    --temperature 1.0 \
    --chat_template_name tulu \
    --total_episodes 10000000 \
    --penalty_reward_value 0.0 \
    --deepspeed_stage 2 \
    --per_device_train_batch_size 2 \
    --local_rollout_forward_batch_size 2 \
    --actor_num_gpus_per_node 4 8 \
    --num_epochs 1 \
    --vllm_tensor_parallel_size 4 \
    --lr_scheduler_type constant \
    --apply_verifiable_reward true \
    --seed 1 \
    --num_evals 30 \
    --save_freq 40 \
    --reward_model_multiplier 0.0 \
    --no_try_launch_beaker_eval_jobs \
    --try_launch_beaker_eval_jobs_on_weka \
    --gradient_checkpointing \
    --with_tracking
done
done
done
done
done
# For Ai2 internal members, this was the experiment URL: https://beaker.allen.ai/orgs/ai2/workspaces/tulu-3-dev/work/01JKA7CSDGG3YA84X89C5HJPXR?taskId=01JKA7CSDQMVBDNAWF5T7ZXDSA&jobId=01JKH4KYJTR2Y2NYNCCQ63ZQHE
```


If you are running on a single node (8 GPUs), consider adjusting the commands as follows. Basically, the idea is to simulate the same batch size. In the two nodes setup, we used `--actor_num_gpus_per_node 4 8` (12 GPUs) for training, so we multiply it with `local_rollout_batch_size=4` to get the rollout batch size `12 * 4 = 48`. Now assume we used `--actor_num_gpus_per_node 6` (6 GPUs) for training, so we get `48 / 6 = 8`, which is the new `local_rollout_batch_size`.

```diff
 for learning_rate in 5e-7; do
 for beta in 0.01; do
 for nspp in 16; do
 for m in half-m ; do
 for kl_estimator in kl3; do
-local_rollout_batch_size=4
+local_rollout_batch_size=8
 if [ $m == "half-m" ]; then
     local_mini_batch_size=$(($local_rollout_batch_size * $nspp / 2))
 else
     local_mini_batch_size=$(($local_rollout_batch_size * $nspp))
 fi
 exp_name="0204_lr_scan_grpo_math_lr_${learning_rate}_${kl_estimator}_${beta}_${nspp}_${m}_${RANDOM}"
 full_bsz=$(($local_rollout_batch_size * nspp * (7) * 2))
 echo $exp_name:
 echo --- local_mini_batch_size=$local_mini_batch_size
 echo --- full_bsz=$full_bsz
 echo --- num_gradient_updates=$(($local_rollout_batch_size * $nspp / $local_mini_batch_size))
 python mason.py \
     --cluster ai2/jupiter \
     --workspace ai2/tulu-3-dev \
     --priority high \
     --preemptible \
     --num_nodes 2 \
     --max_retries 1 \
     --budget ai2/oe-adapt \
     --gpus 8 -- source configs/beaker_configs/ray_node_setup.sh \&\& uv run python open_instruct/grpo_vllm_thread_ray_gtrl.py \
     --exp_name $exp_name \
     --beta $beta \
     --local_mini_batch_size $local_mini_batch_size \
     --number_samples_per_prompt $nspp \
     --output_dir /weka/oe-adapt-default/costah/models/$exp_name \
     --local_rollout_batch_size $local_rollout_batch_size \
     --kl_estimator $kl_estimator \
     --learning_rate $learning_rate \
     --dataset_mixer_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 1.0 \
     --dataset_mixer_list_splits train \
     --dataset_mixer_eval_list allenai/RLVR-GSM-MATH-IF-Mixed-Constraints 16 \
     --dataset_mixer_eval_list_splits train \
     --max_token_length 2048 \
     --max_prompt_token_length 2048 \
     --response_length 2048 \
     --model_name_or_path allenai/Llama-3.1-Tulu-3-8B-DPO \
     --non_stop_penalty \
     --stop_token eos \
     --temperature 1.0 \
     --chat_template_name tulu \
     --total_episodes 10000000 \
     --penalty_reward_value 0.0 \
-    --deepspeed_stage 2 \
+    --deepspeed_stage 3 \
     --per_device_train_batch_size 2 \
     --local_rollout_forward_batch_size 2 \
-    --actor_num_gpus_per_node 4 8 \
+    --actor_num_gpus_per_node 6 \
     --num_epochs 1 \
-    --vllm_tensor_parallel_size 4 \
+    --vllm_tensor_parallel_size 2 \
     --lr_scheduler_type constant \
     --apply_verifiable_reward true \
     --seed 1 \
     --num_evals 30 \
     --save_freq 40 \
     --reward_model_multiplier 0.0 \
     --no_try_launch_beaker_eval_jobs \
     --try_launch_beaker_eval_jobs_on_weka \
     --gradient_checkpointing \
     --with_tracking
 done
 done
 done
 done
 done
```

---


## File: docs/meaisínfhoghlaim/training/open-instruct/human_eval/README.md

# Human Evaluation Annotation Interface

This folder contains the code for the human eval annotation interface used in the paper [How Far Can Camels Go? Exploring the State of Instruction Tuning on Open Resources](https://arxiv.org/abs/2306.04751).

## Installation

```bash
conda create -n human_eval python=3.10
conda activate human_eval
pip install -r requirements.txt
```

## Running the Interface

Before running the app, you need to put evaluation instance in the `data` folder. Each instance should have a prompt and two completions from two different models. We provide an example in `data/eval_instances_tulu_1.jsonl`.

Each line of this file should be in the following format:

```json
{
    "prompt": "prompt text",
    "completions": [
        {
            "model": "model 1 name",
            "completion": "completion text"
        },
        {
            "model": "model 2 name",
            "completion": "completion text"
        }
    ]
}
```

Now you can run the app with:

```bash
python app.py
```

You can open the app in your browser at http://localhost:5001. When doing the annotation, you can track the progress at the following url: http://localhost:5001/summary.

Here is a screenshot of the annotation interface:

<p align="center" width="100%">
      <img src="screenshot.png" alt="Screenshot of the human evaluation interface." style="width: 80%; display: block; margin: auto;">
</p>

## Post-processing and Analysis

The annotation results are saved in a database file `data/evaluation.db` by default. You can use the following command to export the results to an excel file:

```bash
python export_db.py
```

Then, you can use the following command to compute the evaluation metrics and agreements:

```bash
python compute_metrics.py
```

## Tulu 1 Annotation Results

We release the annotations that we collected for the Tulu 1 paper in `data/eval_annotations_tulu_1.xlsx`. The results include comparison of three models pairs: Tulu 65B vs ChatGPT, Tulu 65B vs Tulu 7B, and Tulu 65B vs Tulu (human only) 65B.

## Citation

If you used this code, please cite our paper:

```bibtex
@misc{wang2023far,
   title={How Far Can Camels Go? Exploring the State of Instruction Tuning on Open Resources},
   author={Yizhong Wang and Hamish Ivison and Pradeep Dasigi and Jack Hessel and Tushar Khot and Khyathi Raghavi Chandu and David Wadden and Kelsey MacMillan and Noah A. Smith and Iz Beltagy and Hannaneh Hajishirzi},
   year={2023},
   eprint={2306.04751},
   archivePrefix={arXiv},
   primaryClass={cs.CL}
}
```

---


## File: docs/meaisínfhoghlaim/training/open-instruct/README.md

[![Beaker Experiment Launch](https://github.com/allenai/open-instruct/actions/workflows/beaker-experiment.yml/badge.svg)](https://github.com/allenai/open-instruct/actions/workflows/beaker-experiment.yml) [![build_open_instruct](https://github.com/allenai/open-instruct/actions/workflows/push-image.yml/badge.svg)](https://github.com/allenai/open-instruct/actions/workflows/push-image.yml)

# Training Open Instruction-Following Language Models

This repo serves as an open effort on instruction-tuning and post-training popular pretrained language models on publicly available datasets. We release this repo and will keep updating it with:

1. Code for finetuning language models with latest techniques and instruction datasets in a unified format.
2. Code for DPO, preference finetuning and reinforcement learning with verifiable rewards (RLVR).
3. Checkpoints or other useful artifacts that we build in our exploration.

We also support some evaluations natively in the codebase, but these are now unmaintained and instead we suggest using [OLMES](https://github.com/allenai/olmes), which we used for TÜLU 3.

The latest details on open post-training are found in [TÜLU 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124).

Please see our first paper [How Far Can Camels Go? Exploring the State of Instruction Tuning on Open Resources](https://arxiv.org/abs/2306.04751) for more thoughts behind this project and our initial findings.
Please see our second paper [Camels in a Changing Climate: Enhancing LM Adaptation with Tulu 2](https://arxiv.org/abs/2311.10702) for results using Llama-2 models and direct preference optimization. We are still working on more models.
For more recent results involving PPO and DPO please see our third paper [Unpacking DPO and PPO: Disentangling Best Practices for Learning from Preference Feedback](https://arxiv.org/abs/2406.09279).

<p align="center" width="100%">
      <img src="assets/images/tulu_logo.png" alt="Tülu (a hybrid camel) represents a suite of LLaMa models that we built by fully-finetuning them on a strong mix of datasets." style="width: 20%; min-width: 200px; display: block; margin: auto;">
</p>

Try some of the models we train with Open Instruct. There is a [free demo](https://playground.allenai.org/) or download them from HuggingFace:

| **Stage**           | **Llama 3.1 8B**                                                                                          | **Llama 3.1 70B**                                                                                         | **OLMo-2 7B**                                                                                          | **OLMo-2 13B**                                                                                         |
|----------------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| **Base Model**       | [meta-llama/Llama-3.1-8B](https://huggingface.co/meta-llama/Llama-3.1-8B)                                | [meta-llama/Llama-3.1-70B](https://huggingface.co/meta-llama/Llama-3.1-70B)                              | [allenai/OLMo2-7B-1124](https://huggingface.co/allenai/OLMo2-7B-1124)                                | [allenai/OLMo-2-13B-1124](https://huggingface.co/allenai/OLMo-2-13B-1124)                             |
| **SFT**              | [allenai/Llama-3.1-Tulu-3-8B-SFT](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-SFT)                | [allenai/Llama-3.1-Tulu-3-70B-SFT](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-SFT)              | [allenai/OLMo-2-1124-7B-SFT](https://huggingface.co/allenai/OLMo-2-1124-7B-SFT)                | [allenai/OLMo-2-1124-13B-SFT](https://huggingface.co/allenai/OLMo-2-1124-13B-SFT)              |
| **DPO**              | [allenai/Llama-3.1-Tulu-3-8B-DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-DPO)                | [allenai/Llama-3.1-Tulu-3-70B-DPO](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B-DPO)              | [allenai/OLMo-2-1124-7B-DPO](https://huggingface.co/allenai/OLMo-2-1124-7B-DPO)                | [allenai/OLMo-2-1124-13B-DPO](https://huggingface.co/allenai/OLMo-2-1124-13B-DPO)              |
| **Final Models (RLVR)** | [allenai/Llama-3.1-Tulu-3-8B](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B)                        | [allenai/Llama-3.1-Tulu-3-70B](https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B)                      | [allenai/OLMo-2-1124-7B-Instruct](https://huggingface.co/allenai/OLMo-2-1124-7B-Instruct)                        | [allenai/OLMo-2-1124-13B-Instruct](https://huggingface.co/allenai/OLMo-2-1124-13B-Instruct)                      |
| **Reward Model (RM)**| [allenai/Llama-3.1-Tulu-3-8B-RM](https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B-RM)                                                     | (Same as 8B)                                                     | [allenai/OLMo-2-1124-7B-RM](https://huggingface.co/allenai/OLMo-2-1124-7B-RM)                                                     | (Same as 7B)                                                     |

## News

- [2024-11-22] We released [TÜLU 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124) and updated our entire stack of open post-training recipes with both Llama 3.1 and OLMo 2.
- [2024-07-01] We released [Unpacking DPO and PPO: Disentangling Best Practices for Learning from Preference Feedback](https://arxiv.org/abs/2406.09279) and have majorly updated our codebase to support new models and package versions.
- [2023-11-27] We released [Camels in a Changing Climate: Enhancing LM Adaptation with Tulu 2](https://arxiv.org/abs/2311.10702). Check out our models [here](https://huggingface.co/collections/allenai/tulu-v2-suite-6551b56e743e6349aab45101). We have added a DPO finetuning script for replicating our results.
- [2023-09-26] We switched to use the official [alpaca-eval](https://github.com/tatsu-lab/alpaca_eval) library to run AlpacaFarm evaluation but use regenerated longer reference outputs. This will change our numbers reported in the paper. We will update the paper soon.
- [2023-09-25] Supported using [vLLM](https://github.com/vllm-project/vllm/) for our evaluations, which speeds up the evaluation by 10x.
- [2023-09-17] Supported [LoRA](https://arxiv.org/abs/2106.09685) and [QLoRA](https://arxiv.org/abs/2305.14314) finetuning. See [here](#parameter-efficient-finetuning) for more details.
- [2023-08-18] Added support for [ToxiGen](https://github.com/microsoft/TOXIGEN)/[TruthfulQA](https://github.com/sylinrl/TruthfulQA) evaluation. Check our `scripts/eval/` for examples of running them.
- [2023-08-08] Supported several new instruction dataset, including [LIMA](https://huggingface.co/datasets/GAIR/lima) / [WizardLM](https://github.com/nlpxucan/WizardLM) / [Open-Orca](https://huggingface.co/datasets/Open-Orca/OpenOrca). See the [preparation script](./scripts/data/prepare_train_data.sh) for details. Performance hasn't been evaluated yet.
- [2023-08-06] Supported LLaMa 2 finetuning and FlashAttention-2 by bumping the version of transformers and many other dependencies.
- [2023-06-29] Added [licensing info](#licensing) for our released models.
- [2023-06-09] Released Tülu (a suite of LLaMa models fully-finetuned on a strong mix of datasets) and many other checkpoints on HuggingFace [[Links]](#released-checkpoints).
- [2023-06-09] Initial release of the codebase containing the training and evaluation code for our [arxiv paper](https://arxiv.org/abs/2306.04751).

## Setup

Our setup follows our [Dockerfile](./Dockerfile). *Note that Open Instruct is a research codebase and does not guarantee backward compatibility.*

### Installation with uv

We use [uv](https://docs.astral.sh/uv/) for installation and running code. You can install with `uv sync`.

* **Docker installation**: You can also use the Dockerfile to build a Docker image. You can build the image with the following command:

```bash
docker build . \
    --build-arg GIT_COMMIT=$(git rev-parse --short HEAD) \
	--build-arg GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD) \
	-t open_instruct_dev

# if you are internally at AI2, you can create a beaker image like this:
beaker_user=$(beaker account whoami --format json | jq -r '.[0].name')
beaker image delete $beaker_user/open_instruct_dev
beaker image create open_instruct_dev -n open_instruct_dev -w ai2/$beaker_user
```

If you are internally at AI2, you may launch experiments using our always-up-to-date auto-built image `nathanl/open_instruct_auto`.


## Training

After having setup the environment, you are ready to launch some experiments. We provide a few examples below. To learn more about how to reproduce the Tulu 3 models, please refer to the [Tulu 3 README](./docs/tulu3.md). The instructions and documentations for Tulu 1 and Tulu 2 are in [Tulu 1 and 2 README](./docs/tulu1_tulu2.md).

### Finetuning

You can run the following command for getting started:

```bash
# train an 8B tulu3 model using 8 GPU
bash scripts/train/tulu3/finetune_8b.sh
```


### Preference Tuning

```bash
# train an 8B tulu3 model using 8 GPU
bash scripts/train/tulu3/dpo_8b.sh
```


### Reinforcement Learning with Verifiable Rewards (RLVR)

```bash
# quick debugging run using 1 GPU (0.5 for inference, 0.5 for training)
# here we are using a small model, so it's prob not gonna train good models, but it's easy to test run and print stuff.
bash scripts/train/debug/single_gpu_on_beaker.sh

# train an 8B tulu3 model using 8 GPU (1 for inference, 7 for training)
bash scripts/train/rlvr/tulu_rlvr.sh
```


## Contamination checks

We release our scripts for measuring the overlap between instruction tuning datasets and evaluation datasets in `./decontamination`. See the [README](./decontamination/README.md) for more details.

### Developing
When submitting a PR to this repo, we check the core code in `open_instruct/` for style with the following:
```
make style
make quality
```

Run the tests with `uv run pytest`.

#### Pre-commit hooks

To automatically run linting and formatting on each commit:
```bash
uv add pre-commit --dev
uv run pre-commit install
```

To run on all files (recommended after initial setup):
```bash
uv run pre-commit run --all-files
```

### Repo structure
```
├── assets/                     <- Images, licenses, etc.
├── configs/
|     ├── beaker_configs/       <- AI2 Beaker configs
|     ├── ds_configs/           <- DeepSpeed configs
|     └── train_configs/        <- Training configs
├── decontamination/            <- Scripts for measuring train-eval overlap
├── eval/                       <- Evaluation suite for fine-tuned models
├── human_eval/                 <- Human evaluation interface (not maintained)
├── open_instruct/              <- Source code (flat)
├── quantize/                   <- Scripts for quantization
├── scripts/                    <- Core training and evaluation scripts
└── Dockerfile                  <- Dockerfile
```


## Licensing

This codebase is licensed under Apache 2.0 as given in [LICENSE](./LICENSE).

The license we use for V1 models released (along with the base model licenses) can be found in [assets/model_licenses/tulu_license.txt](./assets/model_licenses/tulu_license.txt) - just replace `<MODELNAME>` with the actual model name (i.e., the name on HuggingFace).

V2 models are licensed under the [low-risk AI2 ImpACT license](https://allenai.org/licenses/impact-lr). See [here](https://allenai.org/impact-license) for more details.


## Acknowledgements

Open Instruct is a project that benefited from many open-source projects and libraries. We would like to particularly thank the following projects:

* [HuggingFace Transformers](https://github.com/huggingface/transformers): We adapted Hugging Face's Trainer for our finetuning scripts.
* [HuggingFace TRL](https://github.com/huggingface/trl) and [eric-mitchell/direct-preference-optimization](https://github.com/eric-mitchell/direct-preference-optimization): our preference tuning code is adapted from TRL and from Eric Mitchell's DPO code.
* OpenAI's [lm-human-preferences](https://github.com/openai/lm-human-preferences), [summarize-from-feedback](https://github.com/openai/summarize-from-feedback), and [vwxyzjn/summarize_from_feedback_details](https://github.com/vwxyzjn/summarize_from_feedback_details): Our core PPO code is adapted from OpenAI's original RLHF code and [Huang et al (2024)'s reproduction work](https://openreview.net/forum?id=kHO2ZTa8e3) of OpenAI's summarize from feedback work.
* [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF): We adapted OpenRLHF's Ray + vLLM distributed code for scaling up PPO RLVR training into the 70B scale.

## Citation

If you used this repository or our models, please cite our work:

Tulu 1:
```bibtex
@misc{wang2023far,
   title={How Far Can Camels Go? Exploring the State of Instruction Tuning on Open Resources},
   author={Yizhong Wang and Hamish Ivison and Pradeep Dasigi and Jack Hessel and Tushar Khot and Khyathi Raghavi Chandu and David Wadden and Kelsey MacMillan and Noah A. Smith and Iz Beltagy and Hannaneh Hajishirzi},
   year={2023},
   eprint={2306.04751},
   archivePrefix={arXiv},
   primaryClass={cs.CL}
}
```

Tulu 2:
```bibtex
@misc{ivison2023camels,
      title={Camels in a Changing Climate: Enhancing LM Adaptation with Tulu 2},
      author={Hamish Ivison and Yizhong Wang and Valentina Pyatkin and Nathan Lambert and Matthew Peters and Pradeep Dasigi and Joel Jang and David Wadden and Noah A. Smith and Iz Beltagy and Hannaneh Hajishirzi},
      year={2023},
      eprint={2311.10702},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

Tulu 2.5:
```bibtex
@misc{ivison2024unpacking,
      title={Unpacking DPO and PPO: Disentangling Best Practices for Learning from Preference Feedback},
      author={Hamish Ivison and Yizhong Wang and Jiacheng Liu and Zeqiu Wu and Valentina Pyatkin and Nathan Lambert and Noah A. Smith and Yejin Choi and Hannaneh Hajishirzi},
      year={2024},
      eprint={2406.09279},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
}
```

Tulu 3:
```bibtex
@article{lambert2024tulu3,
  title = {Tülu 3: Pushing Frontiers in Open Language Model Post-Training},
  author = {
    Nathan Lambert and Jacob Morrison and Valentina Pyatkin and Shengyi Huang and Hamish Ivison and Faeze Brahman and Lester James V. Miranda and Alisa Liu and Nouha Dziri and Shane Lyu and Yuling Gu and Saumya Malik and Victoria Graf and Jena D. Hwang and Jiangjiang Yang and Ronan Le Bras and Oyvind Tafjord and Chris Wilhelm and Luca Soldaini and Noah A. Smith and Yizhong Wang and Pradeep Dasigi and Hannaneh Hajishirzi
  },
  year = {2024},
  email = {tulu@allenai.org}
}
```

---


## File: docs/meaisínfhoghlaim/training/open-instruct/scripts/data/azure_batch/README.md

# Azure OpenAI Batch Processing Scripts

This directory contains scripts for processing datasets using Azure OpenAI's Batch API. These scripts help you regenerate completions for datasets, monitor batch jobs, and process the results.

## Prerequisites

- Python 3.x
- Azure OpenAI API access with the following environment variables set:
  - `AZURE_OPENAI_ENDPOINT`
  - `AZURE_OPENAI_API_KEY`
  - `HF_TOKEN` (for uploading to Hugging Face)

## Scripts Overview

Install dependencies by creating a virtual env and `pip` installing the `requirements.txt` file from the root of the project.
I like to use [`uv`](https://github.com/astral-sh/uv):

```bash
uv venv
uv pip install -r requirements.txt
```

Then, you can either activate the `venv` or run the scripts with `uv run python script.py` (this acts the same as `python script.py`).

### 1. `regenerate_dataset_completions.py`

Regenerates completions for a dataset using Azure OpenAI's Batch API.

**Usage:**

```bash
python regenerate_dataset_completions.py [options]
```

**Key Options:**
- `--input-dataset`: Source dataset name (default: "allenai/tulu-3-sft-personas-code")
- `--split`: Dataset split to use (default: "train")
- `--sample-limit`: Limit number of samples to process
- `--model`: Model to use (default: "o3-batch")
- `--max-completion-tokens`: Maximum completion tokens (default: 8192)
- `--dry-run`: Preview without making API calls

### 2. `check_azure_batch_status.py`

Monitors the status of a batch API submission.

**Usage:**
```bash
# Check status once
python check_azure_batch_status.py <batch_id>

# Watch until completion
python check_azure_batch_status.py <batch_id> --watch
```

### 3. `process_azure_batch_results.py`

Processes batch results and creates a new dataset with updated completions.

**Usage:**
```bash
python process_azure_batch_results.py <batch_id> \
    --input-dataset <source_dataset> \
    --output-dataset <target_dataset> \
    --split <split_name> \
    [--no-upload]
```

## Typical Workflow

1. Use `regenerate_dataset_completions.py` to submit a batch job:
   ```bash
   python regenerate_dataset_completions.py --input-dataset your-dataset --split train
   ```

2. Monitor the batch job status:
   ```bash
   ./check_azure_batch_status.py <batch_id> --watch
   ```

3. Process the results and create a new dataset:
   ```bash
   python process_azure_batch_results.py <batch_id> \
       --input-dataset your-dataset \
       --output-dataset your-username/new-dataset \
       --split train
   ```

## Notes

- Batch jobs have a 24-hour completion window
- Maximum of 95,000 prompts per batch file
- Token usage and costs are tracked and reported
- Error handling and reporting is included in all scripts

If you have a dataset with more than 95k prompts, `regenerate_dataset_completions.py` will automatically split it up into multiple batches, and `process_azure_batch_results.py` will be able to combine them.

## Credentials

There are two main docs with the credentials you need:

- [NAIRR Pilot Azure AI Foundry Access (General Post-training)](https://docs.google.com/document/d/12fZEjqfopzi6hDroXrtgSIo00kpgMTLFs71-Lc2kkNI/edit?tab=t.0#heading=h.5m6cr2r4j0m) for access to GPT 4o, 4o-mini, and 4.1.
- [NAIRR Pilot Azure AI Foundry Access for using OpenAI Models for OLMo](https://docs.google.com/document/d/1PKygtkH-JmvayUwXQ-QaI_wj58P1KAF4uGRSh6yrBqs/edit?tab=t.0)  for access to GPT 4o, 4o-mini, 4.1, o3, o4-mini.

Reach out to [finbarrt@](finbarrt@allenai.org) for access to these docs if you don't have it.

## Validation

I have a [Colab](https://colab.research.google.com/drive/1rGmHyjIwlpg7T81RR9HSCJtX8YG7OQEi?usp=sharing) with a bunch of sanity checks when creating a new dataset.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/scripts/data/filtering_and_updates/README.md

# Data Filtering and Updates Scripts

## Filtering Scripts

* `scripts/data/filtering_and_updates/filter_special_tokens.py`: Removes special tokens like `<think>`, `</think>`, `<answer>`, `</answer>` from dataset text fields
* `scripts/data/filtering_and_updates/filter_wildchat.py`: Filters Wildchat datasets by removing toxic, redacted examples and keeping only English examples
* `scripts/data/filtering_and_updates/filter_chinese.py`: Filters data with a percentage of characters in the unicode range for Chinese charaters, based on treshold from 0 to 100%.
* `scripts/data/filtering_and_updates/filter_cutoff_date.py`: Removes mentions of knowledge cutoff dates from post-training datasets (e.g., "as my last update in April 2023")
* `scripts/data/filtering_and_updates/filter_cots.py`: Filters datasets for proper thinking token format and answer token format, specifically for reasoner model generations
* `scripts/data/filtering_and_updates/filter_dataset_by_keywords.py`: Removes phrases identifying the model as specific entities (e.g., "I am DeepSeek", "OpenAI", "Claude") from datasets
* `scripts/data/filtering_and_updates/filter_ngram_repetitions.py`: Removes examples with repetitive reasoning/text patterns in post-training datasets, focusing on sentence-level repetition patterns that indicate "unhinged" behavior
* `scripts/data/filtering_and_updates/filter_datasets_sequential.sh`: Shell script that runs keyword filtering followed by cutoff date filtering sequentially
* `scripts/data/filtering_and_updates/update_subsets.py`: Loads base dataset, removes unwanted sources, adds additional datasets, removes columns, and pushes combined dataset

## Testing

* `scripts/data/filtering_and_updates/test_filter_ngram_repetitions.py`: Comprehensive test suite for the n-gram repetition filtering functionality
* `scripts/data/filtering_and_updates/run_tests.py`: Test runner that executes all test files in the directory
* `scripts/data/filtering_and_updates/TEST_README.md`: Detailed documentation for running tests and test coverage

### Running Tests

```bash
# Run all tests
cd scripts/data/filtering_and_updates
python run_tests.py

# Run individual test
python test_filter_ngram_repetitions.py
```

See `TEST_README.md` for detailed test coverage information.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/scripts/data/filtering_and_updates/TEST_README.md

# Filtering Scripts Tests

This directory contains tests for the filtering scripts used in the open-instruct project.

## Test Files

- `test_filter_ngram_repetitions.py` - Comprehensive test suite for the n-gram repetition filtering functionality

## Running Tests

### Run All Tests
```bash
cd scripts/data/filtering_and_updates
python run_tests.py
```

### Run Individual Tests
```bash
cd scripts/data/filtering_and_updates
python test_filter_ngram_repetitions.py
```

## Test Coverage

The `test_filter_ngram_repetitions.py` test suite covers:

### Utility Functions
- `split_into_paragraphs()` - Text paragraph splitting
- `split_into_sentences()` - Text sentence splitting
- `is_math_or_code()` - Math/code pattern detection
- `is_code_import_or_return()` - Code import/return detection
- `is_short_phrase()` - Short phrase detection

### Core Functionality
- `detect_exact_block_repetition()` - Main repetition detection algorithm
- `process_example()` - Example processing with repetition detection
- `should_be_filtered_by_repetition()` - Filtering decision logic

### Test Scenarios
- 2x repetitions (minimum threshold testing)
- Consecutive vs non-consecutive repetitions
- Exact block repetition examples (Scooby-Doo, Marketing URL)
- Edge cases (empty text, single words, code patterns)
- N-gram repetition detection functions

### Test Cases Include
- Normal text (should NOT be flagged)
- Repetitive text (should be flagged)
- Code patterns (should be ignored)
- Math expressions (should be ignored)
- Short phrases (should be handled appropriately)
- Various repetition thresholds and patterns

## Notes

- Tests use lower thresholds than production to ensure functionality works
- Focus is on testing that functions work correctly, not exact production thresholds
- Tests verify both positive cases (repetitions detected) and negative cases (normal text not flagged)
- Edge cases and boundary conditions are covered

---


## File: docs/meaisínfhoghlaim/training/open-instruct/scripts/persona_driven_data_gen/README.md

## Persona-driven Data Generation


To start make sure you have your OpenAI and Anthropic API keys and have installed the libraries listed in `requirements.txt`:

```
pip install -r requirements.txt
```

This folder contains code to synthetically generate data (both prompts and responses) for target skill using a [persona-driven approach](https://arxiv.org/pdf/2406.20094):


**1- Precise Instruction Following:**

```
# Generate Instruction Following prompts
python persona_driven_generate_ifdata.py --model "gpt-4o" --start_index 0 --end_index 1000 --output_path if_prompts.jsonl --openai_key Z --org_id YYY --dataset ai2-adapt-dev/personahub_personas --template instruction_following

# Generate Responses for generated prompts
python persona_driven_generate_ifdata.py --model "gpt-4o" --start_index 0 --end_index 1000 --output_path if_solutions.jsonl --openai_key Z --org_id YYY --dataset if_prompts.jsonl --template instruction_following_solution

# Rewrite prompts to form Rejected Response (used for Presona-IF DPO data)
python persona_driven_generate_ifdata.py --model "gpt-4o" --start_index 0 --end_index 1000 --output_path if_solutions.jsonl --openai_key Z --org_id YYY --dataset if_prompts.jsonl --template rewrite_if_prompt
```


**2- Math World Problems**
```
# Generate math word problems
python persona_driven_generate_math_code.py --model "gpt-4o" --end_index 1000 --output_path <MATH_PROBLEMS> --openai_key XXX --org_id YYY --dataset ai2-adapt-dev/personahub_personas --template math

# Generate math solutions for generated math problems
python persona_driven_generate_math_code.py --model "gpt-4o" --end_index 1000 --output_path <OUTPUT_MATH> --openai_key XXX --org_id YYY --dataset <MATH_PROBLEMS> --template math_solution
```
Note that you can change `--template` to any of `['grade_math', 'math_int_algebra']` to generate other types of math data.



**3- Code (python)**
```
# Generate python problems

python persona_driven_generate_math_code.py --model "gpt-4o" --start_index 0 --end_index 1000 --output_path <PYTHON_PROBLEMS> --openai_key XXX --org_id YYY --dataset ai2-adapt-dev/personahub_personas --template code

# Generate python code
python persona_driven_generate_math_code.py --org_name anthropic --model 'claude-3-5-sonnet-20240620' --start_index 0 --end_index 1000 --output_path <OUTPUT_CODE> --openai_key XXX --org_id YYY --dataset <PYTHON_PROBLEMS> --template code_solution
```
Note that we used `claude-3-5-sonnet-20240620` to generate python codes.


All generated prompts and solutions will be saved in the `messages` format ready for supervised finetunig. An example output can be found [here](https://huggingface.co/datasets/ai2-adapt-dev/personahub_math_v5_regen_149960)

---


## File: docs/meaisínfhoghlaim/training/open-instruct/scripts/README.md

# Scripts Docs

There are many scripts in this repo, serving many different purposes. Here's a breakdown of the most important training scripts and how to use them. Generally, they are split into the following categories:
1. Instruction training.
2. Direct Preference Optimization (DPO) training.
3. Submitting jobs on Ai2 infrastructure (Beaker). **Use this type of script for launching multiple jobs easily)
4. Data and results management.

This readme covers each category and normal use-cases.

## Instruct training scripts
The following scripts are used for fine-tuning.
For Ai2 users, these scripts all work best in interactive sessions (not in batch jobs).

1. `finetune_lora_with_acceralate.sh`: Script for running `open_instruct/finetune.py` with LoRA.
2. `finetune_qlora_with_acceralate.sh`: Script for running `open_instruct/finetune.py` with QLoRA.
3. `finetune_with_acceralate_config.sh`: Script for running `open_instruct/finetune.py` with configs found in `configs/train_configs/sft/`. Good for reproducing results. Example usages:

```bash
sh scripts/finetune_with_accelerate_config.sh 1 configs/train_configs/sft/mini.yaml
sh scripts/finetune_with_accelerate_config.sh 1 configs/train_configs/sft/default.yaml
sh scripts/finetune_with_accelerate_config.sh 8 configs/train_configs/sft/olmo_17_sft.yaml
```

4. `finetune_with_acceralate.sh`: Script that the `_config` option above is based on. Uses options provided at CLI. **Change hyperparameters by manually editing or copying the script**.

## Direct Preference Optimization (DPO) scripts

1. `dpo_train_with_accelerate_config.sh`: Script for running `open_instruct/dpo_tune.py` with configs found in `configs/train_configs/dpo/`. Good for reproducing results. E.g.
```bash
sh scripts/dpo_train_with_accelerate_config.sh 1 configs/train_configs/dpo/mini.yaml
sh scripts/dpo_train_with_accelerate_config.sh 1 configs/train_configs/dpo/default.yaml
sh scripts/dpo_train_with_accelerate_config.sh 8 configs/train_configs/dpo/default.yaml
```

2. `dpo_train_with_accelerate.sh`: Script for running `open_instruct/dpo_tune.py` directly. **Change hyperparameters by manually editing or copying the script**.
E.g.
```bash
sh scripts/dpo_train_with_accelerate.sh
```
3. `dpo_train_with_qlora.sh`: Same as (2) with QLoRA quantization.

## Beaker / job submission scripts


0. First-time setup: You need to first obtain API key or tokens from the following website:

* `BEAKER_TOKEN`: https://beaker.org/user
* `WANDB_API_KEY`: https://wandb.ai/authorize
* `HF_TOKEN`: https://huggingface.co/settings/tokens

Then you need to write them in beaker secret as follows (replace the `xxxx` with your own API key or token)
```bash
beaker_whoami=$(beaker account whoami --format json | jq -r '.[0].name')
beaker secret write -w ai2/tulu-2-improvements "${beaker_whoami}_BEAKER_TOKEN" xxxx
beaker secret write -w ai2/tulu-2-improvements "${beaker_whoami}_WANDB_API_KEY" xxxx
beaker secret write -w ai2/tulu-2-improvements "${beaker_whoami}_HF_TOKEN" xxxx
```


1. `submit_eval_jobs.py`: Submit eval jobs for tasks in `scripts/evals/`. For example, llama 3 tulu 2 and upload to the tulu-3 eval database.
```bash
# submit evals on a model in beaker dataset
python scripts/submit_eval_jobs.py --model_name llama_31_tulu_2_8b --location 01J4MGRSS3FM1J4E6XSH3459DK --is_tuned --workspace tulu-3-results --preemptible --use_hf_tokenizer_template --beaker_image nathanl/open_instruct_auto --upload_to_hf allenai/tulu-3-evals

# submit evals on a model in huggingface; note you need to 1) prepend the model name with `hf-` and 2) replace `--location` with the hf repo id
python scripts/submit_eval_jobs.py --model_name hf-llama_31_tulu_2_8b --location allenai/llama-3-tulu-2-8b --is_tuned --workspace tulu-3-results --preemptible --use_hf_tokenizer_template --beaker_image nathanl/open_instruct_auto --upload_to_hf allenai/tulu-3-evals
python scripts/submit_eval_jobs.py --model_name hf-llama_31_tulu_2_8b --location vwxyzjn/online_dpo_tulu_2 --is_tuned --workspace tulu-3-results --preemptible --use_hf_tokenizer_template --beaker_image nathanl/open_instruct_auto --upload_to_hf allenai/tulu-3-evals

python scripts/submit_eval_jobs.py --model_name hf-online-dpo-llama-tulu2-longer --beaker_image costah/open_instruct_test --location vwxyzjn/online_dpo_vllm__allenai_llama-3-tulu-2-8b --hf_revision online_dpo_vllm__1__1724038538 --is_tuned --workspace tulu-3-results --preemptible --use_hf_tokenizer_template --upload_to_hf allenai/tulu-3-evals

```
Here, it is important to know that for using `oe-eval`, normally we run `--skip_oi_evals`, `run_safety_evaluations`, and `run_oe_eval_experiments`.

2. `submit_finetune_jobs.py`: **Core script** for submitting multiple and configurable instruction tuning jobs. This script works for both single- and multi-node configurations. It by default reads configs in `configs/train_configs`, but also can take in CLI arguments matching those in `open_instruct/utils.py` `FlatArguments` class.
Example of running this is in `scripts/submit_finetune_jobs.sh`.
```
python scripts/submit_finetune_job.py --config=configs/train_configs/sft/default.yaml  --learning_rate 1e-6 --exp_name sft_lr_search
python scripts/submit_finetune_job.py --config=configs/train_configs/sft/default.yaml  --learning_rate 4e-6 --exp_name sft_lr_search
python scripts/submit_finetune_job.py --config=configs/train_configs/sft/default.yaml  --learning_rate 1e-5 --exp_name sft_lr_search
python scripts/submit_finetune_job.py --config=configs/train_configs/sft/default.yaml  --learning_rate 4e-5 --exp_name sft_lr_search
```


You may want to add the `--exp_name`, the name that appears in the internal leaderboard.

<img width="1132" alt="image" src="https://github.com/user-attachments/assets/f99ff0d6-5436-4932-9fa7-d6266a68fba0">

<img width="1294" alt="image" src="https://github.com/user-attachments/assets/17251833-e90f-44d1-88f9-dd12c9465914">




To use this for multi-node jobs, here is an example that runs IFT on 4 nodes:
```
python scripts/submit_finetune_job.py --default_beaker_config configs/beaker_configs/default_finetune_multinode.yaml --config configs/train_configs/sft/tulu3_8b_preview_mix_v3.1.yaml --cluster ai2/jupiter --workspace ai2/tulu-3-dev --num_nodes 4 --exp_name preview_mix
```

3. `submit_dpo_job.py`: **Core script** for submitting DPO tuning jobs. It should behave like the finetune script, but additionally can take in beaker datasets to mount via `--datasets`, e.g.:
```
python scripts/submit_dpo_job.py --config configs/train_configs/dpo/my_dpo_config.yaml --datasets my_beaker_id:/model --experiment_name my_experiment_name
```
In this case, we also ask you provide an experiment name, as we don't know the name of the model being finetuned if it is mounted to `/model`.


### Docker-less job submssions

It is possible to re-use the existing environment you have and run things without having to build a docker container. The idea is to install python on NFS. You can refer to https://gist.github.com/vwxyzjn/58a2714cf3fbab5bf672ff750e86a537 for more detail.

Then you can submit jobs via `mason.py`, which we modified from https://github.com/allenai/mason. You can run the following to do a quick check
```bash
python mason.py \
    --cluster ai2/jupiter \
    --priority low \
    --budget ai2/jupiter \
    --gpus 1 -- which python
```

If you are successful in setting up python on NFS, your `which python` should match the `which python` output in the beaker job.

![image](https://github.com/user-attachments/assets/4f37d5bd-64bd-476b-9dad-1e35795b2618)



After setting it up successfully, say you are running `sh scripts/dpo_train_with_accelerate_config.sh 8 configs/train_configs/dpo/default.yaml` locally, now you can submit batch jobs via

```bash
python mason.py \
    --cluster ai2/jupiter \
    --priority low \
    --budget ai2/jupiter \
    --gpus 1 -- sh scripts/finetune_with_accelerate_config.sh 1 configs/train_configs/sft/mini.yaml
```



## Other
1. `collect_eval_results.py`: For collating metrics from `open-instruct` evaluation job. E.g.
```bash
python scripts/collect_eval_results.py \
    --experiment_id 01HV0P4E3MW9211HX0JEKM0PXM \
    --job_suffix _tulu2_13b_dpo_ultrainteract_04082024 \
    --output_file metrics.json \
    --task_order gsm_cot gsm_direct toxigen alpaca_eval \
    --print_table \
    --table_file metrics.tsv
```
2. `weights/weight_diff.py`: For converting weight diffs (as used with LLaMA 1) to full weights for eval/use. E.g.
```bash
python scripts/weights/weight_diff.py recover --path_raw ${hf_llama_path} --path_tuned ${output_path} --path_diff ${diff_location}
```
3. `weights/convert_llama_weights_to_hf.sh`: Use `transformers` to convert weights.
4. `data/*`: scripts for inpecting statistics of and rebuilding Tulu 1/2/N datasets from scratch (where possible).

## Notes on data mixing
Most of the scripts with `_config` take in configs that look like the following (just the data part):
```
dataset_mixer:
 allenai/tulu-v2-sft-mixture: 0.5
 HuggingFaceH4/no_robots: 0.8
```
There are many ways to configure data mixing. This is done with fractions, but also they can be done with number of samples directly. E.g.
```
dataset_mixer:
 allenai/tulu-v2-sft-mixture: 50000
 HuggingFaceH4/no_robots: 2500
```
The mixer is the advanced alternate to existing data arguments (which are still compatible, for reproducibility), such as local files:
```
train_file: data/processed/tulu_v2/tulu_v2_data.jsonl
```
or single HuggingFace datasets,
```
dataset_name: allenai/tulu-v2-sft-mixture
```
**Currently the dataset mixer is only supported for SFT models, but this will be expanded.**
With these options, the script will fail if multiple data args are passed, in the list of `dataset_mixer`, `train_file`, or `dataset_name`.
An internal arg, `dataset_mixer_list` was created to handle conversion from dict to string for Beaker jobs.

---


## File: docs/meaisínfhoghlaim/training/open-instruct/scripts/synth_pref/README.md

# Synthetic Preference Pipeline

This directory contains the implementation of the synthetic data pipeline for Tulu 3.
This pipeline is based on the Ultrafeedback pipeline ([Cui et al., 2023](https://arxiv.org/abs/2310.01377)) but with modifications such as the inclusion of on-policy data during data generation, and the use of GPT-4o for preference annotation.

Here's an overview of the pipeline (and how each script corresponds to each component):

![](https://github.com/allenai/open-instruct/blob/main/scripts/synth_pref/assets/ufpp_pipeline_v2_normal.png)
![](https://github.com/allenai/open-instruct/blob/main/scripts/synth_pref/assets/ufpp_pipeline_v2_code.png)


## Setup

You need to install specific dependencies for this pipeline:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r scripts/synth_pref/requirements.txt
```

We also use the open-source [Batch Inference Runtime (birr) tool](https://github.com/allenai/birr) to handle all calls to VLLM.
In your current directory, run the following:

```sh
git clone git@github.com:allenai/birr.git
git checkout 72e1c14
```

## How-to-use

### Dataset preparation for prompts

First, you need to prepare your prompts in a JSONL file with the following schema:

```
{"text": "Your text", **metadata}
```

Ideally, it is preferable to have multiple JSONL files with at most 250-500 rows each in a single directory so that `birr` can manage the queue more effectively.

> [!TIP]
> You can filter models by using the `--ignore_model` (`-x`) or `--include_model` (`-y`) tags.

### Response generation

First, let's generate configurations for `birr` (assuming your JSONL files in a directory called `source`):

```sh
python3 -m scripts.synth_pref.generate_responses \
    --name myprompts \
    --source_file "example/generate_responses_in/*.jsonl" \
    --target_dir "example/generate_responses_out/" \
    --batch_size 128
```

This command will generate configuration files for each model that you can send to `birr`.
To do so, run the following command:

```sh
python3 src/birr/batch_inference/runner.py --config-file path/to/config/file.yaml
```

After running this command, you'll see all the outputs in the directory you specified for `--target_dir`.
From there, you can create a preference annotation mix that samples four (4) responses for each model:

```sh
python3 -m scripts.synth_pref.create_annotation_mix \
    --name myprompts \
    --input_dir example/generate_responses_out/ \
    --output_dir example/create_annotation_mix_out/ \
    --prompt_template ultrafeedback
```

If you want to create a subset of on-policy data, you can pass a model name in `--one_side_model`.
This will ensure that one of the responses is from that on-policy checkpoint, while the other response will be sampled from the remaining.

### Preference annotation

Once you've created the annotation mix, you can now perform LLM-as-a-judge!
We use OpenAI's Batch API to query large sets of prompts, so first set your token:

```sh
export OPENAI_API_KEY=<your key>
```

Then, let's convert the annotation mix to the format desired by the Batch API:

```sh
python3 -m scripts.synth_pref.annotate_preferences \
    --model gpt-4o-2024-08-06 \
    --input_path create_annotation_mix_out/
    --output_dir create_annotation_mix_out/batch_openai
    --rows_per_shard 10000
```

This command will shard our annotation mix to `n` files with `10000` rows to fit OpenAI's file limits.
Then, we can send the annotations to OpenAI now:

```sh
python3 -m scripts.synth_pref.annotate_preferences \
    --model gpt-4o-2024-08-06 \
    --input_dir create_annotation_mix_out/batch_openai/
    --output_dir target_dir
```

This part may take some time, in the typical OpenAI API, the maximum wait time is 24 hours.
In addition, this command will save a `batch_infer_openai_results.csv` that keeps track of which file and which batch was sent to the server.
You can poll the file to see if they're done and it will automatically download the results via:

```sh
python3 -m scripts.synth_pref.annotate_preferences \
    --model gpt-4o-2024-08-06 \
    --batch_report create_annotation_mix_out/batch_infer_openai_results.csv
    --output_dir create_annotation_mix_out/batch_results/
```

If all files are done and downloaded, you can start parsing the preferences to obtain the final preference dataset:

```sh
python3 -m scripts.synth_pref.parse_preferences \
    --input_dir create_annotation_mix_out/batch_results \
    --output_path final_preference_dataset.yaml
```

---


## File: docs/meaisínfhoghlaim/training/open-instruct/scripts/train/olmo3/README.md

# Overview

For our recent [Olmo3 paper](insert link), we used the following scripts to train our models:

| Model           | Script name           | Beaker Link | Wandb URL | Commit |
|-----------------|----------------------|---|---|--------|
| 7B Think DPO    | `7b_think_dpo.sh`     | https://beaker.org/ex/01K5SXG8YH7NZDT5JCWJSNFCKG | https://wandb.ai/ai2-llm/open_instruct_internal/runs/drm42by2 | [`68da0a1`](https://github.com/allenai/open-instruct/commit/68da0a1) |
| 32B Think DPO   | `32b_think_dpo.sh`    | https://beaker.org/ex/01K9VYQV2RFPS9ECP63JFQFVDN | https://wandb.ai/ai2-llm/open_instruct_internal/runs/te37gyey | [`2fd104e`](https://github.com/allenai/open-instruct/commit/2fd104e) |
| 7B Instruct DPO | `7b_instruct_dpo.sh`  | https://beaker.org/ex/01KA62AJW9P8AWA3YKWE4Y6XZD | https://wandb.ai/ai2-llm/open_instruct_internal/runs/kxc617kc | [`2fd104e`](https://github.com/allenai/open-instruct/commit/2fd104e) |
| 7B Instruct RL  | `7b_instruct_rl.sh`   | https://beaker.org/ex/01KA8BY8MMAQWENWY4087MAPFE | https://wandb.ai/ai2-llm/open_instruct_internal/runs/p0l9m3ri | [`9ade62d`](https://github.com/allenai/open-instruct/commit/9ade62d) |
| 7B Think RL     | `7b_think_rl.sh` | https://beaker.org/ex/01KADRVRYEPW4YPKNN0RRNS137 | https://wandb.ai/ai2-llm/open_instruct_internal/runs/buq6ny46 | [`42aa63c`](https://github.com/allenai/open-instruct/commit/42aa63c) |
| 7B Think RL (no pipeline) | `7b_think_rl_no_pipeline.sh` | https://beaker.org/ex/01K6JZVN4EN3VHTJ820BV23HGC | https://wandb.ai/ai2-llm/open_instruct_internal/runs/pvb181bq | [`42aa63c`](https://github.com/allenai/open-instruct/commit/42aa63c) |
| 32B RL          | `32b_think_rl.sh` | https://beaker.org/ex/01KA4ZXT7MCVK493Y2B3K0BC82 | https://wandb.ai/ai2-llm/open_instruct_internal/runs/29h723j6 | [`42aa63c`](https://github.com/allenai/open-instruct/commit/42aa63c) |
| 7B RL Zero Math | `7b_rlzero_math.sh`   | https://beaker.org/ex/01K8V8TSX5K8BGZPJATZEE1003/ | https://wandb.ai/ai2-llm/open_instruct_internal/runs/w0ql4f5r | [`d928a7c`](https://github.com/allenai/open-instruct/commit/d928a7c) |
| 7B RL Zero Code | `7b_rlzero_code.sh`   | https://beaker.org/ex/01K7FSWM4717FAR9KF6GE958CA/ | https://wandb.ai/ai2-llm/open_instruct_internal/runs/o40rwmu8 | [`d928a7c`](https://github.com/allenai/open-instruct/commit/d928a7c) |
| 7B RL Zero IF   | `7b_rlzero_instruction_following.sh` | https://beaker.org/ex/01K7MVRTNJNYB37GC8SDTYHKC1/ | https://wandb.ai/ai2-llm/open_instruct_internal/runs/hk80a60o | [`d928a7c`](https://github.com/allenai/open-instruct/commit/d928a7c) |
| 7B RL Zero General | `7b_rlzero_general.sh` | https://beaker.org/ex/01K7FSZ2Y16KAV56Q0KB7TSWN7/ | https://wandb.ai/ai2-llm/open_instruct_internal/runs/0tscl05k | [`d928a7c`](https://github.com/allenai/open-instruct/commit/d928a7c) |


To reproduce these runs, if you are internal to Ai2, you can run

```
git checkout $COMMIT
./scripts/train/build_image_and_launch.sh $SCRIPT_NAME
```

This will build an image and launch it. You can also check out the beaker link to see the **exact run** that produced the model! If you are external to Ai2, we have many [fine job postings](https://allenai.org/careers), but, unfortunately, do not have great advice on how to launch these jobs. Preliminary steps to launch on your own infrastructure would involve:

1. Modifying the launch scripts to remove the stuff attached to the `mason.py` command
2. Setting up your own cluster with the requisite number of {H,A}100 nodes, connected together via Ray.

---


## File: docs/meaisínfhoghlaim/training/phone/docs/Federated AI Marketplace on iPhone.md

# **Decentralized Autonomous Knowledge Markets: Integrating Crypteolas Architectures, Agentic x402 Payments, and On-Device Vision Intelligence**

## **Executive Summary**

The digital economy stands at a precipice where the centralization of artificial intelligence conflicts with the imperative for data privacy and the distributed nature of data generation. A new architectural paradigm, synthesized from the principles of "Crypteolas" (Crypto-Federated Learning), is emerging to resolve this tension. This report presents a comprehensive technical and economic blueprint for a decentralized marketplace that leverages the computational power of consumer iOS devices to perform advanced computer vision tasks—specifically Optical Character Recognition (OCR), Handwritten Text Recognition (HTR), and Vision-Language Model (VLM) inference—while maintaining absolute data sovereignty.  
The proposed architecture envisions a network where iPhone users utilize their devices to scan, transcribe, and translate private documents. Instead of uploading this sensitive data to a central cloud for model training, the device utilizes Apple’s MLX framework and the Apple Vision API to perform local fine-tuning of VLM adapters (e.g., LoRA). These local intelligence updates are then commoditized. External agents—autonomous software entities representing researchers, corporations, or other algorithms—utilize the x402 "Payment Required" protocol to purchase access to this intelligence. They pay for ephemeral API access to the device's vision capabilities or fund federated learning rounds to aggregate local insights into a global model using the Flower framework and PySyft for privacy preservation.  
This report argues that the convergence of Apple Silicon’s unified memory architecture, the agentic interoperability of the x402 protocol, and the secure aggregation capabilities of modern federated learning frameworks creates a viable foundation for a "pay-for-compute" economy. This system transforms the iPhone from a passive consumption device into an active, revenue-generating node in a global, decentralized intelligence grid, fundamentally realigning the incentives of the AI economy toward privacy and user ownership.

## ---

**1\. The Crypteolas Paradigm: Convergence of Crypto and Federated Learning**

The term "Crypteolas" refers to the specific intersection of cryptographic incentives and federated learning architectures, a domain often described in academic literature as EdgeFL-Crypto. This paradigm shifts the focus from centralized data lakes to decentralized data grids, where the model travels to the data, and trust is established not by authority, but by cryptographic proof and economic stake.

### **1.1 Theoretical Foundations: From EdgeFL to Crypteolas**

Recent research into EdgeFL-Crypto architectures 1 highlights the efficacy of "Federated Split Learning" in high-frequency, low-latency environments such as cryptocurrency volatility prediction. This research demonstrates that federated learning can provide significant performance boosts—up to a 7.7% reduction in Root Mean Square Error (RMSE)—by leveraging distributed intelligence rather than centralized training. The "Crypteolas" concept extends this by embedding an economic layer directly into the learning protocol.  
In a traditional Federated Learning (FL) setup, participation is often altruistic or coerced (e.g., part of a terms-of-service agreement). In the Crypteolas model, participation is transactional. The iOS device acts as a sovereign entity that "sells" gradient updates. This aligns with the findings in blockchain-based federated learning literature, which posits that immutable audit trails and smart contract-based registries are essential for accountability and fairness in distributed systems.2 By logging model provenance and training participation on a blockchain, the system creates a "Proof of Training" that allows buyers to verify the utility of the contributions they are purchasing without inspecting the raw, private data.3

### **1.2 The Marketplace of Private Intelligence**

The core innovation of this proposal is the commoditization of "private intelligence." Traditional data marketplaces sell datasets, which requires data to change hands, violating privacy. The Crypteolas marketplace sells *insights* derived from data.

* **The Asset:** The asset is not the scanned image of a medical receipt or a handwritten diary entry; it is the *gradient update* generated by a VLM fine-tuned on that document.  
* **The Mechanism:** The mechanism is "Federated Sharing." Buyers pay to aggregate these gradients. The global model improves its ability to read handwriting or translate technical documents without ever "seeing" the source documents.  
* **The Agentic Economy:** The participants in this market are largely autonomous agents. An AI agent representing a logistics company might autonomously detect a drop in OCR accuracy for waybills and automatically dispatch x402 payments to thousands of iPhones to fine-tune a model on recent waybill formats.4

This architecture mirrors the ambitions of platforms like FLock.io, which use blockchain for model coordination and slashing mechanisms to penalize malicious actors 5, and Felt Labs, which facilitates training on distributed data.6 However, the proposed system is distinct in its reliance on high-performance mobile edge computing (Apple Silicon) as the primary compute substrate.

### **1.3 Why iOS? The Hardware Advantage**

The feasibility of this marketplace rests on the capabilities of the edge device. The iPhone, particularly models with A16 Bionic chips and later, possesses a unique architecture suitable for this task:

* **Unified Memory Architecture (UMA):** Unlike traditional architectures where data must be copied between CPU and GPU memory, Apple Silicon allows both processors to access the same memory pool. This is critical for running memory-intensive VLMs and performing training tasks without the latency of data transfer.7  
* **Apple Neural Engine (ANE):** A dedicated NPU optimized for matrix multiplication, essential for efficient inference of vision models and OCR tasks via the Vision framework.8  
* **Privacy Hardware:** The Secure Enclave provides a hardware root of trust for generating the cryptographic signatures required for x402 payments and authenticating the device's contribution to the federated network.

## ---

**2\. The On-Device Intelligence Stack: Vision, OCR, and VLMs**

To participate in the Crypteolas marketplace, the iOS device must perform complex perception and reasoning tasks. This requires a sophisticated stack merging native Apple frameworks with open-source LLM technologies.

### **2.1 The Vision Pipeline: OCR and HTR**

The foundational layer of the data processing pipeline is the extraction of raw text from images. The system utilizes Apple's Vision framework, specifically the VNRecognizeTextRequest API.

* **Optical Character Recognition (OCR):** For printed text, Apple's Vision framework offers state-of-the-art performance, running entirely on-device with minimal energy consumption. It provides bounding box information, allowing the system to map text back to specific regions of the image.  
* **Handwritten Text Recognition (HTR):** The user query specifically emphasizes HTR. The Vision framework supports HTR natively, but its accuracy can vary depending on style and legibility. In this architecture, the Vision framework serves as the "Proposer." It generates an initial transcription of the handwriting.  
* **The VLM Refinement Step:** This is where the value add occurs. A locally running Vision-Language Model (VLM), such as a quantized version of Qwen-VL or Llama-3-Vision, receives both the image embedding and the raw text proposed by the Vision framework. The VLM is prompted to "Correct the following transcription based on the image." This leverages the VLM's semantic understanding to correct HTR errors that a pure pattern-matching OCR system might miss (e.g., correcting "barn" to "born" based on the sentence context "I was born in 1990").

### **2.2 Running VLMs on iOS: GGUF and MLX**

The user explicitly mentions using **GGUF** models on iPhone. GGUF is a file format designed for fast inference of Large Language Models on CPUs and GPUs, popularized by llama.cpp.9

#### **2.2.1 The GGUF Pathway via llama.cpp**

* **Implementation:** Using llama.cpp libraries compiled for iOS, the application can load GGUF models ranging from 2B to 7B parameters. Benchmarks on A17 Pro chips show that 4-bit quantized models can achieve inference speeds of 20-30 tokens per second, which is sufficient for real-time interaction.9  
* **Role:** GGUF is ideal for the *inference* side of the marketplace. When a buyer pays for "API Access" to the device to scan a document, the app uses the efficient GGUF runtime to process the request.

#### **2.2.2 The MLX Pathway for Training**

While GGUF/llama.cpp is excellent for inference, it is not primarily designed for *training* or fine-tuning on Apple Silicon. For the "Federated Learning" aspect of the user's request, the architecture must leverage **MLX**, Apple's array framework designed for machine learning research on Apple Silicon.7

* **MLX Swift:** MLX provides a native Swift API that allows developers to build and train models directly in iOS apps without bridging to Python. This is crucial for performance and integration with other iOS subsystems.11  
* **Fine-Tuning:** The application uses MLX to load a VLM (which can be converted from GGUF or PyTorch formats into MLX's native format). It then performs **Low-Rank Adaptation (LoRA)** fine-tuning.  
* **The Workflow:**  
  1. User scans a handwritten note.  
  2. Apple Vision suggests text.  
  3. User manually corrects the text (creating Ground Truth).  
  4. The app uses MLX to run a training step (backpropagation), updating the LoRA adapter weights to minimize the loss between the model's prediction and the user's correction.  
  5. This "fine-tuned adapter" becomes the product sold in the federated marketplace.

### **2.3 Optimization via FastVLM**

To ensure this process does not render the phone unusable, the architecture should incorporate **FastVLM** principles.13 FastVLM is a research architecture that optimizes the vision encoding step, reducing the Time-To-First-Token (TTFT). Since the vision encoder is often the bottleneck at high resolutions, implementing FastVLM within the MLX environment allows the device to process high-resolution document scans efficiently, balancing the trade-off between accuracy (requiring high res) and latency/thermal throttling.

### **2.4 Translation and Semantic Understanding**

The VLM provides capabilities beyond simple transcription.

* **Translation:** The VLM can be prompted to "Transcribe and Translate this French menu into English JSON." This utilizes the model's pre-trained multilingual capabilities.  
* **Structuring:** The model can convert unstructured OCR data (a jumble of text) into structured formats (JSON with keys like "Date," "Total," "Merchant"), adding significant value for buyers looking for structured data streams.

## ---

**3\. The Economic Layer: Agentic Payments via x402**

The "marketplace" is defined by the exchange of value. The **x402 protocol** (Payment Required) serves as the standard for this exchange, enabling "Agentic Payments"—transactions initiated and settled by software agents without human intervention.4

### **3.1 The x402 Protocol Architecture**

x402 revives the long-dormant HTTP 402 status code to create a native payment layer for the web.

* **The Handshake:**  
  1. **Request:** A Buyer Agent (e.g., a server aggregating medical data) makes an HTTP request to the iOS device's endpoint: POST /api/federated/contribute.  
  2. **Challenge:** The iOS device (Server) checks for a valid payment token. If absent, it returns 402 Payment Required. The response body contains payment metadata: the required amount (e.g., 0.05 USDC), the chain (Base), and the recipient address.4  
  3. **Payment:** The Buyer Agent parses this metadata. Using its own embedded wallet, it signs a transaction transferring the funds. Crucially, x402 often leverages **EIP-3009** (Transfer with Authorization) or similar gasless signatures, allowing the Buyer to prove payment capabilities without waiting for full block confirmation for every micro-transaction.15  
  4. **Fulfillment:** The Buyer resends the request with the signed payment payload in the X-Payment or Authorization header. The iOS device verifies the signature (using a lightweight client or a trusted Facilitator) and accepts the federated contribution.16

### **3.2 x402 vs. L402: The Strategic Choice**

The user request mentions x402, but research snippets also highlight L402 (built on Bitcoin Lightning).17

* **L402 (Lightning):** Uses Macaroons for authentication and Lightning invoices for settlement. It is excellent for high-frequency, sub-cent privacy-preserving payments. However, running a Lightning node or managing channels on iOS is technically complex and resource-intensive.17  
* **x402 (EVM/Stablecoins):** Native to HTTP and works seamlessly with EVM chains like Base. It supports stablecoins (USDC), which is critical for a marketplace where participants (data sellers) want predictable value. The integration of x402 is generally more straightforward for web-native agents and supports the "smart contract" logic required for federated governance (staking/slashing).18  
* **Conclusion:** For this architecture, **x402** is the optimal choice for the primary payment rail due to its stablecoin support and ease of integration with the existing DeFi ecosystem, though L402 remains a viable alternative for purely Bitcoin-centric implementations.

### **3.3 Wallet Integration on iOS**

To participate, the iPhone must have a wallet.

* **Embedded Wallets:** The application utilizes an embedded wallet SDK (like Coinbase Wallet SDK or Web3Auth 20) to generate a non-custodial wallet for the user.  
* **Session Keys:** To enable "agentic" behavior (where the phone automatically sells data while the user sleeps), the user authorizes a "Session Key." This key has limited permissions (e.g., "Can sign transactions to accept payments, cannot withdraw funds") and allows the background process to negotiate x402 handshakes autonomously.

### **3.4 The Role of Facilitators**

Since the iPhone cannot run a full blockchain node to verify every transaction, the x402 architecture uses "Facilitators".21 These are trusted (or trust-minimized) relay nodes. The iPhone sends the payment proof provided by the Buyer to the Facilitator. The Facilitator checks the blockchain state and returns a cryptographically signed receipt to the iPhone, confirming the payment is valid. This allows the iPhone to serve the resource immediately without waiting for block finality.

## ---

**4\. Federated Orchestration: Flower and PySyft**

The mechanism for aggregating the "intelligence" sold by the devices is Federated Learning. The architecture employs **Flower (flwr)** for orchestration and **PySyft** for privacy preservation.

### **4.1 Flower on iOS: The Swift Client**

Flower is a framework-agnostic FL platform that scales to millions of clients.

* **Architecture:** The iOS app implements a FlowerClient subclass using the Flower Swift SDK (currently experimental/in-development but functionally describable).22  
* **Communication:** The client connects to a Flower Server (the Aggregator) via gRPC. This connection is persistent or established periodically via background tasks.  
* **Training Round:**  
  1. The Server sends a FitIns (Fit Instructions) message containing the global model weights and training configuration (learning rate, epochs).  
  2. The iOS client deserializes these weights. Since the weights arrive as byte arrays, the client must convert them into MLX Arrays.23  
  3. The client triggers the local MLX training loop, fine-tuning the model on the user's private scanned documents (OCR/HTR data).  
  4. The client computes the updated weights (or gradients) and serializes them back into a FitRes (Fit Result) message to send back to the server.

### **4.2 Privacy Preservation with PySyft**

To ensure that the updates sent via Flower do not leak information about the specific documents scanned (e.g., a specific name in a medical record), **PySyft** is integrated into the workflow.

* **Differential Privacy (DP):** Before the gradients are serialized for Flower, the iOS client applies Local Differential Privacy. It clips the gradients to a maximum norm (limiting the impact of any single data point) and adds Gaussian noise. This mathematically guarantees that the server cannot reverse-engineer the original data from the update.25  
* **Secure Aggregation (SMPC):** PySyft enables Secure Multi-Party Computation. The iOS devices can participate in a secure aggregation protocol where they mask their updates with random noise that cancels out only when all updates are summed at the server. This ensures the server sees *only* the aggregate result, never the individual updates.26  
* **SwiftSyft:** The iOS specific library, SwiftSyft, allows these PySyft protocols to run natively on the device, bridging the gap between the MLX training loop and the Flower communication layer.25

### **4.3 The "Pay-to-Federate" Workflow**

This is the synthesis of Crypteolas and x402.

1. **Job Posting:** A Buyer (e.g., a medical research group) posts a "Training Job" to the Federation Smart Contract, funding it with 10,000 USDC.  
2. **Selection:** The Flower Server selects 1,000 eligible iOS clients (those with relevant data who have staked tokens).  
3. **Payment Negotiation:** The Flower Server initiates the connection. The iOS clients respond with 402 Payment Required.  
4. **Escrow/Streaming:** The Smart Contract opens a payment stream or escrows funds. The iOS clients receive a proof of this funding.  
5. **Execution:** The clients perform the training round via MLX.  
6. **Settlement:** Upon successful submission of the gradients (verified by the server), the Smart Contract releases the pro-rated payment to the individual wallets of the iOS users.

## ---

**5\. Architectural Synthesis: The Marketplace in Action**

This section details the end-to-end flow of the system, illustrating how the user's "finetuned models" and "scanned images" are monetized.

### **5.1 Scenario A: Selling API Access (Inference)**

* **Context:** A user has a highly tuned model for reading 19th-century cursive handwriting (fine-tuned on their personal collection of letters).  
* **The Buyer:** A genealogy website's autonomous agent needs to transcribe a batch of old letters.  
* **The Flow:**  
  1. **Discovery:** The Buyer discovers the user's node via a decentralized registry (DHT or Blockchain) advertising "19th Century Handwriting Expert".  
  2. **Request:** The Buyer sends the image data to the iPhone's public endpoint (via a secure tunnel like ngrok or libp2p).  
  3. **x402 Gate:** The iPhone responds 402 Payment Required: 0.05 USDC.  
  4. **Payment:** The Buyer signs and sends the payment.  
  5. **Inference:** The iPhone accepts the payment, runs the image through its fine-tuned MLX VLM, extracts the text, and returns the JSON transcription.  
  6. **Result:** The user earns money for their device's unique "skill."

### **5.2 Scenario B: Selling Gradients (Federated Training)**

* **Context:** A consortium wants to build a global "Medical Receipt OCR" model.  
* **The Seller:** A user who frequently scans medical bills for personal expense tracking.  
* **The Flow:**  
  1. **Federation:** The user's device joins the "Medical Receipt" federation managed by Flower.  
  2. **Training:** At night, while charging, the device downloads the global model. It runs a training pass on the user's local receipts using MLX.  
  3. **Privacy:** SwiftSyft adds noise to the gradients.  
  4. **Submission:** The device uploads the gradients to the Flower Server.  
  5. **Reward:** The Federation Contract verifies the submission and streams x402 payments to the user's wallet based on the "Shapley Value" of their contribution (i.e., how much their data improved the model).28

## ---

**6\. Challenges, Security, and Mitigations**

### **6.1 Data Heterogeneity (Non-IID Data)**

* **Challenge:** Data on personal devices is highly skewed (Non-Independent and Identically Distributed). One user has only receipts, another only nature photos. This can destabilize federated learning.  
* **Mitigation:** The Flower server employs **Clustered Federated Learning**. It groups clients with similar data distributions into cohorts and trains specialized "Expert" models rather than a single monolithic model. The x402 metadata can include high-level, privacy-preserving tags (e.g., "Domain: Finance") to aid in this clustering without revealing content.

### **6.2 Poisoning Attacks**

* **Challenge:** Malicious users might submit random noise or adversarial gradients to degrade the model, just to collect the participation reward ("Free-riding").  
* **Mitigation:** **Staking and Slashing.** To participate in a paid round, the iOS user (via the app) must stake a small amount of tokens. The server validates a subset of updates against a known validation set. If a client's update consistently increases the loss (degrades the model), their stake is slashed (confiscated) by the smart contract.5

### **6.3 Resource Constraints**

* **Challenge:** Training VLMs is memory and battery intensive.  
* **Mitigation:**  
  * **LoRA/QLoRA:** Only training adapters reduces memory usage by 90%+.  
  * **Scheduling:** The app strictly limits training to when the device is plugged in and connected to Wi-Fi (BGProcessingTask).  
  * **Entitlements:** The app requests the Increased Memory Limit entitlement to prevent iOS from terminating the process during memory spikes.29

## ---

**7\. Implementation Roadmap**

### **Phase 1: The Local Intelligence Node**

* **Objective:** Build the iOS app capable of capture, OCR, and local VLM fine-tuning.  
* **Tech Stack:** Swift, SwiftUI, Vision Framework, MLX Swift.  
* **Key Deliverable:** A functional "Scanner" app that learns the user's corrections over time using a local LoRA adapter.

### **Phase 2: The Agentic Interface**

* **Objective:** Integrate the wallet and x402 protocol.  
* **Tech Stack:** Coinbase Wallet SDK, Node.js (for x402 middleware logic, potentially running locally or via a relay).  
* **Key Deliverable:** The app can receive testnet USDC for processing an image request from an external script.

### **Phase 3: The Federated Marketplace**

* **Objective:** Connect to the Flower server and enable privacy-preserving aggregation.  
* **Tech Stack:** Flower Swift SDK, SwiftSyft, Smart Contracts (Solidity).  
* **Key Deliverable:** A fully decentralized loop where the global model improves via user contributions, and users are automatically compensated.

## ---

**Conclusion**

The convergence of "Crypteolas" incentives, agentic x402 payments, and the raw power of Apple Silicon creates the conditions for a new digital economy. This report has outlined a viable architecture for a Decentralized Autonomous Knowledge Market. By enabling iPhones to securely fine-tune Vision-Language Models on private data and establishing a trustless, agentic payment rail for that intelligence, we can move beyond the extractive era of "Big AI."  
This system solves the **Cold Start Problem** of Federated Learning by providing direct economic incentives for participation. It solves the **Privacy Problem** of AI by ensuring raw data never leaves the device. And it solves the **Access Problem** by creating a liquid marketplace where any agent can purchase bespoke, high-quality intelligence from the edge. The technical path is complex, requiring deep integration of MLX, Flower, and Blockchain protocols, but the components are now mature enough to make this vision a reality.

### **Data Tables and Comparisons**

#### **Table 1: Comparison of Payment Protocols for Agentic Markets**

| Feature | x402 (Payment Required) | L402 (Lightning Network) | Implication for iOS Marketplace |
| :---- | :---- | :---- | :---- |
| **Settlement Layer** | EVM / Stablecoins (USDC) | Bitcoin Lightning Network | **x402** is preferred for stability and DeFi interoperability. |
| **Privacy** | Pseudonymous (Wallet Address) | High (Onion Routing) | **L402** offers better privacy but higher complexity. |
| **Client Complexity** | Low (Signing Messages) | High (Channel Management) | **x402** is lighter for mobile background tasks. |
| **Agent Support** | High (Coinbase AgentKit, etc.) | High (LangChain Tools) | Both have strong tooling, but **x402** aligns with web standards. |
| **Use Case** | API Access, Model Subscriptions | Streaming Micro-payments | **x402** suits the "Job" nature of FL training rounds. |

#### **Table 2: On-Device Compute Stack for Crypteolas**

| Component | Technology | Role in Marketplace |
| :---- | :---- | :---- |
| **Vision Encoder** | **Apple Vision / FastVLM** | Fast extraction of text/features; reduces VLM load. |
| **Inference Engine** | **llama.cpp (GGUF)** | Efficient, broad compatibility for serving API requests. |
| **Training Engine** | **MLX Swift** | Native, unified memory training for LoRA adapters. |
| **Orchestrator** | **Flower (Swift SDK)** | Manages the federated rounds and communication. |
| **Privacy** | **SwiftSyft** | Adds noise (DP) and manages Secure Aggregation. |

#### **Table 3: Economic Incentives & Governance**

| Role | Action | Incentive/Penalty |
| :---- | :---- | :---- |
| **Data Seller (iPhone)** | Submits Gradient Update | Earns USDC (x402) based on Shapley Value. |
| **Data Seller (iPhone)** | Submits Malicious Update | Staked USDC is slashed (burned). |
| **Buyer (Agent)** | Requests Training Round | Pays USDC to Federation Contract. |
| **Validator (Node)** | Audits Gradient Quality | Earns fee for validating updates (Proof of Training). |

#### **Works cited**

1. (PDF) EdgeFL-Crypto: Federated Split Learning Architecture for IoT- Based Cryptocurrency Volatility Prediction in Edge-Cloud Environments \- ResearchGate, accessed December 15, 2025, [https://www.researchgate.net/publication/397265328\_EdgeFL-Crypto\_Federated\_Split\_Learning\_Architecture\_for\_IoT-\_Based\_Cryptocurrency\_Volatility\_Prediction\_in\_Edge-Cloud\_Environments](https://www.researchgate.net/publication/397265328_EdgeFL-Crypto_Federated_Split_Learning_Architecture_for_IoT-_Based_Cryptocurrency_Volatility_Prediction_in_Edge-Cloud_Environments)  
2. \[2108.06912\] Blockchain-based Trustworthy Federated Learning Architecture \- arXiv, accessed December 15, 2025, [https://arxiv.org/abs/2108.06912](https://arxiv.org/abs/2108.06912)  
3. Blockchain-based federated learning architecture \- ResearchGate, accessed December 15, 2025, [https://www.researchgate.net/figure/Blockchain-based-federated-learning-architecture\_fig3\_380101342](https://www.researchgate.net/figure/Blockchain-based-federated-learning-architecture_fig3_380101342)  
4. X402 Protocol: What It Is, How It Works, and Why It Matters, accessed December 15, 2025, [https://vidrihmarko.medium.com/x402-protocol-what-it-is-how-it-works-and-why-it-matters-2b6bc889ee7f](https://vidrihmarko.medium.com/x402-protocol-what-it-is-how-it-works-and-why-it-matters-2b6bc889ee7f)  
5. FLock \- Federated Machine Learning On the Blockchain, accessed December 15, 2025, [https://www.flock.io/](https://www.flock.io/)  
6. Federated Learning Labs: FELT, accessed December 15, 2025, [https://feltlabs.ai/](https://feltlabs.ai/)  
7. Exploring LLMs with MLX and the Neural Accelerators in the M5 GPU, accessed December 15, 2025, [https://machinelearning.apple.com/research/exploring-llms-mlx-m5](https://machinelearning.apple.com/research/exploring-llms-mlx-m5)  
8. Deploying Transformers on the Apple Neural Engine \- Apple Machine Learning Research, accessed December 15, 2025, [https://machinelearning.apple.com/research/neural-engine-transformers](https://machinelearning.apple.com/research/neural-engine-transformers)  
9. Performance of llama.cpp on Apple Silicon A-series \#4508 \- GitHub, accessed December 15, 2025, [https://github.com/ggml-org/llama.cpp/discussions/4508](https://github.com/ggml-org/llama.cpp/discussions/4508)  
10. Building iOS app with llama cpp \- anyone familiar? : r/LocalLLaMA \- Reddit, accessed December 15, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/1ncy4nz/building\_ios\_app\_with\_llama\_cpp\_anyone\_familiar/](https://www.reddit.com/r/LocalLLaMA/comments/1ncy4nz/building_ios_app_with_llama_cpp_anyone_familiar/)  
11. ml-explore/mlx-swift: Swift API for MLX \- GitHub, accessed December 15, 2025, [https://github.com/ml-explore/mlx-swift](https://github.com/ml-explore/mlx-swift)  
12. On-device ML research with MLX and Swift, accessed December 15, 2025, [https://swift.org/blog/mlx-swift/](https://swift.org/blog/mlx-swift/)  
13. FastVLM: Efficient Vision Encoding for Vision Language Models \- Apple Machine Learning Research, accessed December 15, 2025, [https://machinelearning.apple.com/research/fast-vision-language-models](https://machinelearning.apple.com/research/fast-vision-language-models)  
14. How to Implement a Crypto Paywall with x402 Payment Protocol | Quicknode Guides, accessed December 15, 2025, [https://www.quicknode.com/guides/infrastructure/how-to-use-x402-payment-required](https://www.quicknode.com/guides/infrastructure/how-to-use-x402-payment-required)  
15. What is x402? \- Ledger, accessed December 15, 2025, [https://www.ledger.com/academy/topics/economics-and-regulation/what-is-x402](https://www.ledger.com/academy/topics/economics-and-regulation/what-is-x402)  
16. x402 \- Payment Required | Internet-Native Payments Standard, accessed December 15, 2025, [https://www.x402.org/](https://www.x402.org/)  
17. What Is L402, Lightning-Powered Payments for AI Agents? \- BingX, accessed December 15, 2025, [https://bingx.com/en/learn/article/what-is-l402-payments-for-ai-agents-on-lightning-network-how-does-it-work](https://bingx.com/en/learn/article/what-is-l402-payments-for-ai-agents-on-lightning-network-how-does-it-work)  
18. x402: An AI-Native Payment Protocol for the Web | by Jung-Hua Liu | Oct, 2025 | Medium, accessed December 15, 2025, [https://medium.com/@gwrx2005/x402-an-ai-native-payment-protocol-for-the-web-419358450936](https://medium.com/@gwrx2005/x402-an-ai-native-payment-protocol-for-the-web-419358450936)  
19. When AI Pays the Bill: How AI Agents Will Transact Using Coinbase’s X402 Protocol, accessed December 15, 2025, [https://medium.com/@deadwin/when-ai-pays-the-bill-how-ai-agents-will-transact-using-coinbases-x402-protocol-fc2de513db63](https://medium.com/@deadwin/when-ai-pays-the-bill-how-ai-agents-will-transact-using-coinbases-x402-protocol-fc2de513db63)  
20. Embedded Wallets SDK for iOS | MetaMask developer documentation, accessed December 15, 2025, [https://docs.metamask.io/embedded-wallets/sdk/ios/](https://docs.metamask.io/embedded-wallets/sdk/ios/)  
21. OrbytLabz/x402python: native python library for the x402 standard on Solana. \- GitHub, accessed December 15, 2025, [https://github.com/OrbytLabz/x402python](https://github.com/OrbytLabz/x402python)  
22. FLiOS \- A Flower SDK for iOS Devices with Example, accessed December 15, 2025, [https://flower.ai/docs/examples/ios.html](https://flower.ai/docs/examples/ios.html)  
23. Quickstart iOS \- Flower Framework, accessed December 15, 2025, [https://flower.ai/docs/framework/tutorial-quickstart-ios.html](https://flower.ai/docs/framework/tutorial-quickstart-ios.html)  
24. tutorial-quickstart-mlx.rst.txt \- Flower AI, accessed December 15, 2025, [https://flower.ai/docs/framework/\_sources/tutorial-quickstart-mlx.rst.txt](https://flower.ai/docs/framework/_sources/tutorial-quickstart-mlx.rst.txt)  
25. OpenMinedSwiftSyft on CocoaPods.org, accessed December 15, 2025, [https://cocoapods.org/pods/OpenMinedSwiftSyft](https://cocoapods.org/pods/OpenMinedSwiftSyft)  
26. What is PySyft, and how does it relate to federated learning? \- Milvus, accessed December 15, 2025, [https://milvus.io/ai-quick-reference/what-is-pysyft-and-how-does-it-relate-to-federated-learning](https://milvus.io/ai-quick-reference/what-is-pysyft-and-how-does-it-relate-to-federated-learning)  
27. OpenMined/SwiftSyft: The official Syft worker for iOS, built in Swift \- GitHub, accessed December 15, 2025, [https://github.com/OpenMined/SwiftSyft](https://github.com/OpenMined/SwiftSyft)  
28. Federated Learning Incentive Mechanism with Supervised Fuzzy Shapley Value \- MDPI, accessed December 15, 2025, [https://www.mdpi.com/2075-1680/13/4/254](https://www.mdpi.com/2075-1680/13/4/254)  
29. Exploring MLX Swift: Configuring Different Models \- Rudrank Riyam, accessed December 15, 2025, [https://rudrank.com/exploring-mlx-swift-configuring-different-models](https://rudrank.com/exploring-mlx-swift-configuring-different-models)
---


## File: docs/meaisínfhoghlaim/training/phone/docs/Fine-tuning VLMs for iOS HTR.md

# **Comprehensive Architectural Analysis for Bilingual Irish-English Handwritten Text Recognition on iOS: From Weakly-Supervised Data Generation to Edge Inference**

## **1\. Introduction: The Intersection of Philology and Edge AI**

The digitization of cultural heritage and the operationalization of low-resource languages represent two of the most compelling frontiers in modern artificial intelligence. The specific challenge of developing a bilingual Handwritten Text Recognition (HTR) system for Irish and English—capable of running locally on iOS devices—necessitates a sophisticated convergence of computer vision, natural language processing, and hardware-aware engineering. Unlike printed text, which adheres to rigid typographic standards, handwriting exhibits high variance in stroke, slant, and spacing. In the context of the Irish language, this complexity is often compounded by the historical presence of the *Cló Gaelach* (Gaelic type) or distinct insular scripts in older manuscripts, as well as the code-switching nature of modern bilingual datasets.  
Traditional Optical Character Recognition (OCR) pipelines, historically dependent on Tesseract or similar LSTM-based engines, often fail to capture the nuanced semantic context required to disambiguate difficult handwriting. They operate primarily on visual pattern matching of character glyphs. The advent of Vision-Language Models (VLMs) fundamentally alters this landscape. By projecting visual features into the same embedding space as a Large Language Model (LLM), VLMs allow the transcription process to be guided by linguistic probability. The model does not merely "see" the shape of a letter; it "reads" the likelihood of a word appearing in an Irish sentence structure, essentially hallucinating the correct text constrained by the visual evidence.  
However, the deployment of such massive parameter models on resource-constrained edge devices like the iPhone presents a formidable engineering barrier. While cloud-based inference is trivial, the requirement for on-device inference—driven by privacy, latency, and offline accessibility—demands a rigorous analysis of model compression, memory management, and specialized runtime environments like Apple's CoreML and MLX. Furthermore, the efficacy of any machine learning model is strictly bounded by the quality of its training data. The user’s proposal to utilize **ColPali**, a retrieval-oriented VLM, to construct a training dataset from unaligned page transcriptions introduces a novel paradigm of "weakly-supervised" annotation.  
This report provides an exhaustive technical analysis of this end-to-end pipeline. It dissects the architectural compatibility of **Unsloth** for fine-tuning, evaluates the viability of **Apple's ml-fastvlm** versus the **MLX** framework for deployment, and rigorously examines the mathematical mechanisms of **ColPali** for generating ground-truth bounding boxes. The analysis indicates that while direct compatibility between Unsloth and ml-fastvlm is architecturally obstructed by divergent vision encoders, a robust pathway exists via the MLX ecosystem, enabling the deployment of state-of-the-art Qwen2-VL models on Apple Silicon with high fidelity.

## **2\. Theoretical Foundations of Weakly-Supervised Dataset Generation**

The primary bottleneck in training HTR systems for specific domains (such as Irish manuscripts) is the scarcity of line-level annotated data. Most available data exists as "weakly labeled" pairs: a full image of a page and a full transcription of that page, without the coordinate geometry linking specific text lines to specific pixel regions. Manually drawing bounding boxes is prohibitively expensive. The proposed utilization of **ColPali** to automate this alignment exploits the model's unique architecture to bridge the gap between retrieval and localization.

### **2.1 The ColPali Architecture: Contextualized Late Interaction**

To understand how ColPali can be repurposed for data generation, one must first analyze its retrieval mechanism. Traditional dense retrieval systems (Bi-Encoders) compress an entire document image into a single vector embedding. While efficient for search, this compression results in a massive loss of spatial fidelity. ColPali, built upon the **PaliGemma** VLM, adopts the **ColBERT** (Contextualized Late Interaction over BERT) paradigm, applying it to the visual domain.1  
In ColPali, an image is not encoded into one vector, but into a grid of vectors. The Vision Transformer (ViT) backbone—typically SigLIP-So400m—processes the image at a resolution (e.g., $448 \\times 448$) and outputs a feature map. This map is projected into a sequence of patch embeddings. For a standard input, ColPali generates $32 \\times 32 \= 1024$ visual tokens, where each token represents a specific rectangular region of the image. Crucially, these visual tokens are projected into the same latent space as the text tokens of the language model.3  
The retrieval score $S(q, d)$ between a text query $q$ and a document image $d$ is calculated using the MaxSim operator:

$$S(q, d) \= \\sum\_{i=1}^{|q|} \\max\_{j=1}^{|d|} (E\_{q\_i} \\cdot E\_{d\_j})$$  
Here, $E\_{q\_i}$ is the embedding of the $i$-th token of the text query, and $E\_{d\_j}$ is the embedding of the $j$-th visual patch. This formula dictates that for every word in the query, the model searches for the single most similar patch in the image, and the total score is the sum of these maximum similarities.

### **2.2 Algorithmic Transformation: Attention-to-Geometry**

The user's insight—to use ColPali for indexing and matching to avoid alignment problems—can be operationalized into a rigorous segmentation algorithm. Since the MaxSim operator explicitly links text tokens to image patches, the internal state of the model during this calculation contains the localization data required to build the HTR dataset. By treating a single line of the transcription as the "query" and the full page as the "document," we can extract the **Attention Map** (or Similarity Map) to spatially locate the handwriting.5  
The process of generating the dataset follows a multi-stage pipeline:

1. **Indexing (Forward Pass):** The full page of the Irish manuscript is passed through the ColPali vision encoder. This results in a tensor of shape $$, representing the 1024 patches, each with a 128-dimensional embedding.  
2. **Querying:** A specific line from the transcription (e.g., *"Tá sé páirteach..."*) is tokenized and embedded by the text encoder.  
3. **Similarity Matrix Computation:** A dot product is computed between every text token embedding and every image patch embedding. This yields a matrix of shape $\[N\_{text}, 1024\]$.  
4. **Heatmap Aggregation:** To visualize where the whole line is located, one aggregates this matrix across the text dimension. A common approach is to sum the similarity scores for each patch, resulting in a $$ vector. This vector is reshaped back into a $32 \\times 32$ grid.7  
5. **Upscaling and Thresholding:** The $32 \\times 32$ grid is low-resolution. To derive a usable bounding box:  
   * The grid is bi-linearly interpolated up to the original image resolution (e.g., $2000 \\times 3000$).  
   * A thresholding algorithm (such as **Otsu’s Binarization**) is applied to the heatmap to separate the "active" regions (the text) from the background.9  
   * Contour detection algorithms (like those in OpenCV) identify the bounding rectangle of the largest connected component.11

This algorithm effectively converts the "soft" attention of the VLM into "hard" coordinates for cropping.

### **2.3 Resolving Alignment Challenges in Bilingual Text**

Irish manuscripts often contain mixed scripts or bilingual marginalia. A traditional OCR engine might struggle to differentiate between the main Irish text and English annotations, or might fail to recognize the *Cló Gaelach* entirely. ColPali offers a distinct advantage here: **Semantic Grounding**.  
Because ColPali utilizes a Language Model (Gemma-2B/PaliGemma), it understands the semantic content of the query. If the query is an Irish sentence, the model will attend to the visual features that correspond to those specific words, even if the handwriting is stylized. This is distinct from layout analysis models (like YOLO trained on generic documents) which only look for "text-like" blobs. ColPali aligns the *meaning* of the text to the *pixels*, making it robust against layout noise or interlineations common in handwritten datasets.12  
However, the analysis indicates a critical limitation: **Granularity**. The $32 \\times 32$ patch grid implies that each patch covers a significant area (roughly $60 \\times 60$ pixels on a standard scan). While this is sufficient for identifying the general region of a line, it is not pixel-perfect. The bounding boxes generated via this weakly-supervised method will be "loose." For finetuning Qwen2-VL, this is actually acceptable, as VLMs are generally robust to some background noise around the text, provided the text itself is fully contained.14

## **3\. Deep Dive: The Qwen2-VL Architecture and Unsloth Optimization**

With the dataset of image-text pairs generated via ColPali, the focus shifts to the recognition model. The user has specifically identified **Qwen2-VL** and the **Unsloth** framework. This choice is technically sound; Qwen2-VL represents the current state-of-the-art in open-weights VLMs, outperforming larger proprietary models in OCR benchmarks like DocVQA and OCRBench.15

### **3.1 Qwen2-VL: Naive Dynamic Resolution and M-ROPE**

The suitability of Qwen2-VL for HTR lies in its handling of visual inputs. Traditional VLMs (like the original LLaVA) resize all images to a fixed square (e.g., $336 \\times 336$). For handwriting, which often consists of long, narrow lines or vertically oriented marginalia, this resizing introduces disastrous distortion or downsampling artifacts that obliterate the fine details of the stroke.  
Qwen2-VL introduces **Naive Dynamic Resolution**. It does not enforce a fixed input size. Instead, it processes the image at its native resolution (constrained by a min\_pixels and max\_pixels hyperparameter range). The image is divided into patches of $14 \\times 14$. A line of handwriting that is $1000 \\times 50$ pixels will be tokenized into a sequence of patches that preserves this aspect ratio.17  
To manage this variable sequence length, Qwen2-VL employs **M-ROPE (Multimodal Rotary Positional Embedding)**. Standard ROPE encodes position in a 1D sequence. M-ROPE decomposes the positional embedding into three components: temporal (for video), height, and width. This allows the LLM to understand the 2D spatial relationships of the visual tokens regardless of the grid shape. This is critical for HTR, where the model must track the horizontal progression of cursive script across the image.18

### **3.2 Unsloth: The Mathematics of Efficiency**

Training a VLM like Qwen2-VL (even the 2B version) can be VRAM-intensive due to the long sequence lengths generated by high-resolution images. **Unsloth** provides the necessary optimization infrastructure to make this feasible on consumer-grade or mid-tier hardware.17  
Unsloth optimizes the fine-tuning process not through quantization (though it supports it) but through the manual derivation of backpropagation gradients. In standard PyTorch, the autograd engine constructs a graph that stores intermediate activations for every operation. Unsloth replaces standard Transformer modules (like MLP and Self-Attention) with custom implementations where the backward pass is mathematically derived and implemented in **OpenAI Triton** kernels.19  
**Key Optimizations for Qwen2-VL:**

* **Gradient Checkpointing:** Unsloth manages activation recomputation more efficiently, reducing VRAM usage by up to 60%. This allows for larger batch sizes or higher resolution inputs (higher max\_pixels), which is directly correlated with HTR accuracy.  
* **LoRA Integration:** Unsloth natively integrates Low-Rank Adaptation (LoRA). For HTR, it is recommended to target not just the attention layers (q\_proj, v\_proj) but also the MLP layers (gate\_proj, up\_proj, down\_proj). This "all-linear" targeting has been shown to improve the model's ability to learn new syntactic patterns, such as the specific grammar of Irish.20  
* **Bfloat16 Support:** Unsloth leverages bfloat16 precision, which prevents the numerical instability often seen in mixed-precision training of VLMs, particularly with the large gradient norms associated with visual encoders.

### **3.3 Fine-Tuning Strategy for Irish HTR**

To finetune Qwen2-VL via Unsloth for this specific application, the following configuration is optimal:

* **Model:** unsloth/Qwen2-VL-2B-Instruct-bnb-4bit. The 2B model is selected to fit within the iOS memory budget. The 4-bit quantization (bnb-4bit) enables training on GPUs with as little as 12GB VRAM.20  
* **Vision Tower:** Typically frozen. However, if the Irish handwriting is stylistically divergent from the pre-training data (which is mostly web data and standard OCR datasets), one might consider applying LoRA adapters to the vision tower as well. Unsloth allows setting target\_modules to include vision encoder layers, though this increases VRAM usage.22  
* **Data Formatting:** The dataset must be converted to the conversational format:  
  JSON  
  {  
    "messages":  
      },  
      {  
        "role": "assistant",   
        "content": \[{"type": "text", "text": "Lá breá grianmhar a bhí ann."}\]  
      }  
    \]  
  }

  This format aligns the visual perception with the instruction-following capability of the model.20

## **4\. Architectural Divergence: ml-fastvlm vs. MLX**

A central component of the user's query is the investigation of Apple's ml-fastvlm repository. The analysis reveals a critical architectural schism that impacts the deployment strategy.

### **4.1 Deconstructing ml-fastvlm and FastViT**

ml-fastvlm is the official implementation of the **FastVLM** paper (CVPR 2025). Its primary goal is to solve the latency bottleneck of Vision Transformers on edge devices. Standard ViTs (like the SigLIP encoder in Qwen2-VL) use global self-attention, which scales quadratically with the number of tokens ($O(N^2)$). On mobile chips, this is computationally expensive.23  
FastVLM replaces the standard Transformer vision encoder with **FastViT-HD**. FastViT is a hybrid architecture that uses **structural reparameterization**. During training, it uses complex blocks (RepMixer) that capture diverse features. During inference, these blocks collapse into a single $3 \\times 3$ convolution. This creates a model that is extremely fast on the Apple Neural Engine (ANE), which is optimized for convolutions.25  
The Incompatibility:  
The weights of the Qwen2-VL model (fine-tuned via Unsloth) correspond to a SigLIP-like Vision Transformer. The ml-fastvlm codebase expects a FastViT convolutional encoder. These are fundamentally different neural architectures. One cannot simply "export" the Unsloth Qwen2-VL weights into ml-fastvlm. To use ml-fastvlm, the user would need to:

1. Initialize a FastVLM architecture (FastViT encoder \+ Qwen2 LLM).  
2. Perform **Pre-training (Stage 1 & 2\)** to align the FastViT encoder with the LLM, requiring massive image-text datasets (e.g., LLaVA-665k).  
3. Perform **Supervised Fine-Tuning** on the Irish dataset.

This process is computationally expensive and redundant given the existence of Qwen2-VL. Therefore, ml-fastvlm is **not recommended** for this specific pipeline unless extreme latency optimization (sub-50ms) is the primary constraint over development time.25

### **4.2 The Solution: MLX and mlx-vlm**

**MLX** is Apple's array framework designed specifically for Apple Silicon (M-series and A-series chips). It provides a unified memory model, allowing the CPU and GPU to access the same data without copying, which is crucial for memory-heavy VLMs.27  
The **mlx-vlm** library (and the associated mlx-swift-examples) provides native support for the standard Qwen2-VL architecture. This includes the implementation of the specific ViT encoder, the M-ROPE positional embeddings, and the dynamic resolution preprocessing logic.28  
**Advantages of MLX for iOS Deployment:**

* **Architecture Parity:** It supports the exact model architecture trained by Unsloth.  
* **Conversion Pipeline:** There is a direct, supported path to convert Hugging Face weights (safetensors) to MLX format (weights.npz).  
* **Quantization:** MLX offers 4-bit and 8-bit quantization that is highly optimized for the A-series GPU. A 2B parameter Qwen2-VL model quantized to 4-bits requires approximately 1.2GB \- 1.5GB of RAM.30 This fits comfortably within the "wired memory" limits of modern iPhones (which typically have 6GB or 8GB of RAM), leaving sufficient headroom for the iOS operating system and the application's UI.

### **4.3 CoreML vs. MLX**

The user also inquired about CoreML. While coremltools is the standard for iOS ML, it struggles with the dynamism of Large Language Models and VLMs.

* **Static Graph Requirement:** CoreML traditionally prefers static computation graphs. Qwen2-VL's dynamic resolution (where the number of visual tokens changes per image) and the autoregressive nature of text generation are difficult to express efficiently in CoreML without padding to fixed sizes, which wastes computation.32  
* **ANE Limitations:** The Apple Neural Engine (ANE) lacks support for certain operations required by modern Transformers (like specific types of casting or complex attention masks), forcing fallback to the GPU or CPU. MLX, by contrast, is designed to execute dynamic graphs efficiently on the GPU/CPU immediately.27

**Verdict:** For LLMs and VLMs on iOS today, MLX is the superior choice over pure CoreML.

## **5\. Deployment Implementation Roadmap**

The following roadmap outlines the step-by-step execution of the project, integrating the missing details identified in the analysis.

### **Phase 1: Data Curation (Python/ColPali)**

1. **Ingest:** Load the scanned Irish manuscript pages and their corresponding transcriptions.  
2. **Index:** Use the colpali-engine to encode all page images into patch embeddings.  
3. **Localize:**  
   * Iterate through each line of the transcription.  
   * Compute the MaxSim attention map between the line text and the page image.  
   * Apply **Gaussian smoothing** to the raw attention map to reduce noise.  
   * Apply **Otsu's thresholding** to binarize the map.  
   * Extract the bounding box of the active region.  
   * *Refinement:* Expand the bounding box by 10-15% (padding) to ensure no ascenders/descenders are clipped.  
4. **Crop & Save:** Generate the training pairs: {"image": "crop\_001.jpg", "text": "Agus ansin dúirt sé..."}.

### **Phase 2: Fine-Tuning (Python/Unsloth)**

1. **Setup:** Initialize FastVisionModel from Unsloth with load\_in\_4bit=True.  
2. **Configure LoRA:**  
   * r (rank): 16 or 32\.  
   * target\_modules: \["q\_proj", "k\_proj", "v\_proj", "o\_proj", "gate\_proj", "up\_proj", "down\_proj"\].  
   * *Crucial:* Ensure use\_gradient\_checkpointing="unsloth" is enabled to save VRAM.  
3. **Train:** Run the SFTTrainer (Supervised Fine-Tuning Trainer) on the generated dataset. Monitor the validation loss on a held-out set of Irish handwriting to prevent overfitting to the specific scribal hand.20  
4. **Fuse:** Once training is complete, fuse the LoRA adapters back into the base model using model.save\_pretrained\_merged(...). This is essential because the mobile inference engine requires a single static model file, not a base+adapter configuration.20

### **Phase 3: Conversion (Python/MLX)**

1. **Install:** pip install mlx-vlm.  
2. **Convert:** Use the conversion script to transform the fused Hugging Face model to MLX format.  
   Bash  
   python \-m mlx\_vlm.convert \--hf-path./qwen2-vl-irish-fused \--quantize \--q-bits 4 \--mlx-path./qwen2-vl-irish-4bit

   This command performs the quantization (reducing weights to 4-bit integers) and saves the weights.npz and config.json.33

### **Phase 4: iOS Development (Swift)**

1. **Dependencies:** Add the mlx-swift and mlx-swift-examples packages to the Xcode project.  
2. **Model Loading:** Use the VLMModelFactory to load the model from the local bundle (or download it from Hugging Face).  
3. **Inference Logic:**  
   * Preprocess the camera input or selected image. *Note: Ensure the Swift preprocessor matches the min\_pixels / max\_pixels used during Unsloth training.*  
   * Pass the image and the prompt (e.g., "Transcribe this text") to the generate() function.  
   * Handle the output stream to display text in real-time.  
4. **Performance Tuning:** Monitoring the "Wired Memory" gauge in Xcode Instruments is vital. If memory pressure is too high, reduce the KV-cache quantization to 4-bit or limit the maximum sequence length (context window) since HTR tasks typically require short outputs.34

## **6\. Comparative Analysis: Model Specifications**

The following tables summarize the critical decision points in the architecture.  
**Table 1: Inference Engine Comparison for iOS VLMs**

| Feature | Apple ml-fastvlm | MLX (mlx-vlm) | CoreML |
| :---- | :---- | :---- | :---- |
| **Vision Encoder** | FastViT (Hybrid ConvNet) | SigLIP/ViT (Transformer) | Various (Static) |
| **Qwen2-VL Support** | **No** (Requires retraining) | **Yes** (Native) | **Partial** (Complex conversion) |
| **Dynamic Resolution** | Limited | **Full** (Naive Dynamic) | Difficult (Requires padding) |
| **Memory Efficiency** | High (ANE Optimized) | High (Unified Memory) | Moderate |
| **Dev Effort** | High (Research Code) | Low (Python-to-Swift) | Very High |
| **Best Use Case** | Ultra-low latency, fixed tasks | Generative AI, RAG, HTR | Classical CV, Classification |

**Table 2: Estimated Resource Footprint on iOS (iPhone 15 Pro)**

| Model Variant | Quantization | RAM Usage (Est.) | Inference Speed (Text) | Suitability |
| :---- | :---- | :---- | :---- | :---- |
| Qwen2-VL-2B | FP16 | \~4.5 GB | Slow | **Low** (OOM Risk) |
| Qwen2-VL-2B | 4-bit | **\~1.2 GB** | **\~40 tok/sec** | **High** (Production Ready) |
| Qwen2-VL-7B | 4-bit | \~4.0 GB | \~15 tok/sec | **Moderate** (Pro models only) |

**Table 3: Unsloth Training Metrics (Qwen2-VL-2B)**

| Metric | Standard Hugging Face | Unsloth | Improvement |
| :---- | :---- | :---- | :---- |
| VRAM Usage (2B) | \~14 GB | **\~6 GB** | \-58% |
| Training Speed | 1x | **1.8x \- 2x** | \+80% |
| Batch Size | Low | High | Stability |

## **7\. Future Directions and Bilingual Considerations**

While the primary goal is HTR, the bilingual nature of the data (Irish/English) presents opportunities for "Agentic HTR." Instead of simple transcription, the app could leverage the Qwen2-VL language capabilities to perform tasks like:

* **Translation:** "Transcribe and translate this Irish text to English."  
* **Summarization:** "Summarize the content of this handwritten note."  
* **Entity Extraction:** "List all names and dates found in this manuscript."

These capabilities are inherent to the VLM architecture and are preserved when deploying via MLX (unlike specialized OCR models which only output text). To ensure the model does not "forget" English while learning Irish handwriting, the training dataset should be a mix (e.g., 70% Irish crops, 30% English/Generic crops) to act as regularization.

## **8\. Conclusion**

The development of a bilingual HTR app for Irish on iOS is not only possible but feasible with high performance using the proposed pipeline. By rejecting the architectural rigidity of ml-fastvlm in favor of the **MLX** ecosystem, the developer gains access to the cutting-edge **Qwen2-VL** architecture. Simultaneously, the innovative application of **ColPali** as a weak supervisor solves the chronic lack of annotated data for the Irish language. This integration of retrieval-augmented data generation, efficiency-optimized training via **Unsloth**, and hardware-accelerated inference via **MLX** constitutes a robust, modern solution for mobile Document AI.

#### **Works cited**

1. ColPali: Efficient Document Retrieval with Vision Language Models \- arXiv, accessed December 15, 2025, [https://arxiv.org/html/2407.01449v5](https://arxiv.org/html/2407.01449v5)  
2. \[2407.01449\] ColPali: Efficient Document Retrieval with Vision Language Models \- arXiv, accessed December 15, 2025, [https://arxiv.org/abs/2407.01449](https://arxiv.org/abs/2407.01449)  
3. Advanced Retrieval with ColPali & Qdrant Vector Database, accessed December 15, 2025, [https://qdrant.tech/blog/qdrant-colpali/](https://qdrant.tech/blog/qdrant-colpali/)  
4. Scaling ColPali to billions of PDFs with Vespa, accessed December 15, 2025, [https://blog.vespa.ai/scaling-colpali-to-billions/](https://blog.vespa.ai/scaling-colpali-to-billions/)  
5. illuin-tech/colpali: The code used to train and run inference ... \- GitHub, accessed December 15, 2025, [https://github.com/illuin-tech/colpali](https://github.com/illuin-tech/colpali)  
6. Spatially-Grounded Document Retrieval via Patch-to-Region Relevance Propagation \- arXiv, accessed December 15, 2025, [https://arxiv.org/html/2512.02660v1](https://arxiv.org/html/2512.02660v1)  
7. ColPali: Efficient Document Retrieval with Vision Language Models \- arXiv, accessed December 15, 2025, [https://arxiv.org/html/2407.01449v2](https://arxiv.org/html/2407.01449v2)  
8. ColPali: Enhancing Financial Report Analysis with Multimodal RAG and Gemini, accessed December 15, 2025, [https://learnopencv.com/multimodal-rag-with-colpali/](https://learnopencv.com/multimodal-rag-with-colpali/)  
9. Bounding box extraction from attention maps. \- ResearchGate, accessed December 15, 2025, [https://www.researchgate.net/figure/Bounding-box-extraction-from-attention-maps\_fig2\_386577739](https://www.researchgate.net/figure/Bounding-box-extraction-from-attention-maps_fig2_386577739)  
10. Image Thresholding \- OpenCV Documentation, accessed December 15, 2025, [https://docs.opencv.org/4.x/d7/d4d/tutorial\_py\_thresholding.html](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html)  
11. How to get the feature bounded by the detected box in object detection? \#6311 \- GitHub, accessed December 15, 2025, [https://github.com/ultralytics/ultralytics/issues/6311](https://github.com/ultralytics/ultralytics/issues/6311)  
12. Transforming Product Discovery and Interpretation Using Vision–Language Models \- MDPI, accessed December 15, 2025, [https://www.mdpi.com/0718-1876/20/3/191](https://www.mdpi.com/0718-1876/20/3/191)  
13. Introduction to OCR Free Vision RAG using Colpali For Complex Documents, accessed December 15, 2025, [https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introduction-to-ocr-free-vision-rag-using-colpali-for-complex-documents/4276357](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/introduction-to-ocr-free-vision-rag-using-colpali-for-complex-documents/4276357)  
14. Spatially-Grounded Document Retrieval via Patch-to-Region Relevance Propagation, accessed December 15, 2025, [https://www.researchgate.net/publication/398269244\_Spatially-Grounded\_Document\_Retrieval\_via\_Patch-to-Region\_Relevance\_Propagation](https://www.researchgate.net/publication/398269244_Spatially-Grounded_Document_Retrieval_via_Patch-to-Region_Relevance_Propagation)  
15. Qwen2-VL | OpenLM.ai, accessed December 15, 2025, [https://openlm.ai/qwen2-vl/](https://openlm.ai/qwen2-vl/)  
16. Qwen/Qwen2-VL-2B-Instruct \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct](https://huggingface.co/Qwen/Qwen2-VL-2B-Instruct)  
17. unsloth/Qwen2-VL-2B-Instruct \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct](https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct)  
18. unsloth/Qwen2-VL-2B-Instruct-bnb-4bit \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct-bnb-4bit](https://huggingface.co/unsloth/Qwen2-VL-2B-Instruct-bnb-4bit)  
19. Make LLM Fine-tuning 2x faster with Unsloth and TRL \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/blog/unsloth-trl](https://huggingface.co/blog/unsloth-trl)  
20. Qwen2 Vision Finetuning Unsloth \- Kaggle, accessed December 15, 2025, [https://www.kaggle.com/code/danielhanchen/qwen2-vision-finetuning-unsloth-kaggle](https://www.kaggle.com/code/danielhanchen/qwen2-vision-finetuning-unsloth-kaggle)  
21. Fine-tune Llama3 with function calling via MLX-LM | by Anchen \- Medium, accessed December 15, 2025, [https://medium.com/@anchen.li/fine-tune-llama3-with-function-calling-via-mlx-lm-5ebbee41558f](https://medium.com/@anchen.li/fine-tune-llama3-with-function-calling-via-mlx-lm-5ebbee41558f)  
22. Vision Fine-tuning | Unsloth Documentation, accessed December 15, 2025, [https://docs.unsloth.ai/basics/vision-fine-tuning](https://docs.unsloth.ai/basics/vision-fine-tuning)  
23. apple/ml-fastvlm: This repository contains the official ... \- GitHub, accessed December 15, 2025, [https://github.com/apple/ml-fastvlm](https://github.com/apple/ml-fastvlm)  
24. FastVLM: Efficient Vision Encoding for Vision Language Models : r/apple \- Reddit, accessed December 15, 2025, [https://www.reddit.com/r/apple/comments/1m7gb3j/fastvlm\_efficient\_vision\_encoding\_for\_vision/](https://www.reddit.com/r/apple/comments/1m7gb3j/fastvlm_efficient_vision_encoding_for_vision/)  
25. Fastvlm: Efficient Vision Encoding For Vision Language Models | PDF \- Scribd, accessed December 15, 2025, [https://www.scribd.com/document/863828552/2412-13303v2](https://www.scribd.com/document/863828552/2412-13303v2)  
26. FastVLM: Efficient Vision Encoding for Vision Language Models \- CVF Open Access, accessed December 15, 2025, [https://openaccess.thecvf.com/content/CVPR2025/papers/Vasu\_FastVLM\_Efficient\_Vision\_Encoding\_for\_Vision\_Language\_Models\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Vasu_FastVLM_Efficient_Vision_Encoding_for_Vision_Language_Models_CVPR_2025_paper.pdf)  
27. MLX Swift: Run LLMs and VLMs in iOS Apps \- Reddit, accessed December 15, 2025, [https://www.reddit.com/r/swift/comments/1j4v70y/mlx\_swift\_run\_llms\_and\_vlms\_in\_ios\_apps/](https://www.reddit.com/r/swift/comments/1j4v70y/mlx_swift_run_llms_and_vlms_in_ios_apps/)  
28. Qwen2-VL Best Practice — swift 2.6.1 documentation \- Read the Docs, accessed December 15, 2025, [https://swift2x-en.readthedocs.io/en/latest/Multi-Modal/qwen2-vl-best-practice.html](https://swift2x-en.readthedocs.io/en/latest/Multi-Modal/qwen2-vl-best-practice.html)  
29. mlx-community/Qwen2-VL-2B-4bit \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/mlx-community/Qwen2-VL-2B-4bit](https://huggingface.co/mlx-community/Qwen2-VL-2B-4bit)  
30. README.md · riddhimanrana/fastvlm-0.5b-captions at main \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/riddhimanrana/fastvlm-0.5b-captions/blob/main/README.md](https://huggingface.co/riddhimanrana/fastvlm-0.5b-captions/blob/main/README.md)  
31. Speed Benchmark \- Qwen, accessed December 15, 2025, [https://qwen.readthedocs.io/en/v2.0/benchmark/speed\_benchmark.html](https://qwen.readthedocs.io/en/v2.0/benchmark/speed_benchmark.html)  
32. Load and Convert Model Workflow — Guide to Core ML Tools \- Apple, accessed December 15, 2025, [https://apple.github.io/coremltools/docs-guides/source/load-and-convert-model.html](https://apple.github.io/coremltools/docs-guides/source/load-and-convert-model.html)  
33. mlx-community/Jan-v2-VL-high-8bit-mlx \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/mlx-community/Jan-v2-VL-high-8bit-mlx](https://huggingface.co/mlx-community/Jan-v2-VL-high-8bit-mlx)  
34. llm-tool \- ml-explore/mlx-swift-examples \- GitHub, accessed December 15, 2025, [https://github.com/ml-explore/mlx-swift-examples/blob/main/Tools/llm-tool/README.md](https://github.com/ml-explore/mlx-swift-examples/blob/main/Tools/llm-tool/README.md)
---


## File: docs/meaisínfhoghlaim/training/phone/docs/How to Run and Deploy LLMs on your iOS or Android Phone _ Unsloth Documentation.md

---
title: "How to Run and Deploy LLMs on your iOS or Android Phone | Unsloth Documentation"
source: "https://docs.unsloth.ai/new/deploy-llms-phone"
author:
published: 2025-12-18
created: 2025-12-20
description: "Tutorial for fine-tuning your own LLM and deploying it on your Android or iPhone with ExecuTorch."
tags:
  - "clippings"
---
We’re excited to show how you can train LLMs then **deploy them locally** to **Android phones** and **iPhones**. We collabed with [ExecuTorch](https://github.com/pytorch/executorch/) from PyTorch & Meta to create a streamlined workflow using quantization-aware training ([QAT](https://docs.unsloth.ai/basics/quantization-aware-training-qat)) then deploy them directly to edge devices. With [Unsloth](https://github.com/unslothai/unsloth), TorchAO and ExecuTorch, we show how you can:

- Use the same tech (ExecuTorch) Meta has to power billions on Instagram, WhatsApp
- Deploy Qwen3-0.6B locally to **Pixel 8** and **iPhone 15 Pro at ~40 tokens/s**
- Apply QAT via TorchAO to recover 70% of accuracy
- Use our [free Colab notebook](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_\(0_6B\)-Phone_Deployment.ipynb) to fine-tune Qwen3 0.6B and export it for phone deployment

[iOS Tutorial](https://docs.unsloth.ai/new/deploy-llms-phone#ios-deployment) [Android Tutorial](https://docs.unsloth.ai/new/deploy-llms-phone#android-deployment)

**Qwen3-4B** deployed on a iPhone 15 Pro

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252F7tFjmj9c3p6o4eN3oHQq%252Funknown.png%3Falt%3Dmedia%26token%3D009699b3-e48f-4a94-bcd0-26cf6dedb8eb&width=768&dpr=4&quality=100&sign=ff8f6bf4&sv=2)

**Qwen3-0.6B** running at ~40 tokens/s

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FWI9nU1RQVrPbVXrIihfA%252Fimage.png%3Falt%3Dmedia%26token%3D5d58eb94-aeb3-42c3-a891-561ceb4e22db&width=768&dpr=4&quality=100&sign=59395c0d&sv=2)

We support Qwen3, Gemma3, Llama3, Qwen2.5, Phi4 and many other models for phone deployment! Follow the [**free Colab notebook**](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_\(0_6B\)-Phone_Deployment.ipynb) **for Qwen3-0.6B deployment:**

[Google Colab colab.research.google.com](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_\(0_6B\)-Phone_Deployment.ipynb)

First update Unsloth and install TorchAO and Executorch.

```
pip install --upgrade unsloth unsloth_zoo

pip install torchao==0.14.0 executorch pytorch_tokenizers
```

Then simply use `qat_scheme = "phone-deployment"` to signify we want to deploy it to a phone. Note we also set `full_finetuning = True` for full finetuning!

```
from unsloth import FastLanguageModel

import torch

model, tokenizer = FastLanguageModel.from_pretrained(

    model_name = "unsloth/Qwen3-0.6B",

    max_seq_length = 1024,

    full_finetuning = True,

    qat_scheme = "phone-deployment", # Flag for phone deployment

)
```

We’re using `qat_scheme = "phone-deployment"` we actually use `qat_scheme = "int8-int4"` under the hood to enable Unsloth/TorchAO QAT that *simulates* INT8 dynamic activation quantization with INT4 weight quantization for Linear layers during training (via fake quantization operations) while keeping computations in 16bits. After training, the model is converted to a real quantized version so the on-device model is smaller and typically **retains accuracy better than naïve PTQ**.

After finetuning as described in the [Colab notebook](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_\(0_6B\)-Phone_Deployment.ipynb), we then save it to a `.pte` file via Executorch:

```
# Convert the weight checkpoint state dict keys to one that ExecuTorch expects

python -m executorch.examples.models.qwen3.convert_weights "phone_model" pytorch_model_converted.bin

# Download model config from ExecuTorch repo

curl -L -o 0.6B_config.json https://raw.githubusercontent.com/pytorch/executorch/main/examples/models/qwen3/config/0_6b_config.json

# Export to ExecuTorch pte file

python -m executorch.examples.models.llama.export_llama \

    --model "qwen3_0_6b" \

    --checkpoint pytorch_model_converted.bin \

    --params 0.6B_config.json \

    --output_name qwen3_0.6B_model.pte \

    -kv --use_sdpa_with_kv_cache -X --xnnpack-extended-ops \

    --max_context_length 1024 --max_seq_length 128 --dtype fp32 \

    --metadata '{"get_bos_id":199999, "get_eos_ids":[200020,199999]}'
```

And now with your `qwen3_0.6B_model.pte` file which is around 472MB in size, we can deploy it! Pick your device and jump straight in:

- [iOS Deployment](https://docs.unsloth.ai/new/deploy-llms-phone#ios-deployment) – Xcode route, simulator or device
- [Android Deployment](https://docs.unsloth.ai/new/deploy-llms-phone#android-deployment) – command-line route, no Studio required

Tutorial to get your model running on iOS (tested on an iPhone 16 Pro but will work for other iPhones too). You will need a physical macOS based device which must be capable of running XCode 15.

**Install Xcode & Command Line Tools**

1. Install Xcode from the Mac App Store (must be version 15 or later)
2. Open Terminal and verify your installation: `xcode-select -p`
3. Install command line tools and accept the license:
	1. `xcode-select --install`
	2. `sudo xcodebuild -license accept`
4. Launch Xcode for the first time and install any additional components when prompted
5. If asked to select platforms, choose iOS 18 and download it for simulator access

Important: The first Xcode launch is crucial! Don't skip those extra component installations! Check [here](https://developer.apple.com/documentation/xcode/downloading-and-installing-additional-xcode-components) and [here](https://developer.apple.com/documentation/safari-developer-tools/adding-additional-simulators) for additional help.

**Verify Everything Works:** `xcode-select -p`

You should see a path printed. If not, repeat step 3.

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FJii1jArd6GQrdaCMHvyR%252Funknown.png%3Falt%3Dmedia%26token%3Dbd8b7a75-23e3-4474-b84b-ab9ad34cc401&width=300&dpr=4&quality=100&sign=3e18ea23&sv=2)

**For Physical devices only!**

**Create Your Apple ID**

Don't have an Apple ID? [Sign up here](https://support.apple.com/en-us/108647?device-type=iphone).

1. Open Xcode
2. Click the + button and select Apple ID

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FxG5ifHNeI6xKWqHw1pxL%252Funknown.png%3Falt%3Dmedia%26token%3D875fb5e4-e5f3-4c88-9af6-cb4e587975ca&width=768&dpr=4&quality=100&sign=1d976fcd&sv=2)

ExecuTorch requires the `increased-memory-limit capability`, which needs a paid developer account:

1. Visit [developer.apple.com](https://developer.apple.com/)
2. Enroll in the Apple Developer Program

**Grab the Example Code:**

```
# Download the LLM example app directly

curl -L https://github.com/meta-pytorch/executorch-examples/archive/main.tar.gz | \

  tar -xz --strip-components=2 executorch-examples-main/llm/apple
```

**Open in Xcode**

1. Open `apple/etLLM.xcodeproj` in Xcode
2. In the top toolbar, select `iPhone 16 Pro` Simulator as your target device
3. Hit Play (▶️) to build and run

🎉 Success! The app should now launch in the simulator. It won't work yet, we need to add your model.

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FA4n2u44u9sLlauCkhf1b%252Funknown.png%3Falt%3Dmedia%26token%3Dc93fef18-aab6-47cb-b301-d895466314f6&width=768&dpr=4&quality=100&sign=ff469bdb&sv=2)

**No Developer Account is needed.**

**Prepare Your Model Files**

1. Stop the simulator in Xcode (press the stop button)
2. Download these two files:
	1. `qwen3_0.6B_model.pte` (your exported model)
	2. tokenizer.json (the tokenizer)

**Create a Shared Folder on the Simulator**

1. Click the virtual Home button on the simulator
2. Open the Files App → Browse → On My iPhone
3. Tap the ellipsis (•••) button and create a new folder named `Qwen3test`

**Transfer Files Using the Terminal**

```
# Find the simulator's hidden folder

find ~/Library/Developer/CoreSimulator/Devices/ -type d -iname "*Qwen3test*"
```

When you see the folder run the following:

```
cp tokenizer.json /path/to/Qwen3test/tokenizer.json

cp qwen3_0.6B_model.pte /path/to/Qwen3test/qwen3_model.pte
```

**Load & Chat**

1. Return to the etLLM app in the simulator. Tap it to launch.
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252F55YWFJN49DCiHsy9EKOA%252Funknown.png%3Falt%3Dmedia%26token%3D4f8c8e90-df0b-4121-99eb-24437580724b&width=768&dpr=4&quality=100&sign=7cfc34aa&sv=2)

1. Load the model and tokenizer from the Qwen3test folder
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FpwUCX0nfarr6HSUd0pd3%252Funknown.png%3Falt%3Dmedia%26token%3D923b6ad3-d6e6-4e64-8223-947410c2218e&width=768&dpr=4&quality=100&sign=65601272&sv=2)

1. Start chatting with your fine-tuned model! 🎉
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FJrEzy1bvVeb4qLFxPFit%252Funknown.png%3Falt%3Dmedia%26token%3D36b7c70b-f014-4323-bdc5-cc5bf0fd12af&width=768&dpr=4&quality=100&sign=c00e5698&sv=2)

**Initial Device Setup**

1. Connect your iPhone to your Mac via USB
2. Unlock your iPhone and tap "Trust This Device"
3. In Xcode, go to Window → Devices and Simulators
4. Wait until your device appears on the left (it may show "Preparing" for a bit)

**Configure Xcode Signing**

1. Add your Apple Account: Xcode → Settings → Accounts → `+`
2. Select etLLM under TARGETS
3. Go to the Signing & Capabilities tab
4. Check "Automatically manage signing"
5. Select your Team from the dropdown

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FFm4a47e9Wuo7JiNbEeYl%252Funknown.png%3Falt%3Dmedia%26token%3D3f958363-6c0d-4608-8895-8376b0e1b1b1&width=768&dpr=4&quality=100&sign=ecb063f9&sv=2)

Change the Bundle Identifier to something unique (e.g., com.yourname.etLLM). This fixes 99% of provisioning profile errors

**Add the Required Capability**

1. Still in Signing & Capabilities, click + Capability
2. Search for "Increased Memory Limit" and add it

**Build & Run**

1. In the top toolbar, select your physical iPhone from the device selector
2. Hit Play (▶️) or press Cmd + R

**Trust the Developer Certificate**

Your first build will fail—this is normal!

1. Toggle On
2. Agree and accept notices
3. Restart device, return to Xcode and hit Play again

Developer Mode allows XCode to run and install apps on your iPhone

**Transfer Model Files to Your iPhone**

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FqAGQov6BgjlDSqA5GENN%252Funknown.png%3Falt%3Dmedia%26token%3D386b17df-703c-4e2c-9969-895577a98f0a&width=768&dpr=4&quality=100&sign=cf83faed&sv=2)
1. Once the app is running, open Finder on your Mac
2. Click the Files tab
3. Expand etLLM
4. Drag and drop your.pte and tokenizer.json files directly into this folder
5. Be patient! These files are large and may take a few minutes

**Load & Chat**

1. On your iPhone, switch back to the etLLM app
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FXY4EPFNcxaaBpjVroja3%252Funknown.jpeg%3Falt%3Dmedia%26token%3D7e8eca62-a5de-4705-9f0c-832b40579e78&width=768&dpr=4&quality=100&sign=7be7dba3&sv=2)
1. Load the model and tokenizer from the app interface
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FUzKWYRNR02vkVn5S3SQ5%252Funknown.jpeg%3Falt%3Dmedia%26token%3D84a85440-bf98-438d-a035-d8a11912a7a8&width=768&dpr=4&quality=100&sign=9b3f9639&sv=2)

1. Your fine-tuned Qwen3 is now running natively on your iPhone!
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FBX1nCLPbsnuRQchJXyAS%252Funknown.png%3Falt%3Dmedia%26token%3Dd276d4d6-2fc7-4cba-87f1-634aaea29884&width=768&dpr=4&quality=100&sign=57c97c56&sv=2)

This guide covers how to build and install the ExecuTorch Llama demo app on an Android device (tested using Pixel 8 but will also work on other Android phones too) using a Linux/Mac command line environment. This approach minimizes dependencies (no Android Studio required) and offloads the heavy build process to your computer.

### 🚀 Requirements

Ensure your development machine has the following installed:

- Java 17 (Java 21 is often the default but may cause build issues)
- Git
- Wget / Curl
- Android Command Line Tools
- [Guide to install](https://www.xda-developers.com/install-adb-windows-macos-linux/) and setup `adb` on your android and your computer

#### Verification

Check that your Java version matches 17.x:

```
# Output should look like: openjdk version "17.0.x"

java -version
```

If it does not match, install it via Ubuntu/Debian:

```
sudo apt install openjdk-17-jdk
```

Then set it as default or export `JAVA_HOME`:

```
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

export PATH=$JAVA_HOME/bin:$PATH
```

If you are on a different OS or distribution, you might want to follow [this guide](https://docs.oracle.com/en/java/javase/25/install/overview-jdk-installation.html) or just ask your favorite LLM to guide you through.

Set up a minimal Android SDK environment without the full Android Studio.

1\. Create the SDK directory:

```
mkdir -p ~/android-sdk/cmdline-tools

cd ~/android-sdk
```

1. Install Android Command Line Tools

```
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip

unzip commandlinetools-linux-*.zip -d cmdline-tools

# Important: Reorganize to satisfy SDK structure

mv cmdline-tools/cmdline-tools cmdline-tools/latest
```

Add these to your `~/.bashrc` or `~/.zshrc`:

```
export ANDROID_HOME=$HOME/android-sdk

export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$PATH

export PATH=$ANDROID_HOME/platform-tools:$PATH
```

Reload them:

```
source ~/.zshrc  # or ~/.bashrc depending on your shell
```

ExecuTorch requires specific NDK versions.

```
# Accept licenses

yes | sdkmanager --licenses

# Install API 34 and NDK 25

sdkmanager "platforms;android-34" "platform-tools" "build-tools;34.0.0" "ndk;25.0.8775105"
```

Set the NDK variable:

```
export ANDROID_NDK=$ANDROID_HOME/ndk/25.0.8775105
```

We use the `executorch-examples` repository, which contains the updated Llama demo.

```
cd ~

git clone https://github.com/meta-pytorch/executorch-examples.git

cd executorch-examples
```

Note that the current code doesn't have these issues but we have faced them previously and might be helpful to you:

**Fix "SDK Location not found":**

Create a `local.properties` file to explicitly tell Gradle where the SDK is:

```
echo "sdk.dir=$HOME/android-sdk" > llm/android/LlamaDemo/local.properties
```

**Fix** `**cannot find symbol**` **error:**

The current code uses a deprecated method `getDetailedError()`. Patch it with this command:

```
sed -i 's/e.getDetailedError()/e.getMessage()/g' llm/android/LlamaDemo/app/src/main/java/com/example/executorchllamademo/MainActivity.java
```

This step compiles the app and native libraries.

1. Build with Gradle (explicitly set `JAVA_HOME` to 17 to avoid toolchain errors):
	Note: The first run will take a few minutes.
	```
	export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
	./gradlew :app:assembleDebug
	```
2. The final generated apk can be found at:
	```
	app/build/outputs/apk/debug/app-debug.apk
	```

You have two options to install the app.

If you have `adb` access to your phone:

```
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

If you are on a remote VM or don't have a cable:

1. Upload the app-debug.apk to a place where you can download from on the phone
2. Download it on your phone
3. Tap to Install (Enable "Install from unknown sources" if prompted).

The app needs the.pte model and tokenizer files.

1. Transfer Files: Move your model.pte and tokenizer.bin (or tokenizer.model) to your phone's storage (e.g., Downloads folder).
2. Open LlamaDemo App: Launch the app on your phone.
3. Select Model
4. Tap the Settings (gear icon) or the file picker.
5. Select your.pte file.
6. Select your tokenizer file.

Done! You can now chat with the LLM directly on your device.

### Troubleshooting

- Build Fails? Check java -version. It MUST be 17.
- Model not loading? Ensure you selected both the `.pte` AND the `tokenizer`.
- App crashing? Valid `.pte` files must be exported specifically for ExecuTorch (usually XNNPACK backend for CPU).

Currently, `executorchllama` app that we built only supports loading the model from a specific directory on Android that is unfortunately not accessible via regular file managers. But we can save the model files to the said directory using adb.

```
adb devices
```

1. If you have connected via wireless debugging, you’d see something like this:
	![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FX1uYoIhXRdboBK36FX9D%252Funknown.png%3Falt%3Dmedia%26token%3D32955e17-56b7-4e2c-a06d-a1558d51427b&width=768&dpr=4&quality=100&sign=f8c53a7a&sv=2)
	Or if you have connected via a wire/cable:
	![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FBu88g0y9ivw0UQYsUyJJ%252Funknown.png%3Falt%3Dmedia%26token%3D8eda0918-398f-486d-a1f2-6976f895a7c2&width=768&dpr=4&quality=100&sign=84093363&sv=2)
	If you haven’t given permissions to the computer to access your phone:
	![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FSFkcwJyvgTcjvsPzCoDc%252Funknown.png%3Falt%3Dmedia%26token%3Dcb4bbdb6-4b83-473c-8a96-bbf75d8ba49e&width=768&dpr=4&quality=100&sign=ccc4301&sv=2)

1. Then you need to check your phone for a pop up dialog that looks like (which you might want to allow)
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FfqqtrC2590Wd71uzzbA5%252Funknown.png%3Falt%3Dmedia%26token%3De9a15b34-d794-47d1-ac63-cc5809f3e650&width=768&dpr=4&quality=100&sign=9696b8af&sv=2)

Once done, it's time to create the folder where we need to place the `.pte` and `tokenizer.json` files.

Create the said directory on the phone’s path.

```
adb shell mkdir -p /data/local/tmp/llama

adb shell chmod 777 /data/local/tmp/llama
```

Verify that the directory is created properly.

```
adb shell ls -l /data/local/tmp/llama

total 0
```

Push the contents to the said directory. This might take a couple of minutes to more depending on your computer, the connection and the phone. Please be patient.

```
adb push <path_to_tokenizer.json on your computer> /data/local/tmp/llama

adb push <path_to_model.pte on your computer> /data/local/tmp/llama
```

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FwqtWYiRBiyAOhi3aecn9%252Fimage.png%3Falt%3Dmedia%26token%3Dab04a1d1-194d-420d-a980-3336f90e7e42&width=768&dpr=4&quality=100&sign=493d4305&sv=2)

1. Open the `executorchllamademo` app you installed in Step 5, then tap the gear icon in the top-right to open Settings.
2. Tap the arrow next to Model to open the picker and select a model. If you see a blank white dialog with no filename, your ADB model push likely failed - redo that step. Also note it may initially show “no model selected.”
3. After you select a model, the app should display the model filename.

![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FmwIP3Fg2xWNfq5h719rE%252Funknown.png%3Falt%3Dmedia%26token%3D3b560fc2-6820-4dd1-a8fa-1a76e5523672&width=768&dpr=4&quality=100&sign=b5904ec4&sv=2) ![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252F5ft9HycpKPtCYhWgTmMn%252Funknown.png%3Falt%3Dmedia%26token%3Ddc35909b-9541-4fb1-9c7a-7a4be242afd4&width=768&dpr=4&quality=100&sign=b31c94e4&sv=2)

1. Now repeat the same for tokenizer. Click on the arrow next to the tokenizer field and select the corresponding file.
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252Fhga4tR05b5D0IqLvB2PM%252Funknown.png%3Falt%3Dmedia%26token%3Dfb00738e-9429-4014-836d-3e35821279cd&width=768&dpr=4&quality=100&sign=4b9e4dea&sv=2)

1. You might need to select the model type depending on which model you're uploading. Qwen3 is selected here.
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FjAZd67Ruub3gfblDrwUs%252Funknown.png%3Falt%3Dmedia%26token%3Dcf0f6938-2e9c-4bf4-b0f2-c7512b5506ad&width=768&dpr=4&quality=100&sign=f9b20bc&sv=2)

1. Once you have selected both files, click on the "Load Model" button.
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FGaPBdnweeeRIWgWsK9Fg%252Funknown.png%3Falt%3Dmedia%26token%3D73ec7e74-d9f8-4080-a6b0-ef239fd640d9&width=768&dpr=4&quality=100&sign=e43603e1&sv=2)

1. It will take you back to the original screen with the chat window, and it might show "model loading". It might take a few seconds to finish loading depending on your phone's RAM and storage speeds.
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252F1XHwMpnWEB2JiwNAR6hy%252Funknown.png%3Falt%3Dmedia%26token%3D18bcff85-b67c-4bbe-a961-28f5c5e58ce3&width=768&dpr=4&quality=100&sign=60c3037c&sv=2)

1. Once it says "successfully loaded model," you can start chatting with the model. Et Voila, you now have an LLM running natively on your Android phone!
![](https://docs.unsloth.ai/~gitbook/image?url=https%3A%2F%2F3215535692-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252FxhOjnexMCB3dmuQFQ2Zq%252Fuploads%252FRoYe3aDedHoovwfPJVOh%252Funknown.png%3Falt%3Dmedia%26token%3De9a2cc0a-2407-4c0b-adf1-6e2ba122212c&width=768&dpr=4&quality=100&sign=6adf209b&sv=2)

ExecuTorch [powers on-device ML experiences for billions of people](https://engineering.fb.com/2025/07/28/android/executorch-on-device-ml-meta-family-of-apps/) on Instagram, WhatsApp, Messenger, and Facebook. Instagram Cutouts uses ExecuTorch to extract editable stickers from photos. In encrypted applications like Messenger, ExecuTorch enables on-device privacy aware language identification and translation. ExecuTorch supports over a dozen hardware backends across Apple, Qualcomm, ARM and [Meta’s Quest 3 and Ray Bans](https://ai.meta.com/blog/executorch-reality-labs-on-device-ai/).

- All Qwen 3 dense models ([Qwen3-0.6B](https://huggingface.co/unsloth/Qwen3-0.6B), [Qwen3-4B](https://huggingface.co/unsloth/Qwen3-4B), [Qwen3-32B](https://huggingface.co/unsloth/Qwen3-32B) etc)
- All Gemma 3 models ([Gemma3-270M](https://huggingface.co/unsloth/gemma-3-270m-it), [Gemma3-4B](https://huggingface.co/unsloth/gemma-3-4b-it), [Gemma3-27B](https://huggingface.co/unsloth/gemma-3-27b-it) etc)
- All Llama 3 models ([Llama 3.1 8B](https://huggingface.co/unsloth/Llama-3.1-8B-Instruct), [Llama 3.3 70B Instruct](https://huggingface.co/unsloth/Llama-3.3-70B-Instruct) etc)
- Qwen 2.5, Phi 4 Mini models, and much more!

You can customize the [**free Colab notebook**](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_\(0_6B\)-Phone_Deployment.ipynb) for Qwen3-0.6B to allow phone deployment for any of the models above!

**Qwen3 0.6B main phone deployment notebook**

[Google Colab colab.research.google.com](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_\(0_6B\)-Phone_Deployment.ipynb)

Works with Gemma 3

[Google Colab colab.research.google.com](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Gemma3_\(4B\).ipynb)

Works with Llama 3

[Google Colab colab.research.google.com](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Llama3.2_\(1B_and_3B\)-Conversational.ipynb)

Go to our [Unsloth Notebooks](https://docs.unsloth.ai/get-started/unsloth-notebooks) page for all other notebooks!

[Previous DPO, ORPO, KTO](https://docs.unsloth.ai/get-started/reinforcement-learning-rl-guide/reinforcement-learning-dpo-orpo-and-kto) [Next New 3x Faster Training](https://docs.unsloth.ai/new/3x-faster-training-packing)

Last updated

Was this helpful?
---


## File: docs/meaisínfhoghlaim/training/phone/docs/Irish LLM for iPhone Development.md

# **Strategic Architecture for Indigenous Language Intelligence on the Edge: A Comprehensive Framework for Deploying Irish Large Language Models on iOS**

## **1\. Executive Strategy and Pipeline Architecture**

The convergence of parameter-efficient fine-tuning methodologies, specifically those pioneered by Unsloth, with high-fidelity mobile inference engines like AnyLanguageModel, has created an unprecedented opportunity to deploy indigenous language intelligence on consumer edge hardware. This report provides an exhaustive technical analysis and strategic roadmap for developing a Large Language Model (LLM) tailored to the Irish language (*Gaeilge*), specifically optimized for the constraints of iOS deployment using Unsloth's 4-bit GGUF quantization pipeline.

### **1.1 The Convergence of Efficiency and Accessibility**

The trajectory of LLM development has bifurcated into two distinct paths: the pursuit of massive scale (models exceeding 400 billion parameters) and the refinement of efficiency (Small Language Models or SLMs, typically under 8 billion parameters). For the deployment of Irish language capabilities on iPhones, the latter path is the only viable route. The constraints of the Apple Unified Memory Architecture (UMA), thermal envelopes, and battery capacity necessitate a model that balances linguistic competence with extreme parameter efficiency.  
The Unsloth framework serves as the critical enabler in this architecture. By optimizing the backpropagation engine and introducing Triton-based kernels, Unsloth allows for the fine-tuning of these models on commodity hardware, a crucial factor for low-resource language communities where computational resources are often scarce.1 Furthermore, Unsloth’s integration of "Dynamic 2.0" GGUF quantization provides a lossless pathway from the training environment to the mobile inference environment, preserving the delicate grammatical structures of Irish that are often degraded by standard quantization techniques.3

### **1.2 Architectural Constraints of the iOS Edge**

Deploying an LLM on an iPhone is fundamentally different from server-side deployment. The primary constraint is not merely storage, but **resident memory (RAM)**. Modern iPhones typically feature between 6GB (standard models) and 8GB (Pro models) of unified memory. The iOS operating system dynamically manages this memory, aggressively terminating background processes or applications that exceed safe thresholds to preserve system responsiveness.

* **The 4GB Ceiling:** Practical experience and technical documentation suggest that an iOS application has a "safe" working set of approximately 2GB to 3GB on standard devices before risking termination.  
* **The Quantization Imperative:** A standard 16-bit floating-point (FP16) model requires roughly 2GB of VRAM per 1 billion parameters. A 7B model would thus require 14GB, rendering it deployable only on high-end MacBooks, not phones.  
* **The 4-bit Solution:** By utilizing Unsloth's 4-bit GGUF export, the memory footprint is reduced to approximately 0.7GB per 1 billion parameters. This places a **3B parameter model** (approx. 2.2GB total footprint) squarely in the "Goldilocks zone" for iOS deployment—large enough to retain reasoning capabilities, yet small enough to run stable alongside the application's UI and logic.4

### **1.3 The Role of AnyLanguageModel and Swift Transformers**

The user’s requirement involves AnyLanguageModel, a Swift package designed to abstract the complexities of on-device inference.6 It is crucial to distinguish the internal mechanics of this library to ensure correct implementation. AnyLanguageModel utilizes Swift Package Manager "Traits" to conditionally compile backends 6:

1. **CoreML Trait:** Depends on swift-transformers and runs .mlpackage or .mlmodelc files via the Apple Neural Engine.  
2. **Llama Trait:** Depends on llama.cpp bindings and runs .gguf files.

Since the objective is to leverage **Unsloth GGUF 4bit** models, the architecture must rely on the **Llama trait**. While swift-transformers is a dependency for the CoreML path, the GGUF path bypasses CoreML's graph compilation in favor of llama.cpp's CPU/GPU execution. This is advantageous for Irish language development because GGUF supports a wider range of custom tokenizers and vocabulary expansions than CoreML, which can be rigid regarding custom operations often required by newer architectures like Qwen 2.5 or Llama 3.2.6

## ---

**2\. The Linguistic Landscape: Irish NLP and the Tokenization Bottleneck**

To select the correct model, one must first understand the specific mechanical difficulties the Irish language presents to Transformer architectures. Irish is a VSO (Verb-Subject-Object) language with a complex system of initial mutations (lenition and eclipsis) that fundamentally alters the beginning of words based on their grammatical context.

### **2.1 The Morphology of Gaeilge and Tokenizer Fertility**

Most "multilingual" models are heavily biased toward English and Romance languages. This bias is physically encoded in the **Tokenizer**—the component that breaks text into numerical IDs. A tokenizer trained primarily on English will not recognize Irish roots.  
For example, the Irish word *deartháir* (brother) might be tokenized as a single integer by a specialized tokenizer. An English-centric tokenizer might break it into dear \+ th \+ áir (3 tokens). This phenomenon is known as **Token Fertility**—the average number of tokens required to represent a semantic unit (word).

* **High Fertility \= Low Performance:** If a model needs 3 tokens to say what should take 1, it effectively reduces the context window by 66% and increases inference latency by 300%.8  
* **The Mutation Challenge:** Irish mutations (e.g., *bean* $\\rightarrow$ *bhean* $\\rightarrow$ *mbean*) exacerbate this. If *bhean* is tokenized as b \+ hean, the model must learn that b represents a lenition caused by a preceding preposition or possessive. This wastes parameters on learning orthography rather than semantic reasoning.

Recent analysis of tokenizer fertility across European languages indicates that models like **Qwen 2.5** and **Mistral** often possess more robust vocabularies for non-English scripts compared to older Llama architectures, though Llama 3 has significantly improved this with a 128k vocabulary size.9

### **2.2 Precedents in Irish LLMs: Qomhrá and UCCIX**

Two landmark projects provide the theoretical foundation for this deployment strategy:

1. **UCCIX (University College Cork):** This project utilized Llama 2 (13B) as a base. Crucially, they identified that Llama 2's native 32k vocabulary was insufficient and explicitly expanded it with 10k Irish tokens.11 While effective, vocabulary expansion breaks compatibility with standard inference engines like llama.cpp unless the new tokenizer is perfectly merged and supported upstream. For a streamlined iOS deployment, we must prioritize models that work *without* custom architecture modification.  
2. **Qomhrá (Trinity College Dublin):** This project demonstrated that **Continued Pre-training (CPT)** on mixed English-Irish corpora, followed by instruction tuning, could yield high performance on 8B models without tokenizer modification.12 This validates the "Unsloth approach"—fine-tuning existing weights rather than altering the model structure.

### **2.3 The Low-Resource Data Paradox**

The primary barrier to Irish AI is not the model architecture but the scarcity of high-quality "instruction" data. While raw text exists (CulturaX), structured "Instruction \-\> Response" pairs in Irish are rare. The Qomhrá methodology solves this by using a "Teacher" model (e.g., GPT-4) to synthesize instructions, a strategy we will integrate into the dataset development section.12

## ---

**3\. Unsloth Model Catalog Analysis and Selection**

This section analyzes the specific models available in the Unsloth catalog 1 to identify the optimal candidate for the user's specific constraints: iOS deployment, GGUF compatibility, and Irish language capability.

### **3.1 Candidate A: Llama 3.2 (3B Instruct)**

Classification: The Mobile Native  
Unsloth ID: unsloth/Llama-3.2-3B-Instruct  
Architecture Analysis:  
Llama 3.2 represents a paradigm shift from Meta, explicitly bifurcating their release into "massive" (90B) and "edge" (1B/3B) tiers.15

* **Pros for iOS:**  
  * **Size:** At 3 billion parameters, a 4-bit GGUF (Q4\_K\_M) weighs approximately **1.9 GB**. This is exceptionally safe for iOS memory limits, allowing the model to coexist with heavy Swift UI elements or other on-device ML features (like Vision or Speech).4  
  * **Context:** It inherits the **128,000 token context window** of the Llama 3.1 family. This is transformative for mobile apps, allowing users to load entire PDFs or long conversation histories into context, mitigating the model's smaller knowledge base.  
  * **Unsloth Support:** It is a first-class citizen in the Unsloth ecosystem, with dedicated notebooks and verified GGUF export pipelines.14  
* **Cons for Irish:**  
  * **Training Data:** While Llama 3.2 supports 8 languages officially, Irish is not one of them. Its pre-training data is heavily English-centric. However, the 128k vocabulary (tiktoken-based) is large enough to represent Irish efficiently without excessive fragmentation.10

### **3.2 Candidate B: Qwen 2.5 (3B Instruct)**

Classification: The Multilingual Powerhouse  
Unsloth ID: unsloth/Qwen2.5-3B-Instruct  
Architecture Analysis:  
Qwen 2.5 is widely recognized for its superior performance in coding and mathematics, but its hidden strength is its multilingual capacity.17

* **Pros for Irish:**  
  * **Vocabulary:** Qwen uses a **151,646 token vocabulary**.19 This is significantly larger than Llama 3.2's 128k. A larger vocabulary statistically correlates with better compression of "rare" languages like Irish, reducing fertility rates and increasing inference speed.9  
  * **Pre-training:** Trained on 18 trillion tokens with explicit support for 29+ languages. While Irish is not a primary language, the model's exposure to diverse European syntax makes it more "plastic" and easier to fine-tune on VSO languages.20  
* **Cons for iOS:**  
  * **Ecosystem Friction:** While llama.cpp supports Qwen 2.5, the integration is sometimes less mature than Llama's. Issues with "EOS" (End of Sequence) tokens or chat templates can occasionally cause infinite generation loops in Swift wrappers if not perfectly configured.5

### **3.3 Candidate C: Mistral v0.3 (7B)**

Classification: The Desktop Standard  
Unsloth ID: unsloth/Mistral-7B-Instruct-v0.3  
Architecture Analysis:  
Mistral 7B is a robust workhorse.21

* **Fatal Flaw for this Project:** The 7B size is simply too large for a general-purpose iOS app. A 4-bit quant requires \~4.5 GB of RAM. On a standard iPhone 14/15 (6GB RAM), this leaves \<1.5GB for the OS and App. This guarantees high crash rates due to memory pressure (Jetsam events).22 It is only viable if the app is restricted exclusively to "Pro" model iPhones with 8GB RAM.

### **3.4 Candidate D: Gemma 2 (2B & 9B)**

Classification: The Google Entrant  
Unsloth ID: unsloth/gemma-2-2b-it  
Architecture Analysis:  
Gemma 2 (2B) is highly efficient but has shown fragility in tokenizer support for non-English languages compared to Qwen and Llama.23 Snippets indicate Unsloth supports Gemma 2, but Llama 3.2 3B generally outperforms Gemma 2 2B in instruction following benchmarks.24

### **3.5 Strategic Recommendation**

Primary Selection: Llama 3.2 3B Instruct  
This model represents the optimal intersection of the Venn diagram for this project:

1. **Hardware Viability:** Fits comfortably in iPhone RAM (1.9GB).  
2. **Software Maturity:** Deepest integration with Unsloth and llama.cpp.  
3. **Adaptability:** The 128k context and dense architecture make it highly responsive to fine-tuning.

Secondary Selection (The Backup): Qwen 2.5 3B  
If initial experiments show Llama 3.2 struggles with Irish morphology (e.g., consistently failing to lenite), Qwen 2.5 3B is the immediate fallback due to its larger vocabulary and multilingual pre-training.

## ---

**4\. Dataset Engineering: Building the "Corpas Gaeilge"**

A model is only as good as its data. For a low-resource language like Irish, you cannot rely on the "knowledge" already inside the base model. You must inject it. This requires a three-tiered data strategy: **Continued Pre-training (CPT)**, **Translation Tuning**, and **Instruction Tuning**.

### **4.1 Tier 1: The Raw Corpus (Syntax & Vocabulary)**

Before teaching the model *how* to answer questions, you must teach it *what* Irish looks like. This is done via Continued Pre-training on raw text.  
**Key Dataset: CulturaX (Irish Subset)**

* **Source:** 25 The CulturaX dataset is a massive, cleaned version of the mC4 and OSCAR crawls. It contains an Irish (ga) subset.  
* **Action:** Download the Irish subset. Apply aggressive heuristic filtering:  
  * **Length Filtering:** Discard documents shorter than 200 characters (often navigational clutter).  
  * **Language ID Verification:** Use fastText or similar to verify the text is actually Irish (web crawls often mislabel Welsh or Scots Gaelic as Irish).  
  * **Deduplication:** Remove repeated paragraphs to prevent the model from memorizing loops.

**Key Dataset: ParaCrawl**

* **Source:** 26 Parallel English-Irish text crawled from the web.  
* **Warning:** ParaCrawl is notoriously noisy. It often contains "machine translationese"—bad Irish generated by older Google Translate systems.  
* **Usage:** Use only the highest scored pairs (e.g., Bicleaner score \> 0.7) to teach the model alignment between English concepts and Irish terms.

### **4.2 Tier 2: Domain-Specific Knowledge**

To make the model useful (not just fluent), it needs domain data.  
**Key Dataset: gaHealth**

* **Source:** 28 A specialized English-Irish bilingual corpus focused on healthcare.  
* **Relevance:** This is high-quality, human-verified text. Fine-tuning on this allows the iOS app to serve a specific utility (e.g., a medical translator or health assistant), which is a high-value use case for an edge app.

**Key Dataset: IrishQA & IRLBench**

* **Source:** 30 Question-answering datasets. IRLBench is derived from Leaving Cert exams, providing a "gold standard" for reasoning in Irish across subjects like Science and Business.

### **4.3 Tier 3: The Synthetic Instruction Set (The Teacher Method)**

To make the model act like an assistant (chat), you need "Instruction" data. Since 50k+ Irish instruction pairs do not exist publicly, you must synthesize them.  
The "Teacher" Pipeline (Recommended by Qomhrá 12):

1. **Source:** Select a high-quality English instruction dataset like **OpenHermes-2.5** or **Alpaca-Cleaned**.32  
2. **The Translator:** Use a frontier model (GPT-4o, Claude 3.5 Sonnet, or Gemini 1.5 Pro) via API.  
3. **The Prompt:** Do not ask for a direct translation. Ask for **Localization**.  
   * *Bad Prompt:* "Translate this to Irish."  
   * *Good Prompt:* "You are an expert Irish translator. Translate the following instruction and response to Irish. Ensure the tone is natural and conversational. If the instruction references US-specific concepts (e.g., 'dollars', 'New York'), adapt them to Irish contexts ('Euro', 'Dublin') where appropriate."  
4. **Format:** Save the output in **ChatML** format JSONL files.

Target Data Structure (ChatML):  
Unsloth favors ChatML for Llama 3.2.

JSON

{  
  "messages": \[  
    {"role": "system", "content": "Is cúntóir intleachta saorga thú."},  
    {"role": "user", "content": "Mínigh teoiric na coibhneasta dom."},  
    {"role": "assistant", "content": "Is teoiric fhisice í teoiric na coibhneasta..."}  
  \]  
}

## ---

**5\. The Unsloth Fine-Tuning Pipeline**

This section details the specific technical implementation of the fine-tuning process, leveraging Unsloth's unique optimizations.

### **5.1 Environment Configuration**

The training should be performed in a CUDA-accelerated environment (e.g., Google Colab Pro, Kaggle, or a local Linux box with an NVIDIA GPU).  
**Dependencies:**

Bash

pip install unsloth  
pip install \--no-deps xformers "trl\<0.9.0" peft accelerate bitsandbytes

### **5.2 Phase 1: Continued Pre-training (CPT)**

Before instruction tuning, we perform CPT to adapt the model to the probability distribution of Irish.  
**Unsloth Setup:**

Python

from unsloth import FastLanguageModel  
import torch

max\_seq\_length \= 8192 \# Llama 3.2 supports 128k, but 8k is sufficient for training and saves VRAM  
dtype \= None \# Auto detection  
load\_in\_4bit \= True \# 4-bit quantization is essential for VRAM efficiency

model, tokenizer \= FastLanguageModel.from\_pretrained(  
    model\_name \= "unsloth/Llama-3.2-3B-Instruct-bnb-4bit",  
    max\_seq\_length \= max\_seq\_length,  
    dtype \= dtype,  
    load\_in\_4bit \= load\_in\_4bit,  
)

\# Add LoRA adapters for CPT  
model \= FastLanguageModel.get\_peft\_model(  
    model,  
    r \= 64, \# Higher rank for language adaptation  
    target\_modules \= \["q\_proj", "k\_proj", "v\_proj", "o\_proj",  
                      "gate\_proj", "up\_proj", "down\_proj"\],  
    lora\_alpha \= 128,  
    lora\_dropout \= 0, \# Set to 0 for Unsloth optimization  
    bias \= "none",  
    use\_gradient\_checkpointing \= "unsloth",  
    random\_state \= 3407,  
    use\_rslora \= False,  
    loftq\_config \= None,  
)

**Training Strategy:**

* **Dataset:** CulturaX (Irish subset).  
* **Objective:** Causal Language Modeling (CLM).  
* **Hyperparameters:** Low learning rate (2e-5), 1 epoch. This "warms up" the model to Irish syntax without overwriting its reasoning capabilities.33

### **5.3 Phase 2: Supervised Fine-Tuning (SFT)**

This phase turns the "Irish-aware" model into a "Chatbot."  
**Config Changes:**

* **Dataset:** The Synthetic Instruction dataset \+ gaHealth/IrishQA.  
* **Format:** ChatML. Use Unsloth's standardize\_sharegpt or apply\_chat\_template functions to format the JSONL data.34  
* **Hyperparameters:**  
  * learning\_rate: 2e-4 (Standard SFT rate).  
  * batch\_size: 2 (with gradient accumulation to simulate 16).  
  * max\_seq\_length: 2048 (Instructions rarely exceed this).  
  * packing: True (Speeds up training by combining short sequences).

### **5.4 The Critical Step: Dynamic 2.0 GGUF Export**

For iOS deployment, the model **must** be quantized. Standard quantization often destroys the performance of SLMs (Small Language Models). Unsloth's **Dynamic 2.0 GGUF** export uses a calibration dataset to determine which layers are sensitive to quantization and preserves them at higher precision.3  
Why this matters for Irish:  
Irish grammar relies on subtle mutations (e.g., bhean vs bean). If the layers responsible for detecting these mutations are aggressively quantized, the model will make basic grammatical errors. Dynamic 2.0 mitigates this.  
**Export Code:**

Python

\# Save to GGUF using Unsloth's optimized engine  
model.save\_pretrained\_gguf(  
    "Llama-3.2-3B-Irish-Instruct",   
    tokenizer,   
    quantization\_method \= "q4\_k\_m"   
)

* **q4\_k\_m:** This is the specific quantization format recommended for the 3B model. It balances size (\~1.9GB) with perplexity retention. Avoid q4\_0 (too aggressive) or q8\_0 (too large).

## ---

**6\. iOS Integration: The AnyLanguageModel Implementation**

The final leg of the pipeline is deploying the .gguf file to an iPhone application using Swift.

### **6.1 Understanding AnyLanguageModel Architecture**

The AnyLanguageModel library abstracts the underlying inference engine.

* **CoreML:** Uses the Apple Neural Engine (ANE). Fast, but requires .mlpackage conversion which is complex and often supports fewer model architectures.  
* **Llama (GGUF):** Uses llama.cpp. Runs on the CPU and GPU (via Metal). This is the preferred path for Unsloth models because Unsloth exports directly to GGUF.

Dependency Configuration:  
In your Xcode project's Package.swift, you must enable the Llama trait to pull in the C++ bindings.6

Swift

dependencies: \[  
   .package(  
        url: "https://github.com/mattt/AnyLanguageModel.git",  
        from: "0.5.0",  
        traits: \["Llama"\] // CRITICAL: Enables GGUF support  
    )  
\]

### **6.2 Managing Assets in Xcode**

1. **Import:** Drag the Llama-3.2-3B-Irish-Instruct.Q4\_K\_M.gguf file into your Xcode project.  
2. **Target Membership:** Ensure the file is checked for your App Target so it is bundled into the .ipa.  
3. **Memory Warning:** A 1.9GB file will increase your app download size significantly. For production apps, you should implement an **On-Demand Resource** pattern or a downloader that fetches the model from a server (e.g., Hugging Face) on first launch, rather than bundling it.

### **6.3 Swift Implementation Code**

The following Swift code demonstrates how to load the model and manage the inference session using AnyLanguageModel.

Swift

import SwiftUI  
import AnyLanguageModel

class ModelController: ObservableObject {  
    @Published var output: String \= ""  
    private var session: LanguageModelSession?

    init() {  
        setupModel()  
    }

    func setupModel() {  
        // 1\. Locate the GGUF file in the bundle  
        guard let modelPath \= Bundle.main.path(forResource: "Llama-3.2-3B-Irish-Instruct.Q4\_K\_M", ofType: "gguf") else {  
            print("Error: Model file not found")  
            return  
        }

        // 2\. Initialize the Llama backend  
        // Note: This does not load the full model into RAM yet.  
        let model \= LlamaLanguageModel(modelPath: modelPath)

        // 3\. Create the session  
        // This is where memory allocation occurs.   
        self.session \= LanguageModelSession(model: model)  
    }

    func generateResponse(prompt: String) async {  
        guard let session \= session else { return }  
          
        // 4\. Run Inference  
        do {  
            let response \= try await session.respond(to: prompt)  
            DispatchQueue.main.async {  
                self.output \= response.content  
            }  
        } catch {  
            print("Inference error: \\(error)")  
        }  
    }  
}

### **6.4 Performance Tuning on iOS**

* **Metal Optimization:** llama.cpp (and thus AnyLanguageModel) automatically uses Apple Metal for hardware acceleration. However, on a 3B model, the CPU is often surprisingly competitive and uses less battery.  
* **Context Management:** While the model supports 128k context, allocating a 128k KV cache on an iPhone will crash the app (OOM). In the AnyLanguageModel configuration, limit the context to **4096** or **8192** tokens for safety unless running on a Pro Max device with 8GB RAM.

## ---

**7\. Evaluation, Testing, and Future Roadmap**

### **7.1 Benchmarking the Model**

Before release, the model must be validated not just for "vibes" but for metrics.

* **IRLBench:** Use the Irish Leaving Cert benchmark 30 to test if the model can reason in Irish.  
* **Translation Accuracy:** Use a held-out set of gaHealth and calculate BLEU/COMET scores.  
* **Grammar Check:** Use the **Irish-BLiMP** 35 dataset. This contains minimal pairs of sentences (one grammatically correct, one incorrect). The model should assign a higher probability (lower perplexity) to the correct sentence. If it fails this, it has not learned the grammar rules (mutations) and needs more CPT.

### **7.2 The Update Loop**

Language models are not static.

1. **Feedback Loop:** Implement a "thumbs up/down" in your iOS app.  
2. **DPO (Direct Preference Optimization):** Use this user feedback to create a Preference Dataset.  
3. **Refinement:** Use Unsloth to run DPO training on the model. This is computationally cheap and aligns the model further with user expectations.

### **7.3 Conclusion**

The pathway to high-quality Irish language AI on the iPhone is clear. By selecting **Llama 3.2 3B Instruct** for its architectural efficiency, utilizing **Unsloth** for 4-bit quantization-aware fine-tuning, and leveraging **AnyLanguageModel** with the Llama trait for inference, we can bypass the resource limitations that typically marginalize indigenous languages. This architecture provides a robust, scalable, and high-performance foundation for the next generation of *Gaeilge* technology.

| Component | Selection | Reasoning |
| :---- | :---- | :---- |
| **Base Model** | Llama 3.2 3B Instruct | Optimal size (1.9GB), 128k context, Unsloth native. |
| **Training** | Unsloth (LoRA) | 2x faster, 70% less VRAM, Dynamic GGUF export. |
| **Data Format** | ChatML | Supports multi-turn conversation, maps to Llama 3 tokenizer. |
| **Quantization** | GGUF Q4\_K\_M | Best balance of perplexity vs. memory for SLMs. |
| **iOS Backend** | AnyLanguageModel (Llama) | Swift-native wrapper for llama.cpp, enables GGUF loading. |

This report serves as the blueprint for execution. The technology is mature, the data sources are identified, and the pipeline is validated. The next step is implementation.

#### **Works cited**

1. Unsloth Notebooks | Unsloth Documentation, accessed December 15, 2025, [https://docs.unsloth.ai/get-started/unsloth-notebooks](https://docs.unsloth.ai/get-started/unsloth-notebooks)  
2. unslothai/unsloth: Fine-tuning & Reinforcement Learning for LLMs. Train OpenAI gpt-oss, DeepSeek-R1, Qwen3, Gemma 3, TTS 2x faster with 70% less VRAM. \- GitHub, accessed December 15, 2025, [https://github.com/unslothai/unsloth](https://github.com/unslothai/unsloth)  
3. Unsloth Dynamic 2.0 GGUFs, accessed December 15, 2025, [https://docs.unsloth.ai/basics/unsloth-dynamic-2.0-ggufs](https://docs.unsloth.ai/basics/unsloth-dynamic-2.0-ggufs)  
4. Llama 3 8B vs Mistral 7B: Small LLM Pricing Considerations | Vantage, accessed December 15, 2025, [https://www.vantage.sh/blog/best-small-llm-llama-3-8b-vs-mistral-7b-cost](https://www.vantage.sh/blog/best-small-llm-llama-3-8b-vs-mistral-7b-cost)  
5. Saving to GGUF | Unsloth Documentation, accessed December 15, 2025, [https://docs.unsloth.ai/basics/inference-and-deployment/saving-to-gguf](https://docs.unsloth.ai/basics/inference-and-deployment/saving-to-gguf)  
6. mattt/AnyLanguageModel: An API-compatible, drop-in ... \- GitHub, accessed December 15, 2025, [https://github.com/mattt/AnyLanguageModel](https://github.com/mattt/AnyLanguageModel)  
7. Swift Transformers Reaches 1.0 – and Looks to the Future \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/blog/swift-transformers](https://huggingface.co/blog/swift-transformers)  
8. Tokenizer Evaluation on European Languages | Occiglot, accessed December 15, 2025, [https://occiglot.eu/posts/eu\_tokenizer\_perfomance/](https://occiglot.eu/posts/eu_tokenizer_perfomance/)  
9. Understanding Token Fertility: Why It Matters for Multilingual LLMs | by Biswajit | Medium, accessed December 15, 2025, [https://medium.com/@biswanai92/understanding-token-fertility-why-it-matters-for-multilingual-llms-38c0b9f20da2](https://medium.com/@biswanai92/understanding-token-fertility-why-it-matters-for-multilingual-llms-38c0b9f20da2)  
10. Krikri: Advancing Open Large Language Models for Greek \- ACL Anthology, accessed December 15, 2025, [https://aclanthology.org/2025.findings-emnlp.268.pdf](https://aclanthology.org/2025.findings-emnlp.268.pdf)  
11. UCCIX: Irish-eXcellence Large Language Model \- GitHub, accessed December 15, 2025, [https://github.com/ReML-AI/UCCIX](https://github.com/ReML-AI/UCCIX)  
12. Qomhrá: A Bilingual Irish-English Large Language Model \- arXiv, accessed December 15, 2025, [https://arxiv.org/html/2510.17652v1](https://arxiv.org/html/2510.17652v1)  
13. Qomhra: A Bilingual Irish-English Large Language Model \- ResearchGate, accessed December 15, 2025, [https://www.researchgate.net/publication/396715967\_Qomhra\_A\_Bilingual\_Irish-English\_Large\_Language\_Model](https://www.researchgate.net/publication/396715967_Qomhra_A_Bilingual_Irish-English_Large_Language_Model)  
14. Unsloth Model Catalog, accessed December 15, 2025, [https://docs.unsloth.ai/get-started/unsloth-model-catalog](https://docs.unsloth.ai/get-started/unsloth-model-catalog)  
15. unsloth/Llama-3.2-3B-Instruct \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/unsloth/Llama-3.2-3B-Instruct](https://huggingface.co/unsloth/Llama-3.2-3B-Instruct)  
16. Meta's Llama 3.2 models are now available for fine-tuning in Amazon Bedrock \- AWS, accessed December 15, 2025, [https://aws.amazon.com/about-aws/whats-new/2025/03/metas-llama-3-2-models-fine-tuning-amazon-bedrock/](https://aws.amazon.com/about-aws/whats-new/2025/03/metas-llama-3-2-models-fine-tuning-amazon-bedrock/)  
17. Qwen/Qwen2.5-72B-Instruct \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/Qwen/Qwen2.5-72B-Instruct](https://huggingface.co/Qwen/Qwen2.5-72B-Instruct)  
18. Qwen2.5: A Party of Foundation Models\! | Qwen, accessed December 15, 2025, [https://qwenlm.github.io/blog/qwen2.5/](https://qwenlm.github.io/blog/qwen2.5/)  
19. Key Concepts \- Qwen \- Read the Docs, accessed December 15, 2025, [https://qwen.readthedocs.io/en/v3.0/getting\_started/concepts.html](https://qwen.readthedocs.io/en/v3.0/getting_started/concepts.html)  
20. \[2412.15115\] Qwen2.5 Technical Report \- arXiv, accessed December 15, 2025, [https://arxiv.org/abs/2412.15115](https://arxiv.org/abs/2412.15115)  
21. Mistral 7B Instruct V0.3 · Models \- Dataloop, accessed December 15, 2025, [https://dataloop.ai/library/model/mistralai\_mistral-7b-instruct-v03/](https://dataloop.ai/library/model/mistralai_mistral-7b-instruct-v03/)  
22. mistralai/Mistral-7B-Instruct-v0.3 \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)  
23. Gemma 2 Tokenizer Overview \- Emergent Mind, accessed December 15, 2025, [https://www.emergentmind.com/topics/gemma-2-tokenizer](https://www.emergentmind.com/topics/gemma-2-tokenizer)  
24. llama 3.2 3B is amazing : r/LocalLLaMA \- Reddit, accessed December 15, 2025, [https://www.reddit.com/r/LocalLLaMA/comments/1hl1tso/llama\_32\_3b\_is\_amazing/](https://www.reddit.com/r/LocalLLaMA/comments/1hl1tso/llama_32_3b_is_amazing/)  
25. Rephrasing natural text data with different languages and quality levels for Large Language Model pre-training \- GitHub, accessed December 15, 2025, [https://raw.githubusercontent.com/mlresearch/v262/main/assets/pieler24a/pieler24a.pdf](https://raw.githubusercontent.com/mlresearch/v262/main/assets/pieler24a/pieler24a.pdf)  
26. Datasets \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/datasets?language=language:mt\&p=1\&sort=trending](https://huggingface.co/datasets?language=language:mt&p=1&sort=trending)  
27. Experiments in Filtering Training Sets for Machine Translation \- ACL Anthology, accessed December 15, 2025, [https://aclanthology.org/2023.nodalida-1.58.pdf](https://aclanthology.org/2023.nodalida-1.58.pdf)  
28. \[2403.03575\] gaHealth: An English-Irish Bilingual Corpus of Health Data \- arXiv, accessed December 15, 2025, [https://arxiv.org/abs/2403.03575](https://arxiv.org/abs/2403.03575)  
29. Is Neural Machine Translation viable for Low-Resource Languages? An experimental study of the Irish Language, accessed December 15, 2025, [https://conservancy.umn.edu/bitstreams/96d983aa-8039-4ccf-a68b-4b3721ada3f3/download](https://conservancy.umn.edu/bitstreams/96d983aa-8039-4ccf-a68b-4b3721ada3f3/download)  
30. (PDF) IRLBench: A Multi-modal, Culturally Grounded, Parallel Irish-English Benchmark for Open-Ended LLM Reasoning Evaluation \- ResearchGate, accessed December 15, 2025, [https://www.researchgate.net/publication/391910782\_IRLBench\_A\_Multi-modal\_Culturally\_Grounded\_Parallel\_Irish-English\_Benchmark\_for\_Open-Ended\_LLM\_Reasoning\_Evaluation](https://www.researchgate.net/publication/391910782_IRLBench_A_Multi-modal_Culturally_Grounded_Parallel_Irish-English_Benchmark_for_Open-Ended_LLM_Reasoning_Evaluation)  
31. Daily Papers \- Hugging Face, accessed December 15, 2025, [https://huggingface.co/papers?q=continued%20fraction](https://huggingface.co/papers?q=continued+fraction)  
32. Unsloth: A Fine-Tuning Guide for Developers \- Beam Cloud, accessed December 15, 2025, [https://www.beam.cloud/blog/unsloth-fine-tuning](https://www.beam.cloud/blog/unsloth-fine-tuning)  
33. Fine-tuning LLMs Guide | Unsloth Documentation, accessed December 15, 2025, [https://docs.unsloth.ai/get-started/fine-tuning-llms-guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide)  
34. Datasets Guide | Unsloth Documentation, accessed December 15, 2025, [https://docs.unsloth.ai/get-started/fine-tuning-llms-guide/datasets-guide](https://docs.unsloth.ai/get-started/fine-tuning-llms-guide/datasets-guide)  
35. Irish-BLiMP: A Linguistic Benchmark for Evaluating Human and Language Model Performance in a Low-Resource Setting \- ChatPaper, accessed December 15, 2025, [https://chatpaper.com/paper/203147](https://chatpaper.com/paper/203147)
---


## Original Sources

- `docs/meaisínfhoghlaim/training/KCG_SUMMARY.md`
- `docs/meaisínfhoghlaim/training/open-instruct/AGENTS.md`
- `docs/meaisínfhoghlaim/training/open-instruct/CLAUDE.md`
- `docs/meaisínfhoghlaim/training/open-instruct/decontamination/README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/ai2_internal.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/dataset_transformation.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/dpo.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/finetune.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/grpo.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/online_dpo.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/ppo.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/rejection_sampling.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/reward_modeling.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/synthetic_preference_dataset.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/algorithms/trained_model_location.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/data/preference-data.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/get_started/ai2_internal_setup.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/get_started/installation.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/index.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/olmo2.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/safety-eval/safety.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/safety.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/tulu1_tulu2.md`
- `docs/meaisínfhoghlaim/training/open-instruct/docs/tulu3.md`
- `docs/meaisínfhoghlaim/training/open-instruct/human_eval/README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/scripts/data/azure_batch/README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/scripts/data/filtering_and_updates/README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/scripts/data/filtering_and_updates/TEST_README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/scripts/persona_driven_data_gen/README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/scripts/README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/scripts/synth_pref/README.md`
- `docs/meaisínfhoghlaim/training/open-instruct/scripts/train/olmo3/README.md`
- `docs/meaisínfhoghlaim/training/phone/docs/Federated AI Marketplace on iPhone.md`
- `docs/meaisínfhoghlaim/training/phone/docs/Fine-tuning VLMs for iOS HTR.md`
- `docs/meaisínfhoghlaim/training/phone/docs/How to Run and Deploy LLMs on your iOS or Android Phone _ Unsloth Documentation.md`
- `docs/meaisínfhoghlaim/training/phone/docs/Irish LLM for iPhone Development.md`
