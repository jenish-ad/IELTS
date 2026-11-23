# IELTS Speaking Assessment

## Requirements

- Python 3.10
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Node.js and npm](https://nodejs.org/)
- [FFmpeg](https://ffmpeg.org/download.html) available on your PATH
- Optional: NVIDIA GPU with a compatible CUDA setup

## Install

Open a terminal in the project root.

### Backend

```powershell
cd backend
uv sync --python 3.10
uv run uvicorn app.main:app
```

From `backend`, run an assessment on one candidate answer.

```powershell
uv run python -m app.pipeline.runner ../interview.mp3
```

Assessments save to the project's `output/` directory by default. Pass `--output` to choose another file.
Models download on first use and cache in `backend/model_artifacts/`. Set `IELTS_MODEL_ARTIFACTS_DIR` to override it.

### Frontend

```powershell
cd frontend
npm run dev
cd ..
```

### Git hooks

From the project root:

```powershell
uvx pre-commit install
uvx pre-commit run --all-files
```

`uvx` runs pre-commit as a tool; it does not install it into the backend project.

### Verify FFmpeg

```powershell
ffmpeg -version
```
