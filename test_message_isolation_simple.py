#!/usr/bin/env python3
"""
简单的消息隔离测试脚本
验证重构后的消息隔离功能是否正常工作
"""

import sys
import os
import time
import threading
from typing import List, Dict

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from server.core.server import ChatRoomServer
from client.core.client import ChatClient
from shared.constants import DEFAULT_HOST


class MessageCollector:
    """消息收集器"""
    
    def __init__(self, name: str):
        self.name = name
        self.messages: List[Dict] = []
        self.lock = threading.Lock()
    
    def collect_message(self, message):
        """收集消息"""
        with self.lock:
            msg_data = {
                'sender': getattr(message, 'sender_username', ''),
                'content': getattr(message, 'content', ''),
                'group_id': getattr(message, 'chat_group_id', None),
                'type': getattr(message, 'message_type', ''),
                'time': time.time()
            }
            self.messages.append(msg_data)
            print(f"[{self.name}] 收到消息: {msg_data['sender']}: {msg_data['content']}")
    
    def get_messages_with_content(self, content: str) -> List[Dict]:
        """获取包含特定内容的消息"""
        with self.lock:
            return [msg for msg in self.messages if content in msg['content']]
    
    def clear(self):
        """清空消息"""
        with self.lock:
            self.messages.clear()


def test_message_isolation():
    """测试消息隔离功能"""
    print("🚀 开始测试消息隔离功能...")
    
    # 启动测试服务器
    print("📡 启动测试服务器...")
    server = ChatRoomServer(DEFAULT_HOST, 8889)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(2)  # 等待服务器启动
    
    try:
        # 创建两个客户端
        print("👥 创建测试客户端...")
        client1 = ChatClient(DEFAULT_HOST, 8889)
        client2 = ChatClient(DEFAULT_HOST, 8889)
        
        # 创建消息收集器
        collector1 = MessageCollector("Client1")
        collector2 = MessageCollector("Client2")
        
        # 设置消息处理器
        from shared.constants import MessageType
        client1.network_client.set_message_handler(MessageType.CHAT_MESSAGE, collector1.collect_message)
        client1.network_client.set_message_handler(MessageType.CHAT_HISTORY, collector1.collect_message)
        client2.network_client.set_message_handler(MessageType.CHAT_MESSAGE, collector2.collect_message)
        client2.network_client.set_message_handler(MessageType.CHAT_HISTORY, collector2.collect_message)
        
        # 连接客户端
        print("🔗 连接客户端...")
        assert client1.connect(), "客户端1连接失败"
        assert client2.connect(), "客户端2连接失败"
        
        # 注册和登录用户（使用随机用户名避免冲突）
        import random
        user1_name = f"testuser1_{random.randint(1000, 9999)}"
        user2_name = f"testuser2_{random.randint(1000, 9999)}"

        print("👤 注册和登录用户...")
        success, msg = client1.register(user1_name, "password123")
        assert success, f"用户1注册失败: {msg}"

        success, msg = client1.login(user1_name, "password123")
        assert success, f"用户1登录失败: {msg}"

        success, msg = client2.register(user2_name, "password123")
        assert success, f"用户2注册失败: {msg}"

        success, msg = client2.login(user2_name, "password123")
        assert success, f"用户2登录失败: {msg}"
        
        time.sleep(1)
        
        # 创建两个不同的聊天组（使用随机名称避免冲突）
        group1_name = f"group1_{random.randint(1000, 9999)}"
        group2_name = f"group2_{random.randint(1000, 9999)}"

        print("💬 创建聊天组...")
        success, msg = client1.create_chat_group(group1_name)
        assert success, f"创建{group1_name}失败: {msg}"

        success, msg = client2.create_chat_group(group2_name)
        assert success, f"创建{group2_name}失败: {msg}"
        
        time.sleep(1)
        
        # 用户1进入group1，用户2进入group2
        print("🚪 进入不同聊天组...")
        success, msg = client1.enter_chat_group(group1_name)
        assert success, f"进入{group1_name}失败: {msg}"

        success, msg = client2.enter_chat_group(group2_name)
        assert success, f"进入{group2_name}失败: {msg}"
        
        time.sleep(2)  # 等待进入聊天组和历史消息加载完成
        
        # 清空消息收集器
        collector1.clear()
        collector2.clear()
        
        # 测试消息隔离
        print("📨 测试消息隔离...")
        
        # 用户1在group1发送消息
        success = client1.send_chat_message("Hello from group1", client1.current_chat_group['id'])
        assert success, "用户1发送消息失败"
        
        # 用户2在group2发送消息
        success = client2.send_chat_message("Hello from group2", client2.current_chat_group['id'])
        assert success, "用户2发送消息失败"
        
        time.sleep(2)  # 等待消息传播
        
        # 验证消息隔离
        print("✅ 验证消息隔离...")
        
        # 检查用户1是否只收到group1的消息
        group1_msgs_in_client1 = collector1.get_messages_with_content("Hello from group1")
        group2_msgs_in_client1 = collector1.get_messages_with_content("Hello from group2")
        
        print(f"用户1收到group1消息数量: {len(group1_msgs_in_client1)}")
        print(f"用户1收到group2消息数量: {len(group2_msgs_in_client1)}")
        
        # 检查用户2是否只收到group2的消息
        group1_msgs_in_client2 = collector2.get_messages_with_content("Hello from group1")
        group2_msgs_in_client2 = collector2.get_messages_with_content("Hello from group2")
        
        print(f"用户2收到group1消息数量: {len(group1_msgs_in_client2)}")
        print(f"用户2收到group2消息数量: {len(group2_msgs_in_client2)}")
        
        # 断言验证
        assert len(group1_msgs_in_client1) >= 1, "用户1应该能收到group1的消息"
        assert len(group2_msgs_in_client1) == 0, "用户1不应该收到group2的消息"
        assert len(group1_msgs_in_client2) == 0, "用户2不应该收到group1的消息"
        assert len(group2_msgs_in_client2) >= 1, "用户2应该能收到group2的消息"
        
        print("✅ 消息隔离测试通过！")
        
        # 测试聊天组切换
        print("🔄 测试聊天组切换...")
        
        # 用户2加入group1
        success, msg = client2.join_chat_group(group1_name)
        assert success, f"用户2加入{group1_name}失败: {msg}"

        # 用户2进入group1
        collector2.clear()
        success, msg = client2.enter_chat_group(group1_name)
        assert success, f"用户2进入{group1_name}失败: {msg}"
        
        time.sleep(2)  # 等待历史消息加载
        
        # 检查用户2是否能看到group1的历史消息
        group1_history = collector2.get_messages_with_content("Hello from group1")
        print(f"用户2切换到group1后看到的历史消息数量: {len(group1_history)}")
        
        assert len(group1_history) >= 1, f"用户2切换到{group1_name}后应该能看到历史消息"
        
        print("✅ 聊天组切换测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理资源
        try:
            client1.disconnect()
            client2.disconnect()
            server.stop()
        except:
            pass
    
    print("🎉 所有测试通过！消息隔离功能正常工作。")
    return True


if __name__ == "__main__":
    success = test_message_isolation()
    sys.exit(0 if success else 1)
