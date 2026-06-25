"""Read-only audio loading utilities."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


def load_audio(path: Path) -> dict:
    """Load an audio file as normalized floating point samples."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Audio path is not a file: {path}")

    try:
        info = sf.info(path)
        audio, samplerate = sf.read(path, dtype="float64", always_2d=True)
    except Exception as exc:
        raise ValueError(f"Could not read audio file {path}: {exc}") from exc

    if audio.ndim != 2:
        audio = np.asarray(audio, dtype=np.float64).reshape(-1, 1)

    frames = int(audio.shape[0])
    channels = int(audio.shape[1])
    duration_seconds = frames / float(samplerate) if samplerate else 0.0

    return {
        "path": str(path),
        "samplerate": int(samplerate),
        "channels": channels,
        "frames": frames,
        "duration_seconds": float(duration_seconds),
        "subtype": info.subtype,
        "format": info.format,
        "audio": np.asarray(audio, dtype=np.float64),
    }
