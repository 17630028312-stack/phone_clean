#!/bin/bash
# 修复安装问题并打包

echo "=========================================="
echo "   划一下 - 修复并重新打包"
echo "=========================================="

# 检测 Python 版本
PYTHON_CMD=$(command -v python3 || command -v python)
if [ -z "$PYTHON_CMD" ]; then
    echo "错误: 未找到 Python"
    exit 1
fi

echo "Python: $PYTHON_CMD"

# 安装依赖（尝试多种方式）
echo ""
echo "[1/4] 安装 buildozer..."
pip3 install --upgrade pip

# 方式1: 使用 --break-system-packages (Ubuntu 23.04+)
pip3 install buildozer cython --break-system-packages 2>/dev/null

# 方式2: 使用 --user
if ! command -v buildozer &> /dev/null; then
    pip3 install --user buildozer cython
fi

# 方式3: 使用虚拟环境
if ! command -v buildozer &> /dev/null; then
    echo "创建虚拟环境..."
    $PYTHON_CMD -m venv ~/buildozer-venv
    source ~/buildozer-venv/bin/activate
    pip install buildozer cython
fi

# 确保 PATH 包含本地 bin
echo ""
echo "[2/4] 配置环境变量..."
export PATH="$HOME/.local/bin:$HOME/buildozer-venv/bin:$PATH"
echo "PATH: $PATH"

# 检查 buildozer
if ! command -v buildozer &> /dev/null; then
    echo "错误: buildozer 安装失败"
    echo "尝试查找 buildozer..."
    find ~ -name buildozer 2>/dev/null | head -5
    exit 1
fi

echo "buildozer 版本: $(buildozer --version)"

# 进入项目目录
echo ""
echo "[3/4] 准备项目..."
cd "$(dirname "$0")" || exit 1

# 生成图标
python3 generate_icons.py

# 清理旧构建
echo "清理旧构建..."
rm -rf bin/ .buildozer/

# 开始打包
echo ""
echo "[4/4] 开始打包..."
echo "这可能需要 30-60 分钟，请耐心等待"
echo ""

buildozer android debug 2>&1 | tee build.log

# 检查结果
if [ $? -eq 0 ] && [ -f bin/*.apk ]; then
    echo ""
    echo "=========================================="
    echo "   打包成功！"
    echo "=========================================="
    ls -lh bin/*.apk
else
    echo ""
    echo "=========================================="
    echo "   打包失败"
    echo "=========================================="
    echo "查看日志: tail -50 build.log"
fi
