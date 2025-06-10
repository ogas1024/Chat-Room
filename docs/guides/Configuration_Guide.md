# Chat-Room 配置管理指南

## 📖 概述

Chat-Room项目采用统一的配置文件管理系统，支持YAML和JSON格式，提供服务器端和客户端独立配置，完全移除了对环境变量的依赖。

## 🏗️ 配置架构

### 配置文件结构
```
Chat-Room/
├── config/
│   ├── server_config.yaml          # 服务器配置文件
│   ├── client_config.yaml          # 客户端配置文件
│   ├── server_config.template.yaml # 服务器配置模板
│   └── client_config.template.yaml # 客户端配置模板
├── tools/
│   ├── config_setup.py            # 配置设置工具
│   └── migrate_config.py          # 环境变量迁移工具
└── shared/
    └── config_manager.py          # 配置管理核心模块
```

### 配置管理特性
- ✅ **统一管理**: YAML/JSON格式配置文件
- ✅ **独立配置**: 服务器和客户端分离
- ✅ **配置验证**: 自动验证配置格式和值
- ✅ **默认值**: 配置缺失时使用合理默认值
- ✅ **热重载**: 支持运行时重新加载配置
- ✅ **模板支持**: 提供配置模板和示例
- ✅ **迁移工具**: 从环境变量平滑迁移

## 🔧 服务器配置

### 配置文件位置
- **主配置**: `config/server_config.yaml`
- **模板文件**: `config/server_config.template.yaml`

### 主要配置项

#### 1. 服务器网络配置
```yaml
server:
  host: localhost                    # 服务器监听地址
  port: 8888                        # 服务器监听端口
  max_connections: 100              # 最大连接数
  buffer_size: 4096                 # 缓冲区大小
  heartbeat_interval: 30            # 心跳间隔（秒）
  connection_timeout: 300           # 连接超时时间（秒）
```

#### 2. AI配置（重要）
```yaml
ai:
  enabled: true                     # 是否启用AI功能
  api_key: "your-api-key-here"      # 智谱AI API密钥
  model: glm-4-flash               # 使用的AI模型
  max_tokens: 1024                  # 最大输出令牌数
  temperature: 0.7                  # 创造性参数（0-2）
  top_p: 0.9                       # 多样性控制参数
  enable_group_chat: true           # 在群聊中启用AI
  enable_private_chat: true         # 在私聊中启用AI
```

#### 3. 数据库配置
```yaml
database:
  path: server/data/chatroom.db     # 数据库文件路径
  backup_enabled: true              # 是否启用备份
  backup_interval: 3600             # 备份间隔（秒）
  auto_vacuum: true                 # 自动清理数据库
```

#### 4. 文件存储配置
```yaml
file_storage:
  path: server/data/files           # 文件存储路径
  max_file_size: 104857600          # 最大文件大小（100MB）
  allowed_extensions:               # 允许的文件扩展名
    - .txt
    - .pdf
    - .jpg
    - .png
  chunk_size: 8192                  # 文件传输块大小
```

#### 5. 日志配置
```yaml
logging:
  level: INFO                       # 日志级别
  file_enabled: true                # 是否启用文件日志
  file_path: logs/server.log        # 日志文件路径
  console_enabled: true             # 是否启用控制台日志
```

## 🎨 客户端配置

### 配置文件位置
- **主配置**: `config/client_config.yaml`
- **模板文件**: `config/client_config.template.yaml`

### 主要配置项

#### 1. 连接配置
```yaml
connection:
  default_host: localhost           # 默认服务器地址
  default_port: 8888               # 默认服务器端口
  connection_timeout: 10            # 连接超时时间（秒）
  reconnect_attempts: 3             # 重连尝试次数
  auto_reconnect: true              # 自动重连
```

#### 2. 用户界面配置
```yaml
ui:
  mode: tui                         # 界面模式（tui 或 cli）
  theme: default                    # 主题名称
  language: zh_CN                   # 语言设置
  show_timestamps: true             # 显示时间戳
  auto_scroll: true                 # 自动滚动
```

#### 3. 用户偏好设置
```yaml
user:
  remember_credentials: false       # 记住登录凭据
  auto_login: false                 # 自动登录
  download_path: downloads          # 下载路径
  save_chat_history: true           # 保存聊天历史
```

#### 4. 聊天行为配置
```yaml
chat:
  auto_join_public: true            # 自动加入公共聊天
  message_send_key: Enter           # 消息发送键
  enable_emoji: true                # 启用表情符号
  max_message_length: 2048          # 最大消息长度
```

## 🚀 快速开始

### 1. 首次配置

#### 使用配置工具（推荐）
```bash
# 交互式配置设置
python tools/config_setup.py
```

#### 手动配置
```bash
# 复制模板文件
cp config/server_config.template.yaml config/server_config.yaml
cp config/client_config.template.yaml config/client_config.yaml

# 编辑配置文件
nano config/server_config.yaml
nano config/client_config.yaml
```

### 2. 设置AI功能

编辑 `config/server_config.yaml`：
```yaml
ai:
  enabled: true
  api_key: "your-zhipu-ai-api-key"  # 在此填入您的API密钥
  model: glm-4-flash
```

### 3. 启动服务

```bash
# 启动服务器
python -m server.main

# 启动客户端
python -m client.main
```

## 🔄 环境变量迁移

如果您之前使用环境变量配置，可以使用迁移工具：

```bash
# 自动检测并迁移环境变量
python tools/migrate_config.py
```

迁移工具会：
- 检测现有环境变量（如 `ZHIPU_API_KEY`）
- 自动迁移到配置文件
- 创建迁移备份
- 生成迁移报告

## 🛠️ 高级配置

### 配置验证

配置系统支持自动验证：
```python
from server.config.server_config import get_server_config

config = get_server_config()
info = config.get_config_info()
print(f"配置验证: {'通过' if info['has_schema'] else '跳过'}")
```

### 动态配置更新

```python
# 更新AI API密钥
config.set_ai_api_key("new-api-key")

# 更改AI模型
config.set_ai_model("glm-4-plus")

# 重新加载配置
config.reload_config()
```

### 配置模板导出

```python
# 导出服务器配置模板
config.export_template("my_server_template.yaml")

# 导出客户端配置模板
from client.config.client_config import get_client_config
client_config = get_client_config()
client_config.export_template("my_client_template.yaml")
```

## 🔍 配置管理API

### 服务器配置API

```python
from server.config.server_config import get_server_config

config = get_server_config()

# 基本配置
host = config.get_server_host()
port = config.get_server_port()
max_conn = config.get_max_connections()

# AI配置
ai_enabled = config.is_ai_enabled()
api_key = config.get_ai_api_key()
ai_model = config.get_ai_model()

# 配置管理
config.save_config()
config.reload_config()
```

### 客户端配置API

```python
from client.config.client_config import get_client_config

config = get_client_config()

# 连接配置
host = config.get_default_host()
port = config.get_default_port()
timeout = config.get_connection_timeout()

# UI配置
ui_mode = config.get_ui_mode()
theme = config.get_theme()

# 用户配置
download_path = config.get_download_path()
auto_login = config.is_auto_login_enabled()
```

## 🐛 故障排除

### 常见问题

#### Q: 配置文件不存在？
A: 首次运行时会自动创建默认配置文件，或使用模板文件：
```bash
cp config/server_config.template.yaml config/server_config.yaml
```

#### Q: AI功能无法启用？
A: 检查配置文件中的AI设置：
```yaml
ai:
  enabled: true
  api_key: "your-api-key"  # 确保API密钥正确
```

#### Q: 配置修改不生效？
A: 重启服务器或使用热重载：
```python
config.reload_config()
```

#### Q: 配置验证失败？
A: 检查配置格式和值的有效性，参考模板文件。

### 调试配置

```bash
# 测试配置系统
python test_config_system.py

# 查看配置信息
python -c "
from server.config.server_config import get_server_config
config = get_server_config()
print(config.get_config_info())
"
```

## 📚 最佳实践

### 1. 配置文件管理
- 使用版本控制管理配置模板
- 不要提交包含敏感信息的配置文件
- 定期备份重要配置

### 2. 安全考虑
- API密钥等敏感信息仅存储在配置文件中
- 设置适当的文件权限（600）
- 定期轮换API密钥

### 3. 部署建议
- 为不同环境准备不同的配置文件
- 使用配置模板简化部署
- 自动化配置验证和测试

## 🔗 相关文档

- [AI集成指南](AI_Integration_Guide.md)
- [项目README](../README.md)
- [开发指南](Development.md)

---

**最后更新**: 2025年1月
**版本**: v2.0 - 配置文件系统
