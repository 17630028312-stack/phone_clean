@echo off
chcp 65001 >nul
echo ==========================================
echo    划一下 - 照片整理 App 打包助手
echo ==========================================
echo.

:: 检查是否在 WSL 环境中
wsl -l -v >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 WSL
    echo.
    echo 请先安装 WSL2:
    echo   wsl --install
    echo.
    echo 然后重启电脑，安装 Ubuntu
    pause
    exit /b 1
)

echo [1/4] 正在复制项目到 WSL...
wsl mkdir -p ~/photowipe-app
wsl rm -rf ~/photowipe-app/*

:: 复制文件到 WSL
xcopy /E /I /Y . \wsl$\Ubuntu\home\%USERNAME%\photowipe-app\

echo [2/4] 在 WSL 中安装依赖...
echo 安装 buildozer 和 cython...
wsl bash -c "pip3 install buildozer cython --break-system-packages -q 2>/dev/null || pip3 install --user buildozer cython -q 2>/dev/null || pip3 install buildozer cython -q"

echo 确保 buildozer 在 PATH 中...
wsl bash -c "export PATH=\"$HOME/.local/bin:$PATH\" && echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.bashrc"

echo [3/4] 开始打包...
echo 注意：首次打包需要下载 Android SDK/NDK，可能需要 30-60 分钟
echo 请保持网络连接...
echo.

wsl bash -c "export PATH=\"$HOME/.local/bin:$PATH\" && cd ~/photowipe-app && buildozer android debug 2>&1 | tee build.log"

echo.
echo [4/4] 复制 APK 回 Windows...
if not exist "bin" mkdir bin
wsl bash -c "cp ~/photowipe-app/bin/*.apk /mnt/d/work_room/phone/bin/ 2>/dev/null || cp ~/photowipe-app/bin/*.apk /mnt/c/photowipe-output/ 2>/dev/null || echo 'APK留在WSL: ~/photowipe-app/bin/'"

:: 检查APK是否在Windows目录
set APK_FOUND=0
for %%F in (bin\*.apk) do set APK_FOUND=1

if %APK_FOUND%==1 (
    echo.
    echo ==========================================
    echo    打包成功！
    echo ==========================================
    echo.
    dir /b bin\*.apk
    echo.
    echo APK 文件已保存到 phone/bin/ 目录
) else (
    echo.
    echo [信息] 检查 WSL 中的输出...
    wsl bash -c "ls -lh ~/photowipe-app/bin/*.apk 2>/dev/null || echo '未找到APK'"
    echo.
    echo [提示] 打包可能遇到问题，请查看日志：
    echo   wsl cat ~/photowipe-app/build.log
    echo.
    echo [手动打包命令]
    echo   wsl
    echo   cd ~/photowipe-app
    echo   export PATH="$HOME/.local/bin:$PATH"
    echo   buildozer android debug
)

pause
