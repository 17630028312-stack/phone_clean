#!/bin/bash
# 后台打包脚本

cd /mnt/d/work_room/phone
source ~/.buildozer-venv/bin/activate

# 安装缺失的依赖
pip install setuptools -q

# 开始打包，输出到日志
echo "开始打包，请等待 30-60 分钟..."
echo "可以新开终端运行: tail -f /mnt/d/work_room/phone/build.log 查看进度"
echo ""

buildozer android debug 2>&1 | tee build.log

echo ""
echo "打包完成！"
ls -lh bin/*.apk 2>/dev/null || echo "APK 未生成，请检查 build.log"
