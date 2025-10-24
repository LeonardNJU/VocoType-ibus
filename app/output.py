"""Text injection utilities for Windows."""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wintypes
import logging


logger = logging.getLogger(__name__)

SendInput = ctypes.windll.user32.SendInput
GetMessageExtraInfo = ctypes.windll.user32.GetMessageExtraInfo

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_CONTROL = 0x11
VK_V = 0x56


if hasattr(wintypes, "ULONG_PTR"):
    ULONG_PTR = wintypes.ULONG_PTR  # type: ignore[attr-defined]
else:  # Fallback for Python builds lacking ULONG_PTR in wintypes
    if ctypes.sizeof(ctypes.c_void_p) == ctypes.sizeof(ctypes.c_uint64):
        ULONG_PTR = ctypes.c_uint64
    else:
        ULONG_PTR = ctypes.c_uint32


class KeyboardInput(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class InputUnion(ctypes.Union):
    _fields_ = [("ki", KeyboardInput)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", InputUnion)]


def _emit_unicode_char(char: str) -> bool:
    code_point = ord(char)
    input_array_type = INPUT * 2
    inputs = input_array_type(
        INPUT(
            type=INPUT_KEYBOARD,
            union=InputUnion(
                ki=KeyboardInput(
                    wVk=0,
                    wScan=code_point,
                    dwFlags=KEYEVENTF_UNICODE,
                    time=0,
                    dwExtraInfo=GetMessageExtraInfo(),
                )
            ),
        ),
        INPUT(
            type=INPUT_KEYBOARD,
            union=InputUnion(
                ki=KeyboardInput(
                    wVk=0,
                    wScan=code_point,
                    dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                    time=0,
                    dwExtraInfo=GetMessageExtraInfo(),
                )
            ),
        ),
    )
    pointer = ctypes.byref(inputs[0])
    sent = SendInput(len(inputs), pointer, ctypes.sizeof(INPUT))
    if sent != len(inputs):
        logger.warning("SendInput 发送字符失败，char=%s，返回值=%s", char, sent)
        return False
    return True


def type_text(text: str, append_newline: bool = False, method: str = "auto") -> None:
    if not text:
        return

    payload = text + ("\r\n" if append_newline else "")
    logger.debug("注入文本: %s", payload)

    method = (method or "auto").lower()
    if method == "type":
        order = ["type", "clipboard", "unicode"]
    elif method == "clipboard":
        order = ["clipboard", "type", "unicode"]
    elif method == "unicode":
        order = ["unicode"]
    else:
        order = ["type", "clipboard", "unicode"]

    for mode in order:
        if mode == "type" and _type_with_keyboard(payload):
            return
        if mode == "clipboard" and _try_clipboard_injection(payload):
            return
        if mode == "unicode" and _type_with_unicode(payload):
            return

    logger.error("所有文本注入方式均失败: %s", payload)


def _type_with_keyboard(payload: str) -> bool:
    try:
        import keyboard

        keyboard.write(payload, delay=0)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("keyboard.write 失败: %s", exc)
        return False


def _type_with_unicode(payload: str) -> bool:
    success = True
    for char in payload:
        if not _emit_unicode_char(char):
            success = False
            break
    return success


def _try_clipboard_injection(payload: str) -> bool:
    try:
        import pyperclip
    except ImportError:
        return False

    try:
        prev_clip = pyperclip.paste()
    except Exception:
        prev_clip = None

    try:
        pyperclip.copy(payload)
        success = _emit_ctrl_v()
    except Exception as exc:  # noqa: BLE001
        logger.debug("剪贴板注入失败，退回逐字符输入: %s", exc)
        success = False
    finally:
        if prev_clip is not None:
            try:
                pyperclip.copy(prev_clip)
            except Exception:
                pass

    return success


def _emit_ctrl_v() -> bool:
    input_array_type = INPUT * 4
    inputs = input_array_type(
        INPUT(
            type=INPUT_KEYBOARD,
            union=InputUnion(
                ki=KeyboardInput(
                    wVk=VK_CONTROL,
                    wScan=0,
                    dwFlags=0,
                    time=0,
                    dwExtraInfo=GetMessageExtraInfo(),
                )
            ),
        ),
        INPUT(
            type=INPUT_KEYBOARD,
            union=InputUnion(
                ki=KeyboardInput(
                    wVk=VK_V,
                    wScan=0,
                    dwFlags=0,
                    time=0,
                    dwExtraInfo=GetMessageExtraInfo(),
                )
            ),
        ),
        INPUT(
            type=INPUT_KEYBOARD,
            union=InputUnion(
                ki=KeyboardInput(
                    wVk=VK_V,
                    wScan=0,
                    dwFlags=KEYEVENTF_KEYUP,
                    time=0,
                    dwExtraInfo=GetMessageExtraInfo(),
                )
            ),
        ),
        INPUT(
            type=INPUT_KEYBOARD,
            union=InputUnion(
                ki=KeyboardInput(
                    wVk=VK_CONTROL,
                    wScan=0,
                    dwFlags=KEYEVENTF_KEYUP,
                    time=0,
                    dwExtraInfo=GetMessageExtraInfo(),
                )
            ),
        ),
    )
    pointer = ctypes.byref(inputs[0])
    sent = SendInput(len(inputs), pointer, ctypes.sizeof(INPUT))
    if sent != len(inputs):
        logger.warning("SendInput Ctrl+V 失败，返回值=%s", sent)
        # 尝试一次退避后再次发送
        sent_retry = SendInput(len(inputs), pointer, ctypes.sizeof(INPUT))
        if sent_retry != len(inputs):
            logger.warning("SendInput Ctrl+V 第二次重试失败，返回值=%s", sent_retry)
            return False

    return True

