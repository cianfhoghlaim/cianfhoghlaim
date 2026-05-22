"""
Irish Dialect Classifier.

Classifies Irish audio into three main dialect regions:
- Connacht (Conamara, Aran Islands)
- Munster (Kerry, Cork, Waterford)
- Ulster (Donegal)

Approaches:
1. Acoustic features + XGBoost (fast, no GPU)
2. Wav2Vec2 embeddings + classifier (accurate, requires GPU)
3. Whisper-based + linguistic rules (transcribe-then-classify)

References:
- ABAIR: https://www.abair.ie (dialect-specific synthesis)
- Common Voice Irish: Multiple dialect tags
- Academic: Irish Dialect Classification (DCU NLP)
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np


class IrishDialect(str, Enum):
    """Irish dialect regions."""
    CONNACHT = "connacht"
    MUNSTER = "munster"
    ULSTER = "ulster"
    UNKNOWN = "unknown"


@dataclass
class DialectPrediction:
    """Result of dialect classification."""
    dialect: IrishDialect
    confidence: float
    probabilities: dict[str, float]
    features_used: list[str]
    method: str


@dataclass
class DialectClassifierConfig:
    """Configuration for dialect classifier."""
    # Model settings
    method: str = "acoustic"  # acoustic, wav2vec2, or whisper
    model_path: str | None = None

    # Acoustic features
    sample_rate: int = 16000
    n_mfcc: int = 13
    n_mels: int = 40
    hop_length: int = 512
    n_fft: int = 2048

    # Classification thresholds
    min_confidence: float = 0.6
    min_audio_length: float = 0.5  # seconds

    # Linguistic patterns (for whisper method)
    use_linguistic_rules: bool = True


class AcousticDialectClassifier:
    """
    Classify Irish dialects using acoustic features.

    Uses MFCC, pitch, and formant patterns that differ
    between Irish dialect regions.

    Dialect acoustic differences:
    - Connacht: Flatter intonation, centralized vowels
    - Munster: Musical intonation, diphthongization
    - Ulster: Retroflex /r/, distinct rhythm
    """

    def __init__(self, config: DialectClassifierConfig):
        self.config = config
        self.model = None
        self._feature_names = []

    def extract_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract acoustic features for dialect classification."""
        import librosa

        # Ensure correct sample rate
        if len(audio) < self.config.sample_rate * self.config.min_audio_length:
            raise ValueError(f"Audio too short: {len(audio)/self.config.sample_rate:.2f}s")

        features = []
        feature_names = []

        # 1. MFCCs (capture spectral envelope)
        mfccs = librosa.feature.mfcc(
            y=audio,
            sr=self.config.sample_rate,
            n_mfcc=self.config.n_mfcc,
            n_mels=self.config.n_mels,
            hop_length=self.config.hop_length,
            n_fft=self.config.n_fft,
        )

        # Statistics over time
        for i in range(self.config.n_mfcc):
            features.extend([
                np.mean(mfccs[i]),
                np.std(mfccs[i]),
                np.min(mfccs[i]),
                np.max(mfccs[i]),
            ])
            feature_names.extend([
                f"mfcc_{i}_mean",
                f"mfcc_{i}_std",
                f"mfcc_{i}_min",
                f"mfcc_{i}_max",
            ])

        # 2. Delta MFCCs (capture dynamics)
        delta_mfccs = librosa.feature.delta(mfccs)
        for i in range(self.config.n_mfcc):
            features.extend([
                np.mean(delta_mfccs[i]),
                np.std(delta_mfccs[i]),
            ])
            feature_names.extend([
                f"delta_mfcc_{i}_mean",
                f"delta_mfcc_{i}_std",
            ])

        # 3. Pitch/F0 (intonation patterns)
        pitches, magnitudes = librosa.core.piptrack(
            y=audio,
            sr=self.config.sample_rate,
            hop_length=self.config.hop_length,
        )

        # Get pitch track (non-zero values)
        pitch_track = []
        for t in range(pitches.shape[1]):
            idx = magnitudes[:, t].argmax()
            if pitches[idx, t] > 0:
                pitch_track.append(pitches[idx, t])

        if pitch_track:
            pitch_array = np.array(pitch_track)
            features.extend([
                np.mean(pitch_array),
                np.std(pitch_array),
                np.min(pitch_array),
                np.max(pitch_array),
                np.percentile(pitch_array, 25),
                np.percentile(pitch_array, 75),
            ])
        else:
            features.extend([0, 0, 0, 0, 0, 0])

        feature_names.extend([
            "pitch_mean", "pitch_std", "pitch_min", "pitch_max",
            "pitch_q25", "pitch_q75",
        ])

        # 4. Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio, sr=self.config.sample_rate
        )
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio, sr=self.config.sample_rate
        )
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio, sr=self.config.sample_rate
        )

        features.extend([
            np.mean(spectral_centroid),
            np.std(spectral_centroid),
            np.mean(spectral_bandwidth),
            np.std(spectral_bandwidth),
            np.mean(spectral_rolloff),
            np.std(spectral_rolloff),
        ])
        feature_names.extend([
            "centroid_mean", "centroid_std",
            "bandwidth_mean", "bandwidth_std",
            "rolloff_mean", "rolloff_std",
        ])

        # 5. Rhythm features (tempo, beat strength)
        tempo, beats = librosa.beat.beat_track(
            y=audio, sr=self.config.sample_rate
        )
        features.append(tempo)
        feature_names.append("tempo")

        # 6. Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio)
        features.extend([np.mean(zcr), np.std(zcr)])
        feature_names.extend(["zcr_mean", "zcr_std"])

        # 7. RMS energy
        rms = librosa.feature.rms(y=audio)
        features.extend([np.mean(rms), np.std(rms)])
        feature_names.extend(["rms_mean", "rms_std"])

        self._feature_names = feature_names
        return np.array(features)

    def train(
        self,
        audio_paths: list[str],
        labels: list[IrishDialect],
    ) -> dict:
        """
        Train the acoustic classifier.

        Args:
            audio_paths: Paths to audio files
            labels: Dialect labels

        Returns:
            Training metrics
        """
        import joblib
        import librosa
        from sklearn.ensemble import GradientBoostingClassifier
        from sklearn.model_selection import cross_val_score
        from sklearn.preprocessing import StandardScaler

        X = []
        y = []
        failed = 0

        for path, label in zip(audio_paths, labels):
            try:
                audio, _ = librosa.load(path, sr=self.config.sample_rate)
                features = self.extract_features(audio)
                X.append(features)
                y.append(label.value)
            except Exception as e:
                print(f"Failed to process {path}: {e}")
                failed += 1

        X = np.array(X)
        y = np.array(y)

        # Normalize features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train classifier
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
        )

        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)

        # Fit on all data
        self.model.fit(X_scaled, y)

        # Save model if path specified
        if self.config.model_path:
            model_path = Path(self.config.model_path)
            model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump({
                "model": self.model,
                "scaler": self.scaler,
                "feature_names": self._feature_names,
            }, model_path)

        return {
            "samples_trained": len(y),
            "samples_failed": failed,
            "cv_accuracy": np.mean(cv_scores),
            "cv_std": np.std(cv_scores),
            "feature_count": X.shape[1],
        }

    def load(self, model_path: str | None = None):
        """Load trained model."""
        import joblib

        path = model_path or self.config.model_path
        if not path:
            raise ValueError("No model path specified")

        data = joblib.load(path)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self._feature_names = data.get("feature_names", [])

    def predict(
        self,
        audio: np.ndarray | str,
    ) -> DialectPrediction:
        """
        Predict dialect from audio.

        Args:
            audio: Audio array or path to audio file

        Returns:
            DialectPrediction with dialect, confidence, and probabilities
        """
        import librosa

        if self.model is None:
            raise ValueError("Model not trained or loaded")

        # Load audio if path
        if isinstance(audio, str):
            audio, _ = librosa.load(audio, sr=self.config.sample_rate)

        # Extract features
        features = self.extract_features(audio)
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Predict
        predicted = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]

        # Get class order from model
        classes = self.model.classes_
        prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}

        return DialectPrediction(
            dialect=IrishDialect(predicted),
            confidence=float(max(probabilities)),
            probabilities=prob_dict,
            features_used=self._feature_names,
            method="acoustic",
        )


class Wav2Vec2DialectClassifier:
    """
    Classify Irish dialects using Wav2Vec2 embeddings.

    Uses pretrained Wav2Vec2 model to extract speech representations,
    then classifies with a simple head.
    """

    def __init__(self, config: DialectClassifierConfig):
        self.config = config
        self.model = None
        self.processor = None
        self.classifier = None

    def load(self, model_path: str | None = None):
        """Load Wav2Vec2 model and classifier head."""
        import joblib
        import torch
        from transformers import Wav2Vec2Model, Wav2Vec2Processor

        # Load pretrained Wav2Vec2
        self.processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base")
        self.model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")
        self.model.eval()

        if torch.cuda.is_available():
            self.model = self.model.cuda()

        # Load classifier head
        path = model_path or self.config.model_path
        if path and Path(path).exists():
            self.classifier = joblib.load(path)

    def extract_embeddings(self, audio: np.ndarray) -> np.ndarray:
        """Extract Wav2Vec2 embeddings from audio."""
        import torch

        if self.model is None:
            raise ValueError("Model not loaded")

        # Process audio
        inputs = self.processor(
            audio,
            sampling_rate=self.config.sample_rate,
            return_tensors="pt",
            padding=True,
        )

        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}

        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Pool over time dimension
            embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings.cpu().numpy().flatten()

    def train(
        self,
        audio_paths: list[str],
        labels: list[IrishDialect],
    ) -> dict:
        """Train classifier on Wav2Vec2 embeddings."""
        import joblib
        import librosa
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score

        if self.model is None:
            self.load()

        X = []
        y = []

        for path, label in zip(audio_paths, labels):
            try:
                audio, _ = librosa.load(path, sr=self.config.sample_rate)
                embeddings = self.extract_embeddings(audio)
                X.append(embeddings)
                y.append(label.value)
            except Exception as e:
                print(f"Failed: {path}: {e}")

        X = np.array(X)
        y = np.array(y)

        # Train logistic regression on embeddings
        self.classifier = LogisticRegression(max_iter=1000, random_state=42)
        cv_scores = cross_val_score(self.classifier, X, y, cv=5)
        self.classifier.fit(X, y)

        # Save classifier
        if self.config.model_path:
            joblib.dump(self.classifier, self.config.model_path)

        return {
            "samples_trained": len(y),
            "cv_accuracy": np.mean(cv_scores),
            "embedding_dim": X.shape[1],
        }

    def predict(self, audio: np.ndarray | str) -> DialectPrediction:
        """Predict dialect from audio using Wav2Vec2 embeddings."""
        import librosa

        if self.classifier is None:
            raise ValueError("Classifier not trained or loaded")

        if isinstance(audio, str):
            audio, _ = librosa.load(audio, sr=self.config.sample_rate)

        embeddings = self.extract_embeddings(audio)
        embeddings = embeddings.reshape(1, -1)

        predicted = self.classifier.predict(embeddings)[0]
        probabilities = self.classifier.predict_proba(embeddings)[0]

        classes = self.classifier.classes_
        prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}

        return DialectPrediction(
            dialect=IrishDialect(predicted),
            confidence=float(max(probabilities)),
            probabilities=prob_dict,
            features_used=["wav2vec2_embeddings"],
            method="wav2vec2",
        )


class LinguisticDialectClassifier:
    """
    Classify Irish dialects using linguistic rules on transcribed text.

    Uses known dialectal markers in Irish:
    - Connacht: 'muid' (we), lenition patterns
    - Munster: 'sinn' (we), specific verb forms
    - Ulster: Retroflexion, unique vocabulary
    """

    # Dialect markers based on Irish linguistic research
    DIALECT_MARKERS = {
        IrishDialect.CONNACHT: {
            "patterns": [
                r"\bmuid\b",           # 'we' form
                r"\bndearna\b",        # past tense
                r"\bcheannaigh\b",     # bought (Connacht form)
                r"\bgoidé\b",          # what (informal)
            ],
            "vocabulary": [
                "muide", "shibhse", "cén", "cá",
            ],
            "weight": 1.0,
        },
        IrishDialect.MUNSTER: {
            "patterns": [
                r"\bsinn\b",           # 'we' form (different from Connacht)
                r"\bdo\s+\w+\s*(?:eas|is|íos)\b",  # dependent verb forms
                r"\bcheannaíos\b",     # bought (Munster form)
                r"\bcad\b",            # what (formal)
            ],
            "vocabulary": [
                "sinn", "féin", "do", "amhlaidh",
            ],
            "weight": 1.0,
        },
        IrishDialect.ULSTER: {
            "patterns": [
                r"\bfá\b",             # about (Ulster form)
                r"\bgoide\b",          # what (Ulster)
                r"\bcaidé\b",          # what (Ulster variant)
                r"\bcheannaigh\s+mé\b",  # I bought
            ],
            "vocabulary": [
                "fá", "caidé", "goide", "achan", "chan", "cha",
            ],
            "weight": 1.0,
        },
    }

    def __init__(self, config: DialectClassifierConfig):
        self.config = config

    def classify_text(self, text: str) -> DialectPrediction:
        """
        Classify dialect from Irish text.

        Args:
            text: Irish language text

        Returns:
            DialectPrediction based on linguistic markers
        """
        import re

        text_lower = text.lower()
        scores = {d: 0.0 for d in IrishDialect if d != IrishDialect.UNKNOWN}
        matched_markers = []

        for dialect, markers in self.DIALECT_MARKERS.items():
            weight = markers["weight"]

            # Check patterns
            for pattern in markers["patterns"]:
                matches = re.findall(pattern, text_lower)
                if matches:
                    scores[dialect] += len(matches) * weight
                    matched_markers.extend(matches)

            # Check vocabulary
            for word in markers["vocabulary"]:
                count = text_lower.count(word)
                if count > 0:
                    scores[dialect] += count * weight * 0.5
                    matched_markers.append(word)

        # Normalize to probabilities
        total = sum(scores.values())
        if total > 0:
            probabilities = {d.value: s / total for d, s in scores.items()}
        else:
            probabilities = {d.value: 1/3 for d in IrishDialect if d != IrishDialect.UNKNOWN}

        # Get best prediction
        best_dialect = max(scores.keys(), key=lambda d: scores[d])
        confidence = probabilities[best_dialect.value]

        if confidence < self.config.min_confidence:
            best_dialect = IrishDialect.UNKNOWN

        return DialectPrediction(
            dialect=best_dialect,
            confidence=confidence,
            probabilities=probabilities,
            features_used=matched_markers[:10],
            method="linguistic",
        )


class DialectClassifier:
    """
    Unified dialect classifier that combines multiple methods.

    Supports:
    - Acoustic features (fast, no GPU)
    - Wav2Vec2 embeddings (accurate, needs GPU)
    - Linguistic rules (text-based)
    - Ensemble of all methods
    """

    def __init__(self, config: DialectClassifierConfig | None = None):
        self.config = config or DialectClassifierConfig()

        self._acoustic = None
        self._wav2vec2 = None
        self._linguistic = LinguisticDialectClassifier(self.config)

    @property
    def acoustic(self) -> AcousticDialectClassifier:
        """Get acoustic classifier (lazy load)."""
        if self._acoustic is None:
            self._acoustic = AcousticDialectClassifier(self.config)
        return self._acoustic

    @property
    def wav2vec2(self) -> Wav2Vec2DialectClassifier:
        """Get Wav2Vec2 classifier (lazy load)."""
        if self._wav2vec2 is None:
            self._wav2vec2 = Wav2Vec2DialectClassifier(self.config)
        return self._wav2vec2

    def predict(
        self,
        audio: np.ndarray | str,
        text: str | None = None,
        method: str | None = None,
    ) -> DialectPrediction:
        """
        Predict dialect using specified method.

        Args:
            audio: Audio array or path
            text: Optional transcript for linguistic analysis
            method: acoustic, wav2vec2, linguistic, or ensemble

        Returns:
            DialectPrediction
        """
        method = method or self.config.method

        if method == "acoustic":
            return self.acoustic.predict(audio)
        elif method == "wav2vec2":
            return self.wav2vec2.predict(audio)
        elif method == "linguistic" and text:
            return self._linguistic.classify_text(text)
        elif method == "ensemble":
            return self._ensemble_predict(audio, text)
        else:
            return self.acoustic.predict(audio)

    def _ensemble_predict(
        self,
        audio: np.ndarray | str,
        text: str | None = None,
    ) -> DialectPrediction:
        """Combine predictions from multiple methods."""
        predictions = []
        weights = []

        # Acoustic prediction (weight: 0.4)
        try:
            pred = self.acoustic.predict(audio)
            predictions.append(pred)
            weights.append(0.4)
        except Exception:
            pass

        # Wav2Vec2 prediction (weight: 0.4)
        try:
            pred = self.wav2vec2.predict(audio)
            predictions.append(pred)
            weights.append(0.4)
        except Exception:
            pass

        # Linguistic prediction (weight: 0.2)
        if text:
            pred = self._linguistic.classify_text(text)
            predictions.append(pred)
            weights.append(0.2)

        if not predictions:
            return DialectPrediction(
                dialect=IrishDialect.UNKNOWN,
                confidence=0.0,
                probabilities={d.value: 1/3 for d in [IrishDialect.CONNACHT, IrishDialect.MUNSTER, IrishDialect.ULSTER]},
                features_used=[],
                method="ensemble",
            )

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Combine probabilities
        combined_probs = {d.value: 0.0 for d in [IrishDialect.CONNACHT, IrishDialect.MUNSTER, IrishDialect.ULSTER]}

        for pred, weight in zip(predictions, weights):
            for dialect, prob in pred.probabilities.items():
                if dialect in combined_probs:
                    combined_probs[dialect] += prob * weight

        # Get best dialect
        best_dialect = max(combined_probs.keys(), key=lambda d: combined_probs[d])
        confidence = combined_probs[best_dialect]

        all_features = []
        for pred in predictions:
            all_features.extend(pred.features_used[:3])

        return DialectPrediction(
            dialect=IrishDialect(best_dialect),
            confidence=confidence,
            probabilities=combined_probs,
            features_used=all_features,
            method="ensemble",
        )


def classify_audio_file(
    audio_path: str,
    method: str = "acoustic",
    model_path: str | None = None,
) -> DialectPrediction:
    """
    Convenience function to classify a single audio file.

    Args:
        audio_path: Path to audio file
        method: Classification method
        model_path: Path to trained model

    Returns:
        DialectPrediction
    """
    config = DialectClassifierConfig(
        method=method,
        model_path=model_path,
    )

    classifier = DialectClassifier(config)

    if model_path and Path(model_path).exists():
        if method == "acoustic":
            classifier.acoustic.load(model_path)
        elif method == "wav2vec2":
            classifier.wav2vec2.load(model_path)

    return classifier.predict(audio_path)


def batch_classify(
    audio_paths: list[str],
    method: str = "acoustic",
    model_path: str | None = None,
) -> list[DialectPrediction]:
    """
    Classify multiple audio files.

    Args:
        audio_paths: List of audio file paths
        method: Classification method
        model_path: Path to trained model

    Returns:
        List of DialectPrediction
    """
    config = DialectClassifierConfig(
        method=method,
        model_path=model_path,
    )

    classifier = DialectClassifier(config)

    if model_path and Path(model_path).exists():
        if method == "acoustic":
            classifier.acoustic.load(model_path)
        elif method == "wav2vec2":
            classifier.wav2vec2.load(model_path)

    results = []
    for path in audio_paths:
        try:
            pred = classifier.predict(path)
            results.append(pred)
        except Exception as e:
            print(f"Failed to classify {path}: {e}")
            results.append(DialectPrediction(
                dialect=IrishDialect.UNKNOWN,
                confidence=0.0,
                probabilities={},
                features_used=[],
                method=method,
            ))

    return results
