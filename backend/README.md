# IELTS speaking assessment backend

Use Python 3.10, uv, and FFmpeg on PATH. Run these commands from `backend/`.

```powershell
uv sync --python 3.10
uv run uvicorn app.main:app
```

The API exposes `GET /` as a health check. To assess a recording of one candidate answer, run:

```powershell
uv run python -m app.pipeline.runner path/to/answer.mp3
```

The CLI saves results to `output/<audio-stem>_assessment.json` at the repository root. Pass `--output path/to/result.json` to choose another location. Speech models download on first use. Set `IELTS_MODEL_ARTIFACTS_DIR` to use a cache directory other than `backend/model_artifacts/`.

For a quick transcription-only check, put the temporary recording at
`interview.mp3` in the repository root and run this from `backend/`.
Pass a recording path as an argument to use a different file.

```powershell
uv run python -m app.model_loaders.whisperx
```

## Structure

```text
backend/
├── app/
│   ├── main.py                       # FastAPI app and health route
│   ├── config.py                     # Project and model cache paths
│   ├── schemas/
│   │   ├── analysis.py              # Transcription and fluency types
│   │   └── speaking_result.py        # Speaking report type
│   ├── model_loaders/
│   │   └── whisperx.py              # Speech model loading and inference
│   ├── pipeline/
│   │   ├── runner.py                # Assessment workflow and CLI
│   │   └── fluency.py               # Metrics from aligned word timings
│   └── services/
│       ├── audio.py                 # FFmpeg audio conversion
│       └── storage.py               # JSON result output
├── pyproject.toml                   # Dependencies and FastAPI entry point
└── README.md
```

## Audio-to-result workflow

1. The CLI accepts a local audio path. FFmpeg converts the recording into a temporary 16 kHz mono WAV.
2. WhisperX transcribes the recording and uses its language-specific alignment model to assign word timings. English uses wav2vec2 by default.
3. The fluency module calculates speech rate, pauses, fillers, and repetitions from usable word timings. If alignment fails or produces no usable timings, the result still includes the transcript and reports fluency as unavailable.
4. The runner assembles `transcription`, `fluency`, and `warnings`, then the storage service writes the JSON file.

HTTP audio upload, BERT and Qwen analysis, an ordered scoring feature vector, and XGBoost band prediction are pending. The current workflow ends with transcription and fluency metrics.
