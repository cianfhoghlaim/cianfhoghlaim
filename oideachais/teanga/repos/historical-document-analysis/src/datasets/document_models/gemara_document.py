import pydantic
from typing import List, Optional
class Document(pydantic.BaseModel):
    id: int
    image_urls: List[str]
    ground_truth_transcription: Optional[str]  # Expert transcription (only available for 1k docs)
    description: Optional[str]

class GemaraDocument(Document):
    """Structured representation of a document from the Cairo Genizah."""
    translation: Optional[str]   # Expert translation of the text
    date: Optional[str]
    language: Optional[str]