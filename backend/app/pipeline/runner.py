from pathlib import Path

from ..config import PROJECT_DIR
from ..schemas.speaking_result import AssessmentResult
from ..services.storage import save_result
from .fluency import assess_fluency


def assess_speech(input_path: str | Path) -> AssessmentResult:
    """Transcribe a recording and calculate its fluency measurements.

    Audio and transcription errors propagate to the caller. Alignment failures
    still return the transcript, with fluency marked as unavailable.
    """
    # Load speech dependencies only when processing audio, not on module import.
    from ..model_loaders.whisperx import transcribe_audio

    transcription = transcribe_audio(input_path)
    fluency = assess_fluency(transcription)
    return {
        "transcription": transcription,
        "fluency": {"status": fluency["status"], "metrics": fluency["metrics"]},
        "warnings": fluency["warnings"],
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Transcribe audio and measure fluency."
    )
    parser.add_argument(
        "audio", type=Path, help="Path to a recording of one candidate answer"
    )
    parser.add_argument("--output", type=Path, help="Where to save assessment JSON")
    args = parser.parse_args()

    result = assess_speech(args.audio)
    output_path = (
        args.output or PROJECT_DIR / "output" / f"{args.audio.stem}_assessment.json"
    )
    save_result(output_path, result)
    print(f"Assessment saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
