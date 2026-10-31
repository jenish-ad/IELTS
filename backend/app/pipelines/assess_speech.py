from pathlib import Path

from ..services.fluency import assess_fluency


def assess_speech(input_path: str | Path) -> dict:
    """Transcribe a recording and calculate its fluency measurements.

    Audio and transcription errors propagate to the caller. Alignment failures
    still return the transcript, with fluency marked as unavailable.
    """
    # Load speech dependencies only when processing audio, not on module import.
    from ..services.transcription import transcribe_audio

    transcription = transcribe_audio(input_path)
    fluency = assess_fluency(transcription)

    return {
        "transcription": transcription,
        "fluency": {
            "status": fluency["status"],
            "metrics": fluency["metrics"],
        },
        "warnings": fluency["warnings"],
    }


def main():
    import argparse
    import json

    project_dir = Path(__file__).resolve().parents[3]
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
        args.output or project_dir / "output" / f"{args.audio.stem}_assessment.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Assessment saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
