#!/bin/bash
# VoCoType Linux IBus 语音输入法安装脚本（用户级安装）
# 基于 VoCoType 核心引擎: https://github.com/233stone/vocotype-cli

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 用户级安装路径
INSTALL_DIR="$HOME/.local/share/vocotype"
COMPONENT_DIR="$HOME/.local/share/ibus/component"
LIBEXEC_DIR="$HOME/.local/libexec"

echo "=== VoCoType IBus 语音输入法安装 ==="
echo "项目目录: $PROJECT_DIR"
echo "安装目录: $INSTALL_DIR"
echo ""

echo "请选择 Python 环境："
echo "  [1] 使用项目虚拟环境（推荐）: $PROJECT_DIR/.venv"
echo "  [2] 使用用户级虚拟环境: $INSTALL_DIR/.venv"
echo "  [3] 使用系统 Python（省空间，需自行安装依赖）"
read -r -p "请输入选项 (默认 1): " PY_CHOICE

case "$PY_CHOICE" in
    2)
        PYTHON="$INSTALL_DIR/.venv/bin/python"
        ;;
    3)
        PYTHON="$(command -v python3)"
        USE_SYSTEM_PYTHON=1
        ;;
    ""|1|*)
        PYTHON="$PROJECT_DIR/.venv/bin/python"
        ;;
esac

# 1. 创建目录
echo "[0/5] 创建安装目录与 Python 环境..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$COMPONENT_DIR"
mkdir -p "$LIBEXEC_DIR"

if [ "$USE_SYSTEM_PYTHON" != "1" ] && [ ! -x "$PYTHON" ]; then
    VENV_DIR="$(dirname "$PYTHON")/.."
    echo "创建虚拟环境: $VENV_DIR"
    if command -v uv >/dev/null 2>&1; then
        uv venv --python python3 "$VENV_DIR"
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m venv "$VENV_DIR"
    else
        echo "未找到 uv 或 python3，无法创建虚拟环境。"
        echo "请先安装 uv 或 python3，再重新运行安装脚本。"
        exit 1
    fi
fi

if [ ! -x "$PYTHON" ]; then
    echo "未找到 Python 可执行文件: $PYTHON"
    echo "请确认已创建虚拟环境或系统已安装 python3。"
    exit 1
fi

if [ "$USE_SYSTEM_PYTHON" = "1" ]; then
    if ! "$PYTHON" - << 'PY'
import numpy  # noqa: F401
import sounddevice  # noqa: F401
import soundfile  # noqa: F401
PY
    then
        echo "系统 Python 缺少依赖。请先执行："
        echo "  pip install -r $PROJECT_DIR/requirements.txt"
        exit 1
    fi
else
    echo "安装依赖到虚拟环境..."
    if command -v uv >/dev/null 2>&1; then
        uv pip install --python "$PYTHON" -r "$PROJECT_DIR/requirements.txt"
    else
        "$PYTHON" -m pip install -r "$PROJECT_DIR/requirements.txt"
    fi
fi

# 1. 音频设备配置
echo "[1/5] 音频设备配置..."
echo ""
echo "首先需要配置您的麦克风设备。"
echo "这个过程会："
echo "  - 列出可用的音频输入设备"
echo "  - 测试录音和播放"
echo "  - 验证语音识别效果"
echo ""

if ! "$PYTHON" "$PROJECT_DIR/scripts/setup-audio.py"; then
    echo ""
    echo "音频配置失败或被取消。"
    echo "请稍后运行以下命令重新配置："
    echo "  $PYTHON $PROJECT_DIR/scripts/setup-audio.py"
    exit 1
fi

echo ""

# 2. 复制项目文件
echo "[2/5] 复制项目文件..."
cp -r "$PROJECT_DIR/app" "$INSTALL_DIR/"
cp -r "$PROJECT_DIR/ibus" "$INSTALL_DIR/"
cp "$PROJECT_DIR/vocotype_version.py" "$INSTALL_DIR/"

# 3. 创建启动脚本
echo "[3/5] 创建启动脚本..."
cat > "$LIBEXEC_DIR/ibus-engine-vocotype" << 'LAUNCHER'
#!/bin/bash
# VoCoType IBus Engine Launcher

VOCOTYPE_HOME="$HOME/.local/share/vocotype"
PROJECT_DIR="VOCOTYPE_PROJECT_DIR"

# 使用项目虚拟环境Python
PYTHON="VOCOTYPE_PYTHON"

export PYTHONPATH="$VOCOTYPE_HOME:$PYTHONPATH"
export PYTHONIOENCODING=UTF-8

exec $PYTHON "$VOCOTYPE_HOME/ibus/main.py" "$@"
LAUNCHER

# 替换项目目录路径
sed -i "s|VOCOTYPE_PROJECT_DIR|$PROJECT_DIR|g" "$LIBEXEC_DIR/ibus-engine-vocotype"
sed -i "s|VOCOTYPE_PYTHON|$PYTHON|g" "$LIBEXEC_DIR/ibus-engine-vocotype"
chmod +x "$LIBEXEC_DIR/ibus-engine-vocotype"

# 4. 安装IBus组件文件
echo "[4/5] 安装IBus组件配置..."
EXEC_PATH="$LIBEXEC_DIR/ibus-engine-vocotype"
VOCOTYPE_VERSION="1.0.0"
if VOCOTYPE_VERSION=$(PYTHONPATH="$PROJECT_DIR" "$PYTHON" - << 'PY'
from vocotype_version import __version__
print(__version__)
PY
); then
    :
else
    VOCOTYPE_VERSION="1.0.0"
fi

sed -e "s|VOCOTYPE_EXEC_PATH|$EXEC_PATH|g" \
    -e "s|VOCOTYPE_VERSION|$VOCOTYPE_VERSION|g" \
    "$PROJECT_DIR/data/ibus/vocotype.xml.in" > "$COMPONENT_DIR/vocotype.xml"

echo ""
echo "=== 安装完成 ==="
echo ""
echo "请执行以下步骤完成配置："
echo ""
echo "1. 重启IBus:"
echo "   ibus restart"
echo ""
echo "2. 添加输入法:"
echo "   设置 → 键盘 → 输入源 → +"
echo "   → 滑到最底下点三个点(⋮)"
echo "   → 搜索 'voco' → 中文 → VoCoType Voice Input"
echo ""
echo "3. 使用方法:"
echo "   - 切换到VoCoType输入法"
echo "   - 按住F9说话，松开后自动识别并输入"
echo ""
