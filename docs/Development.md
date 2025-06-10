# Chat-Room 开发指南

## 开发环境搭建

### 系统要求
- **Python**: 3.8+ (推荐 3.10+)
- **Git**: 用于版本控制
- **IDE**: VS Code 或 PyCharm (推荐)

### 环境配置

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd Chat-Room
   ```

2. **创建虚拟环境**
   ```bash
   # 使用 venv
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **安装开发工具**
   ```bash
   pip install black flake8 mypy pytest pytest-cov
   ```

### IDE 配置

#### VS Code 推荐插件
- Python
- Python Docstring Generator
- GitLens
- Better Comments
- Error Lens

#### VS Code 配置文件 (.vscode/settings.json)
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.formatOnSave": true,
    "files.encoding": "utf8"
}
```

## 项目架构详解

### 模块设计原则

1. **单一职责**: 每个模块只负责一个特定功能
2. **低耦合**: 模块间依赖关系清晰简单
3. **高内聚**: 模块内部功能紧密相关
4. **可测试**: 便于编写单元测试

### 核心模块说明

#### shared 模块
**职责**: 客户端和服务器共享的代码
- `constants.py`: 全局常量定义
- `messages.py`: 消息协议和数据结构
- `exceptions.py`: 自定义异常类

**设计要点**:
- 不依赖任何其他模块
- 定义通信协议和数据格式
- 提供统一的异常处理

#### server 模块
**职责**: 服务器端业务逻辑

**core 子模块**:
- `server.py`: Socket服务器和消息路由
- `user_manager.py`: 用户管理（注册、登录、状态）
- `chat_manager.py`: 聊天管理（消息、聊天组）

**database 子模块**:
- `models.py`: 数据模型和数据库操作
- `connection.py`: 数据库连接管理

**utils 子模块**:
- `auth.py`: 认证和验证工具

#### client 模块
**职责**: 客户端功能实现

**network 子模块**:
- `client.py`: 网络通信和协议处理

**commands 子模块**:
- `parser.py`: 命令解析和处理

**ui 子模块** (待实现):
- `app.py`: Textual应用主类
- `widgets.py`: 自定义UI组件

## 开发流程

### 功能开发流程

1. **需求分析**
   - 明确功能需求和用户场景
   - 设计API接口和数据结构
   - 评估技术难点和风险

2. **设计阶段**
   - 更新设计文档
   - 定义模块接口
   - 设计数据库结构（如需要）

3. **编码实现**
   - 遵循代码规范
   - 编写详细注释
   - 实现单元测试

4. **测试验证**
   - 单元测试覆盖率 > 80%
   - 集成测试验证
   - 手动测试确认

5. **代码审查**
   - 自我审查代码质量
   - 同行代码审查
   - 修复发现的问题

6. **文档更新**
   - 更新API文档
   - 更新用户手册
   - 添加示例代码

### Git 工作流

#### 分支策略
- `main`: 主分支，保持稳定
- `develop`: 开发分支，集成新功能
- `feature/*`: 功能分支，开发具体功能
- `hotfix/*`: 热修复分支，紧急修复

#### 提交规范
```bash
# 创建功能分支
git checkout -b feature/user-status-management

# 开发过程中的提交
git add .
git commit -m "[开发]: 添加用户在线状态检测逻辑"

# 功能完成后合并
git checkout develop
git merge feature/user-status-management
git branch -d feature/user-status-management
```

## 代码规范详解

### 文件组织

#### 文件命名
- 模块文件: `user_manager.py`
- 类文件: `chat_room_server.py`
- 工具文件: `auth_utils.py`
- 测试文件: `test_user_manager.py`

#### 导入顺序
```python
# 1. 标准库导入
import os
import sys
import json
from typing import Dict, List, Optional

# 2. 第三方库导入
import sqlite3
from textual.app import App

# 3. 本地模块导入
from shared.constants import MessageType
from shared.exceptions import UserNotFoundError
```

### 函数设计

#### 函数命名
- 动词开头: `send_message()`, `create_user()`
- 布尔返回: `is_online()`, `has_permission()`
- 获取数据: `get_user_info()`, `fetch_messages()`

#### 函数文档
```python
def send_message(self, sender_id: int, receiver_id: int, content: str) -> bool:
    """
    发送消息给指定用户
    
    Args:
        sender_id: 发送者用户ID
        receiver_id: 接收者用户ID  
        content: 消息内容，长度不超过1000字符
        
    Returns:
        bool: 发送成功返回True，失败返回False
        
    Raises:
        UserNotFoundError: 当发送者或接收者不存在时
        PermissionDeniedError: 当发送者没有权限时
        
    Example:
        >>> manager = ChatManager()
        >>> success = manager.send_message(123, 456, "Hello!")
        >>> print(success)
        True
    """
    # 实现逻辑...
```

### 类设计

#### 类命名和结构
```python
class UserManager:
    """
    用户管理器
    
    负责用户的注册、登录、状态管理等功能。
    维护用户会话信息和在线状态。
    
    Attributes:
        db: 数据库管理器实例
        online_users: 在线用户连接映射
        user_sessions: 用户会话信息
    """
    
    def __init__(self):
        """初始化用户管理器"""
        self.db = get_db()
        self.online_users: Dict[int, socket.socket] = {}
        self.user_sessions: Dict[int, Dict] = {}
    
    def register_user(self, username: str, password: str) -> int:
        """注册新用户"""
        # 实现逻辑...
        
    def _validate_username(self, username: str) -> bool:
        """验证用户名格式（私有方法）"""
        # 实现逻辑...
```

### 异常处理

#### 异常设计原则
```python
# 1. 使用具体的异常类型
try:
    user = self.get_user_by_id(user_id)
except UserNotFoundError as e:
    logger.error(f"用户查找失败: {e}")
    return None

# 2. 提供有用的错误信息
raise UserNotFoundError(f"用户ID {user_id} 不存在")

# 3. 在适当的层级处理异常
def handle_login_request(self, request):
    try:
        user = self.authenticate_user(request.username, request.password)
        return LoginResponse(success=True, user_id=user.id)
    except AuthenticationError as e:
        return LoginResponse(success=False, error_message=str(e))
```

## 测试指南

### 测试结构

```
tests/
├── unit/                   # 单元测试
│   ├── test_user_manager.py
│   ├── test_chat_manager.py
│   └── test_database.py
├── integration/            # 集成测试
│   ├── test_client_server.py
│   └── test_full_workflow.py
├── fixtures/               # 测试数据
│   ├── sample_users.json
│   └── sample_messages.json
└── conftest.py            # pytest配置
```

### 单元测试示例

```python
import pytest
from unittest.mock import Mock, patch
from server.core.user_manager import UserManager
from shared.exceptions import UserNotFoundError

class TestUserManager:
    """用户管理器测试类"""
    
    @pytest.fixture
    def user_manager(self):
        """创建用户管理器实例"""
        return UserManager()
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库"""
        with patch('server.core.user_manager.get_db') as mock:
            yield mock.return_value
    
    def test_register_user_success(self, user_manager, mock_db):
        """测试用户注册成功"""
        # 准备测试数据
        username = "testuser"
        password = "password123"
        expected_user_id = 123
        
        # 设置mock行为
        mock_db.create_user.return_value = expected_user_id
        
        # 执行测试
        result = user_manager.register_user(username, password)
        
        # 验证结果
        assert result == expected_user_id
        mock_db.create_user.assert_called_once_with(username, mock_db.hash_password(password))
    
    def test_register_user_duplicate(self, user_manager, mock_db):
        """测试重复用户名注册"""
        # 设置mock行为
        mock_db.create_user.side_effect = UserAlreadyExistsError("用户已存在")
        
        # 执行测试并验证异常
        with pytest.raises(UserAlreadyExistsError):
            user_manager.register_user("existing_user", "password")
```

### 集成测试示例

```python
import pytest
import threading
import time
from server.main import ChatRoomServer
from client.network.client import ChatClient

class TestClientServerIntegration:
    """客户端-服务器集成测试"""
    
    @pytest.fixture(scope="class")
    def server(self):
        """启动测试服务器"""
        server = ChatRoomServer("localhost", 8889)
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        time.sleep(1)  # 等待服务器启动
        yield server
        server.stop()
    
    def test_user_registration_and_login(self, server):
        """测试用户注册和登录流程"""
        client = ChatClient("localhost", 8889)
        
        # 连接服务器
        assert client.connect()
        
        # 注册用户
        success, message = client.register("testuser", "password123")
        assert success
        
        # 登录用户
        success, message = client.login("testuser", "password123")
        assert success
        
        # 清理
        client.disconnect()
```

## 调试技巧

### 日志配置

```python
import logging
from loguru import logger

# 配置日志
logger.add("logs/server_{time}.log", rotation="1 day", level="DEBUG")
logger.add("logs/error_{time}.log", rotation="1 week", level="ERROR")

# 使用日志
logger.info("服务器启动成功")
logger.debug(f"处理消息: {message}")
logger.error(f"数据库连接失败: {error}")
```

### 调试工具

#### 1. pdb 调试器
```python
import pdb

def problematic_function():
    # 设置断点
    pdb.set_trace()
    # 调试代码...
```

#### 2. VS Code 调试配置
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Server",
            "type": "python",
            "request": "launch",
            "module": "server.main",
            "args": ["--debug"],
            "console": "integratedTerminal"
        },
        {
            "name": "Debug Client", 
            "type": "python",
            "request": "launch",
            "module": "client.main",
            "console": "integratedTerminal"
        }
    ]
}
```

### 性能分析

#### 使用 cProfile
```bash
python -m cProfile -o profile_output.prof -m server.main
python -c "import pstats; pstats.Stats('profile_output.prof').sort_stats('cumulative').print_stats(20)"
```

#### 内存使用分析
```python
import tracemalloc

# 开始跟踪
tracemalloc.start()

# 执行代码...

# 获取内存使用情况
current, peak = tracemalloc.get_traced_memory()
print(f"当前内存使用: {current / 1024 / 1024:.1f} MB")
print(f"峰值内存使用: {peak / 1024 / 1024:.1f} MB")

tracemalloc.stop()
```

## 常见问题解决

### 1. 数据库锁定问题
```python
# 使用上下文管理器确保连接正确关闭
with self.get_connection() as conn:
    cursor = conn.cursor()
    # 数据库操作...
    conn.commit()
```

### 2. Socket 连接问题
```python
# 设置 SO_REUSEADDR 选项
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 正确处理连接异常
try:
    client_socket, address = server_socket.accept()
except socket.error as e:
    logger.error(f"接受连接失败: {e}")
```

### 3. 编码问题
```python
# 统一使用 UTF-8 编码
message_bytes = message.encode('utf-8')
message_str = data.decode('utf-8')
```

### 4. 线程安全问题
```python
import threading

class ThreadSafeManager:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = {}
    
    def update_data(self, key, value):
        with self._lock:
            self._data[key] = value
```

## 贡献指南

### 代码审查清单

- [ ] 代码符合项目规范
- [ ] 添加了必要的注释和文档
- [ ] 包含单元测试且覆盖率足够
- [ ] 没有明显的性能问题
- [ ] 错误处理完善
- [ ] 日志记录适当
- [ ] 没有硬编码的配置
- [ ] 向后兼容性考虑

### 提交前检查

```bash
# 代码格式化
black .

# 代码检查
flake8 .

# 类型检查
mypy server/ client/ shared/

# 运行测试
pytest --cov=server --cov=client --cov=shared

# 检查测试覆盖率
coverage report --show-missing
```

这个开发指南为项目贡献者提供了详细的开发环境搭建、代码规范、测试方法和调试技巧，确保代码质量和开发效率。
