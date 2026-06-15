---
title: 'LLM Fine-Tuning — Unsloth, TRL, and LoRA/QLoRA: Reference & Skill Card'
domain: 'ai_ml'
status: 'stable'
description: 'Complete LLM fine-tuning reference — Unsloth (efficient fine-tuning with 70% VRAM reduction, 2x speedup), TRL (Supervised Fine-Tuning, DPO, GRPO for preference optimization), and LoRA/QLoRA (parameter-efficient fine-tuning with 99% parameter reduction, 4-bit quantization). Plus skill card for each with KCG context, integration with our stack (Dagster meaisínfhoghlaim assets, GGUF export, llama-swap serving, MacBook M4 48GB training).'
read_when:
  - fine-tuning a model
  - looking for documentation on this topic
  - choosing between SFT/DPO/GRPO
  - choosing between Unsloth/TRL/PEFT
updated: 2026-06-13
supersedes:
  - docs/ai-ml/unsloth.md
  - docs/ai-ml/trl.md
  - docs/ai-ml/lora-qlora.md
truth: sole
ccc_query_hints:
  - unsloth efficient llm fine-tuning
  - trl transformer reinforcement learning
  - trl dpo grpo preference optimization
  - lora qlora parameter efficient fine-tuning
  - peft huggingface adapter
---

# LLM Fine-Tuning — Unsloth, TRL, and LoRA/QLoRA: Reference & Skill Card

> **Merged from 3 canonical sources**:
> - `unsloth.md` (53 lines) — efficient fine-tuning library
> - `trl.md` (53 lines) — reinforcement learning fine-tuning
> - `lora-qlora.md` (53 lines) — parameter-efficient fine-tuning techniques
>
> All three cover complementary aspects of the same workflow: Unsloth provides the runtime, TRL provides the training algorithms (SFT, DPO, GRPO), and LoRA/QLoRA is the parameter-efficient technique that makes it all feasible on consumer hardware.

---

## Unsloth — Efficient LLM Fine-Tuning

### Overview

Unsloth is an open-source library for efficient LLM fine-tuning that achieves 70% VRAM reduction and 2x training speed compared to standard implementations. It supports LoRA, QLoRA, and full fine-tuning across Llama, Mistral, Gemma, Qwen, and other model families. Designed for consumer hardware — fine-tune 7B models on a single GPU.

### Why This Matters for Kings' College Galway

The project trains domain-specific models for Celtic language processing and educational content generation. Unsloth makes this feasible on the MacBook M4's 48 GB unified memory: fine-tuning a 7B Irish-language model with LoRA on curriculum-aligned text requires under 20 GB VRAM with Unsloth's optimisations, vs 40+ GB with standard libraries. The Dagster `model_conversion` job uses Unsloth for fine-tuning runs, and the fine-tuned GGUFs are served through llama-swap on the same hardware.

### Key Features

- **70% VRAM reduction** — Fine-tune 7B models on consumer GPUs
- **2x speedup** — Flash Attention and kernel optimisations
- **LoRA/QLoRA** — Parameter-efficient fine-tuning with 4-bit quantization
- **Multi-model** — Llama, Mistral, Gemma, Qwen, Phi, and more
- **GGUF export** — Export fine tuned models directly to GGUF format

### Installation

```bash
uv add unsloth
```

### Integration with Our Stack

Unsloth fine-tuning runs as Dagster assets in the `meaisínfhoghlaim/` stream. Fine-tuned models are exported to GGUF and served via llama-swap on the MacBook M4. The `model_conversion` Dagster job orchestrates the full HF → fine-tune → GGUF pipeline.

### Upstream

- **Repository**: <https://github.com/unslothai/unsloth>
- **Documentation**: <https://docs.unsloth.ai>
- **Latest**: v2024.12+ — multilingual support, flash attention v3, 4-bit optimisations

### Screenshot

Unsloth is a programmatic library. Training progress appears in terminal output with loss curves, token throughput, and VRAM usage. The `.agents/skills/unsloth/` directory documents fine-tuning workflows. Fine-tuned model quality is tracked in MLflow experiments with RAGAS evaluation scores.

---

## TRL — Transformer Reinforcement Learning (HuggingFace)

### Overview

TRL (Transformer Reinforcement Learning) is a HuggingFace library for fine-tuning language models with reinforcement learning. It supports SFT (Supervised Fine-Tuning), DPO (Direct Preference Optimization), GRPO (Group Relative Policy Optimization), and reward modeling — enabling alignment training on top of base models.

### Why This Matters for Kings' College Galway

Curriculum-aligned content requires models that not only generate factually correct text but also follow pedagogical best practices — appropriate difficulty level, encouraging tone, correct use of Irish/English bilingual transitions, and academic-rigour-appropriate hedging. TRL's DPO training uses RAGAS evaluation scores as preference signals: when the BAML extraction produces a high-faithfulness output, it serves as a "chosen" example; when it produces a hallucinated prerequisite, it serves as a "rejected" example. This preference optimisation directly improves extraction quality over successive fine-tuning runs.

### Key Features

- **SFT** — Supervised fine-tuning on curriculum-aligned datasets
- **DPO** — Direct preference optimisation using RAGAS scores as signals
- **GRPO** — Group relative policy optimisation for batch preference learning
- **Reward modeling** — Train reward models from human preference data
- **HuggingFace integration** — Seamless with `transformers`, `peft`, `datasets`

### Installation

```bash
uv add trl
```

### Integration with Our Stack

TRL training scripts live in `meaisínfhoghlaim/scripts/`. Training data comes from dlt-curated curriculum datasets. Fine-tuned models are exported to GGUF via Unsloth and served through llama-swap. MLflow tracks training metrics and model versions.

### Upstream

- **Repository**: <https://github.com/huggingface/trl>
- **Documentation**: <https://huggingface.co/docs/trl>
- **Latest**: v0.15.x (2025) — GRPO support, DPO improvements, HuggingFace Jobs integration

### Screenshot

TRL is a programmatic library. Training runs are logged to MLflow showing loss curves, reward scores, and preference accuracy. The HuggingFace model hub provides dataset and model versioning. Training scripts are version-controlled in the Forgejo repository.

---

## LoRA / QLoRA — Parameter-Efficient Fine-Tuning

### Overview

LoRA (Low-Rank Adaptation) and QLoRA (Quantized LoRA) are parameter-efficient fine-tuning techniques that reduce the number of trainable parameters by 99%+ while maintaining model quality. LoRA adds small trainable rank-decomposition matrices to attention layers; QLoRA adds 4-bit quantization on top. Both are implemented via HuggingFace's PEFT library.

### Why This Matters for Kings' College Galway

The MacBook M4's 48 GB unified memory is the primary training hardware. Full fine-tuning of a 7B model requires ~55 GB — impossible on 48 GB. LoRA fine-tuning requires ~16 GB — comfortable. QLoRA reduces this to ~8 GB — room to spare for batch processing. This hardware constraint directly determines the training strategy: all fine-tuned models in the project use LoRA/QLoRA adapters merged into the base model weights, producing GGUFs that are computationally identical to full fine-tunes but trainable on consumer hardware.

### Key Features

- **99% parameter reduction** — Train <1% of model parameters
- **QLoRA 4-bit** — 4-bit NormalFloat quantization for further memory reduction
- **Adapter merging** — Merge LoRA weights into base model for inference
- **PEFT integration** — HuggingFace's standard API via `peft` library
- **Multi-model support** — Llama, Qwen, Gemma, Mistral, and more

### Installation

```bash
uv add peft bitsandbytes
```

### Integration with Our Stack

LoRA/QLoRA is the default fine-tuning method in Unsloth and TRL training scripts. Adapters are trained on the MacBook M4 and merged into GGUF models for llama-swap serving. The `meaisínfhoghlaim/scripts/convert_hf_to_gguf.sh` script handles adapter merging during model conversion.

### Upstream

- **LoRA paper**: <https://arxiv.org/abs/2106.09685>
- **QLoRA paper**: <https://arxiv.org/abs/2305.14314>
- **PEFT library**: <https://github.com/huggingface/peft>

### Screenshot

LoRA/QLoRA are techniques, not standalone tools. Training metrics appear in Unsloth/TRL output showing adapter size (typically 10-50 MB for a 7B model), training loss, and VRAM usage. The `peft` library provides adapter loading/saving APIs. Merged models are functionally identical to full fine-tunes at inference time.

---

## From: docs/04-ai-ml/MODEL_FINETUNING.md (leftover)

> **Source:** `docs/04-ai-ml/MODEL_FINETUNING.md` (623 lines)
> **Original title:** Model Fine-Tuning Strategy for Cryptocurrency Domain
> **Reason for inclusion:** This is the historical strategy document that informed the merged Unsloth/TRL/LoRA skill card above. The crypto-specific use case (DeFi entity extraction, risk analysis, market analysis) demonstrates how fine-tuning workflows are applied in practice. The data prep pipeline, BAML schema integration, MLflow tracking, and LiteLLM serving patterns are useful as concrete examples.

# Model Fine-Tuning Strategy for Cryptocurrency Domain

## Overview

This document outlines the strategy for fine-tuning language models for cryptocurrency and DeFi-specific analysis, adapted from patterns in the gaeilge research for domain-specific model adaptation.

## Fine-Tuning Objectives

### Primary Goals

1. **Domain Vocabulary**: Understand crypto-specific terminology (DeFi, TVL, APY, impermanent loss, yield farming, etc.)
2. **Entity Recognition**: Identify tokens, protocols, exchanges, wallet addresses accurately
3. **Relationship Extraction**: Extract relationships between DeFi entities
4. **Risk Assessment**: Evaluate and articulate protocol risks
5. **Market Analysis**: Generate structured market analysis outputs

### Model Selection Matrix

| Use Case | Base Model | Fine-Tuning Approach | Output |
|----------|------------|---------------------|--------|
| Entity extraction | Qwen2.5-7B | LoRA on crypto NER data | BAML structured output |
| Document analysis | Llama 3.1 70B | Full fine-tune (expensive) | Long-form analysis |
| Chat/reasoning | Claude/GPT-4 | Few-shot prompting | Natural language |
| Code generation | CodeLlama | LoRA on Solidity/Vyper | Smart contract code |
| Risk scoring | Mistral 7B | LoRA on audit data | Risk classifications |

## Data Preparation

### Training Data Sources

```
┌─────────────────────────────────────────────────────────────┐
│                    Training Data Pipeline                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Raw Sources                Processing              Output   │
│  ┌──────────┐              ┌──────────┐          ┌────────┐ │
│  │Whitepapers│───Extract──>│Clean &   │──Format─>│JSONL   │ │
│  │Audits    │              │Chunk     │          │Dataset │ │
│  │Research  │              │          │          │        │ │
│  └──────────┘              └──────────┘          └────────┘ │
│                                                              │
│  ┌──────────┐              ┌──────────┐          ┌────────┐ │
│  │On-chain  │───Transform─>│Annotate  │──Format─>│JSONL   │ │
│  │Data      │              │Entities  │          │Dataset │ │
│  │Events    │              │          │          │        │ │
│  └──────────┘              └──────────┘          └────────┘ │
│                                                              │
│  ┌──────────┐              ┌──────────┐          ┌────────┐ │
│  │Existing  │───Filter────>│Quality   │──Format─>│JSONL   │ │
│  │QA Pairs  │              │Check     │          │Dataset │ │
│  │Forums    │              │          │          │        │ │
│  └──────────┘              └──────────┘          └────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Dataset Categories

#### 1. Entity Extraction Dataset

```json
{
  "instruction": "Extract all cryptocurrency entities from the following text.",
  "input": "Ethena's USDe stablecoin reached $2.5B TVL on Ethereum mainnet. The protocol uses sUSDe for staking rewards distributed to holders.",
  "output": {
    "tokens": [
      {"symbol": "USDe", "type": "stablecoin", "protocol": "Ethena"},
      {"symbol": "sUSDe", "type": "staking_token", "protocol": "Ethena"}
    ],
    "protocols": [
      {"name": "Ethena", "category": "stablecoin"}
    ],
    "metrics": [
      {"type": "TVL", "value": "2.5B", "unit": "USD", "chain": "Ethereum"}
    ]
  }
}
```

#### 2. Risk Analysis Dataset

```json
{
  "instruction": "Analyze the risks described in this audit finding.",
  "input": "Finding: The collateral ratio check in liquidate() can be bypassed by flashloan attacks. An attacker can manipulate the oracle price within a single transaction.",
  "output": {
    "risk_category": "smart_contract",
    "severity": "critical",
    "attack_vector": "flashloan",
    "affected_component": "liquidation_mechanism",
    "potential_impact": "loss_of_collateral",
    "mitigation_suggestions": [
      "Implement TWAP oracle",
      "Add flashloan protection",
      "Multi-block price validation"
    ]
  }
}
```

#### 3. Market Analysis Dataset

```json
{
  "instruction": "Generate a market analysis for the given token metrics.",
  "input": {
    "token": "ETH",
    "price_24h_change": -5.2,
    "volume_24h": 15000000000,
    "funding_rate": -0.02,
    "open_interest": 8500000000
  },
  "output": {
    "sentiment": "bearish",
    "key_observations": [
      "Negative funding suggests short pressure",
      "High volume indicates conviction",
      "Open interest elevated despite price drop"
    ],
    "outlook": "Short-term bearish with potential for short squeeze if funding becomes deeply negative",
    "risk_factors": ["high_volatility", "liquidation_cascade_risk"]
  }
}
```

### Data Quality Pipeline

```python
from typing import List, Dict
import json

class CryptoTrainingDataPipeline:
    """Pipeline for preparing crypto fine-tuning data"""

    def __init__(self):
        self.quality_thresholds = {
            "min_tokens": 50,
            "max_tokens": 4096,
            "required_fields": ["instruction", "input", "output"],
            "crypto_keyword_density": 0.05  # 5% crypto terms
        }

        self.crypto_keywords = self._load_crypto_vocabulary()

    def process_document(self, doc: Dict) -> List[Dict]:
        """Process a document into training examples"""

        examples = []

        # Entity extraction examples
        entities = self._extract_entities(doc["content"])
        if entities:
            examples.append({
                "instruction": "Extract all cryptocurrency entities from the text.",
                "input": doc["content"][:2000],  # Truncate
                "output": json.dumps(entities)
            })

        # Risk analysis examples (for audits)
        if doc.get("doc_type") == "audit":
            findings = self._extract_findings(doc["content"])
            for finding in findings:
                examples.append({
                    "instruction": "Analyze this audit finding and categorize the risk.",
                    "input": finding["text"],
                    "output": json.dumps(finding["analysis"])
                })

        return examples

    def validate_example(self, example: Dict) -> bool:
        """Validate a training example meets quality thresholds"""

        # Check required fields
        for field in self.quality_thresholds["required_fields"]:
            if field not in example:
                return False

        # Check token counts
        total_tokens = self._count_tokens(str(example))
        if not (self.quality_thresholds["min_tokens"] <=
                total_tokens <=
                self.quality_thresholds["max_tokens"]):
            return False

        # Check crypto keyword density
        text = example["input"].lower()
        keyword_count = sum(1 for kw in self.crypto_keywords if kw in text)
        density = keyword_count / len(text.split())
        if density < self.quality_thresholds["crypto_keyword_density"]:
            return False

        return True

    def _load_crypto_vocabulary(self) -> List[str]:
        """Load cryptocurrency domain vocabulary"""
        return [
            "defi", "dex", "cex", "tvl", "apy", "apr", "yield",
            "staking", "liquidity", "pool", "swap", "bridge",
            "token", "nft", "smart contract", "wallet", "gas",
            "ethereum", "bitcoin", "solana", "polygon", "arbitrum",
            "usdt", "usdc", "dai", "eth", "btc", "sol",
            "uniswap", "aave", "compound", "curve", "maker",
            "oracle", "chainlink", "flashloan", "mev", "slippage",
            "impermanent loss", "rug pull", "audit", "exploit"
        ]
```

## Fine-Tuning Approaches

### 1. LoRA Fine-Tuning (Recommended for Most Cases)

```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

def setup_lora_training(
    base_model: str = "Qwen/Qwen2.5-7B-Instruct",
    lora_rank: int = 64,
    lora_alpha: int = 128,
    target_modules: List[str] = ["q_proj", "v_proj", "k_proj", "o_proj"]
):
    """Setup LoRA fine-tuning for crypto domain"""

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype="auto",
        device_map="auto"
    )

    lora_config = LoraConfig(
        r=lora_rank,
        lora_alpha=lora_alpha,
        target_modules=target_modules,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)

    return model, AutoTokenizer.from_pretrained(base_model)
```

### 2. BAML Schema Integration

```baml
// Fine-tune models to output these structured formats

class EntityExtractionOutput {
  tokens Token[]
  protocols Protocol[]
  metrics Metric[]
  relationships Relationship[]
}

class Token {
  symbol string
  name string?
  type "native" | "erc20" | "stablecoin" | "governance" | "lp_token"
  chain string?
  contract_address string?
}

class RiskAnalysisOutput {
  category "smart_contract" | "market" | "oracle" | "governance" | "regulatory"
  severity "critical" | "high" | "medium" | "low"
  title string
  description string
  affected_components string[]
  potential_impact string
  mitigation string[]
  confidence float @description("0.0 to 1.0")
}

// Fine-tuning target: model outputs valid instances of these types
function ExtractEntities(text: string) -> EntityExtractionOutput {
  client "local/crypto-qwen-lora"  // Fine-tuned model

  prompt #"
    Extract all cryptocurrency entities from this text.
    Output must be valid JSON matching the EntityExtractionOutput schema.

    Text: {{ text }}
  "#
}
```

### 3. Evaluation Framework

```python
from typing import Dict, List
import json

class CryptoModelEvaluator:
    """Evaluate fine-tuned crypto models"""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def evaluate_entity_extraction(
        self,
        test_data: List[Dict]
    ) -> Dict[str, float]:
        """Evaluate entity extraction accuracy"""

        results = {
            "token_precision": [],
            "token_recall": [],
            "protocol_precision": [],
            "protocol_recall": [],
            "address_accuracy": []
        }

        for example in test_data:
            predicted = self._generate(example["input"])
            ground_truth = example["output"]

            # Token evaluation
            pred_tokens = set(t["symbol"] for t in predicted.get("tokens", []))
            true_tokens = set(t["symbol"] for t in ground_truth.get("tokens", []))

            if pred_tokens:
                results["token_precision"].append(
                    len(pred_tokens & true_tokens) / len(pred_tokens)
                )
            if true_tokens:
                results["token_recall"].append(
                    len(pred_tokens & true_tokens) / len(true_tokens)
                )

            # Protocol evaluation
            pred_protocols = set(p["name"] for p in predicted.get("protocols", []))
            true_protocols = set(p["name"] for p in ground_truth.get("protocols", []))

            if pred_protocols:
                results["protocol_precision"].append(
                    len(pred_protocols & true_protocols) / len(pred_protocols)
                )
            if true_protocols:
                results["protocol_recall"].append(
                    len(pred_protocols & true_protocols) / len(true_protocols)
                )

        return {k: sum(v) / len(v) if v else 0 for k, v in results.items()}

    def evaluate_risk_analysis(
        self,
        test_data: List[Dict]
    ) -> Dict[str, float]:
        """Evaluate risk analysis accuracy"""

        results = {
            "severity_accuracy": [],
            "category_accuracy": [],
            "mitigation_relevance": []
        }

        for example in test_data:
            predicted = self._generate(example["input"])
            ground_truth = example["output"]

            # Severity match
            results["severity_accuracy"].append(
                1.0 if predicted.get("severity") == ground_truth.get("severity") else 0.0
            )

            # Category match
            results["category_accuracy"].append(
                1.0 if predicted.get("category") == ground_truth.get("category") else 0.0
            )

        return {k: sum(v) / len(v) if v else 0 for k, v in results.items()}
```

## MLflow Integration

### Experiment Tracking

```python
import mlflow
from mlflow.models import infer_signature

def train_crypto_model(
    training_data: str,
    base_model: str,
    experiment_name: str = "crypto-finetuning"
):
    """Train and log crypto model with MLflow"""

    mlflow.set_experiment(experiment_name)

    with mlflow.start_run() as run:
        # Log parameters
        mlflow.log_params({
            "base_model": base_model,
            "lora_rank": 64,
            "lora_alpha": 128,
            "learning_rate": 2e-4,
            "epochs": 3,
            "batch_size": 4
        })

        # Setup model
        model, tokenizer = setup_lora_training(base_model)

        # Train
        trainer = train_model(model, tokenizer, training_data)

        # Evaluate
        eval_results = evaluate_model(model, tokenizer)
        mlflow.log_metrics(eval_results)

        # Log model
        mlflow.pyfunc.log_model(
            artifact_path="model",
            python_model=CryptoModelWrapper(model, tokenizer),
            signature=infer_signature(
                ["Extract entities from: Uniswap V3 pool for ETH/USDC"],
                [{"tokens": [{"symbol": "ETH"}, {"symbol": "USDC"}]}]
            ),
            registered_model_name=f"crypto-{base_model.split('/')[-1]}"
        )

        return run.info.run_id
```

### Model Registry

```python
from mlflow.tracking import MlflowClient

def promote_model(
    model_name: str,
    version: int,
    stage: str = "Production"
):
    """Promote a crypto model to production"""

    client = MlflowClient()

    # Validate on holdout set before promotion
    model_uri = f"models:/{model_name}/{version}"
    model = mlflow.pyfunc.load_model(model_uri)

    validation_results = validate_model(model)

    if validation_results["entity_f1"] > 0.85 and validation_results["risk_accuracy"] > 0.80:
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
        return True

    return False
```

## Langfuse Integration for Observability

```python
from langfuse import Langfuse
from langfuse.decorators import observe

langfuse = Langfuse()

@observe(as_type="generation")
async def crypto_entity_extraction(
    text: str,
    model_name: str = "crypto-qwen-lora"
) -> Dict:
    """Extract entities with Langfuse tracing"""

    # This will be automatically traced
    result = await model.generate(
        prompt=f"Extract crypto entities: {text}",
        max_tokens=1000
    )

    # Log metadata
    langfuse.current_trace.update(
        metadata={
            "domain": "crypto",
            "task": "entity_extraction"
        }
    )

    return result


# Evaluation with Langfuse
def evaluate_with_langfuse(
    test_dataset: List[Dict],
    model_name: str
):
    """Run evaluation and log to Langfuse"""

    dataset = langfuse.create_dataset(
        name=f"crypto-eval-{datetime.now().isoformat()}",
        description="Crypto entity extraction evaluation"
    )

    for example in test_dataset:
        dataset.create_item(
            input=example["input"],
            expected_output=example["output"]
        )

    # Run evaluation
    for item in dataset.items:
        result = crypto_entity_extraction(item.input, model_name)

        # Score the result
        langfuse.score(
            trace_id=langfuse.current_trace.id,
            name="entity_f1",
            value=calculate_f1(result, item.expected_output)
        )
```

## Deployment Strategy

### Model Serving with LiteLLM

```python
# config/litellm_config.yaml
model_list:
  - model_name: crypto-entity-extractor
    litellm_params:
      model: openai/crypto-qwen-lora
      api_base: http://localhost:8000/v1  # Local vLLM endpoint
      api_key: fake-key

  - model_name: crypto-risk-analyzer
    litellm_params:
      model: openai/crypto-mistral-lora
      api_base: http://localhost:8001/v1

  - model_name: crypto-reasoning
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      # Falls back to Claude for complex reasoning
```

### Inference Pipeline

```python
from litellm import completion

async def analyze_crypto_document(
    document: str,
    analysis_type: str = "comprehensive"
) -> Dict:
    """Multi-model analysis pipeline"""

    results = {}

    # Step 1: Entity extraction (fine-tuned model)
    entities_response = await completion(
        model="crypto-entity-extractor",
        messages=[{
            "role": "user",
            "content": f"Extract entities: {document[:4000]}"
        }]
    )
    results["entities"] = json.loads(entities_response.choices[0].message.content)

    # Step 2: Risk analysis (fine-tuned model)
    if analysis_type in ["comprehensive", "risk"]:
        risk_response = await completion(
            model="crypto-risk-analyzer",
            messages=[{
                "role": "user",
                "content": f"Analyze risks: {document[:4000]}"
            }]
        )
        results["risks"] = json.loads(risk_response.choices[0].message.content)

    # Step 3: Synthesis (large model)
    if analysis_type == "comprehensive":
        synthesis_response = await completion(
            model="crypto-reasoning",
            messages=[{
                "role": "user",
                "content": f"""
                Based on these extracted entities and risks:
                Entities: {json.dumps(results['entities'])}
                Risks: {json.dumps(results['risks'])}

                Provide a comprehensive analysis of this protocol.
                """
            }]
        )
        results["synthesis"] = synthesis_response.choices[0].message.content

    return results
```

## References

- Gaeilge fine-tuning patterns: `/data/flows/gaeilge/research/organized/01-celtic-language-ai-resources/`
- MLflow documentation: https://mlflow.org/docs/latest/
- Langfuse documentation: https://langfuse.com/docs
- LoRA paper: https://arxiv.org/abs/2106.09685
- LiteLLM documentation: https://docs.litellm.ai/
