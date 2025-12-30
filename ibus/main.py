#!/usr/bin/env python3
"""VoCoType IBus Engine 主程序"""

from __future__ import annotations

import sys
import os
import argparse
import logging
from pathlib import Path

# 添加项目根目录到path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import gi
gi.require_version('IBus', '1.0')
from gi.repository import IBus, GLib

from ibus.factory import VoCoTypeFactory

logger = logging.getLogger(__name__)


class VoCoTypeIMApp:
    """VoCoType输入法应用"""

    def __init__(self, exec_by_ibus: bool = True):
        IBus.init()
        self._mainloop = GLib.MainLoop()
        self._bus = IBus.Bus()

        if not self._bus.is_connected():
            logger.error("无法连接到IBus守护进程")
            sys.exit(1)

        self._bus.connect("disconnected", self._on_bus_disconnected)
        self._factory = VoCoTypeFactory(self._bus)

        if exec_by_ibus:
            self._bus.request_name("org.vocotype.IBus.VoCoType", 0)
        else:
            self._register_component()

        logger.info("VoCoType IBus引擎已启动")

    def _register_component(self):
        """注册IBus组件（调试用）"""
        component = IBus.Component.new(
            "org.vocotype.IBus.VoCoType",
            "VoCoType Voice Input Method",
            "1.0.0",
            "GPL",
            "VoCoType",
            "https://github.com/vocotype",
            "",
            "vocotype"
        )

        engine = IBus.EngineDesc.new(
            "vocotype",
            "VoCoType Voice Input",
            "Push-to-Talk Voice Input (F9)",
            "zh",
            "GPL",
            "VoCoType",
            "",  # icon
            "default"
        )

        component.add_engine(engine)
        self._bus.register_component(component)

    def run(self):
        """运行主循环"""
        self._mainloop.run()

    def quit(self):
        """退出"""
        self._mainloop.quit()

    def _on_bus_disconnected(self, bus):
        """IBus断开连接"""
        logger.info("IBus连接已断开")
        self._mainloop.quit()


def print_xml():
    """输出引擎XML描述"""
    print('''<?xml version="1.0" encoding="utf-8"?>
<component>
    <name>org.vocotype.IBus.VoCoType</name>
    <description>VoCoType Voice Input Method</description>
    <exec>{exec_path} --ibus</exec>
    <version>1.0.0</version>
    <author>VoCoType</author>
    <license>GPL</license>
    <homepage>https://github.com/vocotype</homepage>
    <textdomain>vocotype</textdomain>
    <engines>
        <engine>
            <name>vocotype</name>
            <language>zh</language>
            <license>GPL</license>
            <author>VoCoType</author>
            <layout>default</layout>
            <longname>VoCoType Voice Input</longname>
            <description>Push-to-Talk Voice Input (F9)</description>
            <rank>50</rank>
            <symbol>🎤</symbol>
        </engine>
    </engines>
</component>'''.format(exec_path=os.path.abspath(__file__)))


def main():
    parser = argparse.ArgumentParser(description='VoCoType IBus Engine')
    parser.add_argument('--ibus', '-i', action='store_true',
                        help='由IBus守护进程启动')
    parser.add_argument('--xml', '-x', action='store_true',
                        help='输出引擎XML描述')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='启用调试日志')
    args = parser.parse_args()

    if args.xml:
        print_xml()
        return

    # 配置日志
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr),
        ]
    )

    # 创建并运行应用
    app = VoCoTypeIMApp(exec_by_ibus=args.ibus)

    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()


if __name__ == "__main__":
    main()
