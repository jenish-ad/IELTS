import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent
MODEL_ARTIFACTS_DIR = (
    Path(os.environ.get("IELTS_MODEL_ARTIFACTS_DIR") or BACKEND_DIR / "model_artifacts")
    .expanduser()
    .resolve()
)
