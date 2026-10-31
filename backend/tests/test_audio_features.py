import json
import unittest

from backend.app.ml.features.audio_features import (
    calculate_fluency_features,
    extract_words,
)


class FluencyFeaturesTests(unittest.TestCase):
    def test_counts_pauses_fillers_and_repetitions_from_transcription(self):
        words = extract_words(
            [
                {
                    "words": [
                        {"word": "Um,", "start": 0, "end": 0.5, "score": 0.8},
                        {"word": "I", "start": 0.75, "end": 1.0, "score": 1.0},
                        {"word": "I", "start": 1.5, "end": 2.0},
                        {"word": "agree", "start": 3.0, "end": 4.0},
                    ]
                }
            ]
        )
        result = calculate_fluency_features(words)
        self.assertEqual(result["speech_rate_wpm"], 60)
        self.assertEqual(result["articulation_rate_wpm"], 106.666667)
        self.assertEqual(result["total_pause_duration_seconds"], 1.75)
        for key in (
            "short_pause_count",
            "medium_pause_count",
            "long_pause_count",
            "filler_word_count",
            "repetition_count",
        ):
            with self.subTest(metric=key):
                self.assertEqual(result[key], 1)
        self.assertEqual(result["mean_alignment_score"], 0.9)

    def test_invalid_timings_are_skipped(self):
        result = calculate_fluency_features(
            [
                {"start": None, "end": 1},
                {"start": 2, "end": 1},
                {"start": float("nan"), "end": 3},
                {"start": 0, "end": float("inf")},
            ]
        )
        self.assertEqual(result, calculate_fluency_features([]))
        self.assertEqual(result["speech_rate_wpm"], 0)
        self.assertIsNone(result["mean_alignment_score"])
        json.dumps(result, allow_nan=False)

    def test_overlapping_words_do_not_create_false_pauses(self):
        result = calculate_fluency_features(
            [
                {"word": "three", "start": 3, "end": 4},
                {"word": "one", "start": 0, "end": 5},
                {"word": "two", "start": 1, "end": 2},
            ]
        )
        self.assertEqual(result["response_duration_seconds"], 5)
        self.assertEqual(result["pause_count"], 0)
        self.assertEqual(result["maximum_length_of_run_words"], 3)

    def test_answer_window_excludes_other_words_and_measures_latency(self):
        result = calculate_fluency_features(
            [
                {"word": "outside", "start": 0, "end": 1},
                {"word": "answer", "start": 3, "end": 4},
            ],
            answer_start=2,
            answer_end=6,
            question_end=1,
        )
        self.assertEqual(result["word_count"], 1)
        self.assertEqual(result["response_duration_seconds"], 4)
        self.assertEqual(result["response_latency_seconds"], 2)
        self.assertEqual(result["speech_rate_wpm"], 15)

    def test_invalid_answer_bounds_raise_value_error(self):
        for options in (
            {"answer_start": 1},
            {"answer_end": 2},
            {"answer_start": 2, "answer_end": 1},
            {"question_end": float("nan")},
        ):
            with self.subTest(options=options), self.assertRaises(ValueError):
                calculate_fluency_features([], **options)


if __name__ == "__main__":
    unittest.main()
