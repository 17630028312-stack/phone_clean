#!/bin/bash
# 使用 Windows IP 作为代理

# 获取 Windows IP（从 resolv.conf）
WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
PROXY_HTTP="http://$WINDOWS_IP:33210"

echo "=========================================="
echo "   划一下 - 使用 Windows 代理打包"
echo "=========================================="
echo "Windows IP: $WINDOWS_IP"
echo "代理: $PROXY_HTTP"

# 测试 Windows 代理是否可用
echo ""
echo "测试代理连接..."
if curl -s -o /dev/null -w "%{http_code}" --proxy $PROXY_HTTP --max-time 5 https://github.com | grep -q "200\|301\|302"; then
    echo "✓ 代理连接成功"
else
    echo "✗ 代理连接失败"
    echo ""
    echo "可能的原因："
    echo "1. Windows 代理软件未启动"
    echo "2. 代理软件未允许局域网连接"
    echo "3. 防火墙阻止了连接"
    echo ""
    echo "请在 Windows 代理软件中开启'允许局域网连接'选项"
    exit 1
fi

# 设置代理
export http_proxy=$PROXY_HTTP
export https_proxy=$PROXY_HTTP
git config --global http.proxy $PROXY_HTTP
git config --global https.proxy $PROXY_HTTP

# 清理旧配置
git config --global --unset-all url."https://ghproxy.com/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://hub.moeyy.cn/https://github.com/".insteadOf 2>/dev/null

# 清理缓存
rm -rf .buildozer/android/platform/python-for-android

# 打包
source ~/.buildozer-venv/bin/activate
echo ""
echo "开始打包..."
buildozer android debug
