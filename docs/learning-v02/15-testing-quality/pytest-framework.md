# Pytest测试框架

## 🎯 学习目标

通过本章学习，您将能够：
- 理解现代Python测试框架的设计理念和最佳实践
- 掌握pytest框架的核心特性和高级用法
- 学会为Chat-Room项目设计完整的测试体系
- 实现测试驱动开发（TDD）的工作流程

## 🧪 Pytest框架概览

### 测试框架架构

```mermaid
graph TB
    subgraph "Pytest测试框架"
        A[测试发现<br/>Test Discovery] --> B[测试收集<br/>Test Collection]
        B --> C[测试执行<br/>Test Execution]
        C --> D[结果报告<br/>Result Reporting]
        
        E[夹具系统<br/>Fixture System] --> C
        F[插件系统<br/>Plugin System] --> A
        G[断言系统<br/>Assertion System] --> C
        H[参数化<br/>Parametrization] --> B
    end
    
    subgraph "测试类型"
        I[单元测试<br/>Unit Tests]
        J[集成测试<br/>Integration Tests]
        K[功能测试<br/>Functional Tests]
        L[性能测试<br/>Performance Tests]
    end
    
    C --> I
    C --> J
    C --> K
    C --> L
    
    style A fill:#e8f5e8
    style D fill:#f8d7da
```

### 测试执行流程

```mermaid
sequenceDiagram
    participant Dev as 开发者
    participant Pytest as Pytest框架
    participant Fixture as 夹具系统
    participant Test as 测试用例
    participant Report as 报告系统
    
    Note over Dev,Report: Pytest测试执行流程
    
    Dev->>Pytest: 运行测试命令
    Pytest->>Pytest: 发现测试文件
    Pytest->>Pytest: 收集测试用例
    
    loop 每个测试用例
        Pytest->>Fixture: 设置测试夹具
        Fixture->>Test: 提供测试数据
        Test->>Test: 执行测试逻辑
        Test->>Pytest: 返回测试结果
        Pytest->>Fixture: 清理测试夹具
    end
    
    Pytest->>Report: 生成测试报告
    Report->>Dev: 显示测试结果
    
    Note over Dev,Report: 测试失败处理
    
    alt 测试失败
        Test->>Pytest: 抛出断言错误
        Pytest->>Report: 记录失败信息
        Report->>Dev: 显示错误详情
    end
```

## 🔧 Pytest框架实现

### Chat-Room测试框架搭建

```python
# tests/conftest.py - Pytest配置和夹具
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, patch
import json
import sqlite3
from datetime import datetime

# 导入Chat-Room模块（假设的导入路径）
# from server.core.server import ChatServer
# from client.core.client import ChatClient
# from shared.models import User, Message, Group
# from shared.config import Config

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环夹具"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir():
    """临时目录夹具"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)

@pytest.fixture
def test_config(temp_dir):
    """测试配置夹具"""
    config_data = {
        "server": {
            "host": "127.0.0.1",
            "port": 0,  # 使用随机端口
            "max_connections": 10
        },
        "database": {
            "url": f"sqlite:///{temp_dir}/test.db",
            "echo": False
        },
        "logging": {
            "level": "DEBUG",
            "file": str(temp_dir / "test.log")
        },
        "ai": {
            "enabled": False,  # 测试时禁用AI
            "api_key": "test_key"
        }
    }
    
    config_file = temp_dir / "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    
    # 模拟配置类
    class TestConfig:
        def __init__(self, data):
            for key, value in data.items():
                if isinstance(value, dict):
                    setattr(self, key, TestConfig(value))
                else:
                    setattr(self, key, value)
    
    return TestConfig(config_data)

@pytest.fixture
async def test_database(test_config):
    """测试数据库夹具"""
    # 创建内存数据库
    db_path = ":memory:"
    conn = sqlite3.connect(db_path)
    
    # 创建测试表
    conn.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        CREATE TABLE groups (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (created_by) REFERENCES users (id)
        );
        
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            group_id INTEGER,
            message_type TEXT DEFAULT 'text',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (group_id) REFERENCES groups (id)
        );
        
        CREATE TABLE group_members (
            group_id INTEGER,
            user_id INTEGER,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            role TEXT DEFAULT 'member',
            PRIMARY KEY (group_id, user_id),
            FOREIGN KEY (group_id) REFERENCES groups (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    
    yield conn
    conn.close()

@pytest.fixture
def sample_users():
    """示例用户数据夹具"""
    return [
        {
            "id": 1,
            "username": "alice",
            "email": "alice@example.com",
            "password_hash": "hashed_password_1",
            "is_active": True
        },
        {
            "id": 2,
            "username": "bob",
            "email": "bob@example.com",
            "password_hash": "hashed_password_2",
            "is_active": True
        },
        {
            "id": 3,
            "username": "charlie",
            "email": "charlie@example.com",
            "password_hash": "hashed_password_3",
            "is_active": False
        }
    ]

@pytest.fixture
def sample_groups():
    """示例群组数据夹具"""
    return [
        {
            "id": 1,
            "name": "技术讨论",
            "description": "技术相关话题讨论",
            "created_by": 1,
            "is_active": True
        },
        {
            "id": 2,
            "name": "随便聊聊",
            "description": "日常闲聊",
            "created_by": 2,
            "is_active": True
        }
    ]

@pytest.fixture
def sample_messages():
    """示例消息数据夹具"""
    return [
        {
            "id": 1,
            "content": "大家好！",
            "user_id": 1,
            "group_id": 1,
            "message_type": "text"
        },
        {
            "id": 2,
            "content": "Hello everyone!",
            "user_id": 2,
            "group_id": 1,
            "message_type": "text"
        },
        {
            "id": 3,
            "content": "今天天气不错",
            "user_id": 1,
            "group_id": 2,
            "message_type": "text"
        }
    ]

@pytest.fixture
async def populated_database(test_database, sample_users, sample_groups, sample_messages):
    """填充数据的测试数据库夹具"""
    conn = test_database
    
    # 插入用户数据
    for user in sample_users:
        conn.execute(
            "INSERT INTO users (id, username, email, password_hash, is_active) VALUES (?, ?, ?, ?, ?)",
            (user["id"], user["username"], user["email"], user["password_hash"], user["is_active"])
        )
    
    # 插入群组数据
    for group in sample_groups:
        conn.execute(
            "INSERT INTO groups (id, name, description, created_by, is_active) VALUES (?, ?, ?, ?, ?)",
            (group["id"], group["name"], group["description"], group["created_by"], group["is_active"])
        )
    
    # 插入消息数据
    for message in sample_messages:
        conn.execute(
            "INSERT INTO messages (id, content, user_id, group_id, message_type) VALUES (?, ?, ?, ?, ?)",
            (message["id"], message["content"], message["user_id"], message["group_id"], message["message_type"])
        )
    
    # 插入群组成员关系
    group_members = [
        (1, 1, "admin"),  # alice是技术讨论群管理员
        (1, 2, "member"), # bob是技术讨论群成员
        (2, 1, "member"), # alice是随便聊聊群成员
        (2, 2, "admin"),  # bob是随便聊聊群管理员
    ]
    
    for group_id, user_id, role in group_members:
        conn.execute(
            "INSERT INTO group_members (group_id, user_id, role) VALUES (?, ?, ?)",
            (group_id, user_id, role)
        )
    
    conn.commit()
    yield conn

@pytest.fixture
def mock_websocket():
    """模拟WebSocket连接夹具"""
    mock_ws = AsyncMock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.closed = False
    
    return mock_ws

@pytest.fixture
def mock_chat_server(test_config):
    """模拟聊天服务器夹具"""
    mock_server = Mock()
    mock_server.config = test_config
    mock_server.clients = {}
    mock_server.groups = {}
    mock_server.running = False
    
    # 模拟异步方法
    mock_server.start = AsyncMock()
    mock_server.stop = AsyncMock()
    mock_server.handle_client = AsyncMock()
    mock_server.broadcast_message = AsyncMock()
    mock_server.add_client = AsyncMock()
    mock_server.remove_client = AsyncMock()
    
    return mock_server

@pytest.fixture
def mock_chat_client(test_config):
    """模拟聊天客户端夹具"""
    mock_client = Mock()
    mock_client.config = test_config
    mock_client.connected = False
    mock_client.user_id = None
    mock_client.username = None
    
    # 模拟异步方法
    mock_client.connect = AsyncMock()
    mock_client.disconnect = AsyncMock()
    mock_client.send_message = AsyncMock()
    mock_client.login = AsyncMock()
    mock_client.join_group = AsyncMock()
    mock_client.leave_group = AsyncMock()
    
    return mock_client

class MockAIService:
    """模拟AI服务"""
    
    def __init__(self):
        self.enabled = False
        self.responses = {
            "hello": "Hello! How can I help you?",
            "help": "I'm here to assist you with your questions.",
            "default": "I understand your message."
        }
    
    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """生成AI响应"""
        message_lower = message.lower()
        
        for keyword, response in self.responses.items():
            if keyword in message_lower:
                return response
        
        return self.responses["default"]
    
    def set_response(self, keyword: str, response: str):
        """设置特定关键词的响应"""
        self.responses[keyword] = response

@pytest.fixture
def mock_ai_service():
    """模拟AI服务夹具"""
    return MockAIService()

# 测试标记定义
pytest_plugins = []

def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "functional: 功能测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "network: 需要网络的测试")
    config.addinivalue_line("markers", "database: 需要数据库的测试")

def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    for item in items:
        # 为所有异步测试添加asyncio标记
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
        
        # 根据测试文件路径添加标记
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "functional" in str(item.fspath):
            item.add_marker(pytest.mark.functional)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
```

## 🛠️ Pytest高级特性

### 参数化测试

```python
import pytest

@pytest.mark.parametrize("username,email,password,expected", [
    ("validuser", "valid@example.com", "validpass123", True),
    ("ab", "valid@example.com", "validpass123", False),  # 用户名太短
    ("validuser", "invalid-email", "validpass123", False),  # 邮箱无效
    ("validuser", "valid@example.com", "123", False),  # 密码太短
])
def test_user_validation(username, email, password, expected):
    """参数化测试用户验证"""
    result = validate_user(username, email, password)
    assert result == expected
```

### 夹具作用域

```python
@pytest.fixture(scope="session")
def database_connection():
    """会话级别的数据库连接"""
    conn = create_database_connection()
    yield conn
    conn.close()

@pytest.fixture(scope="module")
def test_data():
    """模块级别的测试数据"""
    return load_test_data()

@pytest.fixture(scope="function")
def clean_database(database_connection):
    """函数级别的数据库清理"""
    yield
    clean_all_tables(database_connection)
```

### 自定义标记

```python
# pytest.ini
[tool:pytest]
markers =
    unit: 单元测试
    integration: 集成测试
    slow: 慢速测试
    network: 需要网络连接的测试

# 使用标记
@pytest.mark.unit
def test_user_creation():
    pass

@pytest.mark.slow
@pytest.mark.network
def test_api_integration():
    pass

# 运行特定标记的测试
# pytest -m unit
# pytest -m "not slow"
# pytest -m "unit and not network"
```

## 📊 测试报告和覆盖率

### 生成测试报告

```bash
# HTML报告
pytest --html=reports/report.html --self-contained-html

# JUnit XML报告
pytest --junitxml=reports/junit.xml

# 覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term

# 详细输出
pytest -v --tb=short
```

### 覆盖率配置

```ini
# .coveragerc
[run]
source = src/
omit = 
    */tests/*
    */venv/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError

[html]
directory = htmlcov
```

## 📋 学习检查清单

完成本节学习后，请确认您能够：

- [ ] 理解pytest框架的核心概念
- [ ] 编写和组织测试夹具
- [ ] 使用参数化测试
- [ ] 配置测试标记和过滤
- [ ] 生成测试报告和覆盖率分析
- [ ] 使用Mock和AsyncMock进行测试
- [ ] 配置pytest插件和扩展
- [ ] 组织大型项目的测试结构

## 🚀 下一步

掌握pytest框架后，请继续学习：
- [单元测试实践](unit-testing.md) - 具体的单元测试编写
- [集成测试实践](integration-testing.md) - 集成测试方法
- [TDD实践](tdd-practices.md) - 测试驱动开发

---

**Pytest是Python生态中最强大的测试框架，掌握它将大大提高你的测试效率！** 🧪
