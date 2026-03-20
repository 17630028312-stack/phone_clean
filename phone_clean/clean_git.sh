#!/bin/bash
# 彻底清理 Git 镜像配置

echo "彻底清理 Git 配置..."

# 查看当前配置
echo "当前 Git 配置:"
git config --global --get-regexp url 2>/dev/null || echo "(无)"

# 清除所有可能的镜像
git config --global --unset-all url."https://ghps.cc/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://gitclone.com/github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://ghproxy.com/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://hub.moeyy.cn/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://gh.api.99988866.xyz/https://github.com/".insteadOf 2>/dev/null
git config --global --unset-all url."https://github.moeyy.xyz/https://github.com/".insteadOf 2>/dev/null

# 清除代理
git config --global --unset http.proxy 2>/dev/null
git config --global --unset https.proxy 2>/dev/null

echo ""
echo "清理后配置:"
git config --global --get-regexp url 2>/dev/null || echo "(无)"

echo ""
echo "✓ 清理完成"
echo ""
echo "现在请执行:"
echo "  git remote set-url origin https://github.com/17630028312-stack/phone_clean_ag.git"
echo "  git push -u origin main"
