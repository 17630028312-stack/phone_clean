# 打包备选方案大全

## 方案一：使用其他国内镜像

### 1.1 GitClone 镜像
```bash
# 清除之前的镜像配置
git config --global --unset-all url."https://ghproxy.com/https://github.com/".insteadOf

# 使用 gitclone.com
git config --global url."https://gitclone.com/github.com/".insteadOf "https://github.com/"

# 或者使用 moeyy.cn
git config --global url."https://hub.moeyy.cn/https://github.com/".insteadOf "https://github.com/"

# 重新打包
cd /mnt/d/work_room/phone
rm -rf .buildozer/android/platform/python-for-android
buildozer android debug
```

### 1.2 直接在 buildozer.spec 中指定镜像
```spec
# buildozer.spec 中添加
p4a.url = https://gitee.com/mirrors/python-for-android
```

---

## 方案二：Windows 代理共享给 WSL（如果你有 VPN）

```bash
# 1. 获取 Windows IP
export WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
echo "Windows IP: $WINDOWS_IP"

# 2. 设置代理（假设你的代理端口是 7890，Clash 默认）
export http_proxy=http://$WINDOWS_IP:7890
export https_proxy=http://$WINDOWS_IP:7890
export HTTP_PROXY=$http_proxy
export HTTPS_PROXY=$https_proxy

# 3. 配置 Git 使用代理
git config --global http.proxy $http_proxy
git config --global https.proxy $https_proxy

# 4. 清除镜像配置
git config --global --unset-all url."https://ghproxy.com/https://github.com/".insteadOf 2>/dev/null

# 5. 测试连接
curl -I https://github.com

# 6. 打包
cd /mnt/d/work_room/phone
buildozer android debug
```

---

## 方案三：手动下载依赖（离线打包）

```bash
# 在一台能访问 GitHub 的机器上：
# 1. 下载 python-for-android
cd /mnt/d/work_room/phone/.buildozer/android/platform
git clone -b master --single-branch https://github.com/kivy/python-for-android.git

# 2. 下载完成后将整个 .buildozer 目录压缩
# 3. 复制到目标机器解压

# 4. 继续打包
buildozer android debug
```

---

## 方案四：购买临时云服务器（最稳定）

### 阿里云 ECS（按时计费）
```
1. 登录 https://ecs.console.aliyun.com
2. 创建按量付费实例
3. 选择：Ubuntu 22.04, 2核4G, 按量付费
4. 费用约 0.3-0.5 元/小时，打包约需 1-2 小时，总费用 < 1 元
5. 使用宝塔面板或命令行上传项目
6. 打包完成后下载 APK，释放实例
```

### 腾讯云轻量（新用户免费）
```
新用户有免费试用，可以使用
```

---

## 方案五：GitHub Actions（完全免费）

### 步骤：
1. 将代码推送到 GitHub
2. 创建 `.github/workflows/build.yml`

```yaml
name: Build APK
on: [workflow_dispatch]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install deps
      run: |
        sudo apt update
        sudo apt install -y openjdk-17-jdk
        pip install buildozer cython setuptools
    - name: Build
      run: |
        cd phone
        python generate_icons.py
        buildozer android debug
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: photowipe-apk
        path: phone/bin/*.apk
```

3. 在 GitHub 页面点击 Actions → Run workflow
4. 等待 20-30 分钟，下载 APK

**优点**：完全免费，网络稳定，无需本地配置

---

## 方案六：找朋友帮忙

如果你的朋友/同事：
- 有稳定的 GitHub 访问
- 有 Linux/Mac 环境

可以：
1. 将整个 phone 文件夹打包发给他
2. 他运行打包脚本
3. 将生成的 APK 发回给你

---

## 方案七：使用已打包的模板

如果实在无法打包，可以使用预编译的 Kivy 模板：

1. 下载预编译 APK 模板
2. 使用 apktool 解包
3. 替换 Python 代码和资源
4. 重新签名打包

这个方法较复杂，不建议新手使用。

---

## 推荐优先级

| 方案 | 难度 | 成本 | 推荐度 |
|------|------|------|--------|
| GitHub Actions | 低 | 免费 | ⭐⭐⭐⭐⭐ |
| 云服务器 | 低 | ~1元 | ⭐⭐⭐⭐ |
| 朋友帮忙 | 低 | 免费 | ⭐⭐⭐⭐ |
| Windows 代理 | 中 | 免费 | ⭐⭐⭐ |
| 手动下载 | 高 | 免费 | ⭐⭐ |

---

## 最快的解决方案

**GitHub Actions 是最推荐的方案**，只需：
1. 注册 GitHub 账号
2. 上传代码
3. 点击运行
4. 下载 APK

不需要任何本地配置，完全免费！
