from fastapi import APIRouter, HTTPException

from app.schemas.assessment import TextAssessmentRequest, TextAssessmentResponse
from app.services.feedback import assess_text

router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.post("/text", response_model=TextAssessmentResponse)
def assess_text_answer(request: TextAssessmentRequest):
    try:
        return assess_text(request.question, request.answer)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
