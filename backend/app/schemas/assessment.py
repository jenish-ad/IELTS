from pydantic import BaseModel, Field


class TextAssessmentRequest(BaseModel):
    question: str = Field(default="", max_length=4000)
    answer: str = Field(min_length=1, max_length=12000)


class TextAssessmentResponse(BaseModel):
    status: str
    corrected_text: str | None = None
    grammar_errors: list[dict] = Field(default_factory=list)
    feedback: dict | None = None
    estimated_bands: dict | None = None
    message: str | None = None
