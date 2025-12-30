"""Core runtime package for the speak-keyboard application."""

import sys

from .config import DEFAULT_CONFIG, ensure_logging_dir, load_config
from .audio_capture import AudioCapture
from .transcribe import TranscriptionWorker, TranscriptionResult
from .hotkeys import HotkeyManager

# output.py 仅在 Windows 下可用
if sys.platform == "win32":
    from .output import type_text
else:
    type_text = None  # Linux下暂不可用，将由IBus引擎替代

__all__ = [
    "DEFAULT_CONFIG",
    "ensure_logging_dir",
    "load_config",
    "AudioCapture",
    "TranscriptionWorker",
    "TranscriptionResult",
    "HotkeyManager",
    "type_text",
]



