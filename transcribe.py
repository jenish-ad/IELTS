import argparse
import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import torch
import whisperx


PROJECT_DIR = Path(__file__).resolve().parent


def project_path(path_value):
    path = Path(path_value).expanduser()
    return path if path.is_absolute() else PROJECT_DIR / path


def parse_args():
    parser = argparse.ArgumentParser(description="Transcribe and align an audio or video file with WhisperX.")
    parser.add_argument("input_file", help="Path to the input audio or video file")
    parser.add_argument("--model", default="large-v3", help="Whisper model name (default: large-v3)")
    parser.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--language", default="en")
    return parser.parse_args()

def convert_to_wav(input_path, wav_path):
    command = [
        "ffmpeg", "-y", "-i", str(input_path), "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", str(wav_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True)
    if completed.returncode != 0:
        message = completed.stderr.strip() or "FFmpeg returned an unknown error."
        raise RuntimeError(f"FFmpeg could not convert the input file:\n{message}")


def aligned_words(segments):
    words = []
    for segment in segments:
        for item in segment.get("words", []):
            if item.get("start") is not None and item.get("end") is not None:
                words.append(item)
    return sorted(words, key=lambda item: float(item["start"]))


def save_outputs(result, input_path, output_dir, language, duration, alignment_completed):
    stem = input_path.stem
    txt_path = output_dir / f"{stem}.txt"
    json_path = output_dir / f"{stem}.json"
    csv_path = output_dir / f"{stem}_words.csv"
    segments = result.get("segments", [])

    transcript = " ".join(segment.get("text", "").strip() for segment in segments).strip()
    txt_path.write_text(transcript + ("\n" if transcript else ""), encoding="utf-8")

    payload = {
        "source_file": input_path.as_posix(),
        "language": result.get("language", language),
        "duration_seconds": round(float(duration), 3),
        "alignment_completed": alignment_completed,
        "segments": segments,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    previous_end = None
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=("word", "start", "end", "duration", "score", "pause_before")
        )
        writer.writeheader()
        if alignment_completed:
            for item in aligned_words(segments):
                start = float(item["start"])
                end = float(item["end"])
                pause = 0.0 if previous_end is None else max(0.0, start - previous_end)
                writer.writerow({
                    "word": item.get("word", "").strip(),
                    "start": round(start, 3),
                    "end": round(end, 3),
                    "duration": round(max(0.0, end - start), 3),
                    "score": item.get("score", ""),
                    "pause_before": round(pause, 3),
                })
                previous_end = end
    return txt_path, json_path, csv_path


def main():
    args = parse_args()
    input_path = project_path(args.input_file)
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg was not found. Install FFmpeg and add it to the Windows PATH.")
    if args.batch_size < 1:
        raise ValueError("--batch-size must be at least 1.")

    device = "cuda" if args.device == "auto" and torch.cuda.is_available() else args.device
    if device == "auto":
        device = "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested, but PyTorch cannot access a CUDA-capable GPU.")
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"Using device: {device}")

# q
    output_dir = PROJECT_DIR / "output" / input_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temporary_file:
            temporary_path = Path(temporary_file.name)
        print("Converting input to temporary 16 kHz mono WAV...")
        convert_to_wav(input_path, temporary_path)
        audio = whisperx.load_audio(str(temporary_path))
        duration = len(audio) / 16000

        print(f"Loading WhisperX model: {args.model}")
        model = whisperx.load_model(args.model, device, compute_type=compute_type, language=args.language)
        result = model.transcribe(audio, batch_size=args.batch_size, language=args.language)

        alignment_completed = False
        try:
            align_model, metadata = whisperx.load_align_model(
                language_code=result.get("language", args.language), device=device
            )
            result = whisperx.align(
                result.get("segments", []), align_model, metadata, audio, device,
                return_char_alignments=False,
            )
            result["language"] = result.get("language", args.language)
            alignment_completed = True
        except Exception as error:
            print(f"Warning: word-level alignment failed: {error}", file=sys.stderr)
            print("Saving the segment-level transcript without aligned words.", file=sys.stderr)

        paths = save_outputs(
            result, input_path, output_dir, args.language, duration, alignment_completed
        )
        print("\nFirst transcript segments:")
        for segment in result.get("segments", [])[:10]:
            print(f"[{segment.get('start', 0):.2f} - {segment.get('end', 0):.2f}] {segment.get('text', '').strip()}")
        print("\nGenerated files:")
        for path in paths:
            print(path.resolve())
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTranscription cancelled by user.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
