# Chat-Room 架构设计文档

## 📋 概述

Chat-Room采用经典的客户端-服务器架构，通过Socket进行网络通信，使用SQLite作为数据存储，Textual构建用户界面。整个系统采用模块化设计，各模块职责清晰，耦合度低，易于维护和扩展。

## 🏗️ 整体架构

### 系统架构图

```mermaid
graph TB
    subgraph "客户端层"
        TUI[TUI客户端<br/>Textual界面]
        CLI[简单客户端<br/>命令行界面]
        EXT[扩展客户端<br/>其他接口]
    end

    subgraph "网络通信层"
        SOCKET[Socket通信<br/>TCP连接]
    end

    subgraph "服务器核心层"
        SERVER[聊天室服务器<br/>多线程处理]
    end

    subgraph "业务逻辑层"
        USER_MGR[用户管理器<br/>认证&会话]
        CHAT_MGR[聊天管理器<br/>消息路由]
        FILE_MGR[文件管理器<br/>上传下载]
        AI_MGR[AI处理器<br/>智谱AI集成]
    end

    subgraph "数据存储层"
        DB[(SQLite数据库<br/>用户&消息&文件)]
        FILES[文件存储<br/>本地文件系统]
    end

    TUI --> SOCKET
    CLI --> SOCKET
    EXT --> SOCKET
    SOCKET --> SERVER
    SERVER --> USER_MGR
    SERVER --> CHAT_MGR
    SERVER --> FILE_MGR
    SERVER --> AI_MGR
    USER_MGR --> DB
    CHAT_MGR --> DB
    FILE_MGR --> DB
    FILE_MGR --> FILES
    AI_MGR --> DB
```

### 核心组件

#### 1. 客户端层 (Client Layer)
- **TUI客户端**: 基于Textual的现代化界面
- **简单客户端**: 基础命令行界面
- **网络通信模块**: Socket客户端封装

#### 2. 服务器层 (Server Layer)
- **Socket服务器**: 处理客户端连接和消息路由
- **用户管理器**: 用户认证、会话管理、状态跟踪
- **聊天管理器**: 聊天组管理、消息广播、历史记录
- **AI处理器**: 智谱AI集成、智能回复

#### 3. 数据层 (Data Layer)
- **SQLite数据库**: 用户数据、聊天记录、文件信息
- **文件存储**: 上传文件的本地存储

#### 4. 共享层 (Shared Layer)
- **通信协议**: 客户端-服务器消息格式
- **常量定义**: 系统配置常量
- **异常处理**: 统一异常类定义

## 🔧 模块设计

### 客户端模块 (client/)

#### 核心通信模块 (client/core/)
```python
class ChatClient:
    """聊天客户端核心类"""
    
    def __init__(self, host: str, port: int)
    def connect() -> bool
    def login(username: str, password: str) -> Tuple[bool, str]
    def send_message(content: str) -> bool
    def upload_file(file_path: str) -> Tuple[bool, str]
    def download_file(file_id: str) -> Tuple[bool, str]
```

**职责**:
- Socket连接管理
- 消息发送接收
- 文件传输处理
- 协议解析封装

#### TUI界面模块 (client/ui/)
```python
class ChatApp(App):
    """主应用界面"""
    
    def compose() -> ComposeResult
    def on_mount() -> None
    def handle_message(message: Message) -> None
```

**职责**:
- 用户界面渲染
- 用户交互处理
- 实时状态更新
- 主题管理

#### 命令处理模块 (client/commands/)
```python
class CommandParser:
    """命令解析器"""
    
    def parse_command(input_text: str) -> Command
    def execute_command(command: Command) -> CommandResult
    def get_help(command_name: str) -> str
```

**职责**:
- 斜杠命令解析
- 命令参数验证
- 命令执行调度
- 帮助信息提供

### 服务器模块 (server/)

#### 核心服务器 (server/core/server.py)
```python
class ChatRoomServer:
    """聊天室服务器主类"""
    
    def __init__(self, host: str, port: int)
    def start() -> None
    def stop() -> None
    def handle_client(client_socket: socket.socket) -> None
```

**职责**:
- Socket服务器管理
- 客户端连接处理
- 消息路由分发
- 多线程管理

#### 用户管理器 (server/core/user_manager.py)
```python
class UserManager:
    """用户管理器"""
    
    def register_user(username: str, password: str) -> Tuple[bool, str]
    def authenticate_user(username: str, password: str) -> Tuple[bool, User]
    def get_online_users() -> List[User]
    def update_user_status(user_id: int, status: str) -> bool
```

**职责**:
- 用户注册登录
- 会话状态管理
- 在线用户跟踪
- 用户信息查询

#### 聊天管理器 (server/core/chat_manager.py)
```python
class ChatManager:
    """聊天管理器"""
    
    def create_chat_group(name: str, creator_id: int) -> Tuple[bool, str]
    def join_chat_group(group_id: int, user_id: int) -> Tuple[bool, str]
    def send_message(group_id: int, user_id: int, content: str) -> bool
    def broadcast_message(group_id: int, message: Message) -> None
```

**职责**:
- 聊天组管理
- 消息广播
- 历史记录存储
- 成员权限管理

### 数据库模块 (server/database/)

#### 数据模型 (server/database/models.py)
```python
class User:
    """用户数据模型"""
    id: int
    username: str
    password_hash: str
    created_at: datetime
    last_login: datetime

class ChatGroup:
    """聊天组数据模型"""
    id: int
    name: str
    creator_id: int
    created_at: datetime
    is_public: bool

class Message:
    """消息数据模型"""
    id: int
    group_id: int
    user_id: int
    content: str
    message_type: str
    created_at: datetime
```

**职责**:
- 数据结构定义
- 数据库操作封装
- 数据验证
- 关系映射

### AI集成模块 (server/ai/)

#### AI处理器 (server/ai/ai_handler.py)
```python
class AIHandler:
    """AI处理器"""
    
    def __init__(self, api_key: str, model: str)
    def should_respond(message: str, context: dict) -> bool
    def generate_response(message: str, context: dict) -> str
    def update_context(user_id: int, message: str) -> None
```

**职责**:
- 智谱AI API调用
- 对话上下文管理
- 智能回复判断
- AI功能配置

## 🔄 核心流程

### 用户登录流程

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务器
    participant UM as 用户管理器
    participant DB as 数据库

    C->>S: 发送登录请求
    S->>UM: 验证用户凭据
    UM->>DB: 查询用户信息
    DB-->>UM: 返回用户数据
    UM->>UM: 验证密码哈希
    alt 验证成功
        UM->>UM: 创建会话
        UM-->>S: 返回成功+用户信息
        S-->>C: 登录成功响应
        S->>S: 加入公频聊天组
    else 验证失败
        UM-->>S: 返回失败信息
        S-->>C: 登录失败响应
    end
```

### 消息发送流程

```mermaid
sequenceDiagram
    participant C1 as 发送客户端
    participant S as 服务器
    participant CM as 聊天管理器
    participant DB as 数据库
    participant C2 as 接收客户端

    C1->>S: 发送聊天消息
    S->>CM: 处理消息
    CM->>DB: 存储消息记录
    CM->>CM: 获取聊天组成员
    loop 广播给每个在线成员
        CM->>S: 转发消息
        S->>C2: 推送消息
    end
    CM-->>S: 处理完成
    S-->>C1: 发送确认
```

### 文件传输流程

```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务器
    participant FH as 文件处理器
    participant FS as 文件系统
    participant DB as 数据库

    C->>S: 文件上传请求
    S->>FH: 处理上传
    FH->>FH: 验证文件类型和大小
    FH->>FS: 保存文件到磁盘
    FH->>DB: 记录文件信息
    FH-->>S: 上传完成
    S-->>C: 上传成功响应

    Note over C,DB: 文件下载流程
    C->>S: 文件下载请求
    S->>FH: 处理下载
    FH->>DB: 查询文件信息
    FH->>FS: 读取文件数据
    FH-->>S: 返回文件数据
    S-->>C: 发送文件内容
```

## 📡 通信协议

### 消息格式

所有客户端-服务器通信使用JSON格式：

```json
{
    "type": "message_type",
    "data": {
        "key": "value"
    },
    "timestamp": "2025-06-16T10:30:00Z",
    "request_id": "unique_id"
}
```

### 消息类型

#### 认证消息
- `login_request`: 登录请求
- `login_response`: 登录响应
- `register_request`: 注册请求
- `register_response`: 注册响应

#### 聊天消息
- `chat_message`: 聊天消息
- `system_message`: 系统消息
- `user_joined`: 用户加入通知
- `user_left`: 用户离开通知

#### 文件传输
- `file_upload_request`: 文件上传请求
- `file_upload_response`: 文件上传响应
- `file_download_request`: 文件下载请求
- `file_download_response`: 文件下载响应

#### AI交互
- `ai_request`: AI对话请求
- `ai_response`: AI对话响应

## 🔒 安全设计

### 认证安全
- 密码使用bcrypt哈希存储
- 会话token验证
- 输入数据验证和清理

### 通信安全
- 消息格式验证
- 文件类型和大小限制
- 防止SQL注入和XSS攻击

### 数据安全
- 敏感信息加密存储
- 定期清理过期会话
- 访问权限控制

## 📈 性能优化

### 并发处理
- 多线程处理客户端连接
- 异步消息处理
- 连接池管理

### 数据库关系图

```mermaid
erDiagram
    users {
        int id PK
        string username UK
        string password_hash
        datetime created_at
        datetime last_login
        boolean is_active
    }

    chat_groups {
        int id PK
        string name UK
        int creator_id FK
        datetime created_at
        boolean is_public
    }

    group_members {
        int id PK
        int group_id FK
        int user_id FK
        datetime joined_at
        string role
    }

    messages {
        int id PK
        int group_id FK
        int user_id FK
        text content
        string message_type
        datetime created_at
    }

    files {
        int id PK
        string file_id UK
        int group_id FK
        int uploader_id FK
        string original_filename
        string stored_filename
        int file_size
        string file_type
        datetime upload_time
    }

    users ||--o{ chat_groups : creates
    users ||--o{ group_members : joins
    chat_groups ||--o{ group_members : contains
    chat_groups ||--o{ messages : receives
    users ||--o{ messages : sends
    chat_groups ||--o{ files : stores
    users ||--o{ files : uploads
```

### 数据库优化
- 索引优化
- 查询缓存
- 批量操作

### 内存管理
- 对象池复用
- 及时释放资源
- 内存使用监控

## 🔄 扩展性设计

### 插件系统
- 命令插件接口
- AI模型插件接口
- 界面主题插件

### 分布式支持
- 服务器集群部署
- 负载均衡
- 数据同步

### 多协议支持
- WebSocket协议
- HTTP REST API
- gRPC接口

## 📊 监控和日志

### 日志系统
- 分级日志记录
- 日志轮转管理
- 性能指标记录

### 监控指标
- 连接数统计
- 消息吞吐量
- 错误率监控
- 资源使用情况

这个架构设计确保了系统的可维护性、可扩展性和高性能，为Chat-Room项目的长期发展奠定了坚实的基础。
