"""DeepTruth inference providers.

PRODUCTION:
    HuggingFace pretrained AI-image detector.

MY_MODEL:
    Original DeepTruth TensorFlow/Keras .h5 model.

All outputs are probabilistic forensic signals and must not be treated as
absolute proof of authenticity.
"""

from __future__ import annotations

import hashlib
import os
import time
from functools import lru_cache
from typing import Any

from .config import settings


class InferenceProvider:
    def process(self, path: str, media_type: str = "IMAGE") -> dict[str, Any]:
        raise NotImplementedError

    def health_check(self) -> dict[str, Any]:
        raise NotImplementedError


class CommonInferenceMixin:
    @staticmethod
    def _sha256(path: str) -> str:
        digest = hashlib.sha256()

        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def _image_metadata(path: str) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "width": None,
            "height": None,
            "format": None,
            "exif_present": False,
        }

        try:
            from PIL import Image

            with Image.open(path) as image:
                metadata.update(
                    {
                        "width": image.width,
                        "height": image.height,
                        "format": image.format,
                        "exif_present": bool(image.getexif()),
                    }
                )
        except Exception:
            pass

        return metadata

    @staticmethod
    def _verdict(ai_probability: float) -> tuple[str, str]:
        distance = abs(ai_probability - 0.5)

        confidence = (
            "HIGH"
            if distance >= 0.30
            else "MEDIUM"
            if distance >= 0.12
            else "LOW"
        )

        if ai_probability >= 0.75:
            return "AI_GENERATED", confidence

        if ai_probability >= 0.55:
            return "POTENTIALLY_MANIPULATED", confidence

        return "AUTHENTIC", confidence

    @staticmethod
    def _evidence(
        fake: float,
        real: float,
        metadata: dict[str, Any],
        model_title: str,
    ) -> list[dict[str, Any]]:
        margin = abs(fake - real)

        margin_level = (
            "HIGH"
            if margin >= 0.60
            else "MEDIUM"
            if margin >= 0.20
            else "LOW"
        )

        signal_level = (
            "HIGH"
            if fake >= 0.75
            else "MEDIUM"
            if fake >= 0.55
            else "LOW"
        )

        signal_text = (
            "AI-generated signal"
            if fake >= 0.55
            else "Authentic signal"
        )

        return [
            {
                "type": "MODEL_SIGNAL",
                "severity": signal_level,
                "title": model_title,
                "value": f"{fake * 100:.1f}%",
                "explanation": (
                    f"The selected model produced a "
                    f"{fake * 100:.1f}% AI-generation probability "
                    f"({signal_text})."
                ),
            },
            {
                "type": "MODEL_MARGIN",
                "severity": margin_level,
                "title": "Decision margin",
                "value": f"{margin * 100:.1f}%",
                "explanation": (
                    "Distance between real and AI-generated probabilities. "
                    "A small margin should be treated as inconclusive."
                ),
            },
            {
                "type": "METADATA",
                "severity": "INFO",
                "title": "Image metadata",
                "value": (
                    "EXIF present"
                    if metadata.get("exif_present")
                    else "No EXIF metadata"
                ),
                "explanation": (
                    "Metadata presence is contextual evidence only and "
                    "does not prove whether media is authentic."
                ),
            },
        ]

    @staticmethod
    def _detect_faces(path: str) -> list[dict[str, Any]]:
        try:
            import cv2

            image = cv2.imread(path)

            if image is None:
                return []

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            cascade_path = (
                cv2.data.haarcascades
                + "haarcascade_frontalface_default.xml"
            )

            detector = cv2.CascadeClassifier(cascade_path)

            boxes = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(32, 32),
            )

            return [
                {
                    "face_id": f"face-{index + 1}",
                    "bbox": {
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h),
                    },
                    "identity_name": None,
                    "identity_confidence": None,
                    "deepfake_probability": None,
                    "notes": (
                        "Face detected; this detector does not independently "
                        "establish a face swap."
                    ),
                }
                for index, (x, y, w, h) in enumerate(boxes)
            ]

        except Exception:
            return []

    def _base_result(
        self,
        path: str,
        fake: float,
        real: float,
        media_type: str,
        model_metadata: dict[str, Any],
        raw_predictions: Any,
        started: float,
        limitations: list[str],
    ) -> dict[str, Any]:
        verdict, confidence = self._verdict(fake)
        faces = self._detect_faces(path) if media_type == "IMAGE" else []
        metadata = self._image_metadata(path)

        return {
            "verdict": verdict,
            "authenticity_score": round(real, 4),
            "ai_probability": round(fake, 4),
            "face_swap_probability": None,
            "confidence": confidence,
            "faces_detected": len(faces) if media_type == "IMAGE" else None,
            "detected_faces": faces,
            "evidence": self._evidence(
                fake,
                real,
                metadata,
                model_metadata["model_name"],
            ),
            "suspicious_regions": [],
            "frame_results": None,
            "media_metadata": {
                **metadata,
                "sha256": self._sha256(path),
            },
            "model_metadata": {
                **model_metadata,
                "processing_time": round(
                    time.perf_counter() - started,
                    3,
                ),
            },
            "raw_predictions": raw_predictions,
            "limitations": limitations,
        }


class HuggingFaceImageDetector(CommonInferenceMixin, InferenceProvider):
    def __init__(self) -> None:
        self.model_id = settings.model_id
        self.device = settings.model_device
        self._pipeline = None

    def _load(self):
        if self._pipeline is not None:
            return self._pipeline

        try:
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError(
                "Production inference requires transformers and torch. "
                "Install backend/requirements.txt."
            ) from exc

        kwargs: dict[str, Any] = {
            "task": "image-classification",
            "model": self.model_id,
        }

        if settings.model_revision:
            kwargs["revision"] = settings.model_revision

        model_kwargs: dict[str, Any] = {}

        if settings.model_cache_dir:
            model_kwargs["cache_dir"] = settings.model_cache_dir

        if settings.model_low_cpu_mem_usage:
            model_kwargs["low_cpu_mem_usage"] = True

        if model_kwargs:
            kwargs["model_kwargs"] = model_kwargs

        requested = self.device.lower().strip()

        if requested == "cpu":
            kwargs["device"] = -1
        elif requested == "cuda":
            import torch

            if not torch.cuda.is_available():
                raise RuntimeError(
                    "MODEL_DEVICE=cuda was requested, "
                    "but CUDA is not available."
                )

            kwargs["device"] = 0
        elif requested.isdigit():
            kwargs["device"] = int(requested)
        else:
            try:
                import torch

                kwargs["device"] = 0 if torch.cuda.is_available() else -1
            except Exception:
                kwargs["device"] = -1

        self._pipeline = pipeline(**kwargs)
        return self._pipeline

    @staticmethod
    def _scores(
        predictions: list[dict[str, Any]],
    ) -> tuple[float, float]:
        fake = 0.0
        real = 0.0

        for item in predictions:
            label = str(item.get("label", "")).strip().lower()
            score = float(item.get("score", 0.0))

            if label in {
                "fake",
                "ai",
                "ai-generated",
                "ai_generated",
                "synthetic",
                "generated",
            } or any(
                token in label
                for token in ("fake", "synthetic", "generated")
            ):
                fake = max(fake, score)

            elif label in {
                "real",
                "authentic",
                "human",
            } or any(
                token in label
                for token in ("real", "authentic")
            ):
                real = max(real, score)

        if fake == 0.0 and real == 0.0 and len(predictions) == 2:
            by_label = {
                str(item.get("label", "")).strip().lower():
                float(item.get("score", 0.0))
                for item in predictions
            }

            if "label_1" in by_label and "label_0" in by_label:
                fake = by_label["label_1"]
                real = by_label["label_0"]

        total = fake + real

        if total > 0:
            fake, real = fake / total, real / total

        return fake, real

    def process(self, path: str, media_type: str = "IMAGE") -> dict[str, Any]:
        started = time.perf_counter()

        if not path or not os.path.isfile(path):
            raise FileNotFoundError(f"Media file not found: {path}")

        if media_type == "VIDEO":
            raise RuntimeError(
                "Video inference is currently supported only by the "
                "production provider."
            )

        from PIL import Image

        with Image.open(path).convert("RGB") as image:
            raw = self._load()(image, top_k=5)

        fake, real = self._scores(raw)

        return self._base_result(
            path=path,
            fake=fake,
            real=real,
            media_type=media_type,
            model_metadata={
                "model_name": self.model_id,
                "version": settings.model_revision or "main",
                "framework": "Hugging Face Transformers / PyTorch",
                "inference_mode": "REAL",
                "model_provider": "PRODUCTION",
                "device": self._device_name(),
            },
            raw_predictions=raw,
            started=started,
            limitations=[
                "AI-image detection is probabilistic and can produce "
                "false positives/negatives.",
                "The selected model may be weaker on newer generators.",
                "A face detection is not itself evidence of a face swap.",
            ],
        )

    def _device_name(self) -> str:
        try:
            import torch

            return "CUDA:0" if torch.cuda.is_available() else "CPU"
        except Exception:
            return "CPU"

    def health_check(self) -> dict[str, Any]:
        try:
            import torch

            return {
                "model_loaded": self._pipeline is not None,
                "available": True,
                "model_id": self.model_id,
                "device": self._device_name(),
                "cuda_available": bool(torch.cuda.is_available()),
            }

        except Exception as exc:
            return {
                "model_loaded": False,
                "available": False,
                "model_id": self.model_id,
                "reason": str(exc),
            }


class OriginalKerasDetector(CommonInferenceMixin, InferenceProvider):
    """Inference provider for DeepTruth's original experimental .h5 model."""

    def __init__(self) -> None:
        self.model_path = settings.model_path
        self._model = None

    def _load(self):
        if self._model is not None:
            return self._model

        if not self.model_path:
            raise RuntimeError(
                "MODEL_PATH is not configured for MY_MODEL."
            )

        if not os.path.isfile(self.model_path):
            raise FileNotFoundError(
                f"Original .h5 model not found: {self.model_path}"
            )

        try:
            import tensorflow as tf
        except ImportError as exc:
            raise RuntimeError(
                "TensorFlow is required for MY_MODEL. "
                "Install tensorflow==2.15.1."
            ) from exc

        self._model = tf.keras.models.load_model(
            self.model_path,
            compile=False,
        )

        return self._model

    def process(self, path: str, media_type: str = "IMAGE") -> dict[str, Any]:
        started = time.perf_counter()

        if not path or not os.path.isfile(path):
            raise FileNotFoundError(f"Media file not found: {path}")

        if media_type == "VIDEO":
            raise RuntimeError(
                "The original .h5 model currently supports images only."
            )

        from PIL import Image
        import numpy as np

        with Image.open(path).convert("RGB") as image:
            image = image.resize((224, 224))
            array = np.asarray(image, dtype=np.float32) / 255.0

        batch = np.expand_dims(array, axis=0)
        prediction = float(self._load().predict(batch, verbose=0)[0][0])

        # The original training generator used:
        # Fake = 0 and Real = 1.
        # Therefore sigmoid output is interpreted as Real probability.
        real = max(0.0, min(1.0, prediction))
        fake = 1.0 - real

        return self._base_result(
            path=path,
            fake=fake,
            real=real,
            media_type=media_type,
            model_metadata={
                "model_name": os.path.basename(self.model_path),
                "version": "original-experimental",
                "framework": "TensorFlow / Keras",
                "inference_mode": "REAL",
                "model_provider": "MY_MODEL",
                "device": "CPU",
                "model_path": self.model_path,
                "label_mapping": {
                    "class_0": "Fake",
                    "class_1": "Real",
                },
            },
            raw_predictions={
                "sigmoid_output": prediction,
                "fake_probability": fake,
                "real_probability": real,
            },
            started=started,
            limitations=[
                "This is the original DeepTruth model and is experimental.",
                "Its validation accuracy has not been independently verified.",
                "The model was trained on a specific dataset and may not "
                "generalize to unseen media.",
                "A face detection is not itself evidence of a face swap.",
            ],
        )

    def health_check(self) -> dict[str, Any]:
        try:
            self._load()

            return {
                "model_loaded": self._model is not None,
                "available": True,
                "model_id": os.path.basename(self.model_path),
                "model_provider": "MY_MODEL",
                "framework": "TensorFlow / Keras",
                "model_path": self.model_path,
            }

        except Exception as exc:
            return {
                "model_loaded": False,
                "available": False,
                "model_provider": "MY_MODEL",
                "model_path": self.model_path,
                "reason": str(exc),
            }


@lru_cache(maxsize=1)
def get_inference_provider() -> InferenceProvider:
    return HuggingFaceImageDetector()


@lru_cache(maxsize=1)
def get_original_model_provider() -> InferenceProvider:
    return OriginalKerasDetector()


def create_inference_provider(
    model_provider: str = "PRODUCTION",
) -> InferenceProvider:
    provider = (model_provider or "PRODUCTION").upper().strip()

    if provider == "MY_MODEL":
        return get_original_model_provider()

    return get_inference_provider()