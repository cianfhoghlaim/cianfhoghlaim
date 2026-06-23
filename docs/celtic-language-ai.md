---
name: celtic-language-ai
description: Expert assistance for Celtic language AI/ML including Irish (gaBERT, UCCIX), Welsh, Scottish Gaelic, and Manx. Use when users need language models, ASR/TTS, translation, bilingual datasets, or edge deployment for Celtic languages.
---

# Celtic Language AI/ML Resources

**Languages:** Irish (Gaeilge), Welsh (Cymraeg), Scottish Gaelic (Gaidhlig), Manx (Gaelg)

## Overview

| Language | LLMs | ASR | TTS | Translation | Datasets | Maturity |
|----------|------|-----|-----|-------------|----------|----------|
| **Irish** | 5+ (UCCIX, gaBERT) | 7+ | MMS | Excellent | 10+ | High |
| **Welsh** | 2 (Mistral-7B-Cymraeg) | 7+ | MMS | Good | 8+ | High |
| **Scottish Gaelic** | 2 (GPT-2 WECHSEL) | In dev | None | Good | 38+ | Medium |
| **Manx** | None | None | TBD | Basic | 2-3 | Low |

## When to Use This Skill

Activate when users need:

- "Build an Irish language chatbot"
- "Train ASR for Welsh"
- "Translate to/from Scottish Gaelic"
- "Fine-tune models for Celtic languages"
- "Deploy Irish LLM on iPhone"

## 1. Irish (Gaeilge) Resources

**ISO:** ga | **Speakers:** ~1.85M

### Language Models

#### UCCIX - Most Advanced Irish LLM
| Model | HuggingFace |
|-------|-------------|
| Base 13B | `ReliableAI/UCCIX-Llama2-13B` |
| Instruct 13B | `ReliableAI/UCCIX-Llama2-13B-Instruct` |
| Llama 3.1 70B | `ReliableAI/UCCIX-Llama3.1-70B-Instruct` |

**Demo:** https://aine.chat

#### gaBERT & gaELECTRA
- `DCU-NLP/bert-base-irish-cased-v1` - 7.9M sentences
- `DCU-NLP/electra-base-irish-cased-generator-v1`

### Speech Recognition (ASR)

| Model | Notes |
|-------|-------|
| `cpierse/wav2vec2-large-xlsr-53-irish` | Large XLSR fine-tuned |
| `Aditya3107/wav2vec2-large-xls-r-1b-ga-ie` | 1B parameters |
| `facebook/mms-1b-all` | 1162 languages |

### Translation

| Direction | Model |
|-----------|-------|
| EN → GA | `Helsinki-NLP/opus-mt-en-ga` |
| GA → EN | `Helsinki-NLP/opus-mt-ga-en` |
| Multilingual | `facebook/m2m100_418M`, `facebook/m2m100_1.2B` |

### Key Datasets

- `ReliableAI/Irish-English-Parallel-Collection`
- CC-100 (108M Irish tokens)
- Common Voice (9.0-19.0)
- CulturaX (6.3T tokens, 167 languages)

## 2. Welsh (Cymraeg) Resources

**ISO:** cy | **Speakers:** ~884K

### Language Models

- `BangorAI/Mistral-7B-Cymraeg-Welsh-v2` - Bilingual chat (7B)
- **Demo:** https://demo.bangor.ai

### Speech Recognition

| Model | WER |
|-------|-----|
| `techiaith/wav2vec2-xlsr-ft-cy` | 4.05% (with KenLM) |
| `techiaith/wav2vec2-base-cy` | 4000 hours training |
| `techiaith/whisper-large-v3-ft-commonvoice-cy-en` | Bilingual |

### Key Organizations

- **techiaith** (Bangor University) - 21 models on HuggingFace

## 3. Scottish Gaelic Resources

**ISO:** gd | **Speakers:** ~70K

### Models

- `benjamin/gpt2-wechsel-scottish-gaelic` - Transfer learning GPT-2
- `Helsinki-NLP/opus-mt-synthetic-en-gd` - Translation (ChrF: 51.10)

### Development Status

- 2025: **12.8% WER** achieved (32% improvement)
- **GBP 225k** Scottish Government funding
- Speech-to-text API expected **Q4 2025**

## 4. Manx (Gaelg) Resources

**ISO:** gv | **Speakers:** ~1,800 (critically endangered)

### Translation Only

| Model | Direction | BLEU |
|-------|-----------|------|
| `Helsinki-NLP/opus-mt-en-gv` | EN → GV | 70.1 |
| `Helsinki-NLP/opus-mt-gv-en` | GV → EN | 38.9 |

**Recommendation:** Use cross-lingual transfer from Irish.

## Agno Agent Implementation

```python
from agno.agent import Agent
from agno.models.openai.like import OpenAILike

irish_llm = OpenAILike(
    id="uccix-13b",
    api_key=os.getenv("UCCIX_API_KEY"),
    base_url="https://api.uccix.ie/v1/",
    temperature=0.1,
)

chief_agent = Agent(
    name="ChiefExaminer",
    role="Orchestrator for Irish language processing",
    model=irish_llm,
    markdown=True,
)
```

## iOS Edge Deployment

### Device Constraints

| Device | RAM | Safe Model Size |
|--------|-----|-----------------|
| iPhone 14/15 | 6GB | ~2GB model |
| iPhone Pro | 8GB | ~3GB model |

### Unsloth Fine-Tuning for Mobile

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.2-3B-Instruct-bnb-4bit",
    max_seq_length=8192,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=64,  # Higher rank for language adaptation
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=128,
)
```

### GGUF Export

```python
model.save_pretrained_gguf(
    "Llama-3.2-3B-Irish-Instruct",
    tokenizer,
    quantization_method="q4_k_m"
)
```

### Swift Integration

```swift
import AnyLanguageModel

class ModelController: ObservableObject {
    func setupModel() {
        guard let path = Bundle.main.path(
            forResource: "Llama-3.2-3B-Irish-Instruct.Q4_K_M",
            ofType: "gguf"
        ) else { return }

        let model = LlamaLanguageModel(modelPath: path)
        self.session = LanguageModelSession(model: model)
    }
}
```

## Selection Guide by Use Case

### Text Generation
| Language | Model |
|----------|-------|
| Irish | `ReliableAI/UCCIX-Llama2-13B-Instruct` |
| Welsh | `BangorAI/Mistral-7B-Cymraeg-Welsh-v2` |
| Scottish Gaelic | `benjamin/gpt2-wechsel-scottish-gaelic` |

### Speech Recognition
| Language | Model |
|----------|-------|
| Irish | `cpierse/wav2vec2-large-xlsr-53-irish` |
| Welsh | `techiaith/wav2vec2-xlsr-ft-cy` (4.05% WER) |
| Scottish Gaelic | Fine-tune Whisper (no public models) |

### Translation
| Language | Model |
|----------|-------|
| Irish | `Helsinki-NLP/opus-mt-en-ga` |
| Welsh | `AndreasThinks/mistral-7b-english-welsh-translate` |
| Scottish Gaelic | `Helsinki-NLP/opus-mt-synthetic-en-gd` |
| Manx | `Helsinki-NLP/opus-mt-en-gv` |

## Research Gaps

- No Whisper fine-tuned models for Irish
- Limited NER datasets across all Celtic languages
- No Celtic GLUE-equivalent evaluation suite
- Manx has minimal AI resources

## Key Organizations

| Organization | Focus |
|--------------|-------|
| DCU-NLP | gaBERT, gaELECTRA |
| ReliableAI/ReML-AI | UCCIX project |
| techiaith (Bangor) | Welsh speech/NLP |
| Helsinki-NLP | Translation models |
| Meta/Facebook | MMS, M2M100 |

## Resources

- **UCCIX Demo:** https://aine.chat
- **Welsh Demo:** https://demo.bangor.ai
- **Irish HF Resources:** https://huggingface.co/DCU-NLP
- **Welsh HF Resources:** https://huggingface.co/techiaith
