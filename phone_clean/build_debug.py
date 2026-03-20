#!/usr/bin/env python3
"""
调试打包脚本 - 带详细日志
"""

import os
import subprocess
import sys

def run(cmd, capture=True):
    """运行命令并返回详细输出"""
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    
    if result.stdout:
        print("STDOUT:", result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
    
    print(f"Return code: {result.returncode}")
    return result

def main():
    print("=" * 60)
    print("   划一下 - 调试打包")
    print("=" * 60)
    
    venv_dir = os.path.expanduser("~/.buildozer-venv")
    venv_buildozer = os.path.join(venv_dir, "bin/buildozer")
    
    # 检查虚拟环境
    print(f"\n[检查] 虚拟环境: {venv_dir}")
    print(f"  存在: {os.path.exists(venv_dir)}")
    
    print(f"\n[检查] buildozer: {venv_buildozer}")
    print(f"  存在: {os.path.exists(venv_buildozer)}")
    
    # 检查 Java
    print("\n[检查] Java 安装:")
    run("java -version", capture=False)
    
    # 检查网络
    print("\n[检查] 网络连接:")
    run("curl -I https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip 2>&1 | head -5", capture=False)
    
    # 运行打包
    print("\n" + "=" * 60)
    print("开始打包...")
    print("=" * 60)
    
    os.chdir("/mnt/d/work_room/phone")
    
    # 清理并重试
    run("rm -rf .buildozer/android/platform/android-sdk .buildozer/android/platform/android-ndk")
    
    # 运行 buildozer
    result = run(f"{venv_buildozer} android debug 2>&1 | tee build.log")
    
    # 检查日志
    print("\n" + "=" * 60)
    print("打包完成，检查日志...")
    print("=" * 60)
    
    log_file = "/mnt/d/work_room/phone/build.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # 显示最后100行和错误行
            print("\n最后 50 行日志:")
            print("".join(lines[-50:]))
            
            print("\n错误关键词:")
            for i, line in enumerate(lines):
                if any(kw in line.lower() for kw in ['error', 'failed', 'exception', 'permission', 'denied']):
                    print(f"Line {i}: {line.strip()}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
