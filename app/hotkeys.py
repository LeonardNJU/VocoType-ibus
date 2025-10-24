"""Global hotkey management for the application."""

from __future__ import annotations

import logging
import threading
from typing import Callable

import keyboard


logger = logging.getLogger(__name__)


class HotkeyManager:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._registrations = {}

    def register(self, combo: str, callback: Callable[[], None]) -> None:
        with self._lock:
            if combo in self._registrations:
                logger.warning("热键 %s 已注册，覆盖旧的回调", combo)
                keyboard.remove_hotkey(self._registrations[combo])

            try:
                hotkey_id = keyboard.add_hotkey(combo, callback)
            except Exception as exc:  # noqa: BLE001
                logger.error("注册热键 %s 失败: %s", combo, exc)
                raise

            self._registrations[combo] = hotkey_id
            logger.info("已注册热键 %s", combo)

    def unregister_all(self) -> None:
        with self._lock:
            for combo, hotkey_id in list(self._registrations.items()):
                keyboard.remove_hotkey(hotkey_id)
                logger.info("已移除热键 %s", combo)
            self._registrations.clear()

    def cleanup(self) -> None:
        self.unregister_all()
        # 彻底停止 keyboard 库的所有钩子和监听线程
        try:
            keyboard.unhook_all()
            logger.info("已停止 keyboard 监听线程")
        except Exception as exc:
            logger.warning("停止 keyboard 监听线程失败: %s", exc)


