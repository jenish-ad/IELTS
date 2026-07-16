import argparse
import json
import string
import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
MINIMUM_PAUSE = 0.25
MEDIUM_PAUSE = 0.50
LONG_PAUSE = 1.00
FILLER_WORDS = {"um", "uh", "erm", "er", "ah", "hmm", "mm", "uhm"}


def project_path(path_value):
    path = Path(path_value).expanduser()
    return path if path.is_absolute() else PROJECT_DIR / path


def parse_args():
    parser = argparse.ArgumentParser(description="Calculate fluency features from a WhisperX word CSV.")
    parser.add_argument("words_csv", help="Path to the generated word-level CSV")
    parser.add_argument("--answer-start", type=float)
    parser.add_argument("--answer-end", type=float)
    parser.add_argument("--question-end", type=float)
    parser.add_argument("--output", help="Optional path for the JSON result")
    return parser.parse_args()


def clean_word(value):
    return str(value).lower().strip().strip(string.punctuation)


def rounded(value):
    if value is None or not np.isfinite(value):
        return None
    return round(float(value), 6)


def calculate_features(frame, answer_start=None, answer_end=None, question_end=None):
    frame = frame.copy()
    frame["start"] = pd.to_numeric(frame["start"], errors="coerce")
    frame["end"] = pd.to_numeric(frame["end"], errors="coerce")
    frame = frame.dropna(subset=["start", "end"])
    frame = frame[frame["end"] >= frame["start"]].sort_values("start").reset_index(drop=True)

    if answer_start is not None:
        midpoint = (frame["start"] + frame["end"]) / 2
        frame = frame[(midpoint >= answer_start) & (midpoint <= answer_end)].reset_index(drop=True)

    word_count = len(frame)
    if answer_start is not None:
        response_duration = answer_end - answer_start
    elif word_count:
        response_duration = max(0.0, float(frame.iloc[-1]["end"] - frame.iloc[0]["start"]))
    else:
        response_duration = 0.0

    gaps = np.maximum(0.0, frame["start"].to_numpy()[1:] - frame["end"].to_numpy()[:-1])
    pauses = gaps[gaps >= MINIMUM_PAUSE]
    total_pause = float(pauses.sum()) if len(pauses) else 0.0
    speaking_time = max(0.0, response_duration - total_pause)

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

    cleaned_words = [clean_word(word) for word in frame["word"]]
    repetition_count = sum(
        current != "" and current == previous
        for previous, current in zip(cleaned_words, cleaned_words[1:])
    )
    mean_score = None
    if "score" in frame.columns:
        valid_scores = pd.to_numeric(frame["score"], errors="coerce").dropna()
        if not valid_scores.empty:
            mean_score = float(valid_scores.mean())

    latency = None
    if question_end is not None and word_count:
        latency = max(0.0, float(frame.iloc[0]["start"]) - question_end)

    duration_minutes = response_duration / 60
    speaking_minutes = speaking_time / 60
    return {
        "word_count": word_count,
        "response_duration_seconds": rounded(response_duration),
        "response_latency_seconds": rounded(latency),
        "speech_rate_wpm": rounded(word_count / duration_minutes if duration_minutes > 0 else 0.0),
        "articulation_rate_wpm": rounded(word_count / speaking_minutes if speaking_minutes > 0 else 0.0),
        "pause_count": int(len(pauses)),
        "pause_count_per_minute": rounded(len(pauses) / duration_minutes if duration_minutes > 0 else 0.0),
        "total_pause_duration_seconds": rounded(total_pause),
        "average_pause_duration_seconds": rounded(float(pauses.mean()) if len(pauses) else 0.0),
        "maximum_pause_duration_seconds": rounded(float(pauses.max()) if len(pauses) else 0.0),
        "short_pause_count": int(np.sum((pauses >= MINIMUM_PAUSE) & (pauses < MEDIUM_PAUSE))),
        "medium_pause_count": int(np.sum((pauses >= MEDIUM_PAUSE) & (pauses < LONG_PAUSE))),
        "long_pause_count": int(np.sum(pauses >= LONG_PAUSE)),
        "pause_time_ratio": rounded(total_pause / response_duration if response_duration > 0 else 0.0),
        "mean_length_of_run_words": rounded(float(np.mean(run_lengths)) if run_lengths else 0.0),
        "maximum_length_of_run_words": int(max(run_lengths)) if run_lengths else 0,
        "filler_word_count": sum(word in FILLER_WORDS for word in cleaned_words),
        "repetition_count": repetition_count,
        "mean_alignment_score": rounded(mean_score),
    }


def main():
    args = parse_args()
    if (args.answer_start is None) != (args.answer_end is None):
        raise ValueError("--answer-start and --answer-end must be supplied together.")
    if args.answer_start is not None and args.answer_end <= args.answer_start:
        raise ValueError("--answer-end must be greater than --answer-start.")

    csv_path = project_path(args.words_csv)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Word CSV not found: {csv_path}")
    frame = pd.read_csv(csv_path)
    missing = {"word", "start", "end"} - set(frame.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    features = calculate_features(frame, args.answer_start, args.answer_end, args.question_end)
    output_text = json.dumps(features, indent=2, allow_nan=False)
    print(output_text)
    if args.output:
        output_path = project_path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text + "\n", encoding="utf-8")
        print(f"Saved features to: {output_path.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nFluency extraction cancelled by user.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
