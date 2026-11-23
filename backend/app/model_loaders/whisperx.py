import logging
import tempfile
from pathlib import Path
from threading import RLock

from ..config import MODEL_ARTIFACTS_DIR, PROJECT_DIR
from ..schemas.analysis import AlignedWord, Transcription
from ..services.audio import convert_to_wav

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
                import torch

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
                import whisperx

                device = self.device
                logger.info("Loading WhisperX model %s on %s", self.model_name, device)
                self._transcription_model = whisperx.load_model(
                    self.model_name,
                    device,
                    compute_type="float16" if device == "cuda" else "int8",
                    language=self.language,
                    download_root=str(MODEL_ARTIFACTS_DIR / "whisperx"),
                )
            return self._transcription_model

    def get_alignment_model(self, language: str | None = None):
        language = language or self.language
        with self.lock:
            if language not in self._alignment_models:
                import whisperx

                logger.info(
                    "Loading alignment model for %s on %s", language, self.device
                )
                self._alignment_models[language] = whisperx.load_align_model(
                    language_code=language,
                    device=self.device,
                    model_dir=str(MODEL_ARTIFACTS_DIR / "alignment"),
                )
            return self._alignment_models[language]


speech_model_loader = SpeechModelLoader()


def extract_words(segments: list[dict]) -> list[AlignedWord]:
    """Return aligned word timings, durations, and pauses in seconds."""
    aligned_words = []
    for segment in segments:
        for word in segment.get("words", []):
            if word.get("start") is not None and word.get("end") is not None:
                aligned_words.append(word)
    aligned_words.sort(key=lambda word: float(word["start"]))

    words = []
    previous_end = None

    for word in aligned_words:
        start = float(word["start"])
        end = float(word["end"])

        pause = 0.0 if previous_end is None else max(0.0, start - previous_end)

        score = word.get("score")

        words.append(
            {
                "word": word.get("word", "").strip(),
                "start": round(start, 3),
                "end": round(end, 3),
                "duration": round(max(0.0, end - start), 3),
                "score": float(score) if score is not None else None,
                "pause_before": round(pause, 3),
            }
        )

        previous_end = end if previous_end is None else max(previous_end, end)

    return words


class TranscriptionService:
    def __init__(
        self,
        model_name: str = "large-v3",
        device: str = "auto",
        language: str = "en",
        batch_size: int = 8,
        model_loader: SpeechModelLoader | None = None,
    ):
        if device not in {"auto", "cuda", "cpu"}:
            raise ValueError("device must be auto, cuda, or cpu.")

        if batch_size < 1:
            raise ValueError("batch_size must be at least 1.")

        self.model_name = model_name
        self.requested_device = device
        self.language = language
        self.batch_size = batch_size

        self.model_loader = model_loader or SpeechModelLoader(
            model_name=model_name, device=device, language=language
        )
        self.language = self.model_loader.language

    def transcribe(self, input_path: str | Path) -> Transcription:
        input_path = Path(input_path).expanduser().resolve()

        if not input_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {input_path}")

        import whisperx
        from whisperx.audio import SAMPLE_RATE

        # Prevent concurrent requests from using the models together.
        with self.model_loader.lock:
            with tempfile.TemporaryDirectory(prefix="transcription_") as temporary_dir:
                wav_path = Path(temporary_dir) / "audio.wav"
                convert_to_wav(input_path, wav_path)
                audio = whisperx.load_audio(str(wav_path))

            duration = len(audio) / SAMPLE_RATE

            if len(audio) == 0:
                raise ValueError("The audio file contains no samples.")

            model = self.model_loader.get_transcription_model()

            result = model.transcribe(
                audio,
                batch_size=self.batch_size,
                language=self.language,
            )

            language = result.get("language") or self.language
            segments = result.get("segments", [])

            transcript = " ".join(
                segment.get("text", "").strip() for segment in segments
            ).strip()

            alignment_completed = False

            if segments:
                try:
                    align_model, metadata = self.model_loader.get_alignment_model(
                        language
                    )

                    aligned_result = whisperx.align(
                        segments,
                        align_model,
                        metadata,
                        audio,
                        self.model_loader.device,
                        return_char_alignments=False,
                    )

                    segments = aligned_result["segments"]
                    alignment_completed = True

                except Exception:
                    logger.exception(
                        "Word alignment failed; returning the segment-level transcript."
                    )

            return {
                "text": transcript,
                "language": language,
                "duration_seconds": round(duration, 3),
                "alignment_completed": alignment_completed,
                "segments": segments,
                "words": (extract_words(segments) if alignment_completed else []),
            }


transcription_service = TranscriptionService(model_loader=speech_model_loader)


def transcribe_audio(input_path: str | Path) -> Transcription:
    return transcription_service.transcribe(input_path)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Transcribe a local recording.")
    parser.add_argument(
        "audio",
        nargs="?",
        type=Path,
        default=PROJECT_DIR / "interview.mp3",
        help="Path to the recording (defaults to interview.mp3 at the repository root)",
    )
    audio_path = parser.parse_args().audio
    if not audio_path.is_file():
        parser.error(f"Recording not found: {audio_path}")

    result = transcribe_audio(audio_path)

    output_dir = PROJECT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{audio_path.stem}.json"
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(result["text"])
    print(f"Results saved to: {output_path}")
