from typing import Literal, TypedDict


class AlignedWord(TypedDict):
    word: str
    start: float
    end: float
    duration: float
    score: float | None
    pause_before: float


class Transcription(TypedDict):
    text: str
    language: str
    duration_seconds: float
    alignment_completed: bool
    segments: list[dict]
    words: list[AlignedWord]


class FluencyResult(TypedDict):
    status: Literal["available", "unavailable"]
    metrics: dict[str, int | float | None] | None


class FluencyAnalysis(FluencyResult):
    warnings: list[str]
