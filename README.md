# Chat-Room 聊天室项目

一个基于Python的实时聊天室系统，采用客户端-服务器架构，支持多用户聊天、文件传输、AI集成等功能。

## 📖 项目概述

Chat-Room是一个功能完整的聊天室应用，使用Socket进行网络通信，SQLite作为数据存储，Textual库构建TUI界面。项目采用模块化设计，代码结构清晰，易于维护和扩展。

## 🚀 功能特性

### 核心功能
- **实时聊天**：基于Socket的即时消息传输，支持群聊和私聊
- **用户管理**：完整的用户注册、登录、状态管理系统
- **聊天组管理**：支持创建、加入、进入聊天组，默认公频聊天组
- **文件传输**：通过服务器中转的安全文件上传下载功能
- **AI集成**：集成智谱AI，支持私聊和群聊中的智能对话
- **消息历史**：完整的聊天记录存储和漫游功能

### 界面特性
- **TUI界面**：使用Textual库实现的现代化命令行界面
- **三区域布局**：聊天区、输入区、状态区独立刷新
- **命令系统**：丰富的斜杠命令，支持参数和选项
- **实时更新**：在线状态、消息、用户列表实时更新

### 技术特性
- **模块化设计**：低耦合、高内聚的代码架构
- **异常处理**：完善的错误处理和用户友好的错误提示
- **数据验证**：输入验证、文件类型检查、安全性保障
- **多线程**：支持并发连接和消息处理

## 🏗️ 项目架构

```
Chat-Room/
├── client/                 # 客户端代码
│   ├── main.py            # 客户端入口程序
│   ├── ui/                # TUI界面模块
│   ├── core/              # 核心通信模块
│   │   └── client.py      # Socket客户端和高级封装
│   ├── commands/          # 命令处理模块
│   │   └── parser.py      # 命令解析和处理器
│   └── config/            # 客户端配置模块
├── server/                # 服务器端代码
│   ├── main.py           # 服务器入口程序
│   ├── core/             # 核心业务逻辑
│   │   ├── server.py     # Socket服务器和消息路由
│   │   ├── user_manager.py # 用户管理器
│   │   └── chat_manager.py # 聊天管理器
│   ├── database/         # 数据库模块
│   │   ├── models.py     # 数据模型和操作
│   │   └── connection.py # 数据库连接管理
│   ├── utils/            # 服务器工具模块
│   │   └── auth.py       # 认证和验证工具
│   ├── ai/              # AI集成模块
│   ├── config/          # 服务器配置模块
│   └── data/            # 数据存储目录
├── shared/              # 共享模块
│   ├── constants.py     # 全局常量定义
│   ├── messages.py      # 消息协议和数据结构
│   ├── exceptions.py    # 自定义异常类
│   ├── logger.py        # 日志系统
│   ├── protocol.py      # 通信协议
│   └── config_manager.py # 配置管理器
├── config/              # 配置文件目录
│   ├── server_config.yaml # 服务器配置
│   ├── client_config.yaml # 客户端配置
│   ├── templates/       # 配置模板
│   └── examples/        # 配置示例
├── test/                # 正式测试代码
│   ├── unit/            # 单元测试
│   ├── integration/     # 集成测试
│   ├── fixtures/        # 测试数据
│   └── utils/           # 测试工具
├── docs/                # 项目文档
│   ├── design/          # 设计文档
│   ├── guides/          # 使用指南
│   └── api/             # API文档
├── demo/                # 演示代码
├── tools/               # 开发工具
├── logs/                # 日志文件目录
├── archive/             # 归档文件（临时文件和调试脚本）
├── main.py              # 项目主入口
├── package.json         # 项目元数据
└── requirements.txt     # 项目依赖
```

## 📦 安装和运行

### 环境要求
- **Python**: 3.8+ (推荐3.10+)
- **操作系统**: Windows/Linux/macOS
- **内存**: 最少512MB可用内存
- **存储**: 最少100MB可用空间

### 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd Chat-Room
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置系统**

   #### 方式一：使用配置工具（推荐）
   ```bash
   # 交互式配置设置
   python tools/config_setup.py
   ```

   #### 方式二：手动配置
   ```bash
   # 复制配置模板
   cp config/server_config.template.yaml config/server_config.yaml
   cp config/client_config.template.yaml config/client_config.yaml

   # 编辑配置文件设置AI API密钥等
   nano config/server_config.yaml
   ```

   #### 环境变量迁移（如果需要）
   ```bash
   # 如果您之前使用环境变量配置，可以使用迁移工具
   python tools/migrate_config.py
   ```

4. **启动服务器**
   ```bash
   # 使用默认配置启动
   python -m server.main

   # 自定义主机和端口
   python -m server.main --host 0.0.0.0 --port 9999

   # 启用调试模式
   python -m server.main --debug
   ```

4. **启动客户端**
   ```bash
   # 连接到默认服务器
   python -m client.main

   # 连接到自定义服务器
   python -m client.main --host 192.168.1.100 --port 9999
   ```

### 数据库初始化

服务器首次启动时会自动创建数据库和表结构。如需手动初始化：

```bash
python -c "from server.database.connection import init_database; init_database()"
```

数据库文件位置：`server/data/chatroom.db`

## 🎮 使用指南

### 首次使用流程

1. **启动服务器和客户端**（参见上面的安装运行部分）

2. **注册新用户**
   ```
   未登录> /signin
   用户名: alice
   密码: password123
   确认密码: password123
   ✅ 注册成功
   ```

3. **登录系统**
   ```
   未登录> /login
   用户名: alice
   密码: password123
   ✅ 登录成功
   欢迎, alice! 您已进入公频聊天组
   ```

4. **开始聊天**
   ```
   alice> hello everyone!
   alice> /info  # 查看用户信息
   alice> /list -u  # 查看所有用户
   ```

### 命令参考

#### 基础命令
- `/?` - 显示所有可用命令列表
- `/help [命令名]` - 显示命令帮助信息
- `/login` - 用户登录（交互式）
- `/signin` - 用户注册（交互式）
- `/info` - 显示当前用户详细信息
- `/exit` - 退出系统并断开连接

#### 信息查询命令
- `/list -u` - 显示所有用户（包含在线状态）
- `/list -s` - 显示当前聊天组的所有用户
- `/list -c` - 显示本用户已加入的聊天组
- `/list -g` - 显示所有公开群聊
- `/list -f` - 显示当前聊天组的文件列表

#### 聊天组管理命令
- `/create_chat <聊天组名> [用户名1] [用户名2] ...` - 创建新聊天组
- `/enter_chat <聊天组名>` - 进入已加入的聊天组
- `/join_chat <聊天组名>` - 加入现有聊天组

#### 文件传输命令
- `/send_files <文件路径1> [文件路径2] ...` - 发送文件到当前聊天组
- `/recv_files -l` - 列出当前聊天组可下载的文件
- `/recv_files -n <文件标识>` - 下载指定文件
- `/recv_files -a` - 下载当前聊天组的所有文件

### 使用示例

#### 创建和管理聊天组
```bash
# 创建一个包含特定用户的聊天组
alice> /create_chat 项目讨论 bob charlie

# 加入现有聊天组
alice> /join_chat 技术交流

# 进入聊天组开始聊天
alice> /enter_chat 项目讨论
alice> 大家好，我们开始讨论项目吧！
```

#### 文件分享
```bash
# 发送文件
alice> /send_files ./document.pdf ./image.jpg

# 查看可下载文件
bob> /recv_files -l

# 下载特定文件
bob> /recv_files -n document.pdf
```

#### AI对话
```bash
# 配置AI功能（在config/server_config.yaml中设置API密钥）
ai:
  enabled: true
  api_key: "your-zhipu-ai-api-key"
  model: glm-4-flash

# 群聊中@AI或使用关键词
alice> @AI 你好，请帮我解释一下Python的装饰器
alice> AI能帮我写一个函数吗？

# 私聊AI（所有消息都会得到回复）
alice> /enter_chat private_with_ai
alice> 你好，这是私聊消息
```

## 🔧 开发说明

### 开发环境搭建

1. **克隆项目并安装依赖**
   ```bash
   git clone <repository-url>
   cd Chat-Room
   pip install -r requirements.txt
   ```

2. **开发工具推荐**
   - **IDE**: VS Code, PyCharm
   - **代码格式化**: black, flake8
   - **类型检查**: mypy
   - **测试框架**: pytest

### 代码规范

#### 命名规范
- **文件名**: 使用小写字母和下划线，如 `user_manager.py`
- **类名**: 使用驼峰命名法，如 `ChatRoomServer`
- **函数名**: 使用小写字母和下划线，如 `send_message`
- **常量**: 使用大写字母和下划线，如 `DEFAULT_PORT`

#### 注释规范
- **所有注释必须使用中文**
- **函数和类必须有docstring说明**
- **复杂逻辑需要添加行内注释**

```python
def send_message(self, user_id: int, content: str) -> bool:
    """
    发送消息到指定用户

    Args:
        user_id: 目标用户ID
        content: 消息内容

    Returns:
        bool: 发送是否成功

    Raises:
        UserNotFoundError: 用户不存在时抛出
    """
    # 验证用户是否存在
    if not self.user_exists(user_id):
        raise UserNotFoundError(f"用户ID {user_id} 不存在")

    # 发送消息逻辑
    return self._do_send_message(user_id, content)
```

#### 类型提示
- **所有函数参数和返回值必须添加类型提示**
- **复杂类型使用typing模块**

```python
from typing import List, Dict, Optional, Union

def get_user_chats(self, user_id: int) -> List[Dict[str, Any]]:
    """获取用户聊天组列表"""
    pass
```

### Git提交规范

#### 提交信息格式
```
[功能类型]: 简短描述（不超过20字）

详细描述（可选）
- 具体改动1
- 具体改动2
```

#### 功能类型标识
- `[新功能]`: 添加新功能
- `[修复]`: 修复bug
- `[优化]`: 性能优化或代码重构
- `[文档]`: 文档更新
- `[测试]`: 添加或修改测试
- `[配置]`: 配置文件修改

#### 提交示例
```bash
git commit -m "[新功能]: 添加用户在线状态管理"
git commit -m "[修复]: 修复消息发送时的编码错误"
git commit -m "[文档]: 更新API文档和使用说明"
```

### 项目结构说明

#### 模块职责划分
- **shared/**: 客户端和服务器共享的代码（协议、常量、异常等）
- **server/core/**: 服务器核心业务逻辑（用户管理、聊天管理）
- **server/database/**: 数据库相关操作（模型、连接管理）
- **server/utils/**: 服务器工具函数（认证、验证等）
- **server/ai/**: AI集成模块（智谱AI接口）
- **client/core/**: 客户端核心通信模块（Socket客户端）
- **client/commands/**: 客户端命令处理（命令解析器）
- **client/ui/**: 客户端TUI界面（Textual界面）
- **config/**: 配置文件管理（YAML配置文件）
- **test/**: 正式测试代码（单元测试、集成测试）
- **archive/**: 归档文件（临时文件、调试脚本、过时文档）

#### 依赖关系
- **shared模块**: 不依赖其他模块
- **server模块**: 只依赖shared模块
- **client模块**: 只依赖shared模块
- **避免循环依赖**: 严格按照层次结构组织代码

### 测试指南

#### 单元测试
```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_user_manager.py

# 生成覆盖率报告
pytest --cov=server --cov=client --cov=shared
```

#### 集成测试
```bash
# 启动测试服务器
python -m server.main --port 8889

# 运行集成测试
pytest tests/integration/
```

### 调试技巧

#### 服务器调试
```bash
# 启用调试模式
python -m server.main --debug

# 查看详细日志
python -m server.main --debug 2>&1 | tee server.log
```

#### 客户端调试
```bash
# 连接到测试服务器
python -m client.main --host localhost --port 8889
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献指南

### 贡献流程
1. Fork 项目到你的GitHub账户
2. 创建功能分支: `git checkout -b feature/新功能名称`
3. 提交更改: `git commit -m "[新功能]: 功能描述"`
4. 推送分支: `git push origin feature/新功能名称`
5. 创建Pull Request

### 贡献要求
- 遵循项目的代码规范和提交规范
- 添加必要的测试用例
- 更新相关文档
- 确保所有测试通过

### 问题反馈
- 使用GitHub Issues报告bug
- 提供详细的错误信息和复现步骤
- 建议新功能时请先讨论可行性

## 📚 更多文档

- **设计文档**: [docs/Design-v03.md](docs/Design-v03.md) - 详细的系统设计说明
- **配置指南**: [docs/Configuration_Guide.md](docs/Configuration_Guide.md) - 配置文件管理系统使用指南
- **AI集成指南**: [docs/AI_Integration_Guide.md](docs/AI_Integration_Guide.md) - AI功能配置和使用指南
- **API文档**: [docs/API.md](docs/API.md) - 网络协议和API接口文档（待创建）
- **开发指南**: [docs/Development.md](docs/Development.md) - 详细的开发指南（待创建）
- **部署指南**: [docs/Deployment.md](docs/Deployment.md) - 生产环境部署说明（待创建）

## 🔄 项目状态

### 已完成功能 ✅
- [x] 项目基础架构搭建
- [x] 数据库模型设计和实现
- [x] 服务器核心框架和Socket通信
- [x] 客户端网络通信模块
- [x] 用户注册和登录系统
- [x] 完整的命令解析系统
- [x] 消息协议定义和处理
- [x] TUI界面基础框架
- [x] 多客户端并发连接
- [x] 基本功能测试和演示
- [x] 详细项目文档

### 开发中功能 🚧
- [ ] 完整的聊天消息功能
- [ ] 聊天组管理（创建、加入、进入）
- [ ] 文件传输功能
- [ ] TUI界面优化和交互改进

### 计划功能 📋
- [x] AI集成模块（智谱AI GLM-4-Flash）
- [x] 统一配置文件管理系统
- [ ] 聊天历史查看和搜索
- [ ] 用户权限管理
- [ ] 消息加密和安全性
- [ ] 插件系统
- [ ] Web界面（可选）

### 快速体验 🚀
```bash
# 1. 安装依赖
pip install textual bcrypt pytest

# 2. 运行演示
python demo.py

# 3. 启动服务器
python -m server.main

# 4. 启动TUI客户端
python -m client.main --mode tui
```

---

**最后更新**: 2025年1月

如有问题或建议，欢迎提交Issue或联系开发团队！
