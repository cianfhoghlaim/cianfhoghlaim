# Multimodal (Vision / Audio / PDF) Extraction

BAML has built-in support for **multimodal primitive types**
(`image`, `pdf`, `audio`) as function parameters. The BAML runtime
helpers `baml_py.Image.from_base64(...)` and
`baml_py.Pdf.from_base64(...)` convert bytes to typed BAML inputs.

## The BAML signature

```baml
// baml_src/receipts.baml (or ocr_extraction.baml in the KCG repo)
class Transaction {
  item_name string
  quantity int
  unit_price float
  total_price float
}

class ReceiptData {
  transactions Transaction[]
  subtotal float?
  service_charge float?
  tax float?
  discount float?
  rounding float?
  grand_total float
}

function ExtractReceiptTransactions(
  receipt_image: image
) -> ReceiptData {
  client "google-ai/gemini-2.5-flash"
  prompt #"
    Extract all line-item transactions from this receipt image.
    Include the subtotal, service charge, tax, discount, rounding, and grand total.

    {{ ctx.output_format }}
  "#
}
```

## The Python glue

```python
import base64
import baml_py
from baml_client import b

# Image from file
with open("receipt.png", "rb") as f:
    image = baml_py.Image.from_base64(
        "image/png",
        base64.b64encode(f.read()).decode("ascii"),
    )
receipt = b.ExtractReceiptTransactions(receipt_image=image)

# PDF from file
with open("document.pdf", "rb") as f:
    pdf = baml_py.Pdf.from_base64(base64.b64encode(f.read()).decode("ascii"))
result = b.ExtractDocumentStructure(document=pdf)

# Audio (wav, mp3, m4a)
with open("interview.wav", "rb") as f:
    audio = baml_py.Audio.from_base64("audio/wav", base64.b64encode(f.read()).decode("ascii"))
transcript = b.TranscribeAudio(audio_clip=audio)
```

## Preprocessing (PIL)

For OCR-style extraction, preprocess the image with PIL to improve
accuracy:

```python
from PIL import Image, ImageEnhance, ImageOps
import io
import base64

def preprocess_for_ocr(image_bytes: bytes) -> bytes:
    """Grayscale + contrast enhancement + auto-orient."""
    image = Image.open(io.BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image)  # handle EXIF rotation
    image = image.convert("L")  # grayscale
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.5)  # increase contrast
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()

# Use it
with open("receipt.png", "rb") as f:
    raw = f.read()
processed = preprocess_for_ocr(raw)
image = baml_py.Image.from_base64(
    "image/png", base64.b64encode(processed).decode("ascii"),
)
receipt = b.ExtractReceiptTransactions(receipt_image=image)
```

## Multimodal clients

Vision-capable models:

| Provider | Model | Notes |
|:--|:--|:--|
| Google AI | `gemini-2.5-flash`, `gemini-2.5-pro` | Recommended for OCR / receipts |
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `gpt-4-vision-preview` | Good general vision |
| Anthropic | `claude-3-5-sonnet`, `claude-3-opus` | Excellent at structured extraction |
| Vertex AI | `gemini-2.5-flash`, `claude-3-5-sonnet` | GCP-hosted |
| AWS Bedrock | `anthropic.claude-3-5-sonnet`, `amazon.titan-image-generator-v1` | AWS-hosted |
| Azure OpenAI | `gpt-4o` (vision) | Azure-hosted |

```baml
client<llm> ExtractEnVision {
  provider "openai"
  options {
    model "gpt-4o"
    temperature 0.0
  }
}

client<llm> ExtractGeminiVision {
  provider "google-ai"
  options {
    model "gemini-2.5-flash"
    generationConfig { temperature 0.0 }
  }
}
```

## Multi-page PDFs

BAML handles multi-page PDFs natively. For very large PDFs (> 50
pages), consider:

- **Splitting** the PDF into chunks and processing each chunk
- **Summarising** the whole PDF first, then extracting specific
  sections
- **RAG** over the PDF text (extract text with PyMuPDF, embed,
  retrieve) instead of feeding the whole PDF to the LLM

## In-repo KCG usage

- `baml/ocr_extraction.baml` (9,368 bytes) — the
  canonical multimodal pattern in the KCG stack. Extracts text from
  scanned NCCA / SEC PDFs via Gemini vision
- `baml/audio_extraction.baml` — for audio transcripts
- `baml/portfolio_extraction.baml` — for the croilar
  CV / achievements PDFs (mixed text + image content)

## Reference

- The `2025-12-02-multimodal-evals` example (deleted with `docs/baml/`)
  is the canonical reference. The full code is in the upstream
  [BoundaryML/baml-examples](https://github.com/BoundaryML/baml-examples)
  repo.
- BAML multimodal docs: <https://docs.boundaryml.com/docs/snippets/multimodal>
