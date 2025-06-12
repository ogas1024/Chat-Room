#!/usr/bin/env python3
"""
聊天组切换功能修复测试
验证修复后的聊天组切换功能是否正常工作
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
            print(f"[{self.name}] 收到消息: {msg_data['sender']}: {msg_data['content']} (类型: {msg_data['type']})")
    
    def get_messages_with_content(self, content: str) -> List[Dict]:
        """获取包含特定内容的消息"""
        with self.lock:
            return [msg for msg in self.messages if content in msg['content']]
    
    def get_messages_by_type(self, msg_type: str) -> List[Dict]:
        """获取特定类型的消息"""
        with self.lock:
            return [msg for msg in self.messages if msg['type'] == msg_type]
    
    def clear(self):
        """清空消息"""
        with self.lock:
            self.messages.clear()


def test_chat_switching():
    """测试聊天组切换功能"""
    print("🚀 开始测试聊天组切换功能...")
    
    # 启动测试服务器
    print("📡 启动测试服务器...")
    server = ChatRoomServer(DEFAULT_HOST, 8890)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(2)  # 等待服务器启动
    
    try:
        # 创建客户端
        print("👤 创建测试客户端...")
        client = ChatClient(DEFAULT_HOST, 8890)
        
        # 创建消息收集器
        collector = MessageCollector("TestClient")
        
        # 设置消息处理器
        from shared.constants import MessageType
        client.network_client.set_message_handler(MessageType.CHAT_MESSAGE, collector.collect_message)
        client.network_client.set_message_handler(MessageType.CHAT_HISTORY, collector.collect_message)
        
        # 连接客户端
        print("🔗 连接客户端...")
        assert client.connect(), "客户端连接失败"
        
        # 注册和登录用户
        import random
        username = f"testuser_{random.randint(1000, 9999)}"
        print(f"👤 注册和登录用户: {username}")
        
        success, msg = client.register(username, "password123")
        assert success, f"用户注册失败: {msg}"
        
        success, msg = client.login(username, "password123")
        assert success, f"用户登录失败: {msg}"
        
        time.sleep(1)
        
        # 创建两个聊天组
        group1_name = f"group1_{random.randint(1000, 9999)}"
        group2_name = f"group2_{random.randint(1000, 9999)}"
        
        print(f"💬 创建聊天组: {group1_name}, {group2_name}")
        success, msg = client.create_chat_group(group1_name)
        assert success, f"创建{group1_name}失败: {msg}"
        
        success, msg = client.create_chat_group(group2_name)
        assert success, f"创建{group2_name}失败: {msg}"
        
        time.sleep(1)
        
        # 测试第一次进入聊天组
        print(f"🚪 第一次进入聊天组: {group1_name}")
        collector.clear()
        success, msg = client.enter_chat_group(group1_name)
        assert success, f"进入{group1_name}失败: {msg}"
        
        time.sleep(2)  # 等待历史消息加载
        
        # 在第一个聊天组发送消息
        print(f"📨 在{group1_name}中发送消息...")
        success = client.send_chat_message("Hello from group1", client.current_chat_group['id'])
        assert success, "发送消息失败"
        
        time.sleep(1)
        
        # 测试切换到第二个聊天组
        print(f"🔄 切换到聊天组: {group2_name}")
        collector.clear()
        success, msg = client.enter_chat_group(group2_name)
        assert success, f"切换到{group2_name}失败: {msg}"
        
        time.sleep(2)  # 等待历史消息加载
        
        # 在第二个聊天组发送消息
        print(f"📨 在{group2_name}中发送消息...")
        success = client.send_chat_message("Hello from group2", client.current_chat_group['id'])
        assert success, "发送消息失败"
        
        time.sleep(1)
        
        # 测试切换回第一个聊天组
        print(f"🔄 切换回聊天组: {group1_name}")
        collector.clear()
        success, msg = client.enter_chat_group(group1_name)
        assert success, f"切换回{group1_name}失败: {msg}"
        
        time.sleep(2)  # 等待历史消息加载
        
        # 验证历史消息加载
        print("✅ 验证历史消息加载...")
        history_messages = collector.get_messages_by_type(MessageType.CHAT_HISTORY)
        print(f"收到历史消息数量: {len(history_messages)}")
        
        # 检查是否收到了group1的历史消息
        group1_history = collector.get_messages_with_content("Hello from group1")
        print(f"Group1历史消息数量: {len(group1_history)}")
        
        assert len(group1_history) >= 1, f"应该能看到{group1_name}的历史消息"
        
        # 验证没有收到group2的消息
        group2_messages = collector.get_messages_with_content("Hello from group2")
        print(f"Group2消息数量: {len(group2_messages)}")
        
        assert len(group2_messages) == 0, f"在{group1_name}中不应该看到{group2_name}的消息"
        
        print("✅ 聊天组切换功能测试通过！")
        
        # 测试多次切换
        print("🔄 测试多次切换...")
        for i in range(3):
            print(f"  第{i+1}次切换...")
            
            # 切换到group2
            collector.clear()
            success, msg = client.enter_chat_group(group2_name)
            assert success, f"第{i+1}次切换到{group2_name}失败: {msg}"
            time.sleep(1)
            
            # 切换到group1
            collector.clear()
            success, msg = client.enter_chat_group(group1_name)
            assert success, f"第{i+1}次切换到{group1_name}失败: {msg}"
            time.sleep(1)
        
        print("✅ 多次切换测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理资源
        try:
            client.disconnect()
            server.stop()
        except:
            pass
    
    print("🎉 所有聊天组切换测试通过！功能已修复。")
    return True


if __name__ == "__main__":
    success = test_chat_switching()
    sys.exit(0 if success else 1)
