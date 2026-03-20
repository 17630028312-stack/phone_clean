"""
Google Colab 打包脚本 - 修正版
复制以下代码到 https://colab.research.google.com 运行
"""

# ============================================
# 步骤 1: 挂载 Google Drive
# ============================================
from google.colab import drive
drive.mount('/content/drive')

# ============================================
# 步骤 2: 准备项目文件
# ============================================
# 将你的 phone 文件夹压缩为 phone.zip
# 上传到 Google Drive 的任意位置（如 /MyDrive/phone.zip）

import os
import shutil

# 清理旧目录
!rm -rf /content/phone /content/build
!mkdir -p /content/phone

# 解压项目（根据你的实际路径修改）
# 如果 zip 在 MyDrive 根目录：
!unzip -q "/content/drive/MyDrive/phone.zip" -d /content/

# 检查解压后的结构
print("检查文件结构...")
!ls -la /content/

# 如果解压后是 /content/phone/ 直接可用
# 如果解压后是 /content/phone/phone/ 需要调整
if os.path.exists('/content/phone/main.py'):
    print("✓ 目录结构正确")
    %cd /content/phone
else:
    # 可能是嵌套目录，查找 main.py
    print("查找 main.py...")
    !find /content -name "main.py" -type f 2>/dev/null
    
    # 假设在 /content/phone/phone/
    if os.path.exists('/content/phone/phone/main.py'):
        !mv /content/phone/phone/* /content/phone/
        !rm -rf /content/phone/phone
        %cd /content/phone
        print("✓ 已调整目录结构")

# 验证
!ls -la
!ls -la assets/

# ============================================
# 步骤 3: 安装依赖
# ============================================
print("\n安装系统依赖...")
!apt update -qq
!apt install -y -qq python3-pip openjdk-17-jdk git zip unzip libffi-dev libssl-dev

print("\n安装 Python 包...")
!pip install -q buildozer cython setuptools

# ============================================
# 步骤 4: 修复权限警告
# ============================================
# Colab 默认以 root 运行，创建普通用户来运行 buildozer
!useradd -m builduser 2>/dev/null || true
!chown -R builduser:builduser /content/phone

# ============================================
# 步骤 5: 生成图标
# ============================================
!python3 generate_icons.py

# ============================================
# 步骤 6: 开始打包（使用普通用户）
# ============================================
print("\n开始打包...")
print("预计时间: 20-40 分钟")
print("请耐心等待...\n")

# 以 builduser 运行打包
!su - builduser -c "cd /content/phone && /usr/local/bin/buildozer android debug" 2>&1

# 如果上述失败，尝试直接运行（忽略 root 警告）
# !buildozer android debug

# ============================================
# 步骤 7: 保存结果
# ============================================
print("\n打包完成，保存 APK...")

# 确保输出目录存在
!mkdir -p /content/drive/MyDrive/apk_output

# 复制 APK
!cp /content/phone/bin/*.apk /content/drive/MyDrive/apk_output/ 2>/dev/null || echo "APK 未生成"

# 检查结果
print("\n输出文件:")
!ls -lh /content/phone/bin/*.apk 2>/dev/null || echo "检查 bin/ 目录失败"

print("\nDrive 中的文件:")
!ls -lh /content/drive/MyDrive/apk_output/*.apk 2>/dev/null || echo "未找到 APK"

print("\n✓ 完成！APK 已保存到 Google Drive /apk_output/ 文件夹")
