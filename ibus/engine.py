#!/usr/bin/env python3
"""VoCoType IBus Engine - PTT语音输入法引擎

按住F9说话，松开后识别并输入到光标处。
"""

from __future__ import annotations

import logging
import threading
import queue
import tempfile
import os
from pathlib import Path
from typing import Optional

import numpy as np

import gi
gi.require_version('IBus', '1.0')
from gi.repository import IBus, GLib

logger = logging.getLogger(__name__)

# 音频参数
SAMPLE_RATE = 16000
DEFAULT_NATIVE_SAMPLE_RATE = 44100
BLOCK_MS = 20
AUDIO_DEVICE = None  # None 表示使用默认输入设备


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """重采样音频到目标采样率"""
    if orig_sr == target_sr:
        return audio
    duration = len(audio) / orig_sr
    target_length = int(duration * target_sr)
    indices = np.linspace(0, len(audio) - 1, target_length)
    return np.interp(indices, np.arange(len(audio)), audio.astype(np.float32)).astype(np.int16)


class VoCoTypeEngine(IBus.Engine):
    """VoCoType IBus语音输入引擎"""

    __gtype_name__ = 'VoCoTypeEngine'

    # PTT触发键
    PTT_KEYVAL = IBus.KEY_F9

    def __init__(self, bus: IBus.Bus, object_path: str):
        # 需要显式传入 DBus 连接与 object_path，避免 GLib g_variant object_path 断言失败。
        super().__init__(connection=bus.get_connection(), object_path=object_path)

        # 状态
        self._is_recording = False
        self._audio_frames: list[np.ndarray] = []
        self._audio_queue: queue.Queue = queue.Queue(maxsize=500)
        self._stop_event = threading.Event()
        self._capture_thread: Optional[threading.Thread] = None
        self._stream = None

        # ASR服务器（懒加载）
        self._asr_server = None
        self._asr_initializing = False
        self._asr_ready = threading.Event()
        self._native_sample_rate = DEFAULT_NATIVE_SAMPLE_RATE

        logger.info("VoCoTypeEngine 实例已创建")

    def _resolve_input_device(self, sd):
        """选择可用的输入设备，优先使用显式配置。"""
        if AUDIO_DEVICE is not None:
            try:
                info = sd.query_devices(AUDIO_DEVICE)
                if info.get("max_input_channels", 0) > 0:
                    return AUDIO_DEVICE
                logger.warning("设备 %s 无输入通道，回退选择输入设备", AUDIO_DEVICE)
            except Exception as exc:
                logger.warning("查询设备 %s 失败: %s", AUDIO_DEVICE, exc)

        try:
            devices = sd.query_devices()
            for idx, info in enumerate(devices):
                if info.get("max_input_channels", 0) > 0:
                    logger.info("回退至输入设备 #%s (%s)", idx, info.get("name", "unknown"))
                    return idx
        except Exception as exc:
            logger.warning("查询输入设备列表失败: %s", exc)

        return None

    def _resolve_sample_rate(self, sd, device, preferred):
        """选择可用采样率，优先使用指定值。"""
        if preferred:
            try:
                sd.check_input_settings(
                    device=device,
                    samplerate=preferred,
                    channels=1,
                    dtype="int16",
                )
                return preferred
            except Exception:
                pass

        try:
            info = sd.query_devices(device if device is not None else None, kind="input")
            default_sr = int(info.get("default_samplerate", 0)) if info else 0
            if default_sr:
                sd.check_input_settings(
                    device=device,
                    samplerate=default_sr,
                    channels=1,
                    dtype="int16",
                )
                return default_sr
        except Exception:
            pass

        return preferred or SAMPLE_RATE

    def do_enable(self):
        """引擎启用"""
        logger.info("Engine enabled")

    def do_disable(self):
        """引擎禁用"""
        logger.info("Engine disabled")
        if self._is_recording:
            self._stop_recording()

    def do_focus_in(self):
        """获得输入焦点"""
        logger.info("Engine got focus")

    def do_focus_out(self):
        """失去输入焦点"""
        logger.info("Engine lost focus")
        if self._is_recording:
            self._stop_recording()

    def _ensure_asr_ready(self):
        """确保ASR服务器已初始化（懒加载）"""
        if self._asr_server is not None:
            return True

        if self._asr_initializing:
            # 等待初始化完成
            return self._asr_ready.wait(timeout=60)

        self._asr_initializing = True

        def init_asr():
            try:
                logger.info("开始初始化FunASR...")
                from app.funasr_server import FunASRServer
                self._asr_server = FunASRServer()
                result = self._asr_server.initialize()
                if result["success"]:
                    logger.info("FunASR初始化成功")
                    self._asr_ready.set()
                else:
                    logger.error(f"FunASR初始化失败: {result.get('error')}")
                    self._asr_server = None
            except Exception as e:
                logger.error(f"FunASR初始化异常: {e}")
                self._asr_server = None
            finally:
                self._asr_initializing = False

        # 后台初始化
        threading.Thread(target=init_asr, daemon=True).start()
        return False

    def do_process_key_event(self, keyval, keycode, state):
        """处理按键事件"""
        # 调试：记录所有按键
        is_release = bool(state & IBus.ModifierType.RELEASE_MASK)
        logger.info(f"Key event: keyval={keyval}, keycode={keycode}, state={state}, is_release={is_release}, F9={self.PTT_KEYVAL}")

        # 检查是否是松开事件
        is_release = bool(state & IBus.ModifierType.RELEASE_MASK)

        # 只处理F9键
        if keyval != self.PTT_KEYVAL:
            return False

        if not is_release:
            # F9按下 -> 开始录音
            if not self._is_recording:
                self._start_recording()
            return True
        else:
            # F9松开 -> 停止录音并转录
            if self._is_recording:
                self._stop_and_transcribe()
            return True

    def do_focus_out(self):
        """失去焦点时停止录音"""
        if self._is_recording:
            self._stop_recording()
        return

    def do_disable(self):
        """禁用时清理"""
        if self._is_recording:
            self._stop_recording()
        return

    def _start_recording(self):
        """开始录音"""
        if self._is_recording:
            return

        try:
            import sounddevice as sd

            self._is_recording = True
            self._audio_frames.clear()
            self._stop_event.clear()

            # 清空队列
            while not self._audio_queue.empty():
                try:
                    self._audio_queue.get_nowait()
                except queue.Empty:
                    break

            device = self._resolve_input_device(sd)
            sample_rate = self._resolve_sample_rate(sd, device, DEFAULT_NATIVE_SAMPLE_RATE)
            self._native_sample_rate = sample_rate
            block_size = int(sample_rate * BLOCK_MS / 1000)

            def audio_callback(indata, frame_count, time_info, status):
                if status:
                    logger.warning(f"音频状态: {status}")
                try:
                    self._audio_queue.put_nowait(indata.copy())
                except queue.Full:
                    pass

            # 创建音频流
            self._stream = sd.InputStream(
                samplerate=sample_rate,
                blocksize=block_size,
                device=device,
                channels=1,
                dtype='int16',
                callback=audio_callback,
            )
            self._stream.start()

            # 启动采集线程
            def capture_loop():
                while not self._stop_event.is_set():
                    try:
                        frame = self._audio_queue.get(timeout=0.1)
                        self._audio_frames.append(frame)
                    except queue.Empty:
                        continue

            self._capture_thread = threading.Thread(target=capture_loop, daemon=True)
            self._capture_thread.start()

            # 显示录音状态
            self._update_preedit("🎤 录音中...")
            logger.info("开始录音")

            # 确保ASR已初始化
            self._ensure_asr_ready()

        except Exception as e:
            logger.error(f"启动录音失败: {e}")
            self._is_recording = False
            self._update_preedit(f"❌ 录音失败: {e}")
            GLib.timeout_add(2000, self._clear_preedit)

    def _stop_recording(self):
        """停止录音（不转录）"""
        if not self._is_recording:
            return

        self._stop_event.set()

        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except:
                pass
            self._stream = None

        if self._capture_thread:
            self._capture_thread.join(timeout=1.0)
            self._capture_thread = None

        self._is_recording = False
        self._clear_preedit()
        logger.info("录音已停止")

    def _stop_and_transcribe(self):
        """停止录音并转录"""
        if not self._is_recording:
            return

        # 停止录音
        self._stop_event.set()

        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except:
                pass
            self._stream = None

        if self._capture_thread:
            self._capture_thread.join(timeout=1.0)
            self._capture_thread = None

        self._is_recording = False

        # 检查是否有音频数据
        if not self._audio_frames:
            self._clear_preedit()
            return

        # 合并音频
        audio_data = np.concatenate(self._audio_frames).flatten()
        self._audio_frames.clear()

        duration = len(audio_data) / self._native_sample_rate
        logger.info(f"录音完成，时长: {duration:.2f}秒")

        # 检查是否太短
        if duration < 0.3:
            self._clear_preedit()
            return

        # 显示识别中状态
        self._update_preedit("⏳ 识别中...")

        # 在后台线程中转录
        def do_transcribe():
            try:
                # 重采样
                audio_16k = resample_audio(audio_data, self._native_sample_rate, SAMPLE_RATE)

                # 写入临时文件
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    temp_path = f.name
                    from app.wave_writer import write_wav
                    write_wav(Path(temp_path), audio_16k.tobytes(), SAMPLE_RATE)

                try:
                    # 等待ASR就绪
                    if not self._asr_ready.wait(timeout=30):
                        GLib.idle_add(self._show_error, "ASR未就绪")
                        return

                    # 转录
                    result = self._asr_server.transcribe_audio(temp_path)

                    if result.get("success"):
                        text = result.get("text", "").strip()
                        if text:
                            GLib.idle_add(self._commit_text, text)
                        else:
                            GLib.idle_add(self._clear_preedit)
                    else:
                        error = result.get("error", "未知错误")
                        GLib.idle_add(self._show_error, error)
                finally:
                    # 删除临时文件
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

            except Exception as e:
                logger.error(f"转录失败: {e}")
                GLib.idle_add(self._show_error, str(e))

        threading.Thread(target=do_transcribe, daemon=True).start()

    def _update_preedit(self, text: str):
        """更新预编辑文本"""
        preedit = IBus.Text.new_from_string(text)
        self.update_preedit_text(preedit, len(text), True)

    def _clear_preedit(self):
        """清除预编辑文本"""
        self.update_preedit_text(IBus.Text.new_from_string(""), 0, False)
        return False  # 用于GLib.timeout_add

    def _commit_text(self, text: str):
        """提交文本到应用"""
        self._clear_preedit()
        self.commit_text(IBus.Text.new_from_string(text))
        logger.info(f"已提交文本: {text}")
        return False

    def _show_error(self, error: str):
        """显示错误信息"""
        self._update_preedit(f"❌ {error}")
        GLib.timeout_add(2000, self._clear_preedit)
        return False
