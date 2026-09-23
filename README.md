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
uv sync
cd ..
```

`uv sync` installs the Python dependencies from `pyproject.toml` and `uv.lock`. You do not need to create or activate a virtual environment manually.

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
