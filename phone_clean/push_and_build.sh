#!/bin/bash
# 推送代码并触发构建

echo "=========================================="
echo "   推送并构建"
echo "=========================================="

cd /mnt/d/work_room/phone

# 检查 git
git status &>/dev/null
if [ $? -ne 0 ]; then
    echo "请先运行: ./setup_github.sh"
    exit 1
fi

# 推送
echo "[1/3] 推送代码..."
git add .
git commit -m "Update for build" 2>/dev/null || echo "无更改"
git push origin main

echo ""
echo "[2/3] 代码已推送"
echo ""
echo "[3/3] 请在浏览器中打开:"
echo ""
echo "  https://github.com/$(git remote get-url origin | sed 's/.*github.com\///;s/\.git//')/actions"
echo ""
echo "点击 'Run workflow' 开始打包"
echo ""
echo "等待 20-30 分钟后，在 Artifacts 中下载 APK"
