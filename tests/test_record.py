#!/usr/bin/env python3
"""录音测试脚本 - 验证Linux下音频采集功能

使用方式:
    python tests/test_record.py [output.wav]
    python tests/test_record.py --list-devices  # 列出可用设备

    按Enter开始录音，再按Enter停止，保存到output.wav
"""

from __future__ import annotations

import sys
import threading
import queue
from pathlib import Path

import numpy as np
import sounddevice as sd

# 添加项目根目录到path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.wave_writer import write_wav


TARGET_SAMPLE_RATE = 16000  # FunASR需要的采样率
BLOCK_MS = 20


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """重采样音频到目标采样率"""
    if orig_sr == target_sr:
        return audio
    # 简单的线性插值重采样
    duration = len(audio) / orig_sr
    target_length = int(duration * target_sr)
    indices = np.linspace(0, len(audio) - 1, target_length)
    return np.interp(indices, np.arange(len(audio)), audio.astype(np.float32)).astype(np.int16)


def list_devices():
    """列出所有音频设备"""
    print("可用的音频设备:")
    print("-" * 60)
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        # 只显示输入设备
        if dev['max_input_channels'] > 0:
            marker = " <-- 默认输入" if i == sd.default.device[0] else ""
            print(f"  [{i}] {dev['name']}")
            print(f"      输入通道: {dev['max_input_channels']}, 采样率: {dev['default_samplerate']}Hz{marker}")
    print("-" * 60)
    print(f"默认输入设备索引: {sd.default.device[0]}")


def record_audio(device_id=None, output_file=None):
    """录音主函数"""
    output_path = Path(output_file) if output_file else Path("output.wav")

    print(f"录音测试脚本")
    print(f"目标采样率: {TARGET_SAMPLE_RATE}Hz")
    print(f"输出文件: {output_path}")

    # 获取设备信息和原生采样率
    if device_id is not None:
        dev_info = sd.query_devices(device_id)
        native_sr = int(dev_info['default_samplerate'])
        print(f"使用设备: [{device_id}] {dev_info['name']}")
        print(f"设备原生采样率: {native_sr}Hz")
    else:
        default_dev = sd.default.device[0]
        if default_dev is not None:
            dev_info = sd.query_devices(default_dev)
            native_sr = int(dev_info['default_samplerate'])
            print(f"使用默认设备: [{default_dev}] {dev_info['name']}")
            print(f"设备原生采样率: {native_sr}Hz")
        else:
            native_sr = 48000  # 常见默认值

    print("-" * 40)

    # 用于存储录音数据
    frames: list[np.ndarray] = []
    stop_event = threading.Event()

    block_size = int(native_sr * BLOCK_MS / 1000)
    audio_queue: queue.Queue = queue.Queue(maxsize=200)

    def audio_callback(indata, frame_count, time_info, status):
        if status:
            print(f"音频状态: {status}")
        try:
            audio_queue.put_nowait(indata.copy())
        except queue.Full:
            print("警告: 音频队列已满")

    def capture_thread():
        """后台线程持续从队列读取音频帧"""
        while not stop_event.is_set():
            try:
                frame = audio_queue.get(timeout=0.1)
                frames.append(frame)
            except queue.Empty:
                continue

    # 等待用户开始
    input("按 Enter 开始录音...")

    # 创建并启动音频流（使用设备原生采样率）
    try:
        stream = sd.InputStream(
            samplerate=native_sr,
            blocksize=block_size,
            device=device_id,
            channels=1,
            dtype='int16',
            callback=audio_callback,
        )
        stream.start()
    except Exception as e:
        print(f"错误: 无法启动音频流: {e}")
        print("\n尝试使用 --list-devices 查看可用设备")
        print("然后使用 --device N 指定设备号")
        sys.exit(1)

    # 启动采集线程
    collector = threading.Thread(target=capture_thread, daemon=True)
    collector.start()

    print("正在录音... 按 Enter 停止")

    # 等待用户停止
    input()

    # 停止录音
    stop_event.set()
    stream.stop()
    stream.close()
    collector.join(timeout=1.0)

    # 检查是否有数据
    if not frames:
        print("错误: 没有采集到任何音频数据")
        sys.exit(1)

    # 合并音频帧
    audio_data = np.concatenate(frames).flatten()
    duration = len(audio_data) / native_sr

    print(f"录音完成!")
    print(f"  帧数: {len(frames)}")
    print(f"  原始采样点: {len(audio_data)}")
    print(f"  时长: {duration:.2f}秒")

    # 检查是否全是静音
    max_amplitude = np.max(np.abs(audio_data))
    print(f"  最大振幅: {max_amplitude}")
    if max_amplitude < 100:
        print("  警告: 音频信号非常弱，可能是设备选择错误")

    # 重采样到目标采样率
    if native_sr != TARGET_SAMPLE_RATE:
        print(f"  重采样: {native_sr}Hz -> {TARGET_SAMPLE_RATE}Hz")
        audio_data = resample_audio(audio_data, native_sr, TARGET_SAMPLE_RATE)
        print(f"  重采样后采样点: {len(audio_data)}")

    # 保存WAV文件
    pcm_bytes = audio_data.tobytes()
    write_wav(output_path, pcm_bytes, TARGET_SAMPLE_RATE)

    print(f"已保存到: {output_path}")
    print(f"可用以下命令播放: aplay {output_path}")


def main():
    # 解析参数
    if "--list-devices" in sys.argv or "-l" in sys.argv:
        list_devices()
        return

    device_id = None
    output_file = None

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ("--device", "-d") and i + 1 < len(sys.argv):
            device_id = int(sys.argv[i + 1])
            i += 2
        elif arg in ("--output", "-o") and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif not arg.startswith("-"):
            output_file = arg
            i += 1
        else:
            i += 1

    record_audio(device_id, output_file)


if __name__ == "__main__":
    main()
