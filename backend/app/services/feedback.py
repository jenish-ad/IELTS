import json
import logging

from app.core.config import QWEN_ENABLED, QWEN_MAX_NEW_TOKENS
from app.ml.loaders.qwen import QwenModelLoader, qwen_model_loader

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an IELTS English assessor. Analyze the candidate answer, not the question.
Return only valid JSON with this exact shape:
{"corrected_text":"...", "grammar_errors":[{"original":"...","correction":"...","explanation":"..."}], "feedback":{"strengths":["..."],"improvements":["..."],"next_steps":["..."]}, "estimated_bands":{"grammar":0.0,"lexical_resource":0.0,"coherence":0.0}}
Use IELTS band scores from 0 to 9 in 0.5 increments. Do not invent pronunciation or fluency evidence from text alone. Be concise and encouraging."""


def _parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise ValueError("Qwen returned invalid JSON")


def assess_text(question: str, answer: str, loader: QwenModelLoader | None = None) -> dict:
    if not QWEN_ENABLED:
        return {"status": "disabled", "message": "Qwen feedback is disabled by QWEN_ENABLED."}
    if not answer.strip():
        raise ValueError("Answer must not be empty.")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Question:\n{question}\n\nCandidate answer:\n{answer}"},
    ]
    raw = (loader or qwen_model_loader).generate(messages, QWEN_MAX_NEW_TOKENS)
    result = _parse_json(raw)
    result["status"] = "completed"
    return result
