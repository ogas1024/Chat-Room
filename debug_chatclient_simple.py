#!/usr/bin/env python3
"""
使用ChatClient进行简单的历史消息加载测试
直接测试客户端的历史消息接收功能
"""

import sys
import os
import time
import threading

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from client.core.client import ChatClient
from shared.constants import MessageType, DEFAULT_PUBLIC_CHAT


class MessageLogger:
    """消息记录器"""
    
    def __init__(self):
        self.messages = []
        self.lock = threading.Lock()
    
    def log_message(self, message_type, message):
        """记录消息"""
        with self.lock:
            self.messages.append((message_type, message, time.time()))
            print(f"[记录器] {message_type}: {getattr(message, 'content', str(message))}")
    
    def get_messages_by_type(self, message_type):
        """获取指定类型的消息"""
        with self.lock:
            return [msg for msg_type, msg, timestamp in self.messages if msg_type == message_type]
    
    def get_all_messages(self):
        """获取所有消息"""
        with self.lock:
            return self.messages.copy()


def start_test_server():
    """启动测试服务器"""
    try:
        from server.core.server import ChatRoomServer
        server = ChatRoomServer("localhost", 8888)
        server.start()
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")


def test_chatclient_history_loading():
    """测试ChatClient的历史消息加载"""
    print("🧪 测试ChatClient的历史消息加载...")
    
    # 启动服务器
    print("🚀 启动测试服务器...")
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # 等待服务器启动
    
    # 创建消息记录器
    logger = MessageLogger()
    
    try:
        # 创建客户端
        client = ChatClient("localhost", 8888)
        
        # 设置消息记录器
        def log_chat_history(message):
            logger.log_message(MessageType.CHAT_HISTORY, message)
            # 调用原始处理器
            client._handle_chat_history(message)
        
        def log_chat_history_complete(message):
            logger.log_message(MessageType.CHAT_HISTORY_COMPLETE, message)
            # 调用原始处理器
            client._handle_chat_history_complete(message)
        
        def log_system_message(message):
            logger.log_message(MessageType.SYSTEM_MESSAGE, message)
        
        # 替换消息处理器
        client.network_client.set_message_handler(MessageType.CHAT_HISTORY, log_chat_history)
        client.network_client.set_message_handler(MessageType.CHAT_HISTORY_COMPLETE, log_chat_history_complete)
        client.network_client.set_message_handler(MessageType.SYSTEM_MESSAGE, log_system_message)
        
        # 连接客户端
        print("🔗 连接客户端...")
        if not client.connect():
            print("❌ 客户端连接失败")
            return False
        
        print("✅ 客户端连接成功")
        
        # 尝试使用现有用户登录
        print("👤 尝试登录...")
        
        # 先尝试注册一个新用户
        success, msg = client.register("testuser_debug", "password123")
        if success:
            print(f"✅ 注册成功: {msg}")
        else:
            print(f"ℹ️ 注册响应: {msg}")
        
        # 登录
        success, msg = client.login("testuser_debug", "password123")
        if not success:
            print(f"❌ 登录失败: {msg}")
            return False
        
        print(f"✅ 登录成功: {msg}")
        
        # 进入public聊天组
        print(f"📋 进入{DEFAULT_PUBLIC_CHAT}聊天组...")
        success, msg = client.enter_chat_group(DEFAULT_PUBLIC_CHAT)
        if not success:
            print(f"❌ 进入聊天组失败: {msg}")
            return False
        
        print(f"✅ 进入聊天组成功: {msg}")
        
        # 等待历史消息加载
        print("⏳ 等待历史消息加载...")
        time.sleep(8)  # 给足够的时间接收消息
        
        # 分析接收到的消息
        print("\n📊 消息接收分析:")
        all_messages = logger.get_all_messages()
        print(f"总共接收到 {len(all_messages)} 条消息")
        
        # 按类型统计
        message_counts = {}
        for msg_type, msg, timestamp in all_messages:
            message_counts[msg_type] = message_counts.get(msg_type, 0) + 1
        
        for msg_type, count in message_counts.items():
            print(f"  - {msg_type}: {count}条")
        
        # 检查历史消息
        history_messages = logger.get_messages_by_type(MessageType.CHAT_HISTORY)
        complete_notifications = logger.get_messages_by_type(MessageType.CHAT_HISTORY_COMPLETE)
        
        print(f"\n📨 历史消息详情:")
        print(f"历史消息数量: {len(history_messages)}")
        print(f"完成通知数量: {len(complete_notifications)}")
        
        if len(history_messages) > 0:
            print("最近的历史消息:")
            for i, msg in enumerate(history_messages[-3:], 1):
                print(f"  {i}. {msg.sender_username}: {msg.content}")
        
        if len(complete_notifications) > 0:
            complete_msg = complete_notifications[0]
            print(f"完成通知: 聊天组ID={complete_msg.chat_group_id}, 消息数量={complete_msg.message_count}")
        
        # 验证结果
        success = len(history_messages) > 0 and len(complete_notifications) > 0
        
        if success:
            print("\n✅ ChatClient历史消息加载测试成功！")
        else:
            print("\n❌ ChatClient历史消息加载测试失败！")
            if len(history_messages) == 0:
                print("  - 没有收到历史消息")
            if len(complete_notifications) == 0:
                print("  - 没有收到完成通知")
        
        # 断开连接
        client.disconnect()
        return success
        
    except Exception as e:
        print(f"❌ ChatClient测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_manual_enter_chat():
    """手动测试进入聊天组"""
    print("\n🧪 手动测试进入聊天组...")
    
    # 启动服务器
    print("🚀 启动测试服务器...")
    server_thread = threading.Thread(target=start_test_server, daemon=True)
    server_thread.start()
    time.sleep(3)
    
    try:
        client = ChatClient("localhost", 8888)
        
        # 连接和登录
        if not client.connect():
            print("❌ 连接失败")
            return False
        
        success, msg = client.register("testuser_manual", "password123")
        print(f"注册: {msg}")
        
        success, msg = client.login("testuser_manual", "password123")
        if not success:
            print(f"❌ 登录失败: {msg}")
            return False
        
        print(f"✅ 登录成功")
        
        # 手动进入聊天组多次
        for i in range(3):
            print(f"\n🔄 第{i+1}次进入{DEFAULT_PUBLIC_CHAT}聊天组...")
            
            success, msg = client.enter_chat_group(DEFAULT_PUBLIC_CHAT)
            if success:
                print(f"✅ 进入成功: {msg}")
                time.sleep(3)  # 等待历史消息
            else:
                print(f"❌ 进入失败: {msg}")
        
        client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ 手动测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始ChatClient历史消息加载调试...")
    
    # 测试1: ChatClient历史消息加载
    print("="*60)
    print("测试1: ChatClient历史消息加载")
    print("="*60)
    result1 = test_chatclient_history_loading()
    
    # 测试2: 手动进入聊天组
    print("\n" + "="*60)
    print("测试2: 手动进入聊天组")
    print("="*60)
    result2 = test_manual_enter_chat()
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    print(f"ChatClient历史消息加载: {'✅ 通过' if result1 else '❌ 失败'}")
    print(f"手动进入聊天组: {'✅ 通过' if result2 else '❌ 失败'}")
    
    if result1:
        print("\n🎉 ChatClient功能正常！问题可能在TUI界面层面。")
    else:
        print("\n💥 发现ChatClient问题！")
    
    return result1


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
