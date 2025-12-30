#!/usr/bin/env python3
"""VoCoType IBus Engine Factory"""

import logging

from gi.repository import IBus

from .engine import VoCoTypeEngine

logger = logging.getLogger(__name__)


class VoCoTypeFactory(IBus.Factory):
    """创建VoCoType引擎实例的工厂"""

    def __init__(self, bus: IBus.Bus):
        self._bus = bus
        super().__init__(
            connection=bus.get_connection(),
            object_path=IBus.PATH_FACTORY
        )
        self._engine_count = 0
        logger.info("VoCoTypeFactory 已创建")

    def do_create_engine(self, engine_name: str):
        """创建引擎实例"""
        logger.info(f"Creating engine for: {engine_name}")
        self._engine_count += 1
        object_path = f"/org/freedesktop/IBus/Engine/{engine_name}/{self._engine_count}"
        engine = VoCoTypeEngine(self._bus, object_path)
        logger.info(f"Engine #{self._engine_count} created")
        return engine
