#!/usr/bin/env python3
"""
端到端测试聊天记录加载问题
重现用户报告的具体问题场景
"""

import sys
import os
import time
import threading
import sqlite3
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from client.core.client import ChatClient
from server.core.server import ChatRoomServer
from shared.constants import MessageType, DEFAULT_PUBLIC_CHAT
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
            print(f"[收集器] 收到消息: {message.message_type}")
            if hasattr(message, 'content'):
                print(f"[收集器] 消息内容: {message.content}")
            if hasattr(message, 'message_count'):
                print(f"[收集器] 消息数量: {message.message_count}")
    
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


def check_database_messages():
    """检查数据库中的消息"""
    print("\n🔍 检查数据库中的消息...")
    
    try:
        # 连接数据库
        db_path = "server/data/chatroom.db"
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询public聊天组的消息
        cursor.execute('''
            SELECT m.id, m.content, m.message_type, m.timestamp,
                   u.username as sender_username, cg.name as group_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            JOIN chat_groups cg ON m.group_id = cg.id
            WHERE cg.name = ?
            ORDER BY m.timestamp DESC
            LIMIT 10
        ''', (DEFAULT_PUBLIC_CHAT,))
        
        messages = cursor.fetchall()
        
        print(f"📊 数据库中public聊天组的消息数量: {len(messages)}")
        for msg in messages:
            print(f"  - ID: {msg[0]}, 内容: {msg[1]}, 类型: {msg[2]}, 发送者: {msg[4]}")
        
        # 查询聊天组信息
        cursor.execute('SELECT id, name FROM chat_groups WHERE name = ?', (DEFAULT_PUBLIC_CHAT,))
        group_info = cursor.fetchone()
        if group_info:
            print(f"📋 public聊天组信息: ID={group_info[0]}, 名称={group_info[1]}")
        else:
            print("❌ 未找到public聊天组")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        import traceback
        traceback.print_exc()


def test_end_to_end_history_loading():
    """端到端测试历史消息加载"""
    print("🧪 开始端到端测试聊天记录加载问题...")
    
    # 检查数据库初始状态
    check_database_messages()
    
    # 启动服务器
    print("\n🚀 启动测试服务器...")

    def start_test_server():
        server = ChatRoomServer("localhost", 8888)
        server.start()

    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # 等待服务器启动
    
    # 创建测试客户端
    client1 = ChatClient("localhost", 8888)
    client2 = ChatClient("localhost", 8888)
    
    collector1 = MessageCollector()
    collector2 = MessageCollector()
    
    try:
        # 连接客户端
        print("\n🔗 连接客户端...")
        assert client1.connect(), "客户端1连接失败"
        assert client2.connect(), "客户端2连接失败"
        
        # 设置消息收集器
        setup_message_collector(client1, collector1)
        setup_message_collector(client2, collector2)
        
        # 注册和登录用户
        print("\n👤 注册和登录用户...")
        success, msg = client1.register("testuser1", "password123")
        if not success and "already exists" not in msg:
            print(f"用户1注册失败: {msg}")
        
        success, msg = client2.register("testuser2", "password123")
        if not success and "already exists" not in msg:
            print(f"用户2注册失败: {msg}")
        
        success, msg = client1.login("testuser1", "password123")
        assert success, f"用户1登录失败: {msg}"
        print(f"✅ 用户1登录成功: {msg}")
        
        success, msg = client2.login("testuser2", "password123")
        assert success, f"用户2登录失败: {msg}"
        print(f"✅ 用户2登录成功: {msg}")
        
        # 步骤1：用户1进入public聊天组并发送消息
        print(f"\n📨 步骤1: 用户1进入{DEFAULT_PUBLIC_CHAT}聊天组并发送消息...")
        collector1.clear()
        
        success, msg = client1.enter_chat_group(DEFAULT_PUBLIC_CHAT)
        assert success, f"用户1进入{DEFAULT_PUBLIC_CHAT}失败: {msg}"
        print(f"✅ 用户1进入{DEFAULT_PUBLIC_CHAT}成功")
        
        time.sleep(2)  # 等待历史消息加载
        
        # 发送3条测试消息
        test_messages = [
            "这是第一条测试消息",
            "这是第二条测试消息", 
            "这是第三条测试消息"
        ]
        
        for i, content in enumerate(test_messages):
            success = client1.send_chat_message(content, client1.current_chat_group['id'])
            assert success, f"发送消息{i+1}失败"
            print(f"✅ 发送消息{i+1}: {content}")
            time.sleep(1)
        
        # 检查数据库中的消息
        print("\n🔍 检查消息发送后的数据库状态...")
        check_database_messages()
        
        # 步骤2：用户1重新进入public聊天组
        print(f"\n🔄 步骤2: 用户1重新进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        collector1.clear()
        
        success, msg = client1.enter_chat_group(DEFAULT_PUBLIC_CHAT)
        assert success, f"用户1重新进入{DEFAULT_PUBLIC_CHAT}失败: {msg}"
        print(f"✅ 用户1重新进入{DEFAULT_PUBLIC_CHAT}成功")
        
        # 等待历史消息加载
        time.sleep(5)
        
        # 验证历史消息加载
        print("\n✅ 验证用户1的历史消息加载...")
        history_messages = collector1.get_messages_by_type(MessageType.CHAT_HISTORY)
        complete_notifications = collector1.get_messages_by_type(MessageType.CHAT_HISTORY_COMPLETE)
        
        print(f"📊 用户1收到历史消息数量: {len(history_messages)}")
        print(f"📊 用户1收到加载完成通知数量: {len(complete_notifications)}")
        
        for msg in history_messages:
            print(f"  - 历史消息: {msg.content}")
        
        for notification in complete_notifications:
            print(f"  - 完成通知: 聊天组ID={notification.chat_group_id}, 消息数量={notification.message_count}")
        
        # 步骤3：用户2进入public聊天组
        print(f"\n🔄 步骤3: 用户2进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        collector2.clear()
        
        success, msg = client2.enter_chat_group(DEFAULT_PUBLIC_CHAT)
        assert success, f"用户2进入{DEFAULT_PUBLIC_CHAT}失败: {msg}"
        print(f"✅ 用户2进入{DEFAULT_PUBLIC_CHAT}成功")
        
        # 等待历史消息加载
        time.sleep(5)
        
        # 验证历史消息加载
        print("\n✅ 验证用户2的历史消息加载...")
        history_messages2 = collector2.get_messages_by_type(MessageType.CHAT_HISTORY)
        complete_notifications2 = collector2.get_messages_by_type(MessageType.CHAT_HISTORY_COMPLETE)
        
        print(f"📊 用户2收到历史消息数量: {len(history_messages2)}")
        print(f"📊 用户2收到加载完成通知数量: {len(complete_notifications2)}")
        
        for msg in history_messages2:
            print(f"  - 历史消息: {msg.content}")
        
        for notification in complete_notifications2:
            print(f"  - 完成通知: 聊天组ID={notification.chat_group_id}, 消息数量={notification.message_count}")
        
        # 分析结果
        print("\n📋 测试结果分析:")
        
        if len(history_messages) >= 3:
            print("✅ 用户1成功加载历史消息")
        else:
            print(f"❌ 用户1历史消息加载失败，期望至少3条，实际{len(history_messages)}条")
        
        if len(history_messages2) >= 3:
            print("✅ 用户2成功加载历史消息")
        else:
            print(f"❌ 用户2历史消息加载失败，期望至少3条，实际{len(history_messages2)}条")
        
        if len(complete_notifications) > 0:
            print("✅ 用户1收到加载完成通知")
        else:
            print("❌ 用户1未收到加载完成通知")
        
        if len(complete_notifications2) > 0:
            print("✅ 用户2收到加载完成通知")
        else:
            print("❌ 用户2未收到加载完成通知")
        
        return len(history_messages) >= 3 and len(history_messages2) >= 3
        
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


if __name__ == "__main__":
    success = test_end_to_end_history_loading()
    if success:
        print("\n🎉 端到端测试通过！历史消息加载正常工作。")
        sys.exit(0)
    else:
        print("\n💥 端到端测试失败！需要进一步调查问题。")
        sys.exit(1)
