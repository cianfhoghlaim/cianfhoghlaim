"""
Dagster Assets for Irish Education Pipeline.

Provides materialized assets for curriculum processing:
- Grammar validation with Gramadóir
- PDF extraction benchmarking with PDFStract patterns
- HTR model comparison
- Syntactic parsing with UD treebanks
"""
from __future__ import annotations

from .grammar_validation import (
    GramadoirValidator,
    GrammarIssue,
    GrammarValidationResult,
    grammar_validated_curriculum,
)
from .pdf_benchmark import (
    PDFBenchmarkResult,
    PDFExtractorComparison,
    pdf_extraction_benchmark,
)
from .syntactic_parsing import (
    IrishSyntacticParser,
    ParseResult,
    Sentence,
    Token,
    get_treebank_stats,
    load_treebank,
    syntactic_parsed_curriculum,
)

__all__ = [
    # Grammar validation
    "GramadoirValidator",
    "GrammarIssue",
    "GrammarValidationResult",
    "grammar_validated_curriculum",
    # PDF benchmarking
    "PDFBenchmarkResult",
    "PDFExtractorComparison",
    "pdf_extraction_benchmark",
    # Syntactic parsing
    "IrishSyntacticParser",
    "Token",
    "Sentence",
    "ParseResult",
    "load_treebank",
    "get_treebank_stats",
    "syntactic_parsed_curriculum",
]
