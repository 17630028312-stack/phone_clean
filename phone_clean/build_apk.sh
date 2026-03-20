#!/bin/bash
# 安卓 APK 打包脚本
# 需要在 Linux/macOS/WSL 环境下运行

echo "=========================================="
echo "   划一下 - 照片整理 App 打包脚本"
echo "=========================================="

# 检查 buildozer 是否安装
if ! command -v buildozer &> /dev/null; then
    echo "错误: buildozer 未安装"
    echo "请先安装: pip install buildozer cython"
    exit 1
fi

# 清理旧构建
echo "[1/5] 清理旧构建..."
rm -rf bin/ .buildozer/

# 确保 assets 目录存在
echo "[2/5] 检查资源文件..."
if [ ! -d "assets" ]; then
    echo "错误: assets 目录不存在"
    exit 1
fi

# 生成图标（如果需要）
echo "[3/5] 生成图标..."
python3 generate_icons.py

# 构建 APK
echo "[4/5] 开始构建 APK..."
echo "这可能需要 10-30 分钟，请耐心等待..."
buildozer android debug

# 检查结果
if [ $? -eq 0 ]; then
    echo "[5/5] 构建成功！"
    echo ""
    echo "APK 文件位置:"
    ls -lh bin/*.apk
    echo ""
    echo "安装到手机:"
    echo "  buildozer android deploy run"
else
    echo "[5/5] 构建失败，请检查错误信息"
    exit 1
fi
