def extract_words(segments: list) -> list[dict]:
    """Return aligned word timings, durations, and pauses in seconds."""
    aligned_words = sorted(
        (
            word
            for segment in segments
            for word in segment.get("words", [])
            if word.get("start") is not None and word.get("end") is not None
        ),
        key=lambda word: float(word["start"]),
    )

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
