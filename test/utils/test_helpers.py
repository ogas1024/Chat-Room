"""
测试辅助工具类
提供测试中常用的工具函数和类
"""

import json
import time
import socket
import threading
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, MagicMock
from pathlib import Path

from shared.constants import MessageType, DEFAULT_HOST, DEFAULT_PORT
from shared.messages import BaseMessage, LoginRequest, ChatMessage


class MockServer:
    """模拟服务器类，用于测试客户端功能"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化模拟服务器"""
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.clients = []
        self.message_handlers = {}
        self.received_messages = []
        
    def start(self):
        """启动模拟服务器"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.running = True
        
        # 在单独线程中运行服务器
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # 等待服务器启动
        time.sleep(0.1)
    
    def stop(self):
        """停止模拟服务器"""
        self.running = False
        if self.socket:
            self.socket.close()
        for client in self.clients:
            client.close()
        self.clients.clear()
    
    def _run_server(self):
        """运行服务器主循环"""
        while self.running:
            try:
                client_socket, addr = self.socket.accept()
                self.clients.append(client_socket)
                
                # 为每个客户端创建处理线程
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except OSError:
                break
    
    def _handle_client(self, client_socket):
        """处理客户端连接"""
        while self.running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                # 解析消息
                message_str = data.decode('utf-8')
                self.received_messages.append(message_str)
                
                # 处理消息
                self._process_message(client_socket, message_str)
                
            except (ConnectionResetError, OSError):
                break
        
        client_socket.close()
        if client_socket in self.clients:
            self.clients.remove(client_socket)
    
    def _process_message(self, client_socket, message_str: str):
        """处理接收到的消息"""
        try:
            message_data = json.loads(message_str)
            message_type = message_data.get('type')
            
            # 调用对应的消息处理器
            if message_type in self.message_handlers:
                response = self.message_handlers[message_type](message_data)
                if response:
                    self.send_to_client(client_socket, response)
                    
        except json.JSONDecodeError:
            pass
    
    def send_to_client(self, client_socket, message: str):
        """向客户端发送消息"""
        try:
            client_socket.send(message.encode('utf-8'))
        except OSError:
            pass
    
    def register_handler(self, message_type: str, handler):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    def get_received_messages(self) -> List[str]:
        """获取接收到的消息列表"""
        return self.received_messages.copy()
    
    def clear_received_messages(self):
        """清空接收到的消息"""
        self.received_messages.clear()


class MockClient:
    """模拟客户端类，用于测试服务器功能"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化模拟客户端"""
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.received_messages = []
        self.receive_thread = None
    
    def connect(self) -> bool:
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self._receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            return True
        except Exception:
            return False
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.socket:
            self.socket.close()
    
    def send_message(self, message: str) -> bool:
        """发送消息"""
        if not self.connected or not self.socket:
            return False
        
        try:
            self.socket.send(message.encode('utf-8'))
            return True
        except Exception:
            return False
    
    def _receive_messages(self):
        """接收消息线程"""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if data:
                    message = data.decode('utf-8')
                    self.received_messages.append(message)
            except Exception:
                break
    
    def get_received_messages(self) -> List[str]:
        """获取接收到的消息"""
        return self.received_messages.copy()
    
    def clear_received_messages(self):
        """清空接收到的消息"""
        self.received_messages.clear()


class MessageBuilder:
    """消息构建器，用于创建测试消息"""
    
    @staticmethod
    def create_login_request(username: str, password: str) -> str:
        """创建登录请求消息"""
        message = {
            "type": MessageType.LOGIN_REQUEST.value,
            "data": {
                "username": username,
                "password": password
            }
        }
        return json.dumps(message, ensure_ascii=False)
    
    @staticmethod
    def create_login_response(success: bool, user_id: int = None, 
                            username: str = None, error_message: str = None) -> str:
        """创建登录响应消息"""
        data = {"success": success}
        if success and user_id and username:
            data.update({"user_id": user_id, "username": username})
        if not success and error_message:
            data["error_message"] = error_message
            
        message = {
            "type": MessageType.LOGIN_RESPONSE.value,
            "data": data
        }
        return json.dumps(message, ensure_ascii=False)
    
    @staticmethod
    def create_chat_message(sender_id: int, sender_username: str,
                          chat_group_id: int, content: str) -> str:
        """创建聊天消息"""
        message = {
            "type": MessageType.CHAT_MESSAGE.value,
            "data": {
                "sender_id": sender_id,
                "sender_username": sender_username,
                "chat_group_id": chat_group_id,
                "content": content,
                "timestamp": time.time()
            }
        }
        return json.dumps(message, ensure_ascii=False)


class DatabaseTestHelper:
    """数据库测试辅助类"""
    
    @staticmethod
    def create_test_user(db_manager, username: str, password: str) -> int:
        """创建测试用户"""
        return db_manager.create_user(username, password)
    
    @staticmethod
    def create_test_chat_group(db_manager, name: str, is_private: bool = False) -> int:
        """创建测试聊天组"""
        return db_manager.create_chat_group(name, is_private)
    
    @staticmethod
    def add_user_to_chat(db_manager, user_id: int, chat_group_id: int):
        """将用户添加到聊天组"""
        db_manager.add_user_to_chat_group(user_id, chat_group_id)
    
    @staticmethod
    def create_test_message(db_manager, sender_id: int, chat_group_id: int, 
                          content: str) -> int:
        """创建测试消息"""
        return db_manager.save_message(sender_id, chat_group_id, content)


class FileTestHelper:
    """文件测试辅助类"""
    
    @staticmethod
    def create_test_file(path: Path, content: str = "测试文件内容") -> Path:
        """创建测试文件"""
        path.write_text(content, encoding='utf-8')
        return path
    
    @staticmethod
    def create_binary_test_file(path: Path, size: int = 1024) -> Path:
        """创建二进制测试文件"""
        with open(path, 'wb') as f:
            f.write(b'0' * size)
        return path
    
    @staticmethod
    def verify_file_content(path: Path, expected_content: str) -> bool:
        """验证文件内容"""
        try:
            actual_content = path.read_text(encoding='utf-8')
            return actual_content == expected_content
        except Exception:
            return False


def wait_for_condition(condition_func, timeout: float = 5.0, 
                      interval: float = 0.1) -> bool:
    """等待条件满足"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_func():
            return True
        time.sleep(interval)
    return False


def assert_message_received(messages: List[str], expected_type: str, 
                          timeout: float = 5.0) -> Optional[Dict[str, Any]]:
    """断言接收到指定类型的消息"""
    def check_message():
        for msg in messages:
            try:
                data = json.loads(msg)
                if data.get('type') == expected_type:
                    return data
            except json.JSONDecodeError:
                continue
        return None
    
    if wait_for_condition(lambda: check_message() is not None, timeout):
        return check_message()
    return None
