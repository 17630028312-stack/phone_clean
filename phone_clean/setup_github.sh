#!/bin/bash
# GitHub 自动配置脚本

echo "=========================================="
echo "   GitHub Actions 配置助手"
echo "=========================================="

# 检查 git
if ! command -v git &> /dev/null; then
    echo "请先安装 git: sudo apt install git"
    exit 1
fi

# 输入用户名
echo ""
read -p "请输入你的 GitHub 用户名: " USERNAME
read -p "请输入仓库名称 (默认: photowipe): " REPO_NAME
REPO_NAME=${REPO_NAME:-photowipe}

echo ""
echo "配置信息:"
echo "  用户名: $USERNAME"
echo "  仓库: $REPO_NAME"
echo ""
read -p "确认? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ]; then
    echo "已取消"
    exit 1
fi

cd /mnt/d/work_room/phone

# 创建 .github/workflows 目录
mkdir -p .github/workflows

# 创建工作流文件
cat > .github/workflows/build.yml << 'EOF'
name: Build Android APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        sudo apt update
        sudo apt install -y libffi-dev libssl-dev openjdk-17-jdk
        pip install buildozer cython setuptools
    
    - name: Generate icons
      run: |
        cd phone
        python generate_icons.py
    
    - name: Build APK
      run: |
        cd phone
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: photowipe-apk
        path: phone/bin/*.apk
EOF

echo "✓ 工作流文件已创建"

# 初始化 git
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/$USERNAME/$REPO_NAME.git

echo ""
echo "=========================================="
echo "   配置完成！"
echo "=========================================="
echo ""
echo "接下来:"
echo "1. 确保你已在 GitHub 创建了仓库: $REPO_NAME"
echo "2. 运行: git push -u origin main"
echo "3. 访问: https://github.com/$USERNAME/$REPO_NAME/actions"
echo "4. 点击 'Run workflow' 开始打包"
echo ""
echo "或执行: ./push_and_build.sh"
