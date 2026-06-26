"""
End-to-End Tests for Irish Audio Training Pipeline.

Tests the complete pipeline from data sources through training:
1. DLT sources (EdcoLearning, SEC transcripts)
2. Dagster assets (unified audio dataset)
3. Utilities (dialect classifier, transcript aligner)
4. Modal training configs

Run with:
    pytest tests/test_audio_pipeline.py -v
    pytest tests/test_audio_pipeline.py -k "dlt" -v  # Just DLT tests
    pytest tests/test_audio_pipeline.py -k "classifier" -v  # Just classifier tests
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest

# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_audio():
    """Generate sample audio for testing (1 second of sine wave)."""
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Mix of frequencies for more realistic audio
    audio = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.3 * np.sin(2 * np.pi * 880 * t)
    return audio.astype(np.float32)


@pytest.fixture
def sample_transcript():
    """Sample Irish transcript."""
    return "Dia duit, conas atá tú inniu?"


@pytest.fixture
def sample_munster_text():
    """Sample Munster dialect text."""
    return "Do cheannaíos an leabhar seo inné agus is maith liom é."


@pytest.fixture
def sample_connacht_text():
    """Sample Connacht dialect text."""
    return "Cheannaigh muid an leabhar seo inné agus is maith linn é."


@pytest.fixture
def sample_ulster_text():
    """Sample Ulster dialect text."""
    return "Caidé mar atá tú? Tá an aimsir go breá fá láthair."


@pytest.fixture
def temp_audio_file(sample_audio):
    """Create a temporary audio file."""
    import soundfile as sf

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, sample_audio, 16000)
        yield f.name

    Path(f.name).unlink(missing_ok=True)


# =============================================================================
# DLT Source Tests
# =============================================================================

class TestEdcoLearningSource:
    """Tests for EdcoLearning DLT source."""

    def test_source_imports(self):
        """Test that EdcoLearning source can be imported."""
        from dlt_sources.ie.education.edcolearning import (
            EdcoCredentials,
            ExamLevel,
            ExamSubject,
            edcolearning_source,
            irish_lc_audio_source,
        )

        assert EdcoCredentials is not None
        assert ExamLevel is not None
        assert ExamSubject is not None
        assert edcolearning_source is not None
        assert irish_lc_audio_source is not None

    def test_credentials_dataclass(self):
        """Test EdcoCredentials dataclass."""
        from dlt_sources.ie.education.edcolearning import EdcoCredentials

        creds = EdcoCredentials(
            username="test",
            password="test123",
        )

        assert creds.username == "test"
        assert creds.password == "test123"

    def test_exam_levels_enum(self):
        """Test ExamLevel enum values."""
        from dlt_sources.ie.education.edcolearning import ExamLevel

        assert ExamLevel.LEAVING_CERT.value == "leaving_certificate"
        assert ExamLevel.JUNIOR_CYCLE.value == "junior_cycle"

    def test_exam_subjects_enum(self):
        """Test ExamSubject enum values."""
        from dlt_sources.ie.education.edcolearning import ExamSubject

        assert ExamSubject.IRISH.value == "irish"
        assert ExamSubject.FRENCH.value == "french"
        assert ExamSubject.GERMAN.value == "german"
        assert ExamSubject.SPANISH.value == "spanish"


class TestSECTranscriptsSource:
    """Tests for SEC aural transcripts source."""

    def test_source_imports(self):
        """Test that SEC transcripts source can be imported."""
        from dlt_sources.ie.education.sec_aural_transcripts import (
            AuralTranscript,
            IrishDialect,
            SpeakerSegment,
            TranscriptType,
            sec_aural_transcripts_source,
        )

        assert AuralTranscript is not None
        assert IrishDialect is not None
        assert SpeakerSegment is not None
        assert TranscriptType is not None
        assert sec_aural_transcripts_source is not None

    def test_irish_dialect_enum(self):
        """Test IrishDialect enum values."""
        from dlt_sources.ie.education.sec_aural_transcripts import IrishDialect

        assert IrishDialect.CONNACHT.value == "connacht"
        assert IrishDialect.MUNSTER.value == "munster"
        assert IrishDialect.ULSTER.value == "ulster"

    def test_speaker_segment_dataclass(self):
        """Test SpeakerSegment dataclass."""
        from dlt_sources.ie.education.sec_aural_transcripts import (
            IrishDialect,
            SpeakerSegment,
        )

        segment = SpeakerSegment(
            segment_id="seg_1",
            speaker_id="speaker_1",
            text="Dia duit",
            dialect=IrishDialect.CONNACHT.value,
        )

        assert segment.speaker_id == "speaker_1"
        assert segment.text == "Dia duit"
        assert segment.dialect == "connacht"


# =============================================================================
# Dialect Classifier Tests
# =============================================================================

class TestDialectClassifier:
    """Tests for dialect classifier utility."""

    def test_classifier_imports(self):
        """Test that dialect classifier can be imported."""
        from pipelines.dialect_classifier import (
            DialectClassifier,
            DialectPrediction,
            IrishDialect,
        )

        assert DialectClassifier is not None
        assert IrishDialect is not None
        assert DialectPrediction is not None

    def test_irish_dialect_enum(self):
        """Test IrishDialect enum values."""
        from pipelines.dialect_classifier import IrishDialect

        assert IrishDialect.CONNACHT.value == "connacht"
        assert IrishDialect.MUNSTER.value == "munster"
        assert IrishDialect.ULSTER.value == "ulster"
        assert IrishDialect.UNKNOWN.value == "unknown"

    def test_linguistic_classifier_connacht(self, sample_connacht_text):
        """Test linguistic classifier on Connacht text."""
        from pipelines.dialect_classifier import (
            DialectClassifierConfig,
            IrishDialect,
            LinguisticDialectClassifier,
        )

        config = DialectClassifierConfig()
        classifier = LinguisticDialectClassifier(config)

        result = classifier.classify_text(sample_connacht_text)

        # Should identify Connacht markers (muid)
        assert result.dialect in [IrishDialect.CONNACHT, IrishDialect.UNKNOWN]
        assert result.probabilities is not None

    def test_linguistic_classifier_munster(self, sample_munster_text):
        """Test linguistic classifier on Munster text."""
        from pipelines.dialect_classifier import (
            DialectClassifierConfig,
            IrishDialect,
            LinguisticDialectClassifier,
        )

        config = DialectClassifierConfig()
        classifier = LinguisticDialectClassifier(config)

        result = classifier.classify_text(sample_munster_text)

        # Should identify Munster markers (do cheannaíos)
        assert result.dialect in [IrishDialect.MUNSTER, IrishDialect.UNKNOWN]

    def test_linguistic_classifier_ulster(self, sample_ulster_text):
        """Test linguistic classifier on Ulster text."""
        from pipelines.dialect_classifier import (
            DialectClassifierConfig,
            IrishDialect,
            LinguisticDialectClassifier,
        )

        config = DialectClassifierConfig()
        classifier = LinguisticDialectClassifier(config)

        result = classifier.classify_text(sample_ulster_text)

        # Should identify Ulster markers (caidé, fá)
        assert result.dialect == IrishDialect.ULSTER
        assert result.confidence > 0

    def test_acoustic_feature_extraction(self, sample_audio):
        """Test acoustic feature extraction."""
        try:
            import librosa
        except ImportError:
            pytest.skip("librosa not installed")

        from pipelines.dialect_classifier import (
            AcousticDialectClassifier,
            DialectClassifierConfig,
        )

        config = DialectClassifierConfig()
        classifier = AcousticDialectClassifier(config)

        features = classifier.extract_features(sample_audio)

        # Should extract multiple features
        assert features is not None
        assert len(features) > 50  # MFCCs + pitch + spectral


# =============================================================================
# Transcript Aligner Tests
# =============================================================================

class TestTranscriptAligner:
    """Tests for transcript aligner utility."""

    def test_aligner_imports(self):
        """Test that transcript aligner can be imported."""
        from pipelines.transcript_aligner import (
            AlignedWord,
            AlignmentResult,
            TranscriptAligner,
        )

        assert TranscriptAligner is not None
        assert AlignmentResult is not None
        assert AlignedWord is not None

    def test_alignment_method_enum(self):
        """Test AlignmentMethod enum values."""
        from pipelines.transcript_aligner import AlignmentMethod

        assert AlignmentMethod.CTC.value == "ctc"
        assert AlignmentMethod.DTW.value == "dtw"
        assert AlignmentMethod.WHISPERX.value == "whisperx"

    def test_aligned_word_dataclass(self):
        """Test AlignedWord dataclass."""
        from pipelines.transcript_aligner import AlignedWord

        word = AlignedWord(
            word="Dia",
            start_time=0.0,
            end_time=0.5,
            confidence=0.9,
        )

        assert word.word == "Dia"
        assert word.start_time == 0.0
        assert word.end_time == 0.5
        assert word.confidence == 0.9
        assert word.phonemes == []

    def test_alignment_result_to_json(self):
        """Test AlignmentResult JSON export."""
        from pipelines.transcript_aligner import (
            AlignedWord,
            AlignmentMethod,
            AlignmentResult,
        )

        result = AlignmentResult(
            text="Dia duit",
            words=[
                AlignedWord(word="Dia", start_time=0.0, end_time=0.5, confidence=0.9),
                AlignedWord(word="duit", start_time=0.6, end_time=1.0, confidence=0.85),
            ],
            audio_duration=1.5,
            method=AlignmentMethod.DTW,
        )

        json_data = result.to_json()

        assert json_data["text"] == "Dia duit"
        assert len(json_data["words"]) == 2
        assert json_data["method"] == "dtw"
        assert json_data["duration"] == 1.5

    def test_dtw_aligner(self, sample_audio, sample_transcript):
        """Test DTW aligner with sample audio."""
        try:
            import librosa
        except ImportError:
            pytest.skip("librosa not installed")

        from pipelines.transcript_aligner import AlignerConfig, DTWAligner

        config = AlignerConfig(sample_rate=16000)
        aligner = DTWAligner(config)

        result = aligner.align(sample_audio, sample_transcript)

        assert result is not None
        assert result.text == sample_transcript
        assert len(result.words) > 0
        assert result.audio_duration > 0

    def test_alignment_result_textgrid_export(self, sample_audio, sample_transcript):
        """Test TextGrid export."""
        try:
            import librosa
        except ImportError:
            pytest.skip("librosa not installed")

        from pipelines.transcript_aligner import AlignerConfig, DTWAligner

        config = AlignerConfig(sample_rate=16000)
        aligner = DTWAligner(config)

        result = aligner.align(sample_audio, sample_transcript)

        with tempfile.NamedTemporaryFile(suffix=".TextGrid", delete=False) as f:
            result.to_textgrid(f.name)

            # Verify file was created
            assert Path(f.name).exists()
            content = Path(f.name).read_text()
            assert 'Object class = "TextGrid"' in content

        Path(f.name).unlink(missing_ok=True)


# =============================================================================
# Dagster Asset Tests
# =============================================================================

class TestUnifiedAudioAssets:
    """Tests for unified audio dataset Dagster assets."""

    def test_assets_imports(self):
        """Test that unified audio assets can be imported."""
        from dagster_defs.assets.unified_audio_dataset_assets import (
            UnifiedAudioConfig,
            edcolearning_audio_extraction,
            unified_combined_dataset,
        )

        assert UnifiedAudioConfig is not None
        assert edcolearning_audio_extraction is not None
        assert unified_combined_dataset is not None

    def test_unified_audio_config(self):
        """Test UnifiedAudioConfig dataclass."""
        from dagster_defs.assets.unified_audio_dataset_assets import UnifiedAudioConfig

        config = UnifiedAudioConfig(
            min_duration_ms=500,
            max_duration_ms=30000,
        )

        assert config.min_duration_ms == 500
        assert config.max_duration_ms == 30000

    def test_dialect_distribution_config(self):
        """Test dialect distribution in config."""
        from dagster_defs.assets.unified_audio_dataset_assets import UnifiedAudioConfig

        config = UnifiedAudioConfig()

        # Default distribution should match plan
        assert config.target_connacht_pct == 0.40
        assert config.target_munster_pct == 0.35
        assert config.target_ulster_pct == 0.25

        # Ratios should sum to 1.0
        total = config.target_connacht_pct + config.target_munster_pct + config.target_ulster_pct
        assert abs(total - 1.0) < 0.01


# =============================================================================
# Modal Training Config Tests
# =============================================================================

class TestWav2Vec2ModalConfig:
    """Tests for Wav2Vec2-BERT Modal training configuration."""

    def test_config_imports(self):
        """Test that Wav2Vec2 Modal configs can be imported."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "meaisínfhoghlaim" / "training"))

        # Import should work even without Modal installed
        try:
            from wav2vec2_bert_modal import (
                ASRConfig,
                DataConfig,
                IrishDialect,
            )
            assert ASRConfig is not None
            assert DataConfig is not None
        except ImportError:
            # Modal not installed, skip
            pytest.skip("Modal not installed")


class TestUnslothTTSModalConfig:
    """Tests for Unsloth TTS Modal training configuration."""

    def test_config_imports(self):
        """Test that Unsloth TTS Modal configs can be imported."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "meaisínfhoghlaim" / "training"))

        try:
            from unsloth_tts_modal import (
                DialectDataConfig,
                IrishDialect,
                UnslothTTSConfig,
            )
            assert UnslothTTSConfig is not None
            assert DialectDataConfig is not None
        except ImportError:
            pytest.skip("Modal not installed")


# =============================================================================
# Integration Tests
# =============================================================================

class TestPipelineIntegration:
    """Integration tests for the complete pipeline."""

    def test_dialect_classifier_with_aligner(
        self,
        sample_audio,
        sample_connacht_text,
    ):
        """Test dialect classifier and aligner work together."""
        try:
            import librosa
        except ImportError:
            pytest.skip("librosa not installed")

        from pipelines.dialect_classifier import (
            DialectClassifierConfig,
            LinguisticDialectClassifier,
        )
        from pipelines.transcript_aligner import (
            AlignerConfig,
            DTWAligner,
        )

        # Classify text using linguistic classifier
        classifier_config = DialectClassifierConfig(method="linguistic")
        linguistic_classifier = LinguisticDialectClassifier(classifier_config)
        dialect_result = linguistic_classifier.classify_text(sample_connacht_text)

        # Align audio using DTW
        aligner_config = AlignerConfig()
        dtw_aligner = DTWAligner(aligner_config)
        alignment_result = dtw_aligner.align(sample_audio, sample_connacht_text)

        # Both should work and produce consistent results
        assert dialect_result is not None
        assert alignment_result is not None
        assert alignment_result.text == sample_connacht_text

    def test_full_data_flow_structure(self):
        """Test that the full data flow structure is correct."""
        # Verify all required modules exist
        from dagster_defs.assets import unified_audio_assets
        from dlt_sources.ireland import edcolearning_source, sec_aural_transcripts_source
        from pipelines import DialectClassifier, TranscriptAligner

        assert edcolearning_source is not None
        assert sec_aural_transcripts_source is not None
        assert unified_audio_assets is not None
        assert DialectClassifier is not None
        assert TranscriptAligner is not None


# =============================================================================
# Performance Tests
# =============================================================================

class TestPerformance:
    """Performance tests for critical components."""

    def test_acoustic_feature_extraction_speed(self, sample_audio):
        """Test acoustic feature extraction is fast enough."""
        try:
            import librosa
        except ImportError:
            pytest.skip("librosa not installed")

        import time

        from pipelines.dialect_classifier import (
            AcousticDialectClassifier,
            DialectClassifierConfig,
        )

        config = DialectClassifierConfig()
        classifier = AcousticDialectClassifier(config)

        # Should extract features in under 1 second for 1 second of audio
        start = time.time()
        _ = classifier.extract_features(sample_audio)
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Feature extraction took {elapsed:.2f}s"

    def test_dtw_alignment_speed(self, sample_audio, sample_transcript):
        """Test DTW alignment is fast enough."""
        try:
            import librosa
        except ImportError:
            pytest.skip("librosa not installed")

        import time

        from pipelines.transcript_aligner import AlignerConfig, DTWAligner

        config = AlignerConfig(sample_rate=16000)
        aligner = DTWAligner(config)

        # Should align in under 2 seconds for 1 second of audio
        start = time.time()
        _ = aligner.align(sample_audio, sample_transcript)
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Alignment took {elapsed:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
