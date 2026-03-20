#!/bin/bash
# 修复 Git 配置

echo "修复 Git 配置..."

# 清除所有镜像配置
git config --global --unset-all url."https://gitclone.com/github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://ghproxy.com/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://hub.moeyy.cn/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://ghps.cc/https://github.com/".insteadOf 2>/dev/null

# 清除代理
git config --global --unset http.proxy 2>/dev/null
git config --global --unset https.proxy 2>/dev/null

echo "✓ Git 配置已清除"
echo ""
echo "现在使用 GitHub 地址重新推送:"
echo "  git remote set-url origin https://github.com/17630028312-stack/phone_clean_ag.git"
echo "  git push -u origin main"
echo ""
echo "密码输入 GitHub Personal Access Token"
