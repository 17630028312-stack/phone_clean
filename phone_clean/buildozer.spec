# Buildozer 配置 - 使用 main 分支
[app]
title = 划一下
package.name = photowipe
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,txt,db,spec
version = 1.0.0

requirements = python3,kivy,kivymd,Pillow,sqlite3,android,setuptools

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
orientation = portrait
fullscreen = 0
android.archs = armeabi-v7a,arm64-v8a
android.allow_backup = True

# 指定 p4a 分支为 main（GitHub 默认分支）
p4a.branch = main

[buildozer]
log_level = 2
warn_on_root = 1
p4a.branch = main
