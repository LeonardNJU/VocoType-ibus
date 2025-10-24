"""AOP-style wrapper to persist each transcription audio/text when enabled."""

from __future__ import annotations

import json
import logging
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable


logger = logging.getLogger(__name__)


def wrap_result_handler(
    handler: Callable,
    worker,
    dataset_dir: str,
) -> Callable:
    """Wrap the base result handler to dump audio + transcript atomically.

    The wrapper is best-effort: any failure is logged but swallowed so the original
    handler continues unaffected.
    
    Args:
        handler: 原始的 result handler
        worker: TranscriptionWorker 实例（用于访问 last_segment_path）
        dataset_dir: 数据集保存目录
    
    Returns:
        包装后的 handler，会自动保存音频和转录文本
    """

    base = Path(dataset_dir)
    audio_dir = base / "audio"
    jsonl_path = base / "dataset.jsonl"
    audio_dir.mkdir(parents=True, exist_ok=True)
    base.mkdir(parents=True, exist_ok=True)
    
    logger.info("数据集记录器已启用，数据将保存到: %s", base.absolute())

    def _atomic_copy(src: Path, dst: Path) -> None:
        tmp = dst.with_suffix(dst.suffix + ".tmp")
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)

    def wrapped(result) -> None:
        # 先调用原始 handler，确保正常输出不受影响
        handler_result = None
        try:
            handler_result = handler(result)
        except Exception as exc:
            logger.error("原始 handler 执行失败: %s", exc, exc_info=True)
            raise  # 重新抛出，保持原有行为
        
        # 然后保存数据集（失败不影响正常流程）
        try:
            # 跳过错误的转录结果
            if getattr(result, "error", None):
                logger.debug("转录失败，跳过数据集记录")
                return handler_result

            # 获取音频文件路径
            src = getattr(worker, "last_segment_path", None)
            if not src:
                logger.warning("未找到音频文件路径，跳过数据集记录")
                return handler_result

            src_path = Path(src)
            if not src_path.exists():
                logger.warning("音频文件不存在: %s，跳过数据集记录", src_path)
                return handler_result

            # 生成唯一 ID 并保存音频文件
            item_id = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}-{uuid.uuid4().hex[:8]}"
            dst_wav = audio_dir / f"{item_id}.wav"
            _atomic_copy(src_path, dst_wav)

            # 构建记录
            record = {
                "id": item_id,
                "audio": str(Path("audio") / f"{item_id}.wav"),
                "text": getattr(result, "text", ""),
                "raw_text": getattr(result, "raw_text", ""),
                "duration": getattr(result, "duration", 0.0),
                "sample_rate": getattr(worker, "_audio_cfg", {}).get("sample_rate", 16000),
                "inference_latency": getattr(result, "inference_latency", 0.0),
                "confidence": getattr(result, "confidence", 0.0),
                "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
            
            # 追加到 JSONL 文件
            with open(jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            
            logger.info("已保存数据集样本 %s (文本: %s)", item_id, record["text"][:50])
        except Exception as exc:
            logger.error("保存数据集失败: %s", exc, exc_info=True)
            # 吞掉异常，不影响正常流程

        return handler_result

    return wrapped


__all__ = ["wrap_result_handler"]
