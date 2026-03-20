# 网页上传方式（最简单）

## 步骤 1：准备文件

在 WSL 中打包项目：

```bash
cd /mnt/d/work_room/phone

# 清理不需要的文件
rm -rf .buildozer bin __pycache__ .git

# 创建 zip（不包含 .git 和构建文件）
zip -r phone_clean_ag.zip . -x "*.git*" -x "*.buildozer*" -x "bin/*"

# 查看大小
ls -lh phone_clean_ag.zip
```

## 步骤 2：网页上传

1. 访问 https://github.com/17630028312-stack/phone_clean_ag
2. 点击 **Add file** → **Upload files**
3. 拖拽 `phone_clean_ag.zip` 上传
4. 点击 **Commit changes**

## 步骤 3：解压（在 GitHub 网页）

由于 zip 文件不能直接运行，需要解压：

### 方式 A：使用 GitHub Actions 自动解压

1. 在你的仓库页面，点击 **Add file** → **Create new file**
2. 文件名：`.github/workflows/extract.yml`
3. 粘贴以下内容：

```yaml
name: Extract and Build

on:
  workflow_dispatch:

jobs:
  extract:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Extract zip
      run: |
        unzip phone_clean_ag.zip -d temp/
        mv temp/* .
        rm -rf temp/ phone_clean_ag.zip
        
    - name: Commit extracted files
      run: |
        git config user.name "GitHub Action"
        git config user.email "action@github.com"
        git add .
        git commit -m "Extract files"
        git push
```

4. 点击 **Commit new file**
5. 去 Actions 页面运行 workflow

### 方式 B：本地解压后上传（推荐）

在 Windows 上操作：

1. 复制 `phone_clean_ag.zip` 到 Windows 桌面
2. 右键解压
3. 进入解压后的文件夹
4. 全选所有文件 → 拖拽到 GitHub 网页上传区域
5. 等待上传完成（文件较多，可能需要几分钟）

## 步骤 4：创建工作流

文件上传完成后，创建工作流：

1. 点击 **Add file** → **Create new file**
2. 文件名：`.github/workflows/build.yml`
3. 粘贴完整的工作流配置（见下方）
4. 点击 **Commit new file**

### 工作流配置

```yaml
name: Build Android APK

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04
    
    steps:
    - uses: actions/checkout@v3
    
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
```

## 步骤 5：触发构建

1. 点击仓库顶部的 **Actions** 标签
2. 选择 **Build Android APK**
3. 点击右侧 **Run workflow** → **Run workflow**
4. 等待 20-30 分钟
5. 在 **Artifacts** 下载 APK

---

## 备用：我直接帮你上传

如果你还是搞不定，可以把 zip 文件发给我，我帮你上传到 GitHub 并配置 Actions。
