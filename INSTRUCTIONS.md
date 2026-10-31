# Running the project

Run these commands from the project root unless a section says otherwise.

## Set up the backend

```powershell
cd backend
uv sync
```

Check that FFmpeg is installed and available on PATH:

```powershell
ffmpeg -version
```

## Run transcription and fluency extraction together

Place your recording in the root `input` folder. From `backend`, run:

```powershell
uv run python -m app.pipelines.assess_speech ../input/interview.mp3
```

This transcribes the recording, aligns words, and calculates fluency features.
The first run may download speech models. Results are saved to
`output/interview_assessment.json` in the project root.

To choose another recording and output path:

```powershell
uv run python -m app.pipelines.assess_speech ../input/answer.mp3 --output ../output/answer_assessment.json
```

Existing output files are overwritten. Use one candidate answer per recording;
the pipeline does not separate speakers. If word alignment fails or no usable
word timings exist, the transcript is returned with fluency marked unavailable.
IELTS band prediction is not implemented yet.

## Run transcription only

From `backend`:

```powershell
uv run python -m app.services.transcription
```

This command reads `input/interview.mp3` and writes `output/interview.json` at
the project root. It does not calculate fluency features.

## Start the backend API

From `backend`:

```powershell
uv run uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000

API documentation: http://127.0.0.1:8000/docs

The API currently exposes the root status endpoint. The assessment pipeline
is run through the command above and is not connected to an upload endpoint yet.

## Start the frontend

Open a separate terminal at the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000/practice/speaking.
The speaking button is not connected to recording or assessment yet.
