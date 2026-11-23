import json
from pathlib import Path

from ..schemas.speaking_result import AssessmentResult


def save_result(output_path: Path, result: AssessmentResult) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
