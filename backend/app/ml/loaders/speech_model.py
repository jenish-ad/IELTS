import logging
from threading import RLock

import torch
import whisperx

logger = logging.getLogger(__name__)


class SpeechModelLoader:
    """Lazily load and reuse speech models within one process."""

    def __init__(self, model_name="large-v3", device="auto", language="en"):
        if device not in {"auto", "cuda", "cpu"}:
            raise ValueError("device must be auto, cuda, or cpu.")
        self.model_name = model_name
        self.language = language
        self.requested_device = device
        self._device = None
        self._transcription_model = None
        self._alignment_models = {}
        # Inference and loading share this reentrant lock.
        self.lock = RLock()

    @property
    def device(self) -> str:
        with self.lock:
            if self._device is None:
                device = self.requested_device
                if device == "auto":
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                if device == "cuda" and not torch.cuda.is_available():
                    raise RuntimeError("CUDA was requested but is unavailable.")
                self._device = device
            return self._device

    def get_transcription_model(self):
        with self.lock:
            if self._transcription_model is None:
                device = self.device
                logger.info("Loading WhisperX model %s on %s", self.model_name, device)
                self._transcription_model = whisperx.load_model(
                    self.model_name,
                    device,
                    compute_type="float16" if device == "cuda" else "int8",
                    language=self.language,
                )
            return self._transcription_model

    def get_alignment_model(self, language: str | None = None):
        language = language or self.language
        with self.lock:
            if language not in self._alignment_models:
                logger.info(
                    "Loading alignment model for %s on %s", language, self.device
                )
                self._alignment_models[language] = whisperx.load_align_model(
                    language_code=language, device=self.device
                )
            return self._alignment_models[language]


speech_model_loader = SpeechModelLoader()
