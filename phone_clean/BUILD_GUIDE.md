# APK 打包指南

## 环境要求

**注意：Windows 无法直接打包，需要使用 WSL 或 Linux**

### 方案一：Windows WSL (推荐)

1. **安装 WSL2** (Windows 10/11)
```powershell
wsl --install
```

2. **安装 Ubuntu** (Microsoft Store 中搜索安装)

3. **进入 WSL 终端**
```bash
cd /mnt/d/work_room/phone  # 根据你的实际路径调整
```

### 方案二：Linux 虚拟机/服务器

使用 Ubuntu 20.04+ 或 Debian 10+

## 安装依赖

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装必要工具
sudo apt install -y python3 python3-pip python3-venv git zip unzip openjdk-17-jdk

# 3. 安装 buildozer 和依赖
pip3 install --user buildozer cython

# 4. 将 pip 本地 bin 添加到 PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 5. 验证安装
buildozer --version
```

## 项目准备

```bash
# 进入项目目录
cd /path/to/phone

# 确保文件结构正确
ls -la
# 应该看到:
# main.py
# buildozer.spec
# assets/
# generate_icons.py
```

## 打包步骤

### 方式一：使用脚本（推荐）

```bash
chmod +x build_apk.sh
./build_apk.sh
```

### 方式二：手动打包

```bash
# 1. 首次初始化（只需运行一次）
buildozer init

# 2. 构建调试版 APK
buildozer android debug

# 3. 构建并安装到手机（需连接手机）
buildozer android debug deploy run
```

## 输出文件

打包成功后，APK 文件位于：
```
phone/bin/photowipe-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

## 常见问题

### 1. 权限错误
```bash
# 给 buildozer 添加权限
sudo chown -R $USER:$USER ~/.buildozer
sudo chown -R $USER:$USER ./.buildozer
```

### 2. 内存不足
```bash
# 增加交换空间
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 3. 下载失败
```bash
# 手动下载 NDK/SDK 并配置路径
export ANDROIDSDK="/path/to/android-sdk"
export ANDROIDNDK="/path/to/android-ndk"
```

### 4. 构建卡住
如果构建过程卡住，可以尝试：
```bash
# 清理后重新构建
buildozer android clean
buildozer android debug
```

## 发布版本打包

```bash
# 发布版本（需要签名）
buildozer android release

# 签名 APK（需要创建密钥库）
keytool -genkey -v -keystore my-release-key.keystore -alias mykey -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/*.apk mykey
```

## 安装到手机

### 方式一：adb 安装
```bash
# 连接手机并开启 USB 调试
adb devices
adb install -r bin/photowipe-1.0.0-*.apk
```

### 方式二：直接推送
```bash
# 通过 buildozer 自动安装
buildozer android deploy run
```

### 方式三：手动安装
1. 将 APK 文件复制到手机
2. 在手机上打开 APK 文件安装
3. 允许"未知来源"应用安装

## 应用权限说明

安装后需要授予以下权限：
- **存储权限**：读取相册照片
- **媒体权限**（Android 13+）：访问图片媒体

## 文件大小

- 调试版 APK: ~30-50 MB
- 发布版 APK: ~15-25 MB
