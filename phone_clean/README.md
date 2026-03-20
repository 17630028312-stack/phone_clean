# 划一下 - 手机相册整理App

一个基于Python + KivyMD开发的跨平台移动应用，帮助用户快速整理手机相册。

## 功能特性

### 1. 相册权限获取
- 自动请求相册读取权限
- 支持扫描DCIM、Pictures等标准相册目录
- 使用MediaStore API获取所有图片

### 2. 底部导航栏
三个主模块：
- **划一下**：核心功能，滑动整理照片
- **历史记录**：查看整理历史
- **我的**：用户登录/注册

### 3. 划一下功能
- 每次随机选取10张待整理照片
- 手势操作：
  - 👈 **左滑**：删除照片
  - 👉 **右滑**：保留照片
  - 👆 **上滑**：暂不处理
- 已操作的照片不会再次出现
- 完成一组后显示正向鼓励

### 4. 历史记录
- 记录每次整理的详细信息
- 显示操作时间、照片数量、操作统计
- 按时间降序排列

### 5. 用户系统
- 基础登录/注册功能
- SQLite本地数据库存储
- 密码简单加密存储

## 项目结构

```
phone/
├── main.py              # 主程序入口
├── buildozer.spec       # Android打包配置
├── requirements.txt     # Python依赖
└── README.md           # 项目说明
```

## 运行方式

### 方式一：桌面端测试（Windows/macOS/Linux）

1. 安装依赖：
```bash
cd phone
pip install -r requirements.txt
```

2. 运行应用：
```bash
python main.py
```

### 方式二：Android真机运行

#### 前提条件
- 安装buildozer: `pip install buildozer`
- 安装Android SDK/NDK
- Linux/macOS环境（Windows需使用WSL）

#### 打包步骤

1. 进入项目目录：
```bash
cd phone
```

2. 初始化buildozer（首次）：
```bash
buildozer init
```

3. 构建并安装到手机：
```bash
# 调试模式构建
buildozer android debug deploy run

# 发布模式构建
buildozer android release
```

## 依赖说明

- **Kivy**: 跨平台GUI框架
- **KivyMD**: Material Design组件库
- **Pillow**: 图像处理
- **buildozer**: Android打包工具

## 数据存储

应用使用SQLite本地数据库存储：
- 用户信息
- 照片处理状态
- 历史记录

数据库文件: `app_data.db`

## 手势操作说明

| 手势 | 操作 | 效果 |
|------|------|------|
| 左滑 | 删除 | 照片标记为删除，不再显示 |
| 右滑 | 保留 | 照片标记为保留，不再显示 |
| 上滑 | 跳过 | 照片下次仍会显示 |

## 注意事项

1. **权限问题**：首次使用需要授予相册读取权限
2. **照片安全**：删除操作仅标记，不会真正删除文件
3. **存储空间**：数据库会随使用增长，建议定期清理

## 开发计划

- [ ] 添加真正的文件删除功能
- [ ] 云同步备份
- [ ] 智能分类（人脸识别、场景识别）
- [ ] 批量操作
- [ ] 暗黑模式

## 许可证

MIT License
