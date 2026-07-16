# Local WhisperX Transcription

A small Windows project for local transcription, word alignment, and fluency feature extraction.

The scripts, `input` folder, and `output` folder are all located directly in this project folder. Relative paths are resolved from this folder, even when a script is launched from another working directory.

## Requirements

- Python 3.10, 64-bit
- FFmpeg installed and available on the Windows PATH
- An NVIDIA GPU and CUDA are optional
- CPU mode is supported (it is slower than GPU transcription)

## Create the virtual environment

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

PyTorch installation can differ by computer and CUDA version. If needed, follow the current PyTorch installation instructions for your system before installing the requirements.

## Install FFmpeg

Install FFmpeg and add its `bin` directory to the Windows PATH. Open a new terminal and verify it with:

```powershell
ffmpeg -version
```

## Check CUDA

```powershell
python -c "import torch; print(torch.cuda.is_available())"
```

`True` means WhisperX can use an NVIDIA GPU. `False` means the script will use CPU mode. CUDA only speeds up WhisperX transcription and alignment; CSV fluency analysis does not require CUDA.

## Run transcription

Normal:

```powershell
python transcribe.py "input\interview.mp3"
```

Smaller model:

```powershell
python transcribe.py "input\interview.mp3" --model medium
```

CPU:

```powershell
python transcribe.py "input\interview.mp3" --device cpu --model small
```

Lower batch size:

```powershell
python transcribe.py "input\interview.mp3" --batch-size 4
```

## Run fluency extraction

Entire word CSV:

```powershell
python fluency_features.py "output\interview\interview_words.csv"
```

Specific candidate answer:

```powershell
python fluency_features.py "output\interview\interview_words.csv" --answer-start 32.9 --answer-end 43.3 --question-end 31.9
```

Save JSON:

```powershell
python fluency_features.py "output\interview\interview_words.csv" --answer-start 32.9 --answer-end 43.3 --question-end 31.9 --output "output\interview\fluency.json"
```

## Explain the files

- `interview.txt` contains the readable transcript.
- `interview.json` contains the transcript, timestamps, segments, and available word-level alignment data.
- `interview_words.csv` contains one row per aligned word and is used for fluency feature extraction.
- `fluency.json` contains the calculated answer-level fluency features when `--output` is used.

## Important limitations

WhisperX may not reliably transcribe non-lexical sounds such as `ahhh`, `mhmmm`, and `mmm`. These can only be counted as fillers when WhisperX includes them in the transcript. A separate acoustic filler-detection model may be needed later for more accurate filler detection.
