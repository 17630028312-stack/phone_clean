#!/bin/bash
# 修复 WSL 网络连接问题

echo "=========================================="
echo "   网络修复工具"
echo "=========================================="

# 方法1: 配置 Git 使用代理（如果你有 VPN）
echo ""
echo "[方法1] 配置 Git 代理"
echo "如果你有 Windows 代理软件（如 Clash/v2ray），输入代理端口:"
echo "  例如: 7890 或 10808"
echo "  直接回车跳过"
read -p "代理端口: " proxy_port

if [ -n "$proxy_port" ]; then
    # 获取 Windows 主机 IP
    windows_ip=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
    
    # 配置 Git 代理
    git config --global http.proxy http://$windows_ip:$proxy_port
    git config --global https.proxy http://$windows_ip:$proxy_port
    
    # 配置系统代理环境变量
    echo "export http_proxy=http://$windows_ip:$proxy_port" >> ~/.bashrc
    echo "export https_proxy=http://$windows_ip:$proxy_port" >> ~/.bashrc
    
    echo "已配置代理: $windows_ip:$proxy_port"
    echo "测试 GitHub 连接..."
    git ls-remote https://github.com/python-for-android/python-for-android HEAD 2>&1 | head -3
else
    echo "跳过代理配置"
fi

# 方法2: 增加 Git 缓冲区
echo ""
echo "[方法2] 优化 Git 配置"
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
git config --global core.compression 0
echo "Git 配置已优化"

# 方法3: 配置 hosts（如果知道 GitHub IP）
echo ""
echo "[方法3] 配置 hosts 加速"
echo "尝试通过 hosts 加速 GitHub..."

# 使用 GHProxy 镜像
echo ""
echo "[方法4] 使用 GHProxy 镜像"
echo "替换 git 地址为镜像源..."
git config --global url."https://ghproxy.com/https://github.com/".insteadOf "https://github.com/"
echo "已配置 GHProxy 镜像"

# 测试连接
echo ""
echo "=========================================="
echo "   测试网络连接"
echo "=========================================="
echo ""

echo "测试 1: 访问 Google"
curl -s -o /dev/null -w "%{http_code}" https://www.google.com
echo ""

echo ""
echo "测试 2: 访问 GitHub"
curl -s -o /dev/null -w "%{http_code}" https://github.com
echo ""

echo ""
echo "测试 3: Git clone 测试"
rm -rf /tmp/github-test 2>/dev/null
timeout 30 git clone --depth 1 https://github.com/python/cpython.git /tmp/github-test 2>&1 | head -5
if [ -d "/tmp/github-test" ]; then
    echo "✓ GitHub 连接正常"
    rm -rf /tmp/github-test
else
    echo "✗ GitHub 连接失败"
fi

echo ""
echo "=========================================="
echo "   网络修复完成"
echo "=========================================="
echo ""
echo "建议:"
echo "1. 如果测试失败，请开启 Windows 代理软件 (Clash/v2ray)"
echo "2. 确保 WSL 可以访问 Windows 代理端口"
echo "3. 重新运行打包命令"
echo ""
