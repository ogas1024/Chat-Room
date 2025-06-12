"""
消息隔离功能集成测试
验证不同聊天组之间的消息完全隔离
"""

import pytest
import time
import threading
from typing import List, Dict, Any

from server.core.server import ChatRoomServer
from client.core.client import ChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT
from test.utils.test_helpers import create_test_server, create_test_client


class MessageCollector:
    """消息收集器，用于收集客户端接收到的消息"""
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def collect_message(self, message):
        """收集消息"""
        with self.lock:
            self.messages.append({
                'sender_username': getattr(message, 'sender_username', ''),
                'content': getattr(message, 'content', ''),
                'chat_group_id': getattr(message, 'chat_group_id', None),
                'message_type': getattr(message, 'message_type', ''),
                'timestamp': time.time()
            })
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """获取收集到的消息"""
        with self.lock:
            return self.messages.copy()
    
    def clear(self):
        """清空消息"""
        with self.lock:
            self.messages.clear()


class TestMessageIsolation:
    """消息隔离测试类"""
    
    @pytest.fixture(scope="function")
    def test_server(self):
        """创建测试服务器"""
        server = create_test_server()
        server_thread = threading.Thread(target=server.start, daemon=True)
        server_thread.start()
        time.sleep(0.5)  # 等待服务器启动
        yield server
        server.stop()
    
    @pytest.fixture(scope="function")
    def test_clients(self, test_server):
        """创建测试客户端"""
        clients = []
        collectors = []
        
        # 创建两个客户端
        for i in range(2):
            client = create_test_client()
            collector = MessageCollector()
            
            # 设置消息收集器
            from shared.constants import MessageType
            client.network_client.set_message_handler(
                MessageType.CHAT_MESSAGE, collector.collect_message
            )
            client.network_client.set_message_handler(
                MessageType.CHAT_HISTORY, collector.collect_message
            )
            
            clients.append(client)
            collectors.append(collector)
        
        yield clients, collectors
        
        # 清理
        for client in clients:
            if client.is_connected():
                client.disconnect()
    
    def test_message_isolation_between_groups(self, test_clients):
        """测试不同聊天组之间的消息隔离"""
        clients, collectors = test_clients
        client1, client2 = clients
        collector1, collector2 = collectors
        
        # 连接客户端
        assert client1.connect()
        assert client2.connect()
        
        # 注册和登录用户
        success, _ = client1.register("test_user1", "password123")
        assert success
        success, _ = client1.login("test_user1", "password123")
        assert success
        
        success, _ = client2.register("test_user2", "password123")
        assert success
        success, _ = client2.login("test_user2", "password123")
        assert success
        
        # 创建两个不同的聊天组
        success, _ = client1.create_chat_group("group1")
        assert success
        success, _ = client2.create_chat_group("group2")
        assert success
        
        # 用户1进入group1，用户2进入group2
        success, _ = client1.enter_chat_group("group1")
        assert success
        success, _ = client2.enter_chat_group("group2")
        assert success
        
        time.sleep(0.5)  # 等待进入聊天组完成
        
        # 清空消息收集器
        collector1.clear()
        collector2.clear()
        
        # 用户1在group1发送消息
        success = client1.send_chat_message("Hello from group1", client1.current_chat_group['id'])
        assert success
        
        # 用户2在group2发送消息
        success = client2.send_chat_message("Hello from group2", client2.current_chat_group['id'])
        assert success
        
        time.sleep(1)  # 等待消息传播
        
        # 验证消息隔离
        messages1 = collector1.get_messages()
        messages2 = collector2.get_messages()
        
        # 用户1应该只能看到group1的消息
        group1_messages = [msg for msg in messages1 if msg['content'] == "Hello from group1"]
        group2_messages_in_client1 = [msg for msg in messages1 if msg['content'] == "Hello from group2"]
        
        assert len(group1_messages) == 1, "用户1应该能看到自己在group1发送的消息"
        assert len(group2_messages_in_client1) == 0, "用户1不应该看到group2的消息"
        
        # 用户2应该只能看到group2的消息
        group2_messages = [msg for msg in messages2 if msg['content'] == "Hello from group2"]
        group1_messages_in_client2 = [msg for msg in messages2 if msg['content'] == "Hello from group1"]
        
        assert len(group2_messages) == 1, "用户2应该能看到自己在group2发送的消息"
        assert len(group1_messages_in_client2) == 0, "用户2不应该看到group1的消息"
    
    def test_message_isolation_with_group_switching(self, test_clients):
        """测试用户切换聊天组时的消息隔离"""
        clients, collectors = test_clients
        client1, client2 = clients
        collector1, collector2 = collectors
        
        # 连接和登录
        assert client1.connect()
        assert client2.connect()
        
        success, _ = client1.register("switch_user1", "password123")
        assert success
        success, _ = client1.login("switch_user1", "password123")
        assert success
        
        success, _ = client2.register("switch_user2", "password123")
        assert success
        success, _ = client2.login("switch_user2", "password123")
        assert success
        
        # 创建两个聊天组
        success, _ = client1.create_chat_group("groupA")
        assert success
        success, _ = client1.create_chat_group("groupB")
        assert success
        
        # 用户2加入两个聊天组
        success, _ = client2.join_chat_group("groupA")
        assert success
        success, _ = client2.join_chat_group("groupB")
        assert success
        
        # 用户1进入groupA，发送消息
        success, _ = client1.enter_chat_group("groupA")
        assert success
        time.sleep(0.5)
        
        collector1.clear()
        collector2.clear()
        
        success = client1.send_chat_message("Message in groupA", client1.current_chat_group['id'])
        assert success
        time.sleep(0.5)
        
        # 用户1切换到groupB，发送消息
        success, _ = client1.enter_chat_group("groupB")
        assert success
        time.sleep(0.5)
        
        success = client1.send_chat_message("Message in groupB", client1.current_chat_group['id'])
        assert success
        time.sleep(0.5)
        
        # 用户2进入groupA，应该只看到groupA的消息
        success, _ = client2.enter_chat_group("groupA")
        assert success
        time.sleep(1)  # 等待历史消息加载
        
        messages2 = collector2.get_messages()
        groupA_messages = [msg for msg in messages2 if msg['content'] == "Message in groupA"]
        groupB_messages = [msg for msg in messages2 if msg['content'] == "Message in groupB"]
        
        assert len(groupA_messages) >= 1, "用户2在groupA应该能看到groupA的消息"
        assert len(groupB_messages) == 0, "用户2在groupA不应该看到groupB的消息"
        
        # 用户2切换到groupB，应该只看到groupB的消息
        collector2.clear()
        success, _ = client2.enter_chat_group("groupB")
        assert success
        time.sleep(1)  # 等待历史消息加载
        
        messages2 = collector2.get_messages()
        groupA_messages = [msg for msg in messages2 if msg['content'] == "Message in groupA"]
        groupB_messages = [msg for msg in messages2 if msg['content'] == "Message in groupB"]
        
        assert len(groupB_messages) >= 1, "用户2在groupB应该能看到groupB的消息"
        assert len(groupA_messages) == 0, "用户2在groupB不应该看到groupA的消息"


def run_message_isolation_tests():
    """运行消息隔离测试"""
    print("开始运行消息隔离测试...")
    
    # 运行测试
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"  # 显示print输出
    ])
    
    if exit_code == 0:
        print("✅ 所有消息隔离测试通过！")
    else:
        print("❌ 部分测试失败，请检查消息隔离逻辑")
    
    return exit_code


if __name__ == "__main__":
    run_message_isolation_tests()
