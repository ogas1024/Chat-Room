# 文件传输功能使用指南

## 📋 功能概述

Chat-Room项目现已支持完整的文件传输功能，包括：
- 多文件上传
- 按文件名下载
- 文件列表查看
- 自动文件组织

## 🚀 快速开始

### 1. 启动服务器
```bash
cd /home/ogas/Code/CN/Chat-Room
python server/main.py
```

### 2. 启动客户端
```bash
cd /home/ogas/Code/CN/Chat-Room
python client/main.py
```

### 3. 登录并进入聊天组
```
/login
# 输入用户名和密码

/enter_chat 公频
# 或进入其他聊天组
```

## 📤 文件上传功能

### 命令格式
```
/send_files {文件路径1} {文件路径2} ...
```

### 使用示例
```bash
# 上传单个文件
/send_files /home/user/document.pdf

# 上传多个文件
/send_files /home/user/photo1.jpg /home/user/photo2.jpg /home/user/document.pdf

# 支持相对路径
/send_files ./test.txt ../data/config.json
```

### 功能特点
- ✅ 支持多文件同时上传
- ✅ 自动验证文件大小和类型
- ✅ 文件存储在 `server/{group_id}/{file_id}` 格式
- ✅ 自动生成文件通知消息
- ✅ 实时进度反馈

### 支持的文件类型
- 文档：`.txt`, `.doc`, `.docx`, `.pdf`
- 图片：`.jpg`, `.jpeg`, `.png`, `.gif`
- 音视频：`.mp3`, `.mp4`, `.avi`
- 压缩包：`.zip`, `.rar`
- 代码：`.py`, `.js`, `.html`, `.css`

### 文件大小限制
- 最大文件大小：100MB

## 📥 文件下载功能

### 查看文件列表
```
/recv_files -l
```

输出示例：
```
可下载文件列表:
  ID: 1 - document.pdf (2.5MB)
    上传者: alice - 时间: 2025-01-20 10:30:15
  ID: 2 - photo.jpg (1.2MB)
    上传者: bob - 时间: 2025-01-20 11:15:22
```

### 按文件名下载
```bash
# 下载单个文件
/recv_files -n document.pdf

# 下载多个文件
/recv_files -n document.pdf photo.jpg config.json
```

### 下载所有文件
```
/recv_files -a
```

### 下载路径
- 文件自动下载到：`client/Downloads/{用户名}/`
- 例如：`client/Downloads/alice/document.pdf`

## 🗂️ 文件存储结构

### 服务器端
```
server/
├── data/
│   └── files/
│       ├── 1/          # 聊天组1的文件
│       │   ├── 1       # 文件ID为1的文件
│       │   └── 2       # 文件ID为2的文件
│       └── 2/          # 聊天组2的文件
│           └── 3       # 文件ID为3的文件
```

### 客户端
```
client/
└── Downloads/
    ├── alice/          # 用户alice的下载文件
    │   ├── document.pdf
    │   └── photo.jpg
    └── bob/            # 用户bob的下载文件
        └── config.json
```

## 🔧 技术实现

### 数据库设计
```sql
CREATE TABLE files_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT NOT NULL,
    server_filepath TEXT NOT NULL UNIQUE,
    file_size INTEGER NOT NULL,
    uploader_id INTEGER,
    chat_group_id INTEGER,
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_id INTEGER,
    FOREIGN KEY (uploader_id) REFERENCES users(id),
    FOREIGN KEY (chat_group_id) REFERENCES chat_groups(id),
    FOREIGN KEY (message_id) REFERENCES messages(id)
);
```

### 文件传输流程

#### 上传流程
1. 客户端发送 `FileUploadRequest`
2. 服务器验证权限和文件信息
3. 服务器创建文件元数据记录
4. 服务器发送 `FileUploadResponse` 准备接收
5. 客户端分块发送文件数据
6. 服务器接收并保存文件
7. 服务器更新文件元数据
8. 服务器广播文件通知消息

#### 下载流程
1. 客户端发送 `FileDownloadRequest`
2. 服务器验证权限和文件存在性
3. 服务器发送 `FileDownloadResponse` 开始传输
4. 服务器分块发送文件数据
5. 客户端接收并保存文件
6. 客户端验证文件完整性

## ⚠️ 注意事项

1. **权限控制**：只能下载所在聊天组的文件
2. **文件覆盖**：同名文件会被覆盖
3. **网络中断**：传输中断时需要重新上传/下载
4. **存储空间**：注意服务器和客户端的存储空间

## 🐛 故障排除

### 常见问题

**Q: 文件上传失败**
A: 检查文件大小、类型和网络连接

**Q: 找不到下载的文件**
A: 检查 `client/Downloads/{用户名}/` 目录

**Q: 文件列表为空**
A: 确认已进入正确的聊天组

**Q: 权限被拒绝**
A: 确认已登录并加入了相应的聊天组

### 日志查看
```bash
# 查看服务器日志
tail -f logs/server/server.log

# 查看客户端日志
tail -f logs/client/client.log
```

## 🔄 版本更新

### v1.0 (当前版本)
- ✅ 基础文件上传下载
- ✅ 多文件支持
- ✅ 按文件名下载
- ✅ 自动文件组织

### 计划功能
- 📋 文件搜索功能
- 📋 文件预览功能
- 📋 断点续传
- 📋 文件分享链接
