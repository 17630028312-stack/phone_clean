#!/bin/bash
# 手动打包指南脚本 - 在 WSL/Ubuntu 中运行

echo "=========================================="
echo "   划一下 - 手动打包脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在 WSL 中
if grep -q Microsoft /proc/version 2>/dev/null; then
    echo -e "${GREEN}检测到 WSL 环境${NC}"
fi

# 步骤1: 安装系统依赖
echo ""
echo "[步骤1] 安装系统依赖..."
echo "需要 sudo 权限"
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git zip unzip openjdk-17-jdk

# 步骤2: 创建虚拟环境
echo ""
echo "[步骤2] 创建 Python 虚拟环境..."
VENV_DIR="$HOME/.buildozer-venv"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

# 步骤3: 安装 Python 包
echo ""
echo "[步骤3] 安装 buildozer..."
pip install --upgrade pip
pip install buildozer cython

# 步骤4: 验证安装
echo ""
echo "[步骤4] 验证安装..."
if command -v buildozer &> /dev/null; then
    echo -e "${GREEN}buildozer 安装成功: $(buildozer --version)${NC}"
else
    echo -e "${RED}buildozer 未找到${NC}"
    echo "尝试使用虚拟环境中的 buildozer..."
    alias buildozer="$VENV_DIR/bin/buildozer"
fi

# 步骤5: 进入项目目录
echo ""
echo "[步骤5] 准备项目..."
if [ -d "/mnt/d/work_room/phone" ]; then
    cd /mnt/d/work_room/phone
elif [ -d "/mnt/c/phone" ]; then
    cd /mnt/c/phone
else
    echo "请手动进入项目目录:"
    echo "  cd /path/to/phone"
    exit 1
fi

echo "当前目录: $(pwd)"

# 步骤6: 生成图标
echo ""
echo "[步骤6] 生成图标..."
python generate_icons.py

# 步骤7: 打包
echo ""
echo "[步骤7] 开始打包..."
echo -e "${YELLOW}首次打包需要下载 Android SDK/NDK (约2GB)${NC}"
echo -e "${YELLOW}预计时间: 30-60 分钟${NC}"
echo ""
read -p "按回车键开始打包..."

# 使用虚拟环境中的 buildozer
"$VENV_DIR/bin/buildozer" android debug

# 结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}   打包成功！${NC}"
    echo -e "${GREEN}==========================================${NC}"
    ls -lh bin/*.apk 2>/dev/null || ls -lh *.apk 2>/dev/null
    echo ""
    echo "APK 文件位置:"
    find . -name "*.apk" -type f 2>/dev/null | head -5
else
    echo ""
    echo -e "${RED}==========================================${NC}"
    echo -e "${RED}   打包失败${NC}"
    echo -e "${RED}==========================================${NC}"
    echo ""
    echo "常见解决方案:"
    echo "1. 清理后重试: buildozer android clean"
    echo "2. 检查网络连接"
    echo "3. 增加 WSL 内存到 4GB+"
    echo ""
    echo "查看详细日志:"
    echo "  buildozer android debug 2>&1 | tee build.log"
fi
