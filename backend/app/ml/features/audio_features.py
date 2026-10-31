import math
import string

# Pause thresholds are in seconds.
MINIMUM_PAUSE = 0.25
MEDIUM_PAUSE = 0.50
LONG_PAUSE = 1.00
FILLER_WORDS = {"um", "uh", "erm", "er", "ah", "hmm", "mm", "uhm"}


def _finite_number(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def calculate_fluency_features(
    words: list[dict],
    answer_start: float | None = None,
    answer_end: float | None = None,
    question_end: float | None = None,
) -> dict:
    """Calculate fluency from transcription word dictionaries without CSV files.

    Invalid word timings are skipped. Optional answer bounds select words by
    midpoint and define the response duration; otherwise duration spans the first
    word's start through the latest word's end. Pauses are internal gaps of at
    least 0.25 seconds, with overlapping words treated as continuous speech.
    Empty input returns zero counts/rates and unavailable latency/confidence.
    Filler counts only include fillers preserved in the transcript.
    Alignment confidence is not a pronunciation or IELTS band score.
    """
    if (answer_start is None) != (answer_end is None):
        raise ValueError("answer_start and answer_end must be supplied together.")
    if answer_start is not None:
        answer_start = _finite_number(answer_start)
        answer_end = _finite_number(answer_end)
        if answer_start is None or answer_end is None or answer_end <= answer_start:
            raise ValueError(
                "Answer bounds must be finite with answer_end > answer_start."
            )
    if question_end is not None:
        question_end = _finite_number(question_end)
        if question_end is None:
            raise ValueError("question_end must be finite.")

    timed_words = []
    for word in words:
        start = _finite_number(word.get("start"))
        end = _finite_number(word.get("end"))
        if start is None or end is None or start < 0 or end < start:
            continue
        if answer_start is not None:
            midpoint = (start + end) / 2
            if midpoint < answer_start or midpoint > answer_end:
                continue
        timed_words.append((start, end, word))
    timed_words.sort(key=lambda item: item[0])

    word_count = len(timed_words)
    response_duration = 0.0
    if answer_start is not None:
        response_duration = answer_end - answer_start
    elif timed_words:
        first_word_start = timed_words[0][0]
        last_word_end = max(end for _, end, _ in timed_words)
        response_duration = last_word_end - first_word_start

    # Clip to the answer window and use the furthest end to avoid false pauses
    # after overlapping/nested word intervals.
    gaps = []
    previous_end = None
    for start, end, _ in timed_words:
        if answer_start is not None:
            start = max(answer_start, min(start, answer_end))
            end = max(answer_start, min(end, answer_end))
        if previous_end is not None:
            gaps.append(max(0.0, start - previous_end))
        previous_end = end if previous_end is None else max(previous_end, end)

    pauses = [gap for gap in gaps if gap >= MINIMUM_PAUSE]
    total_pause = sum(pauses)
    speaking_time = max(0.0, response_duration - total_pause)
    # A run is a group of words spoken without a qualifying pause.
    run_lengths = []
    if word_count:
        current_run = 1
        for gap in gaps:
            if gap >= MINIMUM_PAUSE:
                run_lengths.append(current_run)
                current_run = 1
            else:
                current_run += 1
        run_lengths.append(current_run)

    cleaned_words = []
    alignment_scores = []
    for _, _, word in timed_words:
        text = str(word.get("word") or "")
        cleaned_words.append(text.lower().strip().strip(string.punctuation))
        score = _finite_number(word.get("score"))
        if score is not None:
            alignment_scores.append(score)

    repetition_count = 0
    for previous, current in zip(cleaned_words, cleaned_words[1:]):
        if current and current == previous:
            repetition_count += 1

    response_latency = None
    if question_end is not None and timed_words:
        response_latency = round(max(0.0, timed_words[0][0] - question_end), 6)

    mean_alignment_score = None
    if alignment_scores:
        mean_alignment_score = round(sum(alignment_scores) / len(alignment_scores), 6)

    def per_minute(count, seconds):
        if seconds <= 0:
            return 0.0
        return round(count * 60 / seconds, 6)

    return {
        "word_count": word_count,
        "response_duration_seconds": round(response_duration, 6),
        "response_latency_seconds": response_latency,
        "speech_rate_wpm": per_minute(word_count, response_duration),
        "articulation_rate_wpm": per_minute(word_count, speaking_time),
        "pause_count": len(pauses),
        "pause_count_per_minute": per_minute(len(pauses), response_duration),
        "total_pause_duration_seconds": round(total_pause, 6),
        "average_pause_duration_seconds": (
            round(total_pause / len(pauses), 6) if pauses else 0.0
        ),
        "maximum_pause_duration_seconds": round(max(pauses), 6) if pauses else 0.0,
        "short_pause_count": sum(MINIMUM_PAUSE <= gap < MEDIUM_PAUSE for gap in pauses),
        "medium_pause_count": sum(MEDIUM_PAUSE <= gap < LONG_PAUSE for gap in pauses),
        "long_pause_count": sum(gap >= LONG_PAUSE for gap in pauses),
        "pause_time_ratio": (
            round(total_pause / response_duration, 6) if response_duration > 0 else 0.0
        ),
        "mean_length_of_run_words": (
            round(word_count / len(run_lengths), 6) if run_lengths else 0.0
        ),
        "maximum_length_of_run_words": max(run_lengths, default=0),
        "filler_word_count": sum(word in FILLER_WORDS for word in cleaned_words),
        "repetition_count": repetition_count,
        "mean_alignment_score": mean_alignment_score,
    }


def extract_words(segments: list) -> list[dict]:
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
