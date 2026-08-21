"""
DLT Source for Universal Dependencies Celtic Treebanks.

Parses CoNLL-U format files from:
- UD_Irish-IDT, UD_Irish-Cadhan, UD_Irish-TwittIrish
- UD_Scottish_Gaelic-ARCOSG
- UD_Welsh-CCG
- UD_Breton-KEB
- UD_Manx-Cadhan
- UD_Old_Irish-DipSGG, UD_Old_Irish-DipWBG
- UD_Middle_Irish-CritMITB, UD_Middle_Irish-DipMITB
- UD_Archaic_Irish-OGAM
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterator, Optional, List, Dict

import dlt
from dlt.sources import DltResource


# Celtic language treebanks
CELTIC_TREEBANKS = {
    # Modern Irish
    "UD_Irish-IDT": {"language": "ga", "variety": "standard"},
    "UD_Irish-Cadhan": {"language": "ga", "variety": "historical"},
    "UD_Irish-TwittIrish": {"language": "ga", "variety": "twitter"},
    # Scottish Gaelic
    "UD_Scottish_Gaelic-ARCOSG": {"language": "gd", "variety": "standard"},
    # Welsh
    "UD_Welsh-CCG": {"language": "cy", "variety": "standard"},
    # Breton
    "UD_Breton-KEB": {"language": "br", "variety": "standard"},
    # Manx
    "UD_Manx-Cadhan": {"language": "gv", "variety": "standard"},
    # Old Irish
    "UD_Old_Irish-DipSGG": {"language": "sga", "variety": "st_gall"},
    "UD_Old_Irish-DipWBG": {"language": "sga", "variety": "wuerzburg"},
    # Middle Irish
    "UD_Middle_Irish-CritMITB": {"language": "mga", "variety": "critical"},
    "UD_Middle_Irish-DipMITB": {"language": "mga", "variety": "diplomatic"},
    # Archaic Irish
    "UD_Archaic_Irish-OGAM": {"language": "pgl", "variety": "ogham"},
}


@dlt.source(name="universal_dependencies")
def ud_source(
    ud_path: str = "repos/universal_dependencies",
    treebanks: Optional[List[str]] = None,
    splits: Optional[List[str]] = None,
) -> Iterator[DltResource]:
    """
    Source for Universal Dependencies Celtic treebanks.

    Args:
        ud_path: Path to UD treebanks directory (relative or absolute)
        treebanks: List of treebank names to process (None = all)
        splits: List of splits to process (train, dev, test). None = all.

    Yields:
        DLT resources for sentences and tokens
    """
    if splits is None:
        splits = ["train", "dev", "test"]

    if treebanks is None:
        treebanks = list(CELTIC_TREEBANKS.keys())

    @dlt.resource(
        name="sentences",
        write_disposition="merge",
        primary_key="sent_id",
    )
    def sentences_resource() -> Iterator[dict]:
        """Extract sentences from UD treebanks."""
        base_path = Path(ud_path)

        for treebank_name in treebanks:
            if treebank_name not in CELTIC_TREEBANKS:
                print(f"Unknown treebank: {treebank_name}")
                continue

            treebank_info = CELTIC_TREEBANKS[treebank_name]
            treebank_path = base_path / treebank_name

            if not treebank_path.exists():
                print(f"Treebank not found: {treebank_path}")
                continue

            # Find CoNLL-U files
            for split in splits:
                conllu_pattern = f"*-ud-{split}.conllu"
                for conllu_file in treebank_path.glob(conllu_pattern):
                    for sentence in _parse_conllu_sentences(conllu_file):
                        sentence["treebank"] = treebank_name
                        sentence["language"] = treebank_info["language"]
                        sentence["variety"] = treebank_info["variety"]
                        sentence["split"] = split
                        sentence["source_file"] = str(conllu_file)
                        yield sentence

    @dlt.resource(
        name="tokens",
        write_disposition="merge",
        primary_key="token_id",
    )
    def tokens_resource() -> Iterator[dict]:
        """Extract tokens with morphological features."""
        base_path = Path(ud_path)

        for treebank_name in treebanks:
            if treebank_name not in CELTIC_TREEBANKS:
                continue

            treebank_info = CELTIC_TREEBANKS[treebank_name]
            treebank_path = base_path / treebank_name

            if not treebank_path.exists():
                continue

            for split in splits:
                conllu_pattern = f"*-ud-{split}.conllu"
                for conllu_file in treebank_path.glob(conllu_pattern):
                    for token in _parse_conllu_tokens(conllu_file, treebank_name):
                        token["treebank"] = treebank_name
                        token["language"] = treebank_info["language"]
                        token["variety"] = treebank_info["variety"]
                        token["split"] = split
                        yield token

    @dlt.resource(
        name="morphological_features",
        write_disposition="merge",
        primary_key="feature_id",
    )
    def morphological_features_resource() -> Iterator[dict]:
        """Extract unique morphological feature combinations."""
        seen_features = set()
        base_path = Path(ud_path)

        for treebank_name in treebanks:
            if treebank_name not in CELTIC_TREEBANKS:
                continue

            treebank_info = CELTIC_TREEBANKS[treebank_name]
            treebank_path = base_path / treebank_name

            if not treebank_path.exists():
                continue

            for split in splits:
                conllu_pattern = f"*-ud-{split}.conllu"
                for conllu_file in treebank_path.glob(conllu_pattern):
                    for token in _parse_conllu_tokens(conllu_file, treebank_name):
                        feats = token.get("feats")
                        upos = token.get("upos")

                        if feats and upos:
                            feature_key = f"{treebank_info['language']}_{upos}_{feats}"
                            if feature_key not in seen_features:
                                seen_features.add(feature_key)
                                yield {
                                    "feature_id": feature_key,
                                    "language": treebank_info["language"],
                                    "upos": upos,
                                    "feats_string": feats,
                                    "feats_parsed": _parse_features(feats),
                                    "treebank": treebank_name,
                                }

    @dlt.resource(
        name="dependency_relations",
        write_disposition="merge",
        primary_key="relation_id",
    )
    def dependency_relations_resource() -> Iterator[dict]:
        """Extract dependency relation statistics."""
        relation_counts: Dict[str, Dict[str, int]] = {}
        base_path = Path(ud_path)

        for treebank_name in treebanks:
            if treebank_name not in CELTIC_TREEBANKS:
                continue

            treebank_info = CELTIC_TREEBANKS[treebank_name]
            treebank_path = base_path / treebank_name

            if not treebank_path.exists():
                continue

            lang = treebank_info["language"]
            if lang not in relation_counts:
                relation_counts[lang] = {}

            for split in splits:
                conllu_pattern = f"*-ud-{split}.conllu"
                for conllu_file in treebank_path.glob(conllu_pattern):
                    for token in _parse_conllu_tokens(conllu_file, treebank_name):
                        deprel = token.get("deprel")
                        if deprel:
                            relation_counts[lang][deprel] = relation_counts[lang].get(deprel, 0) + 1

        # Yield unique relations per language
        for lang, relations in relation_counts.items():
            for deprel, count in relations.items():
                yield {
                    "relation_id": f"{lang}_{deprel}",
                    "language": lang,
                    "deprel": deprel,
                    "count": count,
                }

    yield sentences_resource
    yield tokens_resource
    yield morphological_features_resource
    yield dependency_relations_resource


def _parse_conllu_sentences(filepath: Path) -> Iterator[dict]:
    """Parse sentences from a CoNLL-U file."""
    current_sentence: Dict[str, any] = {}
    current_tokens: List[dict] = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                # End of sentence
                if current_sentence.get("sent_id"):
                    current_sentence["token_count"] = len(current_tokens)
                    current_sentence["tokens"] = current_tokens
                    yield current_sentence
                current_sentence = {}
                current_tokens = []
                continue

            if line.startswith("#"):
                # Metadata comment
                if line.startswith("# sent_id"):
                    match = re.match(r"# sent_id\s*=\s*(.+)", line)
                    if match:
                        current_sentence["sent_id"] = match.group(1).strip()
                elif line.startswith("# text"):
                    match = re.match(r"# text\s*=\s*(.+)", line)
                    if match:
                        current_sentence["text"] = match.group(1).strip()
                continue

            # Token line
            fields = line.split("\t")
            if len(fields) >= 10:
                token = _parse_token_line(fields)
                if token:
                    current_tokens.append(token)

    # Handle last sentence
    if current_sentence.get("sent_id"):
        current_sentence["token_count"] = len(current_tokens)
        current_sentence["tokens"] = current_tokens
        yield current_sentence


def _parse_conllu_tokens(filepath: Path, treebank: str) -> Iterator[dict]:
    """Parse individual tokens from a CoNLL-U file."""
    current_sent_id = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith("# sent_id"):
                match = re.match(r"# sent_id\s*=\s*(.+)", line)
                if match:
                    current_sent_id = match.group(1).strip()
                continue

            if line.startswith("#"):
                continue

            # Token line
            fields = line.split("\t")
            if len(fields) >= 10:
                token = _parse_token_line(fields)
                if token:
                    token["sent_id"] = current_sent_id
                    token["token_id"] = f"{treebank}_{current_sent_id}_{token['id']}"
                    yield token


def _parse_token_line(fields: List[str]) -> Optional[dict]:
    """Parse a single token line from CoNLL-U format."""
    token_id = fields[0]

    # Skip multiword tokens (e.g., "1-2") and empty nodes (e.g., "2.1")
    if "-" in token_id or "." in token_id:
        return None

    return {
        "id": token_id,
        "form": fields[1] if fields[1] != "_" else None,
        "lemma": fields[2] if fields[2] != "_" else None,
        "upos": fields[3] if fields[3] != "_" else None,
        "xpos": fields[4] if fields[4] != "_" else None,
        "feats": fields[5] if fields[5] != "_" else None,
        "head": fields[6] if fields[6] != "_" else None,
        "deprel": fields[7] if fields[7] != "_" else None,
        "deps": fields[8] if fields[8] != "_" else None,
        "misc": fields[9] if fields[9] != "_" else None,
    }


def _parse_features(feats_string: str) -> dict:
    """Parse UD morphological features string into a dict."""
    if not feats_string or feats_string == "_":
        return {}

    result = {}
    for feat in feats_string.split("|"):
        if "=" in feat:
            key, value = feat.split("=", 1)
            result[key] = value
    return result


# Celtic-specific feature extraction functions
def extract_mutation_features(token: dict) -> Optional[dict]:
    """Extract Celtic initial mutation features from a token."""
    feats = token.get("feats", "")
    if not feats:
        return None

    mutation = None
    if "Form=Len" in feats:
        mutation = "lenition"
    elif "Form=Ecl" in feats:
        mutation = "eclipsis"
    elif "Form=HPref" in feats:
        mutation = "h_prefix"

    if mutation:
        return {
            "token_id": token.get("token_id"),
            "form": token.get("form"),
            "lemma": token.get("lemma"),
            "mutation_type": mutation,
        }
    return None


def extract_verb_features(token: dict) -> Optional[dict]:
    """Extract Celtic verb features from a token."""
    if token.get("upos") != "VERB":
        return None

    feats = _parse_features(token.get("feats", ""))
    if not feats:
        return None

    return {
        "token_id": token.get("token_id"),
        "lemma": token.get("lemma"),
        "form": token.get("form"),
        "tense": feats.get("Tense"),
        "mood": feats.get("Mood"),
        "person": feats.get("Person"),
        "number": feats.get("Number"),
        "polarity": feats.get("Polarity"),
        "voice": feats.get("Voice"),
    }
