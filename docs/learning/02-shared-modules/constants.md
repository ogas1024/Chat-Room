# 常量定义学习 - shared/constants.py

## 📋 模块概述

`shared/constants.py` 是整个Chat-Room项目的常量定义中心。这个文件定义了项目中使用的所有常量，包括网络配置、消息类型、错误代码等。

## 🎯 为什么需要常量文件？

### 避免魔法数字和字符串

**不好的做法**：
```python
# 代码中直接使用数字和字符串
if port == 8888:  # 魔法数字
    print("连接到默认端口")

if message_type == "login_request":  # 魔法字符串
    handle_login()
```

**好的做法**：
```python
# 使用常量
if port == DEFAULT_PORT:
    print("连接到默认端口")

if message_type == MessageType.LOGIN_REQUEST:
    handle_login()
```

### 集中管理配置

**优势**：
- **易于维护**：修改配置只需要改一个地方
- **避免错误**：减少拼写错误和不一致
- **提高可读性**：常量名称比数字更有意义
- **便于重构**：修改常量值不影响业务逻辑

## 🔧 常量分类详解

### 1. 网络配置常量

```python
# 网络相关常量
DEFAULT_HOST = "localhost"      # 默认服务器地址
DEFAULT_PORT = 8888            # 默认服务器端口
BUFFER_SIZE = 4096             # 网络缓冲区大小
MAX_CONNECTIONS = 100          # 最大连接数
```

**学习要点**：
- **DEFAULT_HOST**：开发环境使用localhost，生产环境可能是具体IP
- **BUFFER_SIZE**：影响网络传输效率，太小会频繁读取，太大浪费内存
- **MAX_CONNECTIONS**：服务器能同时处理的最大客户端数量

**实际应用**：
```python
# 在服务器启动时使用
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((DEFAULT_HOST, DEFAULT_PORT))
server_socket.listen(MAX_CONNECTIONS)
```

### 2. 消息类型枚举

```python
class MessageType(Enum):
    """消息类型枚举"""
    # 认证相关
    LOGIN_REQUEST = "login_request"
    LOGIN_RESPONSE = "login_response"
    REGISTER_REQUEST = "register_request"
    REGISTER_RESPONSE = "register_response"
    
    # 聊天相关
    CHAT_MESSAGE = "chat_message"
    SYSTEM_MESSAGE = "system_message"
    ERROR_MESSAGE = "error_message"
```

**为什么使用枚举**：
```python
# 枚举的优势
from enum import Enum

class MessageType(Enum):
    LOGIN_REQUEST = "login_request"
    
# 1. 类型安全
def handle_message(msg_type: MessageType):
    if msg_type == MessageType.LOGIN_REQUEST:  # IDE会提供自动补全
        # 处理登录请求
        pass

# 2. 避免拼写错误
# 错误：MessageType.LOGIN_REQEUST  # IDE会报错
# 正确：MessageType.LOGIN_REQUEST

# 3. 便于重构
# 如果要修改消息类型的值，只需要修改枚举定义
```

### 3. 错误代码定义

```python
class ErrorCode(Enum):
    """错误代码枚举"""
    # 认证错误 (1000-1099)
    AUTHENTICATION_FAILED = 1001
    USER_ALREADY_EXISTS = 1002
    USER_NOT_FOUND = 1003
    
    # 权限错误 (1100-1199)
    PERMISSION_DENIED = 1101
    NOT_IN_CHAT_GROUP = 1102
    
    # 服务器错误 (1200-1299)
    SERVER_ERROR = 1201
    DATABASE_ERROR = 1202
```

**错误代码设计原则**：
- **分类编号**：不同类型的错误使用不同的数字范围
- **便于扩展**：预留足够的编号空间
- **语义明确**：错误代码名称要清楚表达错误类型

**实际使用**：
```python
# 在服务器端返回错误
def authenticate_user(username, password):
    user = database.get_user(username)
    if not user:
        raise AuthenticationError(ErrorCode.USER_NOT_FOUND)
    
    if not verify_password(password, user.password_hash):
        raise AuthenticationError(ErrorCode.AUTHENTICATION_FAILED)
```

### 4. 文件传输常量

```python
# 文件传输相关常量
FILES_STORAGE_PATH = "server/data/files"  # 文件存储路径
FILE_CHUNK_SIZE = 8192                    # 文件传输块大小
MAX_FILE_SIZE = 100 * 1024 * 1024        # 最大文件大小 (100MB)

# 允许的文件扩展名
ALLOWED_FILE_EXTENSIONS = [
    ".txt", ".doc", ".docx", ".pdf",
    ".jpg", ".jpeg", ".png", ".gif",
    ".mp3", ".mp4", ".avi",
    ".zip", ".rar", ".py", ".js"
]
```

**设计考虑**：
- **FILE_CHUNK_SIZE**：平衡内存使用和传输效率
- **MAX_FILE_SIZE**：防止过大文件影响系统性能
- **文件类型限制**：安全考虑，只允许特定类型文件

### 5. 用户状态和聊天类型

```python
class UserStatus(Enum):
    """用户状态枚举"""
    ONLINE = "online"      # 在线
    OFFLINE = "offline"    # 离线
    AWAY = "away"          # 离开
    BUSY = "busy"          # 忙碌

class ChatType(Enum):
    """聊天类型枚举"""
    PUBLIC = "public"      # 公频聊天
    GROUP = "group"        # 群聊
    PRIVATE = "private"    # 私聊
```

### 6. AI相关常量

```python
# AI用户配置
AI_USER_ID = 999999           # AI用户的特殊ID
AI_USERNAME = "AI"            # AI用户名
AI_DISPLAY_NAME = "智能助手"   # AI显示名称

# AI触发关键词
AI_KEYWORDS = [
    "ai", "AI", "人工智能", "助手", 
    "机器人", "智能", "问答"
]
```

## 🎨 常量使用最佳实践

### 1. 命名规范

```python
# 好的命名
DEFAULT_PORT = 8888           # 全大写，下划线分隔
MAX_CONNECTIONS = 100         # 语义清晰
BUFFER_SIZE = 4096           # 表达具体含义

# 不好的命名
port = 8888                  # 小写，不明确是常量
MAX_CONN = 100              # 缩写不清楚
SIZE = 4096                 # 太泛化
```

### 2. 分组组织

```python
# 按功能分组
# ========== 网络配置 ==========
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8888
BUFFER_SIZE = 4096

# ========== 文件配置 ==========
FILES_STORAGE_PATH = "server/data/files"
MAX_FILE_SIZE = 100 * 1024 * 1024

# ========== 时间配置 ==========
CONNECTION_TIMEOUT = 30
HEARTBEAT_INTERVAL = 60
```

### 3. 类型提示

```python
from typing import List, Final

# 使用Final表示常量
DEFAULT_PORT: Final[int] = 8888
DEFAULT_HOST: Final[str] = "localhost"
ALLOWED_EXTENSIONS: Final[List[str]] = [".txt", ".jpg", ".pdf"]
```

## 🔍 实际应用示例

### 在服务器中使用常量

```python
# server/core/server.py
from shared.constants import (
    DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE,
    MessageType, ErrorCode, MAX_CONNECTIONS
)

class ChatRoomServer:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.buffer_size = BUFFER_SIZE
        
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(MAX_CONNECTIONS)
        
    def handle_message(self, message_type: str, data: dict):
        if message_type == MessageType.LOGIN_REQUEST.value:
            return self.handle_login(data)
        elif message_type == MessageType.CHAT_MESSAGE.value:
            return self.handle_chat_message(data)
```

### 在客户端中使用常量

```python
# client/core/client.py
from shared.constants import DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE

class NetworkClient:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        
    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except socket.error:
            return False
```

## 💡 学习练习

### 练习1：添加新的消息类型

尝试添加一个新的消息类型用于心跳检测：

```python
class MessageType(Enum):
    # 现有的消息类型...
    
    # 新增心跳消息类型
    HEARTBEAT_REQUEST = "heartbeat_request"
    HEARTBEAT_RESPONSE = "heartbeat_response"
```

### 练习2：定义时间相关常量

```python
# 时间相关常量（秒）
CONNECTION_TIMEOUT = 30        # 连接超时时间
HEARTBEAT_INTERVAL = 60        # 心跳间隔
SESSION_TIMEOUT = 3600         # 会话超时时间
MESSAGE_HISTORY_DAYS = 30      # 消息历史保留天数
```

### 练习3：创建配置验证函数

```python
def validate_constants():
    """验证常量配置的合理性"""
    assert DEFAULT_PORT > 1024, "端口号应大于1024"
    assert BUFFER_SIZE > 0, "缓冲区大小应大于0"
    assert MAX_FILE_SIZE > 0, "最大文件大小应大于0"
    assert len(ALLOWED_FILE_EXTENSIONS) > 0, "应至少允许一种文件类型"
    
    print("✅ 常量配置验证通过")

# 在程序启动时调用
if __name__ == "__main__":
    validate_constants()
```

## 🤔 思考题

1. **为什么要使用枚举而不是普通的字符串常量？**
   - 类型安全
   - IDE支持
   - 避免拼写错误
   - 便于重构

2. **如何设计错误代码的编号规则？**
   - 按错误类型分段
   - 预留扩展空间
   - 保持一致性

3. **常量文件过大时如何组织？**
   - 按功能模块拆分
   - 使用子模块
   - 保持导入简洁

## 📚 扩展学习

### 相关Python概念
- **枚举 (Enum)**：学习Python枚举的高级用法
- **类型提示**：了解Final、Literal等类型
- **模块组织**：学习Python包和模块的最佳实践

### 设计模式
- **常量模式**：集中管理配置的设计模式
- **枚举模式**：使用枚举替代魔法数字

---

**下一步**：学习消息协议设计 → [messages.md](./messages.md)
