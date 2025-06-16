"""
pytest配置文件
定义全局测试夹具和配置
"""

import os
import sys
import pytest
import tempfile
import shutil
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.constants import DEFAULT_HOST, DEFAULT_PORT
from shared.logger import get_logger
from server.database.models import DatabaseManager


@pytest.fixture(scope="session")
def project_root_path():
    """项目根目录路径夹具"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root_path):
    """测试数据目录夹具"""
    test_dir = project_root_path / "test" / "test_data"
    test_dir.mkdir(exist_ok=True)
    return test_dir


@pytest.fixture
def temp_dir():
    """临时目录夹具"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_db_path(temp_dir):
    """测试数据库路径夹具"""
    return temp_dir / "test_chatroom.db"


@pytest.fixture
def db_manager(test_db_path):
    """数据库管理器夹具"""
    manager = DatabaseManager(str(test_db_path))
    manager.init_database()
    yield manager
    # 清理
    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture
def sample_users():
    """示例用户数据夹具"""
    return [
        {"username": "alice", "password": "password123"},
        {"username": "bob", "password": "password456"},
        {"username": "charlie", "password": "password789"},
    ]


@pytest.fixture
def sample_chat_groups():
    """示例聊天组数据夹具"""
    return [
        {"name": "public", "is_private_chat": False},
        {"name": "test_group", "is_private_chat": False},
        {"name": "private_alice_bob", "is_private_chat": True},
    ]


@pytest.fixture
def sample_messages():
    """示例消息数据夹具"""
    return [
        {
            "sender_username": "alice",
            "chat_group_name": "public",
            "content": "Hello everyone!",
            "message_type": "chat"
        },
        {
            "sender_username": "bob",
            "chat_group_name": "public", 
            "content": "Hi Alice!",
            "message_type": "chat"
        },
        {
            "sender_username": "charlie",
            "chat_group_name": "test_group",
            "content": "Test message",
            "message_type": "chat"
        },
    ]


@pytest.fixture
def test_file_content():
    """测试文件内容夹具"""
    return "这是一个测试文件\nTest file content\n测试中文内容\n"


@pytest.fixture
def test_file(temp_dir, test_file_content):
    """测试文件夹具"""
    file_path = temp_dir / "test_file.txt"
    file_path.write_text(test_file_content, encoding='utf-8')
    return file_path


@pytest.fixture
def mock_socket():
    """Mock socket夹具"""
    with patch('socket.socket') as mock_sock:
        mock_instance = Mock()
        mock_sock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_zhipu_client():
    """Mock智谱AI客户端夹具"""
    with patch('server.ai.zhipu_client.ZhipuClient') as mock_client:
        mock_instance = Mock()
        mock_instance.test_connection.return_value = True
        mock_instance.chat_completion.return_value = "这是AI的回复"
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def server_config():
    """服务器配置夹具"""
    return {
        "server": {
            "host": DEFAULT_HOST,
            "port": DEFAULT_PORT,
            "max_connections": 10,
            "buffer_size": 4096,
        },
        "database": {
            "path": ":memory:",
            "backup_enabled": False,
        },
        "file_storage": {
            "path": "/tmp/test_files",
            "max_file_size": 1024 * 1024,  # 1MB
            "chunk_size": 8192,
        },
        "ai": {
            "enabled": True,
            "api_key": "test_api_key",
            "model": "glm-4-flash",
        }
    }


@pytest.fixture
def client_config():
    """客户端配置夹具"""
    return {
        "connection": {
            "host": DEFAULT_HOST,
            "port": DEFAULT_PORT,
            "timeout": 10,
            "retry_attempts": 3,
        },
        "ui": {
            "mode": "simple",
            "theme": "default",
            "auto_scroll": True,
        },
        "file_transfer": {
            "download_path": "/tmp/test_downloads",
            "chunk_size": 8192,
        }
    }


@pytest.fixture(autouse=True)
def setup_logging():
    """自动设置测试日志"""
    # 在测试期间禁用日志输出到控制台
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)


@pytest.fixture
def event_loop():
    """事件循环夹具（用于异步测试）"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# 测试标记定义
def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "functional: 功能测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "network: 需要网络的测试")
    config.addinivalue_line("markers", "ai: AI相关测试")


# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试收集项"""
    for item in items:
        # 为不同目录的测试添加标记
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "functional" in str(item.fspath):
            item.add_marker(pytest.mark.functional)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
