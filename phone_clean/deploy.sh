#!/bin/bash
# 一键部署到 GitHub

set -e  # 出错时停止

echo "=========================================="
echo "   划一下 - GitHub 一键部署"
echo "=========================================="

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查 git
if ! command -v git &> /dev/null; then
    echo -e "${RED}错误: 未安装 git${NC}"
    echo "运行: sudo apt install git"
    exit 1
fi

# 进入目录
cd "$(dirname "$0")"

echo ""
echo -e "${YELLOW}步骤 1/5: 检查 GitHub 配置${NC}"

# 检查是否已配置 git
if ! git config --global user.email &>/dev/null; then
    echo "首次使用 Git，请配置用户名和邮箱:"
    read -p "GitHub 用户名: " GIT_USER
    read -p "GitHub 邮箱: " GIT_EMAIL
    git config --global user.name "$GIT_USER"
    git config --global user.email "$GIT_EMAIL"
fi

echo ""
echo -e "${YELLOW}步骤 2/5: 创建 GitHub 工作流${NC}"

# 创建工作流目录和文件
mkdir -p .github/workflows

cat > .github/workflows/build.yml << 'EOF'
name: Build Android APK

on:
  push:
    branches: [ main ]
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
        python3 generate_icons.py
    
    - name: Build APK
      run: |
        cd phone
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: photowipe-apk
        path: phone/bin/*.apk
        
    - name: Upload to Release
      if: github.event_name == 'push'
      uses: softprops/action-gh-release@v1
      with:
        tag_name: v1.0.${{ github.run_number }}
        name: 划一下 v1.0.${{ github.run_number }}
        body: 自动构建的 APK 文件
        files: phone/bin/*.apk
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      continue-on-error: true
EOF

echo -e "${GREEN}✓ 工作流文件已创建${NC}"

echo ""
echo -e "${YELLOW}步骤 3/5: 初始化 Git 仓库${NC}"

# 初始化 git
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✓ Git 仓库已初始化${NC}"
else
    echo "Git 仓库已存在"
fi

# 创建 .gitignore
cat > .gitignore << 'EOF'
# Build
bin/
.buildozer/
*.apk
*.aab

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database
*.db
EOF

echo -e "${GREEN}✓ .gitignore 已创建${NC}"

echo ""
echo -e "${YELLOW}步骤 4/5: 提交代码${NC}"

git add .
git commit -m "Initial commit: 划一下照片整理 App" || echo "无新更改"

echo -e "${GREEN}✓ 代码已提交${NC}"

echo ""
echo -e "${YELLOW}步骤 5/5: 配置远程仓库${NC}"

# 检查是否已有远程仓库
if git remote get-url origin &>/dev/null; then
    echo "远程仓库已配置:"
    git remote -v
else
    echo ""
    echo "请输入 GitHub 信息:"
    read -p "GitHub 用户名: " USERNAME
    read -p "仓库名称 (默认: photowipe): " REPO
    REPO=${REPO:-photowipe}
    
    # 添加远程仓库
    git remote add origin "https://github.com/$USERNAME/$REPO.git"
    git branch -M main
    
    echo ""
    echo -e "${GREEN}✓ 远程仓库已配置${NC}"
    echo ""
    echo -e "${YELLOW}重要提示:${NC}"
    echo "1. 请确保你已在 GitHub 创建了仓库: $REPO"
    echo "   访问: https://github.com/new"
    echo ""
    echo "2. 然后运行以下命令推送代码:"
    echo -e "   ${GREEN}git push -u origin main${NC}"
    echo ""
    echo "3. 推送后，访问 Actions 页面触发构建:"
    echo -e "   ${GREEN}https://github.com/$USERNAME/$REPO/actions${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}   部署准备完成！${NC}"
echo "=========================================="
echo ""
echo "下一步操作:"
echo ""
if git remote get-url origin &>/dev/null; then
    echo "1. 推送代码到 GitHub:"
    echo "   git push -u origin main"
    echo ""
    echo "2. 触发自动构建:"
    echo "   访问 GitHub Actions 页面，点击 'Run workflow'"
    echo ""
    echo "3. 等待 20-30 分钟后下载 APK"
else
    echo "1. 在 GitHub 创建仓库"
    echo "2. 运行: git push -u origin main"
    echo "3. 访问 Actions 页面触发构建"
fi
echo ""
