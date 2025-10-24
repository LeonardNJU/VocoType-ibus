"""Utility to persist PCM data to WAV files for diagnostics."""

from __future__ import annotations

import contextlib
import wave
from pathlib import Path
from typing import Iterable


def write_wav(path: Path, samples: bytes, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.closing(wave.open(str(path), "wb")) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples)


