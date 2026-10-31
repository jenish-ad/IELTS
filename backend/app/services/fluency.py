from ..ml.features.audio_features import calculate_fluency_features


def assess_fluency(transcription: dict) -> dict:
    """Measure fluency when transcription has usable aligned word timings."""
    if not transcription.get("alignment_completed"):
        return {
            "status": "unavailable",
            "metrics": None,
            "warnings": [
                "Fluency could not be measured because word alignment did not complete."
            ],
        }

    words = transcription.get("words") or []
    metrics = calculate_fluency_features(words)
    if metrics["word_count"] == 0:
        return {
            "status": "unavailable",
            "metrics": None,
            "warnings": [
                "Fluency could not be measured because no usable word timings were found."
            ],
        }

    return {
        "status": "available",
        "metrics": metrics,
        "warnings": [
            "Filler counts only include fillers preserved in the transcript.",
            "Metrics cover all speakers in the recording; use one candidate answer per assessment.",
        ],
    }
