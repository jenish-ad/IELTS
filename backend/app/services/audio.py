import shutil
import subprocess
from pathlib import Path


def convert_to_wav(
    input_path: str | Path,
    wav_path: str | Path,
) -> Path:
    # convert input audio into 16KHz mono wav file using ffmpeg
    input_path = Path(input_path).expanduser().resolve()
    wav_path = Path(wav_path).expanduser().resolve()

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if input_path == wav_path:
        raise ValueError("Input and output paths must be different.")

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("Install FFmpeg and add it to PATH.")

    wav_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        ffmpeg,
        "-nostdin",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        "-f",
        "wav",
        str(wav_path),
    ]

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Audio conversion exceeded the 300-second timeout.") from exc

    if completed.returncode != 0:
        message = completed.stderr.strip() or "Unknown FFmpeg error."
        raise RuntimeError(f"Audio conversion failed: {message}")

    return wav_path
