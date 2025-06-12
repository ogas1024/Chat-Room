#!/usr/bin/env python3
"""
TUI历史消息显示修复测试
验证TUI界面中的历史消息处理和显示是否正常工作
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
from shared.constants import DEFAULT_HOST, MessageType


class TUIMessageCollector:
    """TUI消息收集器，模拟TUI应用程序的消息处理"""
    
    def __init__(self, name: str):
        self.name = name
        self.chat_messages: List[Dict] = []
        self.history_messages: List[Dict] = []
        self.system_messages: List[Dict] = []
        self.error_messages: List[Dict] = []
        self.lock = threading.Lock()
        self.history_loading = False
        self.history_message_count = 0
    
    def handle_chat_message(self, message):
        """处理实时聊天消息"""
        with self.lock:
            msg_data = {
                'sender': getattr(message, 'sender_username', ''),
                'content': getattr(message, 'content', ''),
                'group_id': getattr(message, 'chat_group_id', None),
                'type': 'chat_message',
                'time': time.time()
            }
            self.chat_messages.append(msg_data)
            print(f"[{self.name}] 实时消息: {msg_data['sender']}: {msg_data['content']}")
    
    def handle_chat_history(self, message):
        """处理历史聊天消息"""
        with self.lock:
            msg_data = {
                'sender': getattr(message, 'sender_username', ''),
                'content': getattr(message, 'content', ''),
                'group_id': getattr(message, 'chat_group_id', None),
                'type': 'chat_history',
                'time': time.time()
            }
            self.history_messages.append(msg_data)
            self.history_message_count += 1
            print(f"[{self.name}] 历史消息: {msg_data['sender']}: {msg_data['content']}")
    
    def handle_system_message(self, message):
        """处理系统消息"""
        with self.lock:
            msg_data = {
                'content': getattr(message, 'content', ''),
                'type': 'system_message',
                'time': time.time()
            }
            self.system_messages.append(msg_data)
            print(f"[{self.name}] 系统消息: {msg_data['content']}")
    
    def handle_error_message(self, message):
        """处理错误消息"""
        with self.lock:
            msg_data = {
                'content': getattr(message, 'error_message', ''),
                'type': 'error_message',
                'time': time.time()
            }
            self.error_messages.append(msg_data)
            print(f"[{self.name}] 错误消息: {msg_data['content']}")
    
    def clear_messages(self):
        """清空所有消息"""
        with self.lock:
            self.chat_messages.clear()
            self.history_messages.clear()
            self.system_messages.clear()
            self.error_messages.clear()
            self.history_loading = True
            self.history_message_count = 0
    
    def get_message_counts(self):
        """获取消息计数"""
        with self.lock:
            return {
                'chat_messages': len(self.chat_messages),
                'history_messages': len(self.history_messages),
                'system_messages': len(self.system_messages),
                'error_messages': len(self.error_messages)
            }


def test_tui_history_display():
    """测试TUI历史消息显示功能"""
    print("🚀 开始测试TUI历史消息显示功能...")
    
    # 启动测试服务器
    print("📡 启动测试服务器...")
    server = ChatRoomServer(DEFAULT_HOST, 8891)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    time.sleep(2)  # 等待服务器启动
    
    try:
        # 创建客户端
        print("👤 创建测试客户端...")
        client = ChatClient(DEFAULT_HOST, 8891)
        
        # 创建TUI消息收集器
        collector = TUIMessageCollector("TUIClient")
        
        # 设置消息处理器（模拟TUI应用程序的设置）
        client.network_client.set_message_handler(MessageType.CHAT_MESSAGE, collector.handle_chat_message)
        client.network_client.set_message_handler(MessageType.CHAT_HISTORY, collector.handle_chat_history)
        client.network_client.set_message_handler(MessageType.SYSTEM_MESSAGE, collector.handle_system_message)
        client.network_client.set_message_handler(MessageType.ERROR_MESSAGE, collector.handle_error_message)
        
        # 连接客户端
        print("🔗 连接客户端...")
        assert client.connect(), "客户端连接失败"
        
        # 注册和登录用户
        import random
        username = f"tuiuser_{random.randint(1000, 9999)}"
        print(f"👤 注册和登录用户: {username}")
        
        success, msg = client.register(username, "password123")
        assert success, f"用户注册失败: {msg}"
        
        success, msg = client.login(username, "password123")
        assert success, f"用户登录失败: {msg}"
        
        time.sleep(1)
        
        # 进入public聊天组并发送一些消息
        print("🚪 进入public聊天组...")
        success, msg = client.enter_chat_group("public")
        assert success, f"进入public失败: {msg}"
        
        time.sleep(2)  # 等待历史消息加载
        
        # 发送一些测试消息
        print("📨 发送测试消息...")
        for i in range(3):
            message_content = f"测试消息 {i+1}"
            success = client.send_chat_message(message_content, client.current_chat_group['id'])
            assert success, f"发送消息失败: {message_content}"
            time.sleep(0.5)
        
        time.sleep(2)  # 等待消息处理
        
        # 检查消息接收情况
        counts = collector.get_message_counts()
        print(f"📊 消息接收统计:")
        print(f"   实时消息: {counts['chat_messages']}")
        print(f"   历史消息: {counts['history_messages']}")
        print(f"   系统消息: {counts['system_messages']}")
        print(f"   错误消息: {counts['error_messages']}")
        
        # 验证没有"未处理的消息类型"错误
        assert counts['error_messages'] == 0, f"不应该有错误消息，但收到了 {counts['error_messages']} 条"
        
        # 验证收到了实时消息
        assert counts['chat_messages'] >= 3, f"应该收到至少3条实时消息，实际收到 {counts['chat_messages']} 条"
        
        print("✅ 第一阶段测试通过：消息处理器正常工作")
        
        # 测试重新进入聊天组的历史消息加载
        print("🔄 测试重新进入聊天组...")
        collector.clear_messages()
        
        # 重新进入public聊天组
        success, msg = client.enter_chat_group("public")
        assert success, f"重新进入public失败: {msg}"
        
        time.sleep(3)  # 等待历史消息加载
        
        # 检查历史消息接收情况
        counts = collector.get_message_counts()
        print(f"📊 重新进入后的消息统计:")
        print(f"   实时消息: {counts['chat_messages']}")
        print(f"   历史消息: {counts['history_messages']}")
        print(f"   系统消息: {counts['system_messages']}")
        print(f"   错误消息: {counts['error_messages']}")
        
        # 验证收到了历史消息
        assert counts['history_messages'] > 0, f"应该收到历史消息，但实际收到 {counts['history_messages']} 条"
        
        # 验证没有错误消息
        assert counts['error_messages'] == 0, f"不应该有错误消息，但收到了 {counts['error_messages']} 条"
        
        print("✅ 第二阶段测试通过：历史消息加载正常")
        
        # 测试聊天组切换
        print("🔄 测试聊天组切换...")
        
        # 创建新的聊天组
        group_name = f"testgroup_{random.randint(1000, 9999)}"
        success, msg = client.create_chat_group(group_name)
        assert success, f"创建聊天组失败: {msg}"
        
        # 进入新聊天组
        collector.clear_messages()
        success, msg = client.enter_chat_group(group_name)
        assert success, f"进入新聊天组失败: {msg}"
        
        time.sleep(2)  # 等待历史消息加载
        
        # 在新聊天组发送消息
        success = client.send_chat_message("新聊天组的消息", client.current_chat_group['id'])
        assert success, "在新聊天组发送消息失败"
        
        time.sleep(1)
        
        # 切换回public聊天组
        collector.clear_messages()
        success, msg = client.enter_chat_group("public")
        assert success, f"切换回public失败: {msg}"
        
        time.sleep(3)  # 等待历史消息加载
        
        # 检查是否只收到public聊天组的历史消息
        counts = collector.get_message_counts()
        print(f"📊 切换回public后的消息统计:")
        print(f"   实时消息: {counts['chat_messages']}")
        print(f"   历史消息: {counts['history_messages']}")
        print(f"   系统消息: {counts['system_messages']}")
        print(f"   错误消息: {counts['error_messages']}")
        
        # 验证收到了public的历史消息
        assert counts['history_messages'] > 0, "应该收到public聊天组的历史消息"
        
        # 验证没有收到新聊天组的消息
        new_group_messages = [msg for msg in collector.history_messages if "新聊天组的消息" in msg['content']]
        assert len(new_group_messages) == 0, "不应该收到其他聊天组的消息"
        
        print("✅ 第三阶段测试通过：聊天组切换和消息隔离正常")
        
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
    
    print("🎉 所有TUI历史消息显示测试通过！修复成功。")
    return True


if __name__ == "__main__":
    success = test_tui_history_display()
    sys.exit(0 if success else 1)
