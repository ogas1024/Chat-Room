#!/usr/bin/env python3
"""
测试消息隔离修复
验证不同聊天组之间的消息是否正确隔离
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
from client.core.client import ChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT
from shared.logger import init_logger, get_logger
from server.database.connection import DatabaseConnection


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
            'chat_group_id': getattr(message, 'chat_group_id', None),
            'timestamp': time.time()
        }
        self.received_messages.append(msg_info)
        self.logger.info(f"[{self.client_name}] 收到消息", 
                        sender=message.sender_username, 
                        content=message.content,
                        chat_group_id=msg_info['chat_group_id'])
        print(f"[{self.client_name}] 收到消息: {message.sender_username} -> {message.content} (组ID: {msg_info['chat_group_id']})")
    
    def handle_system_message(self, message):
        """处理系统消息"""
        self.logger.info(f"[{self.client_name}] 系统消息", content=message.content)
        print(f"[{self.client_name}] 系统: {message.content}")
    
    def handle_error_message(self, message):
        """处理错误消息"""
        self.logger.error(f"[{self.client_name}] 错误", error=message.error_message)
        print(f"[{self.client_name}] 错误: {message.error_message}")
    
    def get_messages_from_group(self, group_id: int):
        """获取来自特定聊天组的消息"""
        return [msg for msg in self.received_messages if msg['chat_group_id'] == group_id]
    
    def clear_messages(self):
        """清空消息记录"""
        self.received_messages.clear()


def test_message_isolation():
    """测试消息隔离功能"""
    print("🧪 开始测试消息隔离修复...")

    # 使用测试端口和数据库
    test_port = 9999
    test_db_path = "test/test_isolation.db"

    # 设置测试数据库
    DatabaseConnection.set_database_path(test_db_path)

    # 初始化日志系统
    logging_config = {
        'level': 'INFO',
        'file_enabled': True,
        'console_enabled': False,
        'file_max_size': 1048576,
        'file_backup_count': 3
    }
    init_logger(logging_config, "test_isolation")

    # 启动服务器
    print(f"🚀 启动测试服务器 (端口: {test_port})...")
    server = ChatRoomServer(DEFAULT_HOST, test_port)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    try:
        # 创建两个客户端
        print("👥 创建测试客户端...")
        
        # 客户端1 (test用户)
        client1 = ChatClient()
        handler1 = TestMessageHandler("Client1")
        client1.network_client.set_message_handler("CHAT_MESSAGE", handler1.handle_chat_message)
        client1.network_client.set_message_handler("SYSTEM_MESSAGE", handler1.handle_system_message)
        client1.network_client.set_message_handler("ERROR_MESSAGE", handler1.handle_error_message)
        
        # 客户端2 (test1用户)
        client2 = ChatClient()
        handler2 = TestMessageHandler("Client2")
        client2.network_client.set_message_handler("CHAT_MESSAGE", handler2.handle_chat_message)
        client2.network_client.set_message_handler("SYSTEM_MESSAGE", handler2.handle_system_message)
        client2.network_client.set_message_handler("ERROR_MESSAGE", handler2.handle_error_message)
        
        # 连接到服务器
        print(f"🔗 连接到服务器 (端口: {test_port})...")
        client1.network_client.port = test_port
        client2.network_client.port = test_port

        if not client1.connect():
            print("❌ 客户端1连接失败")
            return False

        if not client2.connect():
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
        print(f"   用户1当前聊天组: {client1.current_chat_group}")
        print(f"   用户2当前聊天组: {client2.current_chat_group}")
        
        # 等待一下让消息处理完成
        time.sleep(1)
        
        # 创建测试聊天组
        print("🏗️ 创建测试聊天组...")
        success, message = client2.create_chat_group("testgroup", [])
        if not success:
            print(f"❌ 创建聊天组失败: {message}")
            return False

        # 用户2进入testgroup聊天组
        success, message = client2.enter_chat_group("testgroup")
        if not success:
            print(f"❌ 用户2进入testgroup聊天组失败: {message}")
            return False

        # 等待状态更新
        time.sleep(0.5)
        
        print("✅ 聊天组设置完成")
        print(f"   用户1在聊天组: {client1.current_chat_group['name'] if client1.current_chat_group else 'None'}")
        print(f"   用户2在聊天组: {client2.current_chat_group['name'] if client2.current_chat_group else 'None'}")
        
        # 清空之前的消息记录
        handler1.clear_messages()
        handler2.clear_messages()
        
        # 测试消息隔离
        print("💬 测试消息隔离...")
        
        # 用户1在public聊天组发送消息
        print("📤 用户1在public聊天组发送消息...")
        if client1.current_chat_group:
            group_id = client1.current_chat_group['id']
            success = client1.send_chat_message("hello", group_id)
            if not success:
                print("❌ 用户1消息发送失败")
                return False
            
            success = client1.send_chat_message("chat", group_id)
            if not success:
                print("❌ 用户1第二条消息发送失败")
                return False
        else:
            print("❌ 用户1未在聊天组中")
            return False
        
        # 等待消息传播
        time.sleep(1)
        
        # 用户2在testgroup聊天组发送消息
        print("📤 用户2在testgroup聊天组发送消息...")
        if client2.current_chat_group:
            group_id = client2.current_chat_group['id']
            success = client2.send_chat_message("hello from testgroup", group_id)
            if not success:
                print("❌ 用户2消息发送失败")
                return False
        else:
            print("❌ 用户2未在聊天组中")
            return False
        
        # 等待消息传播
        time.sleep(1)
        
        # 检查消息隔离情况
        print("🔍 检查消息隔离情况...")
        
        # 获取各自收到的消息
        client1_messages = handler1.received_messages
        client2_messages = handler2.received_messages
        
        print(f"   客户端1收到消息数量: {len(client1_messages)}")
        for msg in client1_messages:
            print(f"     - {msg['sender']}: {msg['content']} (组ID: {msg['chat_group_id']})")
        
        print(f"   客户端2收到消息数量: {len(client2_messages)}")
        for msg in client2_messages:
            print(f"     - {msg['sender']}: {msg['content']} (组ID: {msg['chat_group_id']})")
        
        # 验证消息隔离
        public_group_id = client1.current_chat_group['id']
        testgroup_id = client2.current_chat_group['id']

        # 客户端1应该只收到public聊天组的消息
        client1_public_messages = [msg for msg in client1_messages if msg['chat_group_id'] == public_group_id]
        client1_testgroup_messages = [msg for msg in client1_messages if msg['chat_group_id'] == testgroup_id]

        # 客户端2应该只收到testgroup聊天组的消息
        client2_public_messages = [msg for msg in client2_messages if msg['chat_group_id'] == public_group_id]
        client2_testgroup_messages = [msg for msg in client2_messages if msg['chat_group_id'] == testgroup_id]

        print("\n📊 消息隔离验证结果:")
        print(f"   客户端1收到public组消息: {len(client1_public_messages)}")
        print(f"   客户端1收到testgroup组消息: {len(client1_testgroup_messages)}")
        print(f"   客户端2收到public组消息: {len(client2_public_messages)}")
        print(f"   客户端2收到testgroup组消息: {len(client2_testgroup_messages)}")
        
        # 验证结果
        success = True

        if len(client1_testgroup_messages) > 0:
            print("❌ 错误：客户端1收到了testgroup聊天组的消息（应该被隔离）")
            success = False

        if len(client2_public_messages) > 0:
            print("❌ 错误：客户端2收到了public聊天组的消息（应该被隔离）")
            success = False

        if len(client1_public_messages) != 2:
            print(f"❌ 错误：客户端1应该收到2条public组消息，实际收到{len(client1_public_messages)}条")
            success = False

        if len(client2_testgroup_messages) != 1:
            print(f"❌ 错误：客户端2应该收到1条testgroup组消息，实际收到{len(client2_testgroup_messages)}条")
            success = False
        
        if success:
            print("✅ 消息隔离测试通过！")
            print("   - 不同聊天组的消息正确隔离")
            print("   - 用户只能看到当前聊天组的消息")
            return True
        else:
            print("❌ 消息隔离测试失败")
            return False
    
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

        # 清理测试数据库
        try:
            if os.path.exists(test_db_path):
                os.remove(test_db_path)
        except:
            pass


if __name__ == "__main__":
    success = test_message_isolation()
    
    if success:
        print("\n🎉 消息隔离修复验证成功！")
        print("📝 修复总结:")
        print("- 客户端消息处理器增加了聊天组验证")
        print("- 只显示当前聊天组的消息")
        print("- 不同聊天组之间的消息完全隔离")
    else:
        print("\n❌ 消息隔离修复验证失败")
        print("需要进一步检查和修复")
    
    sys.exit(0 if success else 1)
