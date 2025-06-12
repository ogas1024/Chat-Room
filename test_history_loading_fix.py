#!/usr/bin/env python3
"""
测试聊天记录加载修复效果
验证用户切换聊天组时历史消息的正确加载和显示
"""

import sys
import os
import time
import threading
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from client.core.client import ChatClient
from server.main import start_server
from shared.constants import MessageType
from shared.messages import BaseMessage


class MessageCollector:
    """消息收集器，用于测试时收集接收到的消息"""
    
    def __init__(self):
        self.messages = []
        self.lock = threading.Lock()
    
    def add_message(self, message: BaseMessage):
        """添加消息"""
        with self.lock:
            self.messages.append(message)
    
    def get_messages_by_type(self, message_type: str) -> List[BaseMessage]:
        """根据类型获取消息"""
        with self.lock:
            return [msg for msg in self.messages if msg.message_type == message_type]
    
    def clear(self):
        """清空消息"""
        with self.lock:
            self.messages.clear()
    
    def get_all_messages(self) -> List[BaseMessage]:
        """获取所有消息"""
        with self.lock:
            return self.messages.copy()


def setup_message_collector(client: ChatClient, collector: MessageCollector):
    """为客户端设置消息收集器"""
    
    def collect_message(message):
        collector.add_message(message)
        # 保持原有的处理逻辑
        if hasattr(client, '_original_handlers'):
            original_handler = client._original_handlers.get(message.message_type)
            if original_handler:
                original_handler(message)
    
    # 保存原有的处理器
    if not hasattr(client, '_original_handlers'):
        client._original_handlers = {}
    
    # 设置收集器
    for message_type in [MessageType.CHAT_HISTORY, MessageType.CHAT_HISTORY_COMPLETE, 
                        MessageType.CHAT_MESSAGE, MessageType.SYSTEM_MESSAGE]:
        if message_type in client.network_client.message_handlers:
            client._original_handlers[message_type] = client.network_client.message_handlers[message_type]
        client.network_client.set_message_handler(message_type, collect_message)


def test_history_loading_fix():
    """测试历史消息加载修复"""
    print("🧪 开始测试聊天记录加载修复...")
    
    # 启动服务器
    print("🚀 启动测试服务器...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # 等待服务器启动
    
    # 创建测试客户端
    client1 = ChatClient("localhost", 8888)
    client2 = ChatClient("localhost", 8888)
    
    collector1 = MessageCollector()
    collector2 = MessageCollector()
    
    try:
        # 连接客户端
        print("🔗 连接客户端...")
        assert client1.connect(), "客户端1连接失败"
        assert client2.connect(), "客户端2连接失败"
        
        # 设置消息收集器
        setup_message_collector(client1, collector1)
        setup_message_collector(client2, collector2)
        
        # 注册和登录用户
        print("👤 注册和登录用户...")
        success, msg = client1.register("testuser1", "password123")
        assert success, f"用户1注册失败: {msg}"
        
        success, msg = client2.register("testuser2", "password123")
        assert success, f"用户2注册失败: {msg}"
        
        success, msg = client1.login("testuser1", "password123")
        assert success, f"用户1登录失败: {msg}"
        
        success, msg = client2.login("testuser2", "password123")
        assert success, f"用户2登录失败: {msg}"
        
        # 创建测试聊天组
        group1_name = "test_group_1"
        group2_name = "test_group_2"
        
        print(f"🏗️ 创建聊天组: {group1_name}, {group2_name}")
        success, msg = client1.create_chat_group(group1_name, ["testuser2"])
        assert success, f"创建{group1_name}失败: {msg}"
        
        success, msg = client1.create_chat_group(group2_name, ["testuser2"])
        assert success, f"创建{group2_name}失败: {msg}"
        
        # 用户2加入聊天组
        success, msg = client2.join_chat_group(group1_name)
        assert success, f"用户2加入{group1_name}失败: {msg}"
        
        success, msg = client2.join_chat_group(group2_name)
        assert success, f"用户2加入{group2_name}失败: {msg}"
        
        # 进入第一个聊天组并发送一些消息
        print(f"📨 在{group1_name}中发送测试消息...")
        success, msg = client1.enter_chat_group(group1_name)
        assert success, f"用户1进入{group1_name}失败: {msg}"
        
        success, msg = client2.enter_chat_group(group1_name)
        assert success, f"用户2进入{group1_name}失败: {msg}"
        
        # 发送一些测试消息
        for i in range(3):
            success = client1.send_chat_message(f"来自用户1的消息 {i+1}", client1.current_chat_group['id'])
            assert success, f"发送消息失败: {i+1}"
            time.sleep(0.5)
            
            success = client2.send_chat_message(f"来自用户2的消息 {i+1}", client2.current_chat_group['id'])
            assert success, f"发送消息失败: {i+1}"
            time.sleep(0.5)
        
        # 进入第二个聊天组并发送消息
        print(f"📨 在{group2_name}中发送测试消息...")
        success, msg = client1.enter_chat_group(group2_name)
        assert success, f"用户1进入{group2_name}失败: {msg}"
        
        success, msg = client2.enter_chat_group(group2_name)
        assert success, f"用户2进入{group2_name}失败: {msg}"
        
        # 在第二个聊天组发送消息
        for i in range(2):
            success = client1.send_chat_message(f"Group2消息 {i+1}", client1.current_chat_group['id'])
            assert success, f"发送Group2消息失败: {i+1}"
            time.sleep(0.5)
        
        # 测试关键功能：切换回第一个聊天组，验证历史消息加载
        print(f"🔄 测试切换回{group1_name}，验证历史消息加载...")
        collector1.clear()
        
        success, msg = client1.enter_chat_group(group1_name)
        assert success, f"切换回{group1_name}失败: {msg}"
        
        # 等待历史消息加载
        time.sleep(3)
        
        # 验证历史消息加载
        print("✅ 验证历史消息加载...")
        history_messages = collector1.get_messages_by_type(MessageType.CHAT_HISTORY)
        complete_notifications = collector1.get_messages_by_type(MessageType.CHAT_HISTORY_COMPLETE)
        
        print(f"收到历史消息数量: {len(history_messages)}")
        print(f"收到加载完成通知数量: {len(complete_notifications)}")
        
        # 验证结果
        assert len(history_messages) > 0, "应该收到历史消息"
        assert len(complete_notifications) == 1, "应该收到一个加载完成通知"
        
        complete_notification = complete_notifications[0]
        assert complete_notification.message_count == len(history_messages), \
            f"完成通知中的消息数量({complete_notification.message_count})应该与实际历史消息数量({len(history_messages)})一致"
        
        print("✅ 历史消息加载修复测试通过！")
        
        # 测试空聊天组的情况
        print("🔄 测试空聊天组的历史消息加载...")
        empty_group_name = "empty_group"
        success, msg = client1.create_chat_group(empty_group_name, ["testuser2"])
        assert success, f"创建空聊天组失败: {msg}"
        
        success, msg = client2.join_chat_group(empty_group_name)
        assert success, f"加入空聊天组失败: {msg}"
        
        collector1.clear()
        success, msg = client1.enter_chat_group(empty_group_name)
        assert success, f"进入空聊天组失败: {msg}"
        
        time.sleep(2)
        
        # 验证空聊天组的处理
        history_messages = collector1.get_messages_by_type(MessageType.CHAT_HISTORY)
        complete_notifications = collector1.get_messages_by_type(MessageType.CHAT_HISTORY_COMPLETE)
        
        print(f"空聊天组历史消息数量: {len(history_messages)}")
        print(f"空聊天组完成通知数量: {len(complete_notifications)}")
        
        assert len(history_messages) == 0, "空聊天组应该没有历史消息"
        assert len(complete_notifications) == 1, "空聊天组也应该收到加载完成通知"
        assert complete_notifications[0].message_count == 0, "空聊天组的消息数量应该为0"
        
        print("✅ 空聊天组历史消息加载测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理资源
        if client1.is_connected():
            client1.disconnect()
        if client2.is_connected():
            client2.disconnect()
    
    return True


if __name__ == "__main__":
    success = test_history_loading_fix()
    if success:
        print("🎉 所有测试通过！聊天记录加载修复成功！")
        sys.exit(0)
    else:
        print("💥 测试失败！")
        sys.exit(1)
