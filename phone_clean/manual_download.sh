#!/bin/bash
# 手动下载依赖后离线打包
# 需要在一台能访问 GitHub 的机器上先下载，然后复制过来

echo "=========================================="
echo "   手动下载依赖脚本"
echo "=========================================="

P4A_DIR=".buildozer/android/platform/python-for-android"

if [ -d "$P4A_DIR" ]; then
    echo "✓ python-for-android 已存在"
else
    echo "✗ python-for-android 不存在"
    echo ""
    echo "请在一台能访问 GitHub 的机器上执行："
    echo ""
    echo "  cd /mnt/d/work_room/phone/.buildozer/android/platform"
    echo "  git clone -b main --single-branch https://github.com/kivy/python-for-android.git"
    echo "  cd python-for-android"
    echo "  git submodule update --init --recursive"
    echo ""
    echo "然后将整个 .buildozer 目录压缩复制到当前机器"
    echo ""
    echo "或者使用浏览器下载："
    echo "  https://github.com/kivy/python-for-android/archive/refs/heads/main.zip"
    echo "  解压到: .buildozer/android/platform/python-for-android"
fi

# 检查
if [ -d "$P4A_DIR/.git" ]; then
    echo ""
    echo "检查更新..."
    cd $P4A_DIR
    git log --oneline -3
    cd -
    
    echo ""
    echo "开始打包..."
    source ~/.buildozer-venv/bin/activate
    buildozer android debug
else
    echo ""
    echo "请先下载 python-for-android"
fi
