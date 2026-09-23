import logging
import tempfile
from pathlib import Path

import whisperx

from app.ml.features.audio_features import extract_words
from app.ml.loaders.speech_model import SpeechModelLoader, speech_model_loader
from app.services.audio_preprocessing import convert_to_wav

logger = logging.getLogger(__name__)


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

    def transcribe(self, input_path: str | Path) -> dict:
        input_path = Path(input_path).expanduser().resolve()

        if not input_path.is_file():
            raise FileNotFoundError(f"Audio file not found: {input_path}")

        # Prevent concurrent requests from using the models together.
        with self.model_loader.lock:
            with tempfile.TemporaryDirectory(prefix="transcription_") as temporary_dir:
                wav_path = Path(temporary_dir) / "audio.wav"
                convert_to_wav(input_path, wav_path)
                audio = whisperx.load_audio(str(wav_path))

            duration = len(audio) / 16000

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


def transcribe_audio(input_path: str | Path) -> dict:
    return transcription_service.transcribe(input_path)


if __name__ == "__main__":
    import json

    root_dir = Path(__file__).resolve().parents[3]

    # Change this filename to select your recording.
    audio_path = root_dir / "input" / "interview.mp3"

    result = transcribe_audio(audio_path)

    output_dir = root_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{audio_path.stem}.json"
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(result["text"])
    print(f"Results saved to: {output_path}")
