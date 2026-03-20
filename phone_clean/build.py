#!/usr/bin/env python3
"""
划一下 - APK 打包脚本
在 WSL/Ubuntu 中运行: python3 build.py
"""

import os
import subprocess
import sys

def run(cmd, check=True):
    """运行命令"""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    if check and result.returncode != 0:
        print(f"命令失败: {cmd}")
        return False
    return True

def main():
    print("=" * 50)
    print("   划一下 - 照片整理 App 打包")
    print("=" * 50)
    
    # 检测是否在 WSL
    is_wsl = False
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                is_wsl = True
                print("\n✓ 检测到 WSL 环境")
    except:
        pass
    
    # 步骤1: 安装系统依赖
    print("\n[步骤1] 安装系统依赖...")
    print("需要 sudo 权限，请输入密码...")
    run("sudo apt update", check=False)
    run("sudo apt install -y python3 python3-pip python3-venv git zip unzip openjdk-17-jdk", check=False)
    
    # 步骤2: 创建虚拟环境
    print("\n[步骤2] 创建 Python 虚拟环境...")
    venv_dir = os.path.expanduser("~/.buildozer-venv")
    if not os.path.exists(venv_dir):
        run(f"python3 -m venv {venv_dir}")
    
    venv_python = os.path.join(venv_dir, "bin/python")
    venv_pip = os.path.join(venv_dir, "bin/pip")
    venv_buildozer = os.path.join(venv_dir, "bin/buildozer")
    
    # 步骤3: 安装 Python 包
    print("\n[步骤3] 安装 buildozer...")
    run(f"{venv_pip} install --upgrade pip")
    run(f"{venv_pip} install buildozer cython")
    
    # 步骤4: 验证安装
    print("\n[步骤4] 验证安装...")
    if os.path.exists(venv_buildozer):
        print(f"✓ buildozer 已安装")
    else:
        print("✗ buildozer 安装失败")
        return 1
    
    # 步骤5: 准备项目
    print("\n[步骤5] 准备项目...")
    
    # 生成图标
    print("生成图标...")
    run("python3 generate_icons.py", check=False)
    
    # 清理旧构建
    print("清理旧构建...")
    run("rm -rf bin/ .buildozer/", check=False)
    
    # 步骤6: 打包
    print("\n[步骤6] 开始打包...")
    print("⚠ 首次打包需要下载 Android SDK/NDK (约2GB)")
    print("⚠ 预计时间: 30-60 分钟")
    print("⚠ 请保持网络连接...")
    print("")
    input("按回车键开始打包...")
    
    result = run(f"{venv_buildozer} android debug", check=False)
    
    # 结果
    if result and os.path.exists("bin"):
        apks = [f for f in os.listdir("bin") if f.endswith(".apk")]
        if apks:
            print("\n" + "=" * 50)
            print("   打包成功！")
            print("=" * 50)
            for apk in apks:
                size = os.path.getsize(f"bin/{apk}") / (1024*1024)
                print(f"  {apk} ({size:.1f} MB)")
            
            # 复制到 Windows 桌面（如果在 WSL）
            if is_wsl:
                desktop = "/mnt/c/Users/$(whoami)/Desktop"
                run(f"cp bin/*.apk {desktop}/ 2>/dev/null || echo 'APK 在 bin/ 目录'", check=False)
            
            print(f"\nAPK 位置: {os.path.abspath('bin/')}")
            return 0
    
    print("\n" + "=" * 50)
    print("   打包失败")
    print("=" * 50)
    print("\n排查建议:")
    print("1. 检查网络连接")
    print("2. 增加 WSL 内存: 在 .wslconfig 中设置 memory=4GB")
    print("3. 手动运行: ~/.buildozer-venv/bin/buildozer android debug")
    return 1

if __name__ == "__main__":
    sys.exit(main())
