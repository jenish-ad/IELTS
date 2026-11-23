from typing import TypedDict

from .analysis import FluencyResult, Transcription


class AssessmentResult(TypedDict):
    transcription: Transcription
    fluency: FluencyResult
    warnings: list[str]
