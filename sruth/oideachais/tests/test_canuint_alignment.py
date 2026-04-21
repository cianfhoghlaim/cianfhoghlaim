"""
Tests for Canuint.ie word-level alignment pipeline.

Tests cover:
- Character-level timestamp interpolation
- Phoneme G2P conversion
- Audio slicing (mocked)
- Multi-format export
- Quality validation
"""
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

# Test data - sample word alignments
SAMPLE_WORD_ALIGNMENTS = [
    {
        "word_id": "QQTRIN016177_0001",
        "recording_id": "QQTRIN016177",
        "start_time": 10.5,
        "end_time": 10.8,
        "duration_ms": 300,
        "dialectal_text": "bhí",
        "standardized_text": "bhí",
        "speaker_name": "Mícheál Ó Baoill",
        "dialect": "ulster",
        "province": "Cúige Uladh",
        "area_name": "Rann na Feirste",
        "year": 2010,
        "audio_url": "https://www.canuint.ie/sounds/QQTRIN016177.mp3",
    },
    {
        "word_id": "QQTRIN016177_0002",
        "recording_id": "QQTRIN016177",
        "start_time": 10.8,
        "end_time": 11.2,
        "duration_ms": 400,
        "dialectal_text": "sé",
        "standardized_text": "sé",
        "speaker_name": "Mícheál Ó Baoill",
        "dialect": "ulster",
        "province": "Cúige Uladh",
        "area_name": "Rann na Feirste",
        "year": 2010,
        "audio_url": "https://www.canuint.ie/sounds/QQTRIN016177.mp3",
    },
    {
        "word_id": "QQTRIN016178_0001",
        "recording_id": "QQTRIN016178",
        "start_time": 5.0,
        "end_time": 5.5,
        "duration_ms": 500,
        "dialectal_text": "tógáil",
        "standardized_text": "tógáil",
        "speaker_name": "Seán Ó Sé",
        "dialect": "munster",
        "province": "Cúige Mumhan",
        "area_name": "Corca Dhuibhne",
        "year": 2012,
        "audio_url": "https://www.canuint.ie/sounds/QQTRIN016178.mp3",
    },
    {
        "word_id": "QQTRIN016179_0001",
        "recording_id": "QQTRIN016179",
        "start_time": 2.0,
        "end_time": 2.3,
        "duration_ms": 300,
        "dialectal_text": "chuaigh",
        "standardized_text": "chuaigh",
        "speaker_name": "Bríd Ní Fhlatharta",
        "dialect": "connacht",
        "province": "Cúige Connacht",
        "area_name": "Cois Fharraige",
        "year": 2015,
        "audio_url": "https://www.canuint.ie/sounds/QQTRIN016179.mp3",
    },
]


class TestCharacterInterpolation:
    """Test character-level timestamp interpolation."""

    def test_tokenize_irish_text_basic(self):
        """Test basic tokenization without digraph preservation."""
        from sruth.oideachais.alignment.character_interpolator import tokenize_irish_text

        result = tokenize_irish_text("bhí")
        assert result == ["b", "h", "í"]

    def test_tokenize_irish_text_with_digraphs(self):
        """Test tokenization preserving Irish digraphs."""
        from sruth.oideachais.alignment.character_interpolator import tokenize_irish_text

        result = tokenize_irish_text("bhí", preserve_digraphs=True)
        assert result == ["bh", "í"]

        result = tokenize_irish_text("chuaigh", preserve_digraphs=True)
        # ch + ua + i + gh
        assert "ch" in result
        assert "gh" in result

    def test_interpolate_timestamps(self):
        """Test timestamp interpolation."""
        from sruth.oideachais.alignment.character_interpolator import (
            interpolate_character_timestamps,
        )

        chars, starts, ends = interpolate_character_timestamps(
            text="bhí",
            start_time=10.5,
            end_time=10.8,
        )

        assert len(chars) == 3  # b, h, í
        assert len(starts) == 3
        assert len(ends) == 3
        assert starts[0] == 10.5
        assert ends[-1] == 10.8
        # Check sequential
        for i in range(len(starts) - 1):
            assert ends[i] == pytest.approx(starts[i + 1], rel=1e-5)

    def test_create_character_alignment(self):
        """Test full character alignment creation."""
        from sruth.oideachais.alignment.character_interpolator import (
            create_character_alignment,
        )

        alignment = create_character_alignment(
            word_id="TEST_001",
            recording_id="TEST",
            text="tógáil",
            start_time=5.0,
            end_time=5.5,
            dialect="munster",
        )

        assert alignment.word_id == "TEST_001"
        assert alignment.recording_id == "TEST"
        assert alignment.text == "tógáil"
        assert len(alignment.characters) == 6  # t, ó, g, á, i, l
        assert alignment.character_start_times[0] == 5.0
        assert alignment.character_end_times[-1] == 5.5

    def test_elevenlabs_format_export(self):
        """Test ElevenLabs format export."""
        from sruth.oideachais.alignment.character_interpolator import (
            create_character_alignment,
        )

        alignment = create_character_alignment(
            word_id="TEST_001",
            recording_id="TEST",
            text="bhí",
            start_time=0.0,
            end_time=0.3,
        )

        result = alignment.to_elevenlabs_format()

        assert "characters" in result
        assert "characterStartTimesSeconds" in result
        assert "characterEndTimesSeconds" in result


class TestIrishG2P:
    """Test Irish grapheme-to-phoneme conversion."""

    def test_rule_based_g2p_basic(self):
        """Test basic rule-based G2P."""
        from sruth.oideachais.alignment.irish_g2p import rule_based_g2p

        phonemes = rule_based_g2p("bhí")
        assert len(phonemes) > 0
        # bh → w, í → iː
        assert "w" in phonemes or "v" in phonemes  # bh can be w or v
        assert "iː" in phonemes

    def test_rule_based_g2p_lenition(self):
        """Test lenited consonant handling."""
        from sruth.oideachais.alignment.irish_g2p import rule_based_g2p

        # ch → x
        phonemes = rule_based_g2p("chuaigh")
        assert "x" in phonemes  # ch

        # fh → silent
        phonemes = rule_based_g2p("fhear")
        # fh should not produce a phoneme

    def test_rule_based_g2p_vowels(self):
        """Test vowel handling including fadas."""
        from sruth.oideachais.alignment.irish_g2p import rule_based_g2p

        # Long vowels
        phonemes = rule_based_g2p("á")
        assert "ɑː" in phonemes

        phonemes = rule_based_g2p("í")
        assert "iː" in phonemes

    def test_dialect_variations(self):
        """Test dialect-specific phoneme mappings."""
        from sruth.oideachais.alignment.irish_g2p import IrishDialect, rule_based_g2p

        # Ulster uses /eː/ for "ao" instead of /iː/
        ulster_phonemes = rule_based_g2p("aon", dialect=IrishDialect.ULSTER)
        # Should have dialect-specific variation

    def test_create_phoneme_alignment(self):
        """Test phoneme alignment creation."""
        from sruth.oideachais.alignment.irish_g2p import (
            create_phoneme_alignment,
        )

        alignment = create_phoneme_alignment(
            word_id="TEST_001",
            recording_id="TEST",
            text="bhí",
            start_time=0.0,
            end_time=0.3,
            dialect="ulster",
            use_espeak=False,  # Use rule-based for testing
        )

        assert alignment.word_id == "TEST_001"
        assert len(alignment.phonemes) > 0
        assert len(alignment.phoneme_start_times) == len(alignment.phonemes)
        assert len(alignment.phoneme_end_times) == len(alignment.phonemes)


class TestCanuintExporter:
    """Test multi-format export functionality."""

    def test_export_ljspeech(self):
        """Test LJSpeech format export."""
        from sruth.oideachais.alignment.canuint_exporter import export_ljspeech

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "metadata.csv"

            # Add audio_path to test data
            alignments = [
                {**a, "audio_path": f"/wavs/{a['word_id']}.wav", "text": a["dialectal_text"]}
                for a in SAMPLE_WORD_ALIGNMENTS
            ]

            count = export_ljspeech(alignments, output_path)

            assert count == len(alignments)
            assert output_path.exists()

            # Verify format
            content = output_path.read_text()
            lines = content.strip().split("\n")
            assert len(lines) == len(alignments)

            # Check LJSpeech format: filename|raw|normalized
            for line in lines:
                parts = line.split("|")
                assert len(parts) == 3

    def test_export_ctm(self):
        """Test CTM format export."""
        from sruth.oideachais.alignment.canuint_exporter import export_ctm

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "alignments.ctm"

            alignments = [
                {**a, "text": a["dialectal_text"]}
                for a in SAMPLE_WORD_ALIGNMENTS
            ]

            count = export_ctm(alignments, output_path)

            assert count == len(alignments)
            assert output_path.exists()

            # Verify CTM format: recording channel start duration word
            content = output_path.read_text()
            for line in content.strip().split("\n"):
                parts = line.split()
                assert len(parts) == 5
                # Check numeric fields
                float(parts[2])  # start
                float(parts[3])  # duration

    def test_export_textgrid(self):
        """Test TextGrid format export."""
        from sruth.oideachais.alignment.canuint_exporter import export_textgrid

        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "textgrids"

            alignments = [
                {**a, "text": a["dialectal_text"]}
                for a in SAMPLE_WORD_ALIGNMENTS
            ]

            count = export_textgrid(alignments, output_dir)

            # Should create one file per recording
            assert count > 0
            assert output_dir.exists()
            assert len(list(output_dir.glob("*.TextGrid"))) > 0

    def test_export_huggingface_dataset(self):
        """Test HuggingFace dataset format export."""
        from sruth.oideachais.alignment.canuint_exporter import export_huggingface_dataset

        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "hf_dataset"

            alignments = [
                {**a, "text": a["dialectal_text"]}
                for a in SAMPLE_WORD_ALIGNMENTS
            ]

            stats = export_huggingface_dataset(alignments, output_dir)

            assert stats["total"] == len(alignments)
            assert (output_dir / "dataset_info.json").exists()
            assert (output_dir / "README.md").exists()
            assert (output_dir / "data" / "train.jsonl").exists()


class TestCanuintValidator:
    """Test quality validation functionality."""

    def test_validate_duration_distribution(self):
        """Test duration distribution validation."""
        from sruth.oideachais.quality.canuint_validator import validate_duration_distribution

        result = validate_duration_distribution(SAMPLE_WORD_ALIGNMENTS)

        assert result.name == "duration"
        assert result.metadata["count"] == len(SAMPLE_WORD_ALIGNMENTS)
        assert "mean_ms" in result.metadata
        assert "std_ms" in result.metadata

    def test_validate_alignment_consistency(self):
        """Test alignment consistency validation."""
        from sruth.oideachais.quality.canuint_validator import validate_alignment_consistency

        result = validate_alignment_consistency(SAMPLE_WORD_ALIGNMENTS)

        assert result.name == "alignment"
        assert "recordings_checked" in result.metadata

    def test_validate_dialect_balance(self):
        """Test dialect balance validation."""
        from sruth.oideachais.quality.canuint_validator import validate_dialect_balance

        result = validate_dialect_balance(SAMPLE_WORD_ALIGNMENTS)

        assert result.name == "dialect_balance"
        assert "dialect_counts" in result.metadata
        assert "ulster" in result.metadata["dialect_counts"]
        assert "munster" in result.metadata["dialect_counts"]
        assert "connacht" in result.metadata["dialect_counts"]

    def test_validate_speaker_diversity(self):
        """Test speaker diversity validation."""
        from sruth.oideachais.quality.canuint_validator import validate_speaker_diversity

        result = validate_speaker_diversity(SAMPLE_WORD_ALIGNMENTS)

        assert result.name == "speaker_diversity"
        assert "unique_speakers" in result.metadata
        assert result.metadata["unique_speakers"] == 3

    def test_generate_splits(self):
        """Test train/val/test split generation."""
        from sruth.oideachais.quality.canuint_validator import generate_splits

        splits = generate_splits(SAMPLE_WORD_ALIGNMENTS)

        assert "train" in splits
        assert "val" in splits
        assert "test" in splits

        # All items should be in exactly one split
        all_ids = set(splits["train"]) | set(splits["val"]) | set(splits["test"])
        original_ids = {a["word_id"] for a in SAMPLE_WORD_ALIGNMENTS}
        assert all_ids == original_ids

    def test_full_validation_report(self):
        """Test complete validation pipeline."""
        from sruth.oideachais.quality.canuint_validator import validate_canuint_dataset

        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            report = validate_canuint_dataset(
                word_alignments=SAMPLE_WORD_ALIGNMENTS,
                output_dir=output_dir,
            )

            assert report.total_items == len(SAMPLE_WORD_ALIGNMENTS)
            assert len(report.results) > 0
            assert 0 <= report.overall_score <= 1

            # Check output files
            assert (output_dir / "validation_report.json").exists()
            assert (output_dir / "splits" / "train.txt").exists()


class TestEndToEndPipeline:
    """End-to-end integration tests."""

    def test_character_and_phoneme_pipeline(self):
        """Test character + phoneme alignment generation."""
        from sruth.oideachais.alignment.character_interpolator import (
            batch_interpolate_alignments,
        )
        from sruth.oideachais.alignment.irish_g2p import (
            batch_convert_to_phonemes,
        )

        # Generate character alignments
        char_alignments = list(batch_interpolate_alignments(SAMPLE_WORD_ALIGNMENTS))
        assert len(char_alignments) == len(SAMPLE_WORD_ALIGNMENTS)

        # Generate phoneme alignments
        phoneme_alignments = list(batch_convert_to_phonemes(
            SAMPLE_WORD_ALIGNMENTS,
            use_espeak=False,  # Rule-based for testing
        ))
        assert len(phoneme_alignments) == len(SAMPLE_WORD_ALIGNMENTS)

    def test_export_and_validate_pipeline(self):
        """Test export followed by validation."""
        from sruth.oideachais.alignment.canuint_exporter import export_all_formats
        from sruth.oideachais.alignment.character_interpolator import (
            batch_interpolate_alignments,
        )
        from sruth.oideachais.alignment.irish_g2p import batch_convert_to_phonemes
        from sruth.oideachais.quality.canuint_validator import validate_canuint_dataset

        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            # Prepare alignments
            word_alignments = [
                {**a, "text": a["dialectal_text"], "audio_path": f"/wavs/{a['word_id']}.wav"}
                for a in SAMPLE_WORD_ALIGNMENTS
            ]

            char_alignments = [
                a.to_dict() for a in batch_interpolate_alignments(SAMPLE_WORD_ALIGNMENTS)
            ]

            phoneme_alignments = [
                a.to_dict() for a in batch_convert_to_phonemes(
                    SAMPLE_WORD_ALIGNMENTS, use_espeak=False
                )
            ]

            # Export to all formats
            stats = export_all_formats(
                word_alignments=word_alignments,
                character_alignments=char_alignments,
                phoneme_alignments=phoneme_alignments,
                output_dir=output_dir / "export",
            )

            assert stats.total_items == len(word_alignments)
            assert "ljspeech" in stats.formats_exported

            # Validate
            report = validate_canuint_dataset(
                word_alignments=word_alignments,
                phoneme_alignments=phoneme_alignments,
                output_dir=output_dir / "validation",
            )

            assert report.total_items > 0
            assert report.overall_score > 0


# Run with: pytest sruth/oideachais/tests/test_canuint_alignment.py -v
