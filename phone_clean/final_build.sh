#!/bin/bash
# 最终修复打包脚本

echo "=========================================="
echo "   划一下 - 最终修复打包"
echo "=========================================="

# 1. 清除之前的镜像配置
echo "[1/5] 清除旧的 Git 配置..."
git config --global --unset-all url."https://ghproxy.com/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://hub.moeyy.cn/https://github.com/".insteadOf 2>/dev/null
git config --global --unset http.proxy 2>/dev/null
git config --global --unset https.proxy 2>/dev/null

# 2. 设置 GitHub 代理（如果你有 Clash/v2ray）
echo "[2/5] 配置代理..."
echo "如果你有 Windows 代理软件，请输入代理端口（如 7890）："
echo "如果没有代理，直接回车使用镜像源"
read -p "代理端口 (直接回车跳过): " proxy_port

if [ -n "$proxy_port" ]; then
    # 使用 Windows 代理
    WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
    export http_proxy=http://$WINDOWS_IP:$proxy_port
    export https_proxy=http://$WINDOWS_IP:$proxy_port
    git config --global http.proxy $http_proxy
    git config --global https.proxy $https_proxy
    echo "已配置代理: $WINDOWS_IP:$proxy_port"
else
    # 使用 ghps.cc 镜像
    echo "使用 ghps.cc 镜像..."
    git config --global url."https://ghps.cc/https://github.com/".insteadOf "https://github.com/"
fi

# 3. 清理缓存
echo "[3/5] 清理缓存..."
rm -rf .buildozer/android/platform/python-for-android
rm -rf .buildozer/android/platform/build-*

# 4. 确保使用 main 分支
echo "[4/5] 检查 buildozer.spec..."
if ! grep -q "p4a.branch" buildozer.spec; then
    echo "p4a.branch = main" >> buildozer.spec
    echo "已添加 p4a.branch = main"
fi

# 5. 开始打包
echo "[5/5] 开始打包..."
echo "预计时间: 20-40 分钟"
echo ""

source ~/.buildozer-venv/bin/activate
buildozer android debug 2>&1 | tee final_build.log

# 检查结果
if [ -f bin/*.apk ]; then
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
    echo "查看日志: tail -50 final_build.log"
fi
