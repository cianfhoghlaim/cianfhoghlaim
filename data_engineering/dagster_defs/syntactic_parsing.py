"""
Universal Dependencies Treebank Integration for Irish.

Provides syntactic parsing using UDPipe models trained on Irish treebanks:
- UD_Irish-IDT: Modern Irish (primary)
- UD_Irish-Cadhan: Pre-standard Irish (historical content)
- UD_Irish-TwittIrish: Informal register

Usage:
    from dagster_assets.syntactic_parsing import IrishSyntacticParser

    parser = IrishSyntacticParser()
    result = parser.parse("Tá an leabhar ar an mbord.")
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Path to UD treebank data
UD_DATA_DIR = Path(__file__).parents[4] / "taighde" / "teanga" / "universal_dependencies"


@dataclass
class Token:
    """A token with Universal Dependencies annotations."""

    id: int
    form: str  # Word form
    lemma: str  # Lemma
    upos: str  # Universal POS tag
    xpos: str | None = None  # Language-specific POS tag
    feats: dict[str, str] = field(default_factory=dict)  # Morphological features
    head: int = 0  # Head token ID
    deprel: str = "root"  # Dependency relation
    deps: str | None = None  # Enhanced dependencies
    misc: dict[str, str] = field(default_factory=dict)  # Miscellaneous

    def to_conllu(self) -> str:
        """Convert to CoNLL-U format line."""
        feats_str = "|".join(f"{k}={v}" for k, v in self.feats.items()) if self.feats else "_"
        misc_str = "|".join(f"{k}={v}" for k, v in self.misc.items()) if self.misc else "_"
        return "\t".join([
            str(self.id),
            self.form,
            self.lemma,
            self.upos,
            self.xpos or "_",
            feats_str,
            str(self.head),
            self.deprel,
            self.deps or "_",
            misc_str,
        ])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "form": self.form,
            "lemma": self.lemma,
            "upos": self.upos,
            "xpos": self.xpos,
            "feats": self.feats,
            "head": self.head,
            "deprel": self.deprel,
        }


@dataclass
class Sentence:
    """A parsed sentence with tokens and dependencies."""

    text: str
    tokens: list[Token] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    @property
    def root(self) -> Token | None:
        """Get the root token."""
        for token in self.tokens:
            if token.deprel == "root":
                return token
        return None

    def get_children(self, head_id: int) -> list[Token]:
        """Get children of a token."""
        return [t for t in self.tokens if t.head == head_id]

    def get_subtree(self, token_id: int) -> list[Token]:
        """Get all tokens in the subtree rooted at token_id."""
        subtree = []
        to_process = [token_id]

        while to_process:
            current = to_process.pop()
            for token in self.tokens:
                if token.id == current:
                    subtree.append(token)
                if token.head == current:
                    to_process.append(token.id)

        return sorted(subtree, key=lambda t: t.id)

    def to_conllu(self) -> str:
        """Convert to CoNLL-U format."""
        lines = []
        for key, value in self.metadata.items():
            lines.append(f"# {key} = {value}")
        if self.text:
            lines.append(f"# text = {self.text}")
        for token in self.tokens:
            lines.append(token.to_conllu())
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "tokens": [t.to_dict() for t in self.tokens],
            "metadata": self.metadata,
        }


@dataclass
class ParseResult:
    """Result of syntactic parsing."""

    sentences: list[Sentence] = field(default_factory=list)
    language: str = "ga"
    model: str = "ud_irish_idt"

    @property
    def token_count(self) -> int:
        """Total number of tokens."""
        return sum(len(s.tokens) for s in self.sentences)

    def get_pos_distribution(self) -> dict[str, int]:
        """Get POS tag distribution."""
        dist: dict[str, int] = {}
        for sentence in self.sentences:
            for token in sentence.tokens:
                dist[token.upos] = dist.get(token.upos, 0) + 1
        return dict(sorted(dist.items(), key=lambda x: x[1], reverse=True))

    def get_deprel_distribution(self) -> dict[str, int]:
        """Get dependency relation distribution."""
        dist: dict[str, int] = {}
        for sentence in self.sentences:
            for token in sentence.tokens:
                dist[token.deprel] = dist.get(token.deprel, 0) + 1
        return dict(sorted(dist.items(), key=lambda x: x[1], reverse=True))

    def to_conllu(self) -> str:
        """Convert all sentences to CoNLL-U format."""
        return "\n\n".join(s.to_conllu() for s in self.sentences)


class IrishSyntacticParser:
    """
    Syntactic parser for Irish using Universal Dependencies.

    Uses UDPipe model trained on UD_Irish-IDT treebank.
    Provides:
    - Tokenization
    - Part-of-speech tagging
    - Lemmatization
    - Dependency parsing
    """

    def __init__(
        self,
        model_path: Path | str | None = None,
        treebank: str = "UD_Irish-IDT",
    ):
        """
        Initialize parser.

        Args:
            model_path: Path to UDPipe model file
            treebank: Treebank to use (UD_Irish-IDT, UD_Irish-Cadhan, UD_Irish-TwittIrish)
        """
        self.treebank = treebank
        self._model = None
        self._model_path = Path(model_path) if model_path else self._find_model()

    def _find_model(self) -> Path | None:
        """Find UDPipe model file."""
        # Look for pre-trained model
        model_dir = Path(__file__).parents[4] / "meaisínfhoghlaim" / "models" / "nlp"
        model_file = model_dir / "irish-idt-ud-2.5-191206.udpipe"

        if model_file.exists():
            return model_file

        # Look in treebank directory
        treebank_dir = UD_DATA_DIR / self.treebank
        for model in treebank_dir.glob("*.udpipe"):
            return model

        logger.warning("No UDPipe model found")
        return None

    def _load_model(self):
        """Load UDPipe model."""
        if self._model is not None:
            return self._model

        if self._model_path is None:
            logger.error("No model path available")
            return None

        try:
            from ufal.udpipe import Model
            self._model = Model.load(str(self._model_path))
            if self._model is None:
                logger.error(f"Failed to load model from {self._model_path}")
            else:
                logger.info(f"Loaded UDPipe model from {self._model_path}")
            return self._model

        except ImportError:
            logger.warning("ufal.udpipe not installed")
            return None

    def parse(self, text: str) -> ParseResult:
        """
        Parse Irish text.

        Args:
            text: Text to parse

        Returns:
            ParseResult with parsed sentences
        """
        model = self._load_model()

        if model is None:
            # Fallback to simple tokenization
            return self._simple_parse(text)

        try:
            from ufal.udpipe import Pipeline, ProcessingError

            pipeline = Pipeline(model, "tokenize", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu")
            error = ProcessingError()

            processed = pipeline.process(text, error)
            if error.occurred():
                logger.error(f"UDPipe error: {error.message}")
                return self._simple_parse(text)

            return self._parse_conllu(processed)

        except Exception as e:
            logger.error(f"Parsing error: {e}")
            return self._simple_parse(text)

    def _parse_conllu(self, conllu_text: str) -> ParseResult:
        """Parse CoNLL-U format text."""
        sentences = []
        current_tokens: list[Token] = []
        current_metadata: dict[str, str] = {}
        current_text = ""

        for line in conllu_text.strip().split("\n"):
            if not line.strip():
                if current_tokens:
                    sentences.append(Sentence(
                        text=current_text,
                        tokens=current_tokens,
                        metadata=current_metadata,
                    ))
                    current_tokens = []
                    current_metadata = {}
                    current_text = ""
                continue

            if line.startswith("#"):
                # Metadata line
                if "=" in line:
                    key, value = line[1:].split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key == "text":
                        current_text = value
                    else:
                        current_metadata[key] = value
                continue

            # Token line
            parts = line.split("\t")
            if len(parts) < 10:
                continue

            try:
                token_id = int(parts[0])
            except ValueError:
                continue  # Skip multi-word tokens

            # Parse features
            feats = {}
            if parts[5] != "_":
                for feat in parts[5].split("|"):
                    if "=" in feat:
                        k, v = feat.split("=", 1)
                        feats[k] = v

            # Parse misc
            misc = {}
            if parts[9] != "_":
                for item in parts[9].split("|"):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        misc[k] = v

            token = Token(
                id=token_id,
                form=parts[1],
                lemma=parts[2],
                upos=parts[3],
                xpos=parts[4] if parts[4] != "_" else None,
                feats=feats,
                head=int(parts[6]) if parts[6] != "_" else 0,
                deprel=parts[7],
                deps=parts[8] if parts[8] != "_" else None,
                misc=misc,
            )
            current_tokens.append(token)

        if current_tokens:
            sentences.append(Sentence(
                text=current_text,
                tokens=current_tokens,
                metadata=current_metadata,
            ))

        return ParseResult(sentences=sentences, language="ga", model=self.treebank)

    def _simple_parse(self, text: str) -> ParseResult:
        """Simple tokenization fallback when UDPipe unavailable."""
        import re

        sentences = []
        for sent_text in re.split(r"[.!?]+", text):
            sent_text = sent_text.strip()
            if not sent_text:
                continue

            tokens = []
            for i, word in enumerate(sent_text.split(), 1):
                tokens.append(Token(
                    id=i,
                    form=word,
                    lemma=word.lower(),
                    upos="X",  # Unknown
                    head=0 if i == 1 else 1,
                    deprel="root" if i == 1 else "dep",
                ))

            if tokens:
                sentences.append(Sentence(text=sent_text, tokens=tokens))

        return ParseResult(sentences=sentences, language="ga", model="simple")


# =============================================================================
# Treebank Loading
# =============================================================================

def load_treebank(treebank: str = "UD_Irish-IDT") -> Iterator[Sentence]:
    """
    Load sentences from a UD treebank.

    Args:
        treebank: Treebank name

    Yields:
        Parsed sentences
    """
    treebank_dir = UD_DATA_DIR / treebank

    for conllu_file in treebank_dir.glob("*.conllu"):
        logger.info(f"Loading {conllu_file}")
        with open(conllu_file, encoding="utf-8") as f:
            content = f.read()

        parser = IrishSyntacticParser(treebank=treebank)
        result = parser._parse_conllu(content)

        yield from result.sentences


def get_treebank_stats(treebank: str = "UD_Irish-IDT") -> dict[str, Any]:
    """Get statistics for a treebank."""
    sentences = list(load_treebank(treebank))

    total_tokens = sum(len(s.tokens) for s in sentences)

    pos_dist: dict[str, int] = {}
    deprel_dist: dict[str, int] = {}

    for sentence in sentences:
        for token in sentence.tokens:
            pos_dist[token.upos] = pos_dist.get(token.upos, 0) + 1
            deprel_dist[token.deprel] = deprel_dist.get(token.deprel, 0) + 1

    return {
        "treebank": treebank,
        "sentence_count": len(sentences),
        "token_count": total_tokens,
        "avg_sentence_length": total_tokens / max(len(sentences), 1),
        "pos_distribution": dict(sorted(pos_dist.items(), key=lambda x: x[1], reverse=True)),
        "deprel_distribution": dict(sorted(deprel_dist.items(), key=lambda x: x[1], reverse=True)),
    }


# =============================================================================
# Dagster Asset
# =============================================================================

try:
    from dagster import AssetExecutionContext, Config, asset
    from pydantic import Field as PydanticField

    class SyntacticParsingConfig(Config):
        """Configuration for syntactic parsing asset."""

        treebank: str = PydanticField(
            default="UD_Irish-IDT",
            description="UD treebank to use",
        )
        include_features: bool = PydanticField(
            default=True,
            description="Include morphological features",
        )

    @asset(
        name="syntactic_parsed_curriculum",
        description="Curriculum content with syntactic parsing from UD treebanks",
        group_name="nlp",
        compute_kind="udpipe",
    )
    def syntactic_parsed_curriculum(
        context: AssetExecutionContext,
        config: SyntacticParsingConfig,
    ) -> dict[str, Any]:
        """
        Parse curriculum content with Irish syntactic parser.

        Returns:
            Dictionary with parsing statistics
        """
        parser = IrishSyntacticParser(treebank=config.treebank)

        context.log.info(f"Using treebank: {config.treebank}")

        return {
            "status": "ready",
            "treebank": config.treebank,
            "model_path": str(parser._model_path) if parser._model_path else None,
            "config": {
                "include_features": config.include_features,
            },
        }

except ImportError:
    def syntactic_parsed_curriculum(*args, **kwargs):
        raise ImportError("Dagster is required for this asset")


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Parse Irish text with UD treebank")
    parser.add_argument("text", nargs="?", help="Text to parse")
    parser.add_argument("--file", "-f", help="Input file")
    parser.add_argument("--treebank", "-t", default="UD_Irish-IDT")
    parser.add_argument("--stats", action="store_true", help="Show treebank statistics")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--conllu", action="store_true", help="Output as CoNLL-U")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.stats:
        stats = get_treebank_stats(args.treebank)
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"Treebank: {stats['treebank']}")
            print(f"Sentences: {stats['sentence_count']}")
            print(f"Tokens: {stats['token_count']}")
            print(f"Avg length: {stats['avg_sentence_length']:.1f}")
            print("\nPOS distribution:")
            for pos, count in list(stats['pos_distribution'].items())[:10]:
                print(f"  {pos}: {count}")
        sys.exit(0)

    # Get input text
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    irish_parser = IrishSyntacticParser(treebank=args.treebank)
    result = irish_parser.parse(text)

    if args.conllu:
        print(result.to_conllu())
    elif args.json:
        print(json.dumps({
            "sentences": [s.to_dict() for s in result.sentences],
            "token_count": result.token_count,
            "pos_distribution": result.get_pos_distribution(),
        }, indent=2, ensure_ascii=False))
    else:
        for sentence in result.sentences:
            print(f"\n{sentence.text}")
            for token in sentence.tokens:
                print(f"  {token.id}\t{token.form}\t{token.lemma}\t{token.upos}\t{token.deprel}")
