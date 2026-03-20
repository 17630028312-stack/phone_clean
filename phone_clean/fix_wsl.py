#!/usr/bin/env python3
"""
WSL 环境修复和诊断
"""

import os
import subprocess

def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("=" * 60)
print("   WSL 环境诊断与修复")
print("=" * 60)

# 1. 检查 WSL 版本
print("\n[1] 检查 WSL 版本...")
result = run("wsl.exe -l -v")
print(result.stdout)
if result.returncode != 0:
    print("请在 PowerShell 中运行: wsl --version")

# 2. 检查内存配置
print("\n[2] 检查内存配置...")
wsl_config = os.path.expanduser("~/.wslconfig")
if os.path.exists(wsl_config):
    with open(wsl_config) as f:
        print(f"WSL 配置 ({wsl_config}):")
        print(f.read())
else:
    print("未找到 .wslconfig，建议创建以分配更多内存")
    print("\n创建配置? (y/n)")
    choice = input().strip().lower()
    if choice == 'y':
        config = """[wsl2]
memory=6GB
processors=4
swap=2GB
localhostForwarding=true
"""
        with open(wsl_config, 'w') as f:
            f.write(config)
        print("配置已创建，请运行: wsl --shutdown")
        print("然后重新打开 WSL")

# 3. 检查磁盘空间
print("\n[3] 检查磁盘空间...")
run("df -h")

# 4. 检查网络
print("\n[4] 检查网络...")
result = run("curl -s https://www.google.com -o /dev/null -w '%{http_code}'")
print(f"Google 访问状态: {result.stdout}")

# 5. 检查 DNS
print("\n[5] 检查 DNS...")
run("cat /etc/resolv.conf")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)

print("""
常见问题解决:

1. 内存不足 (最常见)
   创建/修改 ~/.wslconfig:
   [wsl2]
   memory=6GB
   processors=4
   
   然后运行: wsl --shutdown

2. 网络问题
   在 /etc/resolv.conf 添加:
   nameserver 8.8.8.8
   nameserver 114.114.114.114

3. 磁盘空间不足
   清理 Docker: docker system prune -a
   清理 APT: sudo apt autoremove && sudo apt clean

4. 手动打包步骤:
   source ~/.buildozer-venv/bin/activate
   cd /mnt/d/work_room/phone
   buildozer android debug
""")
