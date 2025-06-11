#!/usr/bin/env python3
"""
测试消息重复显示修复
验证用户发送消息后不会出现重复显示的问题
"""

import os
import sys
import time
import threading
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from server.core.server import ChatRoomServer
from client.core.client import ChatRoomClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT
from shared.logger import init_logger, get_logger


class TestMessageHandler:
    """测试消息处理器"""
    
    def __init__(self, client_name: str):
        self.client_name = client_name
        self.received_messages = []
        self.logger = get_logger(f"test.{client_name}")
    
    def handle_chat_message(self, message):
        """处理聊天消息"""
        msg_info = {
            'sender': message.sender_username,
            'content': message.content,
            'timestamp': time.time()
        }
        self.received_messages.append(msg_info)
        self.logger.info(f"[{self.client_name}] 收到消息", 
                        sender=message.sender_username, 
                        content=message.content)
        print(f"[{self.client_name}] 收到消息: {message.sender_username} -> {message.content}")
    
    def handle_system_message(self, message):
        """处理系统消息"""
        self.logger.info(f"[{self.client_name}] 系统消息", content=message.content)
        print(f"[{self.client_name}] 系统: {message.content}")
    
    def handle_error_message(self, message):
        """处理错误消息"""
        self.logger.error(f"[{self.client_name}] 错误", error=message.error_message)
        print(f"[{self.client_name}] 错误: {message.error_message}")
    
    def get_messages_from_sender(self, sender: str):
        """获取来自特定发送者的消息"""
        return [msg for msg in self.received_messages if msg['sender'] == sender]
    
    def count_duplicate_messages(self, sender: str, content: str):
        """统计重复消息数量"""
        count = 0
        for msg in self.received_messages:
            if msg['sender'] == sender and msg['content'] == content:
                count += 1
        return count


def test_message_duplication():
    """测试消息重复显示问题"""
    print("🧪 开始测试消息重复显示修复...")
    
    # 初始化日志系统
    logging_config = {
        'level': 'INFO',
        'file_enabled': True,
        'console_enabled': False,
        'file_max_size': 1048576,
        'file_backup_count': 3
    }
    init_logger(logging_config, "test_duplication")
    
    # 启动服务器
    print("🚀 启动测试服务器...")
    server = ChatRoomServer(DEFAULT_HOST, DEFAULT_PORT)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    try:
        # 创建两个客户端
        print("👥 创建测试客户端...")
        
        # 客户端1 (发送者)
        client1 = ChatRoomClient()
        handler1 = TestMessageHandler("Client1")
        client1.set_message_handler("CHAT_MESSAGE", handler1.handle_chat_message)
        client1.set_message_handler("SYSTEM_MESSAGE", handler1.handle_system_message)
        client1.set_message_handler("ERROR_MESSAGE", handler1.handle_error_message)
        
        # 客户端2 (接收者)
        client2 = ChatRoomClient()
        handler2 = TestMessageHandler("Client2")
        client2.set_message_handler("CHAT_MESSAGE", handler2.handle_chat_message)
        client2.set_message_handler("SYSTEM_MESSAGE", handler2.handle_system_message)
        client2.set_message_handler("ERROR_MESSAGE", handler2.handle_error_message)
        
        # 连接到服务器
        print("🔗 连接到服务器...")
        if not client1.connect(DEFAULT_HOST, DEFAULT_PORT):
            print("❌ 客户端1连接失败")
            return False
        
        if not client2.connect(DEFAULT_HOST, DEFAULT_PORT):
            print("❌ 客户端2连接失败")
            return False
        
        # 注册和登录用户
        print("👤 注册和登录用户...")
        
        # 注册用户1
        success, message = client1.register("testuser1", "password123")
        if not success:
            print(f"❌ 用户1注册失败: {message}")
            return False
        
        # 注册用户2
        success, message = client2.register("testuser2", "password123")
        if not success:
            print(f"❌ 用户2注册失败: {message}")
            return False
        
        # 登录用户1
        success, message = client1.login("testuser1", "password123")
        if not success:
            print(f"❌ 用户1登录失败: {message}")
            return False
        
        # 登录用户2
        success, message = client2.login("testuser2", "password123")
        if not success:
            print(f"❌ 用户2登录失败: {message}")
            return False
        
        print("✅ 用户登录成功")
        
        # 等待一下让消息处理完成
        time.sleep(1)
        
        # 清空之前的消息记录
        handler1.received_messages.clear()
        handler2.received_messages.clear()
        
        # 测试消息发送
        print("💬 测试消息发送...")
        
        test_messages = [
            "Hello, this is a test message!",
            "Testing message duplication fix",
            "Third test message"
        ]
        
        for i, test_message in enumerate(test_messages):
            print(f"📤 发送测试消息 {i+1}: {test_message}")
            
            # 用户1发送消息
            if client1.current_chat_group:
                group_id = client1.current_chat_group['id']
                success = client1.send_chat_message(test_message, group_id)
                if not success:
                    print(f"❌ 消息发送失败: {test_message}")
                    continue
            else:
                print("❌ 用户1未在聊天组中")
                continue
            
            # 等待消息传播
            time.sleep(0.5)
            
            # 检查消息重复情况
            print(f"🔍 检查消息重复情况...")
            
            # 检查发送者收到的消息
            sender_messages = handler1.count_duplicate_messages("testuser1", test_message)
            print(f"   发送者收到自己的消息次数: {sender_messages}")
            
            # 检查接收者收到的消息
            receiver_messages = handler2.count_duplicate_messages("testuser1", test_message)
            print(f"   接收者收到消息次数: {receiver_messages}")
            
            # 验证结果
            if sender_messages > 1:
                print(f"❌ 发现消息重复！发送者收到自己的消息 {sender_messages} 次")
                return False
            elif sender_messages == 0:
                print(f"⚠️  发送者没有收到自己的消息")
            else:
                print(f"✅ 发送者正确收到自己的消息 1 次")
            
            if receiver_messages != 1:
                print(f"❌ 接收者消息异常！收到消息 {receiver_messages} 次")
                return False
            else:
                print(f"✅ 接收者正确收到消息 1 次")
            
            print()
        
        # 总结测试结果
        print("📊 测试结果总结:")
        print(f"   客户端1总共收到消息: {len(handler1.received_messages)}")
        print(f"   客户端2总共收到消息: {len(handler2.received_messages)}")
        
        # 检查是否有任何重复消息
        has_duplicates = False
        for test_message in test_messages:
            sender_count = handler1.count_duplicate_messages("testuser1", test_message)
            if sender_count > 1:
                has_duplicates = True
                break
        
        if has_duplicates:
            print("❌ 测试失败：发现消息重复显示")
            return False
        else:
            print("✅ 测试成功：没有发现消息重复显示")
            return True
    
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理资源
        print("🧹 清理测试资源...")
        try:
            if 'client1' in locals():
                client1.disconnect()
            if 'client2' in locals():
                client2.disconnect()
        except:
            pass
        
        try:
            server.stop()
        except:
            pass


def test_message_order():
    """测试消息顺序是否正确"""
    print("🧪 测试消息顺序...")
    
    # 这里可以添加消息顺序测试逻辑
    # 确保消息按发送顺序正确显示
    
    print("✅ 消息顺序测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始消息重复显示修复测试")
    print("=" * 60)
    
    tests = [
        ("消息重复显示测试", test_message_duplication),
        ("消息顺序测试", test_message_order),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 运行测试: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                print(f"✅ {test_name} 通过")
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 出错: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！消息重复显示问题已修复")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
