# Speech assessment pipeline

From the `backend` directory, transcribe a recording and calculate fluency:

```powershell
uv run python -m app.pipelines.assess_speech ../input/interview.mp3
```

Use a recording of one candidate answer for meaningful fluency measurements.
The pipeline does not separate speakers or predict IELTS bands.
FFmpeg must be on PATH; speech models may download on the first run.

Results are saved to `output/interview_assessment.json` at the project root.
Use `--output path/to/result.json` to choose another output file. Existing
output files are overwritten. Relative paths are resolved from your terminal's
current directory.

The result contains `transcription`, `fluency`, and `warnings`. When alignment
fails or no usable word timings exist, fluency has `status: "unavailable"` and
`metrics: null`; the transcript is still returned. Other processing errors
propagate to the caller.
