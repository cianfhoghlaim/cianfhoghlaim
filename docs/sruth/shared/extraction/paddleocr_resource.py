"""PaddleOCR Resource for table and formula extraction.

Provides SOTA OCR capabilities via PaddleOCR:
- Table structure recognition (SLANet, PubLayNet)
- Formula/equation extraction (LaTeX output)
- Multi-language OCR (109 languages including Irish)
- Layout analysis for complex documents

Model Selection:
- PP-OCRv4: General text recognition (0.9B params)
- PP-Structure: Table + layout analysis
- PP-Formula: Mathematical expression recognition

Usage:
    @asset(resource_defs={"paddle": paddleocr_resource()})
    def extract_tables(paddle: PaddleOCRResource, page_image: bytes):
        table = paddle.extract_table(page_image)
        return table.to_dataframe()
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from typing import Any, Literal

import dagster as dg
import structlog

try:
    from pydantic import Field
except ImportError:
    from dagster import Field

logger = structlog.get_logger(__name__)


@dataclass
class TableCell:
    """Represents a single cell in a table."""

    text: str
    row: int
    col: int
    row_span: int = 1
    col_span: int = 1
    is_header: bool = False


@dataclass
class ExtractedTable:
    """Result of table extraction."""

    cells: list[TableCell]
    rows: int
    cols: int
    html: str | None = None
    confidence: float = 0.0
    page_number: int | None = None
    bbox: tuple[int, int, int, int] | None = None  # x1, y1, x2, y2

    def to_rows(self) -> list[list[str]]:
        """Convert cells to 2D list of strings."""
        result = [[""] * self.cols for _ in range(self.rows)]
        for cell in self.cells:
            if 0 <= cell.row < self.rows and 0 <= cell.col < self.cols:
                result[cell.row][cell.col] = cell.text
        return result

    def to_markdown(self) -> str:
        """Convert table to markdown format."""
        rows = self.to_rows()
        if not rows:
            return ""

        lines = []
        # Header row
        lines.append("| " + " | ".join(rows[0]) + " |")
        lines.append("| " + " | ".join(["---"] * self.cols) + " |")
        # Data rows
        for row in rows[1:]:
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)

    def to_csv(self, delimiter: str = ",") -> str:
        """Convert table to CSV format."""
        rows = self.to_rows()
        return "\n".join(delimiter.join(row) for row in rows)


@dataclass
class FormulaResult:
    """Result of formula extraction."""

    latex: str
    confidence: float = 0.0
    bbox: tuple[int, int, int, int] | None = None
    page_number: int | None = None


@dataclass
class LayoutElement:
    """Represents a detected layout element."""

    element_type: str  # table, figure, text, title, list, formula
    bbox: tuple[int, int, int, int]
    confidence: float
    text: str | None = None


@dataclass
class OCRResult:
    """Result of OCR text extraction."""

    text: str
    boxes: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    language: str | None = None


class PaddleOCRResource(dg.ConfigurableResource):
    """PaddleOCR-based extraction for tables and formulas.

    Provides:
    - PP-OCRv4: General text recognition (109 languages)
    - PP-Structure: Table structure recognition
    - PP-Formula: LaTeX formula extraction

    Example:
        @asset(resource_defs={"paddle": paddleocr_resource()})
        def process_exam_tables(paddle: PaddleOCRResource, image_bytes):
            tables = paddle.extract_tables(image_bytes)
            formulas = paddle.extract_formulas(image_bytes)
            return {"tables": tables, "formulas": formulas}
    """

    # Language configuration
    lang: str = Field(
        default="en",
        description="OCR language code (en, ga, cy for Irish, Welsh)",
    )

    # Model selection
    use_angle_cls: bool = Field(
        default=True,
        description="Enable text direction classification",
    )

    det_model_dir: str | None = Field(
        default=None,
        description="Custom detection model directory",
    )

    rec_model_dir: str | None = Field(
        default=None,
        description="Custom recognition model directory",
    )

    # Table extraction configuration
    table_algorithm: str = Field(
        default="SLANet",
        description="Table structure algorithm: SLANet or TableMASTER",
    )

    table_max_len: int = Field(
        default=488,
        description="Maximum image dimension for table extraction",
    )

    # Formula extraction configuration
    formula_enabled: bool = Field(
        default=True,
        description="Enable formula extraction (requires paddleocr formula module)",
    )

    # GPU configuration
    use_gpu: bool = Field(
        default=False,
        description="Use GPU for inference (requires CUDA)",
    )

    # LiteLLM fallback for VLM-based extraction
    litellm_base_url: str = Field(
        default_factory=lambda: os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        description="LiteLLM proxy URL for VLM fallback",
    )

    vlm_model: str = Field(
        default="vision",
        description="LiteLLM model alias for VLM fallback",
    )

    def _get_ocr_engine(self) -> Any:
        """Get PaddleOCR engine instance (lazy import)."""
        try:
            from paddleocr import PaddleOCR

            return PaddleOCR(
                use_angle_cls=self.use_angle_cls,
                lang=self.lang,
                use_gpu=self.use_gpu,
                det_model_dir=self.det_model_dir,
                rec_model_dir=self.rec_model_dir,
                show_log=False,
            )
        except ImportError:
            logger.warning(
                "paddleocr_not_installed",
                message="Install: pip install paddleocr",
            )
            return None

    def _get_table_engine(self) -> Any:
        """Get PPStructure table engine (lazy import)."""
        try:
            from paddleocr import PPStructure

            return PPStructure(
                table_algorithm=self.table_algorithm,
                table_max_len=self.table_max_len,
                use_gpu=self.use_gpu,
                show_log=False,
            )
        except ImportError:
            logger.warning(
                "ppstructure_not_available",
                message="Install: pip install paddleocr",
            )
            return None

    def _get_layout_engine(self) -> Any:
        """Get layout analysis engine (lazy import)."""
        try:
            from paddleocr import PPStructure

            return PPStructure(
                layout=True,
                table=False,
                ocr=True,
                use_gpu=self.use_gpu,
                show_log=False,
            )
        except ImportError:
            logger.warning("layout_engine_not_available")
            return None

    def ocr_text(
        self,
        image_bytes: bytes,
        language: str | None = None,
    ) -> OCRResult:
        """Extract text from image using PaddleOCR.

        Args:
            image_bytes: Image content
            language: Language code (overrides default)

        Returns:
            OCRResult with extracted text and bounding boxes
        """
        engine = self._get_ocr_engine()
        if engine is None:
            return self._fallback_ocr_vlm(image_bytes)

        try:
            import numpy as np
            from PIL import Image
            import io

            # Convert bytes to numpy array
            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)

            # Run OCR
            result = engine.ocr(img_array, cls=True)

            if not result or not result[0]:
                return OCRResult(text="", confidence=0.0)

            # Extract text and boxes
            texts = []
            boxes = []
            confidences = []

            for line in result[0]:
                box, (text, conf) = line
                texts.append(text)
                boxes.append(
                    {
                        "box": box,
                        "text": text,
                        "confidence": conf,
                    }
                )
                confidences.append(conf)

            full_text = "\n".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            logger.info(
                "ocr_completed",
                text_length=len(full_text),
                line_count=len(texts),
                avg_confidence=avg_confidence,
            )

            return OCRResult(
                text=full_text,
                boxes=boxes,
                confidence=avg_confidence,
                language=language or self.lang,
            )

        except Exception as e:
            logger.error("ocr_failed", error=str(e))
            return self._fallback_ocr_vlm(image_bytes)

    def _fallback_ocr_vlm(self, image_bytes: bytes) -> OCRResult:
        """Fallback to VLM-based OCR via LiteLLM."""
        try:
            import litellm

            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            image_url = f"data:image/png;base64,{image_b64}"

            response = litellm.completion(
                model=self.vlm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this image exactly as written:",
                            },
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                api_base=self.litellm_base_url,
            )

            text = response.choices[0].message.content
            logger.info("vlm_ocr_fallback_used", text_length=len(text))

            return OCRResult(
                text=text,
                boxes=[],
                confidence=0.8,  # Estimate for VLM
            )

        except Exception as e:
            logger.error("vlm_ocr_fallback_failed", error=str(e))
            return OCRResult(text="", confidence=0.0)

    def extract_table(
        self,
        image_bytes: bytes,
        page_number: int | None = None,
    ) -> ExtractedTable | None:
        """Extract table structure from image.

        Args:
            image_bytes: Image containing table
            page_number: Page number for metadata

        Returns:
            ExtractedTable with cells and structure, or None if no table found
        """
        engine = self._get_table_engine()
        if engine is None:
            return self._fallback_table_vlm(image_bytes, page_number)

        try:
            import numpy as np
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)

            result = engine(img_array)

            # Find table results
            tables = []
            for item in result:
                if item.get("type") == "table":
                    tables.append(item)

            if not tables:
                logger.info("no_table_detected")
                return None

            # Process first table (could extend to handle multiple)
            table_data = tables[0]
            html = table_data.get("res", {}).get("html", "")

            # Parse HTML to cells
            cells = self._parse_table_html(html)
            rows = max((c.row for c in cells), default=0) + 1
            cols = max((c.col for c in cells), default=0) + 1

            logger.info(
                "table_extracted",
                rows=rows,
                cols=cols,
                page=page_number,
            )

            return ExtractedTable(
                cells=cells,
                rows=rows,
                cols=cols,
                html=html,
                confidence=0.9,  # PPStructure confidence
                page_number=page_number,
            )

        except Exception as e:
            logger.error("table_extraction_failed", error=str(e))
            return self._fallback_table_vlm(image_bytes, page_number)

    def _parse_table_html(self, html: str) -> list[TableCell]:
        """Parse HTML table structure to cells."""
        cells = []

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table")
            if not table:
                return cells

            row_idx = 0
            for row in table.find_all("tr"):
                col_idx = 0
                for cell in row.find_all(["td", "th"]):
                    text = cell.get_text(strip=True)
                    is_header = cell.name == "th"
                    row_span = int(cell.get("rowspan", 1))
                    col_span = int(cell.get("colspan", 1))

                    cells.append(
                        TableCell(
                            text=text,
                            row=row_idx,
                            col=col_idx,
                            row_span=row_span,
                            col_span=col_span,
                            is_header=is_header,
                        )
                    )
                    col_idx += col_span
                row_idx += 1

        except ImportError:
            logger.warning("beautifulsoup_not_installed")
        except Exception as e:
            logger.warning("html_parse_failed", error=str(e))

        return cells

    def _fallback_table_vlm(
        self,
        image_bytes: bytes,
        page_number: int | None = None,
    ) -> ExtractedTable | None:
        """Fallback to VLM-based table extraction."""
        try:
            import litellm
            import json

            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            image_url = f"data:image/png;base64,{image_b64}"

            response = litellm.completion(
                model=self.vlm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Extract the table from this image. "
                                    "Return JSON with format: "
                                    '{"rows": [["cell1", "cell2"], ["cell3", "cell4"]]}'
                                ),
                            },
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                api_base=self.litellm_base_url,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            data = json.loads(content)
            rows_data = data.get("rows", [])

            if not rows_data:
                return None

            cells = []
            for row_idx, row in enumerate(rows_data):
                for col_idx, text in enumerate(row):
                    cells.append(
                        TableCell(
                            text=str(text),
                            row=row_idx,
                            col=col_idx,
                            is_header=(row_idx == 0),
                        )
                    )

            rows = len(rows_data)
            cols = max(len(row) for row in rows_data) if rows_data else 0

            logger.info(
                "vlm_table_fallback_used",
                rows=rows,
                cols=cols,
            )

            return ExtractedTable(
                cells=cells,
                rows=rows,
                cols=cols,
                confidence=0.7,
                page_number=page_number,
            )

        except Exception as e:
            logger.error("vlm_table_fallback_failed", error=str(e))
            return None

    def extract_tables(
        self,
        image_bytes: bytes,
        page_number: int | None = None,
    ) -> list[ExtractedTable]:
        """Extract all tables from an image.

        Args:
            image_bytes: Image content
            page_number: Page number for metadata

        Returns:
            List of ExtractedTable objects
        """
        engine = self._get_table_engine()
        if engine is None:
            table = self._fallback_table_vlm(image_bytes, page_number)
            return [table] if table else []

        try:
            import numpy as np
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)

            result = engine(img_array)

            tables = []
            for idx, item in enumerate(result):
                if item.get("type") == "table":
                    html = item.get("res", {}).get("html", "")
                    cells = self._parse_table_html(html)
                    rows = max((c.row for c in cells), default=0) + 1
                    cols = max((c.col for c in cells), default=0) + 1

                    bbox = item.get("bbox")
                    if bbox:
                        bbox = tuple(int(x) for x in bbox)

                    tables.append(
                        ExtractedTable(
                            cells=cells,
                            rows=rows,
                            cols=cols,
                            html=html,
                            confidence=0.9,
                            page_number=page_number,
                            bbox=bbox,
                        )
                    )

            logger.info(
                "tables_extracted",
                count=len(tables),
                page=page_number,
            )
            return tables

        except Exception as e:
            logger.error("tables_extraction_failed", error=str(e))
            return []

    def extract_formula(
        self,
        image_bytes: bytes,
        page_number: int | None = None,
    ) -> FormulaResult | None:
        """Extract mathematical formula as LaTeX.

        Args:
            image_bytes: Image containing formula
            page_number: Page number for metadata

        Returns:
            FormulaResult with LaTeX string, or None if no formula found
        """
        if not self.formula_enabled:
            return self._fallback_formula_vlm(image_bytes, page_number)

        try:
            # Try PaddleOCR formula module
            from paddleocr import PaddleOCR

            ocr = PaddleOCR(use_angle_cls=True, lang="en", use_gpu=self.use_gpu)

            import numpy as np
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)

            result = ocr.ocr(img_array, cls=True)

            if not result or not result[0]:
                return self._fallback_formula_vlm(image_bytes, page_number)

            # Extract text - for formulas, we typically get raw text
            # that needs LaTeX conversion
            texts = [line[1][0] for line in result[0]]
            raw_text = " ".join(texts)

            # Use VLM to convert to proper LaTeX
            return self._convert_to_latex(raw_text, image_bytes, page_number)

        except ImportError:
            return self._fallback_formula_vlm(image_bytes, page_number)
        except Exception as e:
            logger.error("formula_extraction_failed", error=str(e))
            return self._fallback_formula_vlm(image_bytes, page_number)

    def _fallback_formula_vlm(
        self,
        image_bytes: bytes,
        page_number: int | None = None,
    ) -> FormulaResult | None:
        """Fallback to VLM-based formula extraction."""
        try:
            import litellm

            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            image_url = f"data:image/png;base64,{image_b64}"

            response = litellm.completion(
                model=self.vlm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Extract the mathematical formula from this image. "
                                    "Return ONLY the LaTeX code, no explanation. "
                                    "Use proper LaTeX syntax including \\frac, \\sqrt, \\sum, etc."
                                ),
                            },
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                api_base=self.litellm_base_url,
            )

            latex = response.choices[0].message.content.strip()

            # Clean up LaTeX (remove markdown code blocks if present)
            if latex.startswith("```"):
                latex = latex.split("```")[1]
                if latex.startswith("latex"):
                    latex = latex[5:]
                latex = latex.strip()

            logger.info(
                "vlm_formula_extracted",
                latex_length=len(latex),
            )

            return FormulaResult(
                latex=latex,
                confidence=0.8,
                page_number=page_number,
            )

        except Exception as e:
            logger.error("vlm_formula_fallback_failed", error=str(e))
            return None

    def _convert_to_latex(
        self,
        raw_text: str,
        image_bytes: bytes,
        page_number: int | None = None,
    ) -> FormulaResult | None:
        """Convert raw formula text to LaTeX using VLM."""
        try:
            import litellm

            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            image_url = f"data:image/png;base64,{image_b64}"

            response = litellm.completion(
                model=self.vlm_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    f"OCR detected: {raw_text}\n\n"
                                    "Convert this to proper LaTeX notation. "
                                    "Return ONLY the LaTeX code."
                                ),
                            },
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                api_base=self.litellm_base_url,
            )

            latex = response.choices[0].message.content.strip()

            return FormulaResult(
                latex=latex,
                confidence=0.85,
                page_number=page_number,
            )

        except Exception as e:
            logger.error("latex_conversion_failed", error=str(e))
            return FormulaResult(
                latex=raw_text,
                confidence=0.5,
                page_number=page_number,
            )

    def analyze_layout(
        self,
        image_bytes: bytes,
    ) -> list[LayoutElement]:
        """Analyze document layout to detect regions.

        Args:
            image_bytes: Document page image

        Returns:
            List of LayoutElement with detected regions
        """
        engine = self._get_layout_engine()
        if engine is None:
            return []

        try:
            import numpy as np
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))
            img_array = np.array(img)

            result = engine(img_array)

            elements = []
            for item in result:
                element_type = item.get("type", "unknown")
                bbox = item.get("bbox", [0, 0, 0, 0])
                confidence = item.get("score", 0.0)
                text = (
                    item.get("res", {}).get("text", "")
                    if isinstance(item.get("res"), dict)
                    else None
                )

                elements.append(
                    LayoutElement(
                        element_type=element_type,
                        bbox=tuple(int(x) for x in bbox),
                        confidence=confidence,
                        text=text,
                    )
                )

            logger.info(
                "layout_analyzed",
                element_count=len(elements),
                types=[e.element_type for e in elements],
            )

            return elements

        except Exception as e:
            logger.error("layout_analysis_failed", error=str(e))
            return []

    def extract_formulas(
        self,
        image_bytes: bytes,
        page_number: int | None = None,
    ) -> list[FormulaResult]:
        """Extract all formulas from a document image.

        Uses layout analysis to find formula regions, then extracts each.

        Args:
            image_bytes: Document page image
            page_number: Page number for metadata

        Returns:
            List of FormulaResult objects
        """
        # First analyze layout to find formula regions
        elements = self.analyze_layout(image_bytes)
        formula_regions = [e for e in elements if e.element_type == "formula"]

        if not formula_regions:
            # Try extracting from full image
            result = self.extract_formula(image_bytes, page_number)
            return [result] if result else []

        formulas = []
        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))

            for region in formula_regions:
                # Crop to formula region
                x1, y1, x2, y2 = region.bbox
                cropped = img.crop((x1, y1, x2, y2))

                # Convert back to bytes
                buffer = io.BytesIO()
                cropped.save(buffer, format="PNG")
                region_bytes = buffer.getvalue()

                result = self.extract_formula(region_bytes, page_number)
                if result:
                    result.bbox = region.bbox
                    formulas.append(result)

        except Exception as e:
            logger.error("formula_region_extraction_failed", error=str(e))
            # Fall back to full image extraction
            result = self.extract_formula(image_bytes, page_number)
            if result:
                formulas.append(result)

        logger.info(
            "formulas_extracted",
            count=len(formulas),
            page=page_number,
        )

        return formulas


# Resource factory function
def paddleocr_resource(**kwargs) -> PaddleOCRResource:
    """Factory for PaddleOCR resource.

    Usage:
        @asset(resource_defs={"paddle": paddleocr_resource()})
        def my_asset(paddle: PaddleOCRResource):
            tables = paddle.extract_tables(image_bytes)
            return [t.to_markdown() for t in tables]
    """
    return PaddleOCRResource(**kwargs)
