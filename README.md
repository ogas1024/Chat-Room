# Chat-Room 聊天室项目

一个基于Python的实时聊天室系统，支持多用户聊天、文件传输、AI集成等功能。

## 🚀 功能特性

### 核心功能
- **实时聊天**：支持即时消息传输，在线用户可实时接收消息
- **用户管理**：用户注册、登录、状态管理
- **聊天组管理**：支持群聊和私聊，默认公频聊天组
- **文件传输**：通过服务器中转的文件上传下载功能
- **AI集成**：集成智谱AI，支持私聊和群聊中的AI对话

### 界面特性
- **TUI界面**：使用Textual库实现的命令行界面
- **三区域布局**：聊天区、输入区、状态区
- **命令系统**：丰富的斜杠命令支持

## 🏗️ 项目架构

```
Chat-Room/
├── client/          # 客户端代码
├── server/          # 服务器端代码
├── shared/          # 共享模块
├── tests/           # 测试代码
└── docs/            # 项目文档
```

## 📦 安装和运行

### 环境要求
- Python 3.8+
- SQLite3

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行服务器
```bash
python -m server.main
```

### 运行客户端
```bash
python -m client.main
```

## 🎮 使用指南

### 基本命令
- `/?` - 显示所有可用命令
- `/help {command}` - 显示特定命令的帮助
- `/login` - 用户登录
- `/signin` - 用户注册
- `/info` - 显示用户信息
- `/exit` - 退出系统

### 聊天命令
- `/list -u` - 显示所有用户
- `/list -s` - 显示当前聊天组用户
- `/list -c` - 显示已加入的聊天组
- `/create_chat {name} {users...}` - 创建聊天组
- `/enter_chat {name}` - 进入聊天组
- `/join_chat {name}` - 加入聊天组

### 文件命令
- `/send_files {path...}` - 发送文件
- `/recv_files -l` - 列出可下载文件
- `/recv_files -n {file}` - 下载指定文件
- `/recv_files -a` - 下载所有文件

## 🔧 开发说明

### 代码规范
- 所有注释使用中文
- 遵循PEP8代码风格
- 使用类型提示

### 提交规范
- commit信息使用中文
- 格式：[功能类型]: 具体功能描述

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📚 更多文档

详细设计文档请参考 [docs/Design-v03.md](docs/Design-v03.md)
