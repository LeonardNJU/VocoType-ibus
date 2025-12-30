#!/usr/bin/env python3
"""转写测试脚本 - 验证FunASR语音识别功能

使用方式:
    python tests/test_transcribe.py input.wav
    python tests/test_transcribe.py input.wav --use-vad   # 启用VAD
    python tests/test_transcribe.py input.wav --use-punc  # 启用标点恢复
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# 添加项目根目录到path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.funasr_server import FunASRServer


def main():
    # 解析参数
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        print("示例:")
        print("  python tests/test_transcribe.py output.wav")
        sys.exit(0 if "--help" in sys.argv or "-h" in sys.argv else 1)

    audio_path = Path(sys.argv[1])
    if not audio_path.exists():
        print(f"错误: 文件不存在: {audio_path}")
        sys.exit(1)

    use_vad = "--use-vad" in sys.argv
    use_punc = "--use-punc" in sys.argv

    print(f"转写测试脚本")
    print(f"音频文件: {audio_path}")
    print(f"VAD: {'启用' if use_vad else '禁用'}")
    print(f"标点恢复: {'启用' if use_punc else '禁用'}")
    print("-" * 40)

    # 创建FunASR服务器
    print("正在初始化FunASR...")
    start_time = time.time()

    server = FunASRServer()
    init_result = server.initialize()

    if not init_result["success"]:
        print(f"错误: 初始化失败: {init_result.get('error', '未知错误')}")
        sys.exit(1)

    init_time = time.time() - start_time
    print(f"初始化完成 (耗时 {init_time:.2f}秒)")
    print("-" * 40)

    # 转录音频
    print("正在转录...")
    start_time = time.time()

    options = {
        "use_vad": use_vad,
        "use_punc": use_punc,
    }

    result = server.transcribe_audio(str(audio_path), options)

    transcribe_time = time.time() - start_time

    if not result.get("success", False):
        print(f"错误: 转录失败: {result.get('error', '未知错误')}")
        sys.exit(1)

    # 显示结果
    text = result.get("text", "")
    print(f"转录完成 (耗时 {transcribe_time:.2f}秒)")
    print("-" * 40)
    print("识别结果:")
    print()
    print(text)
    print()
    print("-" * 40)

    # 清理
    server.cleanup()


if __name__ == "__main__":
    main()
