#!/bin/bash
# 使用本地代理打包

PROXY_HTTP="http://127.0.0.1:33210"
PROXY_SOCKS="socks5://127.0.0.1:33211"

echo "=========================================="
echo "   划一下 - 使用本地代理打包"
echo "=========================================="
echo "HTTP 代理: $PROXY_HTTP"
echo "SOCKS 代理: $PROXY_SOCKS"

# 1. 清除镜像配置
echo "[1/4] 清除镜像配置..."
git config --global --unset-all url."https://ghproxy.com/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://hub.moeyy.cn/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://ghps.cc/https://github.com/".insteadOf 2>/dev/null

# 2. 设置代理环境变量
echo "[2/4] 设置代理..."
export http_proxy=$PROXY_HTTP
export https_proxy=$PROXY_HTTP
export HTTP_PROXY=$PROXY_HTTP
export HTTPS_PROXY=$PROXY_HTTP
export all_proxy=$PROXY_SOCKS
export ALL_PROXY=$PROXY_SOCKS

# Git 代理
git config --global http.proxy $PROXY_HTTP
git config --global https.proxy $PROXY_HTTP

echo "环境变量已设置:"
echo "  http_proxy=$http_proxy"
echo "  https_proxy=$https_proxy"
echo "  all_proxy=$all_proxy"

# 3. 清理缓存
echo "[3/4] 清理缓存..."
rm -rf .buildozer/android/platform/python-for-android
rm -rf .buildozer/android/platform/build-*

# 4. 确保配置正确
echo "[4/4] 检查 buildozer.spec..."
if ! grep -q "p4a.branch" buildozer.spec; then
    echo "p4a.branch = main" >> buildozer.spec
    echo "已添加 p4a.branch = main"
fi

# 5. 测试连接
echo ""
echo "测试 GitHub 连接..."
curl -s -o /dev/null -w "HTTP %{http_code}\n" --max-time 10 https://github.com

# 6. 开始打包
echo ""
echo "=========================================="
echo "   开始打包"
echo "=========================================="
echo "预计时间: 20-40 分钟"
echo ""

source ~/.buildozer-venv/bin/activate
buildozer android debug 2>&1 | tee build.log

# 结果
echo ""
if ls bin/*.apk 1>/dev/null 2>&1; then
    echo "=========================================="
    echo "   ✓ 打包成功！"
    echo "=========================================="
    ls -lh bin/*.apk
else
    echo "=========================================="
    echo "   ✗ 打包失败"
    echo "=========================================="
    echo "查看日志: tail -50 build.log"
fi
