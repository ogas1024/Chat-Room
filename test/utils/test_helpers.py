"""
测试辅助工具
提供创建测试服务器和客户端的便捷方法
"""

import os
import tempfile
import threading
from typing import Optional

from server.core.server import ChatRoomServer
from client.core.client import ChatClient
from server.database.connection import DatabaseConnection
from shared.constants import DEFAULT_HOST, DEFAULT_PORT


def create_test_database() -> str:
    """创建测试数据库"""
    # 创建临时数据库文件
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_chatroom.db")
    
    # 设置测试数据库路径
    DatabaseConnection.set_database_path(db_path)
    
    # 初始化数据库
    db_manager = DatabaseConnection.get_instance()
    
    return db_path


def create_test_server(host: str = DEFAULT_HOST, port: int = None) -> ChatRoomServer:
    """创建测试服务器"""
    if port is None:
        # 使用动态端口避免冲突
        import socket
        sock = socket.socket()
        sock.bind(('', 0))
        port = sock.getsockname()[1]
        sock.close()

    # 创建测试数据库
    create_test_database()

    # 创建服务器实例
    server = ChatRoomServer(host, port)

    return server


def create_test_client(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> ChatClient:
    """创建测试客户端"""
    client = ChatClient(host, port)
    return client


class TestServerManager:
    """测试服务器管理器"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = None):
        self.host = host
        self.port = port
        self.server: Optional[ChatRoomServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
    
    def start(self) -> int:
        """启动测试服务器，返回实际端口号"""
        if self.running:
            return self.port
        
        self.server = create_test_server(self.host, self.port)
        self.port = self.server.port  # 获取实际分配的端口
        
        self.server_thread = threading.Thread(
            target=self.server.start,
            daemon=True
        )
        self.server_thread.start()
        
        # 等待服务器启动
        import time
        time.sleep(0.5)
        
        self.running = True
        return self.port
    
    def stop(self):
        """停止测试服务器"""
        if not self.running:
            return
        
        if self.server:
            self.server.stop()
        
        self.running = False
        self.server = None
        self.server_thread = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop()


class TestClientManager:
    """测试客户端管理器"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.clients = []
    
    def create_client(self) -> ChatClient:
        """创建新的测试客户端"""
        client = create_test_client(self.host, self.port)
        self.clients.append(client)
        return client
    
    def cleanup(self):
        """清理所有客户端"""
        for client in self.clients:
            if client.is_connected():
                client.disconnect()
        self.clients.clear()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()


def setup_test_environment():
    """设置测试环境"""
    # 创建测试数据库
    create_test_database()
    
    # 可以在这里添加其他测试环境设置
    pass


def teardown_test_environment():
    """清理测试环境"""
    # 关闭数据库连接
    DatabaseConnection.close()
    
    # 可以在这里添加其他清理逻辑
    pass


def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1) -> bool:
    """等待条件满足"""
    import time
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    
    return False


def assert_message_received(collector, expected_content: str, timeout: float = 2.0) -> bool:
    """断言消息已接收"""
    def check_message():
        messages = collector.get_messages()
        return any(msg['content'] == expected_content for msg in messages)
    
    return wait_for_condition(check_message, timeout)


def assert_no_message_received(collector, unexpected_content: str, wait_time: float = 1.0) -> bool:
    """断言消息未接收"""
    import time
    time.sleep(wait_time)  # 等待一段时间确保消息不会到达
    
    messages = collector.get_messages()
    return not any(msg['content'] == unexpected_content for msg in messages)
