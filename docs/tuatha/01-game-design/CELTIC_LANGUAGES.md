# Celtic Languages Integration

Guide for working with Celtic languages in the Tuath platform.

## Overview

Tuath supports three Celtic languages with bilingual (English + target language) interfaces:

| Language | Code | Name | Region | Status |
|----------|------|------|--------|--------|
| Irish | `ga` | Gaeilge | Ireland | Primary |
| Welsh | `cy` | Cymraeg | Wales | Supported |
| Scottish Gaelic | `gd` | Gaidhlig | Scotland | Supported |
| Manx | `gv` | Gaelg | Isle of Man | Planned |

### Language Model Performance Gap

Celtic languages represent <0.1% of web content, resulting in ~20% lower model performance compared to English. This guide covers strategies to mitigate this gap.

---

## Language Detection

### Using langdetect

```python
from langdetect import detect, detect_langs


def detect_celtic_language(text: str) -> str | None:
    """
    Detect Celtic language in text.

    Returns language code or None if not Celtic.
    """
    try:
        detected = detect(text)

        # Map to our language codes
        celtic_map = {
            "ga": "ga",  # Irish
            "cy": "cy",  # Welsh
            "gd": "gd",  # Scottish Gaelic
            "gv": "gv",  # Manx
        }

        return celtic_map.get(detected)

    except Exception:
        return None


def get_language_probabilities(text: str) -> dict[str, float]:
    """Get probability scores for detected languages."""
    try:
        langs = detect_langs(text)
        return {str(lang.lang): lang.prob for lang in langs}
    except Exception:
        return {}
```

### Enhanced Detection for Mixed Text

```python
import re
from collections import Counter


# Celtic-specific character patterns
IRISH_PATTERNS = [
    r"\bníl\b", r"\btá\b", r"\bagus\b", r"\ban\b",
    r"\bár\b", r"\bbhí\b", r"\bsé\b", r"\bsí\b",
]

WELSH_PATTERNS = [
    r"\byn\b", r"\byr\b", r"\bydd\b", r"\bmae\b",
    r"\bgyda\b", r"\bdim\b", r"\boedd\b",
]

GAELIC_PATTERNS = [
    r"\btha\b", r"\bann\b", r"\bair\b", r"\ble\b",
    r"\bcha\b", r"\bnas\b", r"\bbha\b",
]


def detect_celtic_enhanced(text: str) -> tuple[str, float]:
    """
    Enhanced Celtic language detection using patterns.

    Returns (language_code, confidence).
    """
    text_lower = text.lower()

    scores = {
        "ga": sum(1 for p in IRISH_PATTERNS if re.search(p, text_lower)),
        "cy": sum(1 for p in WELSH_PATTERNS if re.search(p, text_lower)),
        "gd": sum(1 for p in GAELIC_PATTERNS if re.search(p, text_lower)),
    }

    if max(scores.values()) == 0:
        return ("en", 0.5)

    best_lang = max(scores, key=scores.get)
    confidence = scores[best_lang] / len(text.split()) * 10
    confidence = min(confidence, 1.0)

    return (best_lang, confidence)
```

---

## Specialized Models

### Irish Language Models

| Model | Purpose | Hugging Face ID |
|-------|---------|-----------------|
| GaBERT | NER, classification | `DCU-NLP/bert-base-irish-cased-v1` |
| UCCIX-Llama2 | Generation, chat | `ReliableAI/UCCIX-Llama2-13B-Instruct` |
| Whisper-ga | Speech recognition | `openai/whisper-large-v3` (Irish fine-tuned) |

### Using GaBERT for NER

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline


def create_irish_ner_pipeline():
    """Create NER pipeline for Irish text."""

    model_id = "DCU-NLP/bert-base-irish-cased-v1"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForTokenClassification.from_pretrained(model_id)

    return pipeline(
        "ner",
        model=model,
        tokenizer=tokenizer,
        aggregation_strategy="simple",
    )


def extract_irish_entities(text: str) -> list[dict]:
    """Extract named entities from Irish text."""

    ner = create_irish_ner_pipeline()
    entities = ner(text)

    return [
        {
            "text": ent["word"],
            "type": ent["entity_group"],
            "score": ent["score"],
            "start": ent["start"],
            "end": ent["end"],
        }
        for ent in entities
    ]
```

### Using UCCIX for Generation

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


def create_uccix_model():
    """Load UCCIX model for Irish text generation."""

    model_id = "ReliableAI/UCCIX-Llama2-13B-Instruct"

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    return tokenizer, model


def generate_irish_text(
    prompt: str,
    max_tokens: int = 256,
) -> str:
    """Generate Irish text from prompt."""

    tokenizer, model = create_uccix_model()

    # UCCIX prompt format
    formatted_prompt = f"""### Instruction:
{prompt}

### Response:
"""

    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        temperature=0.7,
        do_sample=True,
        top_p=0.95,
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract response after marker
    if "### Response:" in response:
        response = response.split("### Response:")[-1].strip()

    return response
```

### Welsh and Scottish Gaelic

```python
# Welsh models
WELSH_MODELS = {
    "ner": "declanlloyd/NER-cy",
    "sentiment": "declanlloyd/sentiment-cy",
}

# Scottish Gaelic - fewer specialized models, use multilingual
GAELIC_MODELS = {
    "embedding": "BAAI/bge-m3",  # Multilingual
    "generation": "google/gemma-2-9b",  # Good Celtic support
}
```

---

## Translation Services

### Between Celtic Languages

```python
from transformers import MarianMTModel, MarianTokenizer


class CelticTranslator:
    """Translate between Celtic languages and English."""

    # Available translation pairs
    MODELS = {
        ("en", "ga"): "Helsinki-NLP/opus-mt-en-ga",
        ("ga", "en"): "Helsinki-NLP/opus-mt-ga-en",
        ("en", "cy"): "Helsinki-NLP/opus-mt-en-cy",
        ("cy", "en"): "Helsinki-NLP/opus-mt-cy-en",
        # No direct ga<->cy, route through English
    }

    def __init__(self):
        self._models = {}

    def _load_model(self, source: str, target: str):
        """Load translation model."""
        key = (source, target)
        if key not in self._models:
            model_id = self.MODELS.get(key)
            if not model_id:
                raise ValueError(f"No model for {source}->{target}")

            self._models[key] = {
                "tokenizer": MarianTokenizer.from_pretrained(model_id),
                "model": MarianMTModel.from_pretrained(model_id),
            }

        return self._models[key]

    def translate(
        self,
        text: str,
        source: str,
        target: str,
    ) -> str:
        """Translate text between languages."""

        # Direct translation if available
        if (source, target) in self.MODELS:
            return self._direct_translate(text, source, target)

        # Route through English
        if source != "en" and target != "en":
            english = self._direct_translate(text, source, "en")
            return self._direct_translate(english, "en", target)

        raise ValueError(f"Cannot translate {source} to {target}")

    def _direct_translate(
        self,
        text: str,
        source: str,
        target: str,
    ) -> str:
        """Perform direct translation."""
        model_data = self._load_model(source, target)

        inputs = model_data["tokenizer"](
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )

        outputs = model_data["model"].generate(**inputs)

        return model_data["tokenizer"].decode(
            outputs[0],
            skip_special_tokens=True,
        )
```

### Pronunciation Guide

```python
# Irish pronunciation rules (simplified)
IRISH_PRONUNCIATION = {
    # Broad consonants
    "bh": "v/w",
    "ch": "kh",
    "dh": "gh/y",
    "fh": "(silent)",
    "gh": "gh/y",
    "mh": "v/w",
    "ph": "f",
    "sh": "h",
    "th": "h",

    # Slender consonants (before e, i)
    "bhí": "vee",
    "chí": "khee",

    # Common words
    "dia": "DEE-a",
    "duit": "dit/gwit",
    "slán": "slawn",
    "fáilte": "FAWL-cheh",
}


def get_pronunciation(word: str, language: str = "ga") -> str:
    """Get pronunciation guide for Celtic word."""

    if language == "ga":
        # Check exact matches first
        if word.lower() in IRISH_PRONUNCIATION:
            return IRISH_PRONUNCIATION[word.lower()]

        # Apply rules
        result = word.lower()
        for pattern, replacement in IRISH_PRONUNCIATION.items():
            if pattern in result and len(pattern) > 1:
                result = result.replace(pattern, f"[{replacement}]")

        return result

    # TODO: Add Welsh, Scottish Gaelic
    return word
```

---

## Dialect Handling

### Irish Dialects

| Dialect | Region | Key Features |
|---------|--------|--------------|
| Connacht | Galway, Mayo | Strong "s" pronunciation |
| Munster | Cork, Kerry | Different verb endings |
| Ulster | Donegal | Closest to Scottish Gaelic |
| Standard | Official | Taught in schools |

```python
from enum import Enum


class IrishDialect(str, Enum):
    STANDARD = "standard"
    CONNACHT = "connacht"
    MUNSTER = "munster"
    ULSTER = "ulster"


# Dialect-specific vocabulary
DIALECT_VARIATIONS = {
    "how are you": {
        IrishDialect.STANDARD: "Conas atá tú?",
        IrishDialect.CONNACHT: "Cén chaoi a bhfuil tú?",
        IrishDialect.MUNSTER: "Conas atánn tú?",
        IrishDialect.ULSTER: "Cad é mar atá tú?",
    },
    "thank you": {
        IrishDialect.STANDARD: "Go raibh maith agat",
        IrishDialect.CONNACHT: "Go raibh maith agat",
        IrishDialect.MUNSTER: "Go raibh maith agat",
        IrishDialect.ULSTER: "Go raibh maith agat",
    },
}


def get_dialect_form(
    phrase: str,
    dialect: IrishDialect = IrishDialect.STANDARD,
) -> str:
    """Get dialect-specific form of phrase."""

    if phrase.lower() in DIALECT_VARIATIONS:
        variations = DIALECT_VARIATIONS[phrase.lower()]
        return variations.get(dialect, variations[IrishDialect.STANDARD])

    return phrase
```

---

## Content Processing

### Bilingual Content Extraction

```python
import re


def extract_bilingual_pairs(text: str) -> list[tuple[str, str]]:
    """
    Extract English/Irish pairs from bilingual text.

    Handles formats:
    - "English (Gaeilge)"
    - "English / Gaeilge"
    - "English - Gaeilge"
    """

    patterns = [
        r"([A-Za-z\s]+)\s*\(([^)]+)\)",  # English (Gaeilge)
        r"([A-Za-z\s]+)\s*/\s*([^/\n]+)",  # English / Gaeilge
        r"([A-Za-z\s]+)\s*-\s*([^-\n]+)",  # English - Gaeilge
    ]

    pairs = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        pairs.extend([(m[0].strip(), m[1].strip()) for m in matches])

    return pairs


def create_vocabulary_entry(
    english: str,
    celtic: str,
    language: str,
    context: str = "",
) -> dict:
    """Create structured vocabulary entry."""

    return {
        "english": english,
        "celtic": celtic,
        "language": language,
        "pronunciation": get_pronunciation(celtic, language),
        "context": context,
        "difficulty": estimate_difficulty(celtic),
    }


def estimate_difficulty(word: str) -> str:
    """Estimate word difficulty based on length and patterns."""

    # Length-based
    if len(word) <= 4:
        base = 1
    elif len(word) <= 7:
        base = 2
    else:
        base = 3

    # Complexity factors
    if any(c in word for c in ["á", "é", "í", "ó", "ú"]):
        base += 0.5  # Fadas

    if any(pattern in word.lower() for pattern in ["bh", "ch", "dh", "gh"]):
        base += 0.5  # Lenition

    if base <= 1.5:
        return "beginner"
    elif base <= 2.5:
        return "intermediate"
    else:
        return "advanced"
```

### Irish Curriculum Standards

```python
# NCCA Curriculum levels for Irish
IRISH_LEVELS = {
    "primary": {
        "junior_infants": {"age": 4, "cefr": "A0"},
        "senior_infants": {"age": 5, "cefr": "A0"},
        "first_class": {"age": 6, "cefr": "A1"},
        "second_class": {"age": 7, "cefr": "A1"},
        "third_class": {"age": 8, "cefr": "A1"},
        "fourth_class": {"age": 9, "cefr": "A2"},
        "fifth_class": {"age": 10, "cefr": "A2"},
        "sixth_class": {"age": 11, "cefr": "A2-B1"},
    },
    "secondary": {
        "first_year": {"age": 12, "cefr": "A2-B1"},
        "second_year": {"age": 13, "cefr": "B1"},
        "third_year": {"age": 14, "cefr": "B1"},  # Junior Cert
        "transition_year": {"age": 15, "cefr": "B1"},
        "fifth_year": {"age": 16, "cefr": "B1-B2"},
        "sixth_year": {"age": 17, "cefr": "B2"},  # Leaving Cert
    },
}


def get_appropriate_level(age: int, native_speaker: bool = False) -> dict:
    """Get appropriate curriculum level for age."""

    if native_speaker:
        # Gaeltacht students have higher proficiency
        cefr_boost = 1  # +1 CEFR level

    for stage, levels in IRISH_LEVELS.items():
        for level, info in levels.items():
            if info["age"] == age:
                return {
                    "stage": stage,
                    "level": level,
                    "cefr": info["cefr"],
                }

    return {"stage": "adult", "level": "general", "cefr": "varies"}
```

---

## Embedding Strategies

### Multilingual Embeddings for Celtic

```python
from sentence_transformers import SentenceTransformer


def create_celtic_embedder():
    """Create embedding model optimized for Celtic languages."""

    # BGE-M3 has best multilingual coverage
    model = SentenceTransformer("BAAI/bge-m3")

    return model


def embed_celtic_text(
    texts: list[str],
    model: SentenceTransformer,
    batch_size: int = 100,
) -> list[list[float]]:
    """
    Generate embeddings for Celtic text.

    CRITICAL: Always batch for performance!
    """

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()
```

### Cross-Lingual Search

```python
async def search_across_languages(
    query: str,
    source_language: str,
    target_languages: list[str] = ["ga", "cy", "gd", "en"],
    limit: int = 10,
) -> list[dict]:
    """
    Search across multiple Celtic languages.

    The query is embedded once and compared against all language content.
    """

    from tuath.storage.lancedb_client import LanceDBClient

    client = LanceDBClient()
    embedder = create_celtic_embedder()

    # Embed query
    query_embedding = embedder.encode(query, normalize_embeddings=True)

    # Search each language table
    all_results = []

    for lang in target_languages:
        table_name = f"curriculum_{lang}"

        try:
            results = await client.search(
                table=table_name,
                query_vector=query_embedding,
                limit=limit,
            )

            for r in results:
                r["language"] = lang
                all_results.append(r)

        except Exception:
            continue  # Table may not exist

    # Sort by score and limit
    all_results.sort(key=lambda x: x["score"], reverse=True)

    return all_results[:limit]
```

---

## Game Integration

### Zone Language Assignment

```typescript
// scenes/zone-config.ts

interface ZoneConfig {
  zoneId: string;
  language: 'ga' | 'cy' | 'gd';
  dialect?: string;
  displayName: string;
  celticName: string;
}

const ZONE_LANGUAGES: Record<string, ZoneConfig> = {
  gaeltacht: {
    zoneId: 'gaeltacht',
    language: 'ga',
    dialect: 'connacht',
    displayName: 'An Ghaeltacht',
    celticName: 'An Ghaeltacht',
  },
  alba: {
    zoneId: 'alba',
    language: 'gd',
    displayName: 'Alba',
    celticName: 'Alba',
  },
  cymru: {
    zoneId: 'cymru',
    language: 'cy',
    displayName: 'Cymru',
    celticName: 'Cymru',
  },
};
```

### NPC Dialogue Localization

```typescript
// dialogue/dialogue-manager.ts

interface DialogueLine {
  id: string;
  english: string;
  celtic: string;
  pronunciation?: string;
  audioFile?: string;
}

const DIALOGUE_DATABASE: Record<string, DialogueLine[]> = {
  'npc_elder_greeting': [
    {
      id: 'greeting_1',
      english: 'Welcome, young one.',
      celtic: 'Fáilte, a dhuine óig.',
      pronunciation: 'FAWL-cheh, a GHIN-eh OHG',
      audioFile: 'audio/dialogue/elder_greeting_1.mp3',
    },
    {
      id: 'greeting_2',
      english: 'The ancient stories await you.',
      celtic: 'Tá na seanscéalta ag fanacht leat.',
      pronunciation: 'taw na SHAN-shkale-ta eg FAN-akht lat',
      audioFile: 'audio/dialogue/elder_greeting_2.mp3',
    },
  ],
};


function getDialogue(
  dialogueId: string,
  showBilingual: boolean = true,
): string {
  const lines = DIALOGUE_DATABASE[dialogueId];
  if (!lines) return '';

  const line = lines[Math.floor(Math.random() * lines.length)];

  if (showBilingual) {
    return `${line.celtic}\n(${line.english})`;
  }

  return line.celtic;
}
```

---

## Testing

### Language-Specific Tests

```python
# tests/test_celtic_languages.py
import pytest
from tuath.services.language import (
    detect_celtic_language,
    translate,
    get_pronunciation,
)


class TestLanguageDetection:
    def test_detect_irish(self):
        text = "Dia duit, conas atá tú?"
        assert detect_celtic_language(text) == "ga"

    def test_detect_welsh(self):
        text = "Bore da, sut mae heddiw?"
        assert detect_celtic_language(text) == "cy"

    def test_detect_english(self):
        text = "Hello, how are you today?"
        assert detect_celtic_language(text) is None


class TestTranslation:
    def test_english_to_irish(self):
        result = translate("Hello", source="en", target="ga")
        assert "Dia" in result or "Haigh" in result

    def test_irish_to_english(self):
        result = translate("Slán", source="ga", target="en")
        assert "goodbye" in result.lower() or "bye" in result.lower()


class TestPronunciation:
    def test_common_words(self):
        assert "DEE" in get_pronunciation("dia", "ga")
        assert "slawn" in get_pronunciation("slán", "ga").lower()
```

---

## Related Documentation

- [Adding Data Sources](./ADDING_DATA_SOURCES.md) - Curriculum ingestion
- [Performance Tuning](./PERFORMANCE_TUNING.md) - Embedding optimization
- [Architecture](../ARCHITECTURE.md) - System overview
