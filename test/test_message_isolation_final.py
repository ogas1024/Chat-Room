#!/usr/bin/env python3
"""
最终测试消息隔离修复
验证修复后的消息隔离功能是否正常工作
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


class MessageCollector:
    """消息收集器"""
    
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
    
    def clear_messages(self):
        """清空消息记录"""
        self.received_messages.clear()


def test_message_isolation_final():
    """最终测试消息隔离功能"""
    print("🧪 开始最终消息隔离测试...")
    
    # 使用测试端口和数据库
    test_port = 9997
    test_db_path = "test/test_final_isolation.db"
    
    # 清理旧的测试数据库
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
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
    init_logger(logging_config, "test_final_isolation")
    
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
        
        # 客户端1 (alice)
        client1 = ChatClient()
        client1.network_client.port = test_port
        collector1 = MessageCollector("Alice")
        client1.network_client.set_message_handler("CHAT_MESSAGE", collector1.handle_chat_message)
        client1.network_client.set_message_handler("SYSTEM_MESSAGE", collector1.handle_system_message)
        client1.network_client.set_message_handler("ERROR_MESSAGE", collector1.handle_error_message)
        
        # 客户端2 (bob)
        client2 = ChatClient()
        client2.network_client.port = test_port
        collector2 = MessageCollector("Bob")
        client2.network_client.set_message_handler("CHAT_MESSAGE", collector2.handle_chat_message)
        client2.network_client.set_message_handler("SYSTEM_MESSAGE", collector2.handle_system_message)
        client2.network_client.set_message_handler("ERROR_MESSAGE", collector2.handle_error_message)
        
        # 连接到服务器
        print(f"🔗 连接到服务器 (端口: {test_port})...")
        if not client1.connect():
            print("❌ 客户端1连接失败")
            return False
        
        if not client2.connect():
            print("❌ 客户端2连接失败")
            return False
        
        # 注册和登录用户
        print("👤 注册和登录用户...")
        
        # 注册用户
        success, message = client1.register("alice", "password123")
        if not success:
            print(f"❌ Alice注册失败: {message}")
            return False
        
        success, message = client2.register("bob", "password123")
        if not success:
            print(f"❌ Bob注册失败: {message}")
            return False
        
        # 登录用户
        success, message = client1.login("alice", "password123")
        if not success:
            print(f"❌ Alice登录失败: {message}")
            return False
        
        success, message = client2.login("bob", "password123")
        if not success:
            print(f"❌ Bob登录失败: {message}")
            return False
        
        print("✅ 用户登录成功")
        print(f"   Alice当前聊天组: {client1.current_chat_group}")
        print(f"   Bob当前聊天组: {client2.current_chat_group}")
        
        # 等待状态稳定
        time.sleep(1)
        
        # 创建测试聊天组
        print("🏗️ 创建测试聊天组...")
        success, message = client2.create_chat_group("testroom", [])  # 不自动添加成员
        if not success:
            print(f"❌ 创建聊天组失败: {message}")
            return False
        
        # Bob进入testroom聊天组
        success, message = client2.enter_chat_group("testroom")
        if not success:
            print(f"❌ Bob进入testroom聊天组失败: {message}")
            return False
        
        print("✅ 聊天组设置完成")
        print(f"   Alice在聊天组: {client1.current_chat_group['name'] if client1.current_chat_group else 'None'}")
        print(f"   Bob在聊天组: {client2.current_chat_group['name'] if client2.current_chat_group else 'None'}")
        
        # 清空之前的消息记录
        collector1.clear_messages()
        collector2.clear_messages()
        
        # 等待状态更新
        time.sleep(1)
        
        # 测试消息隔离
        print("💬 测试消息隔离...")
        
        # Alice在public聊天组发送消息
        print("📤 Alice在public聊天组发送消息...")
        if client1.current_chat_group:
            group_id = client1.current_chat_group['id']
            success = client1.send_chat_message("Hello from public!", group_id)
            if not success:
                print("❌ Alice消息发送失败")
                return False
        else:
            print("❌ Alice未在聊天组中")
            return False
        
        # 等待消息传播
        time.sleep(1)
        
        # Bob在testroom聊天组发送消息
        print("📤 Bob在testroom聊天组发送消息...")
        if client2.current_chat_group:
            group_id = client2.current_chat_group['id']
            success = client2.send_chat_message("Hello from testroom!", group_id)
            if not success:
                print("❌ Bob消息发送失败")
                return False
        else:
            print("❌ Bob未在聊天组中")
            return False
        
        # 等待消息传播
        time.sleep(1)
        
        # Alice再发一条消息
        print("📤 Alice再次在public聊天组发送消息...")
        group_id = client1.current_chat_group['id']
        success = client1.send_chat_message("Another message from public!", group_id)
        if not success:
            print("❌ Alice第二条消息发送失败")
            return False
        
        # 等待消息传播
        time.sleep(1)
        
        # 检查消息隔离情况
        print("🔍 检查消息隔离情况...")
        
        # 获取各自收到的消息
        alice_messages = collector1.received_messages
        bob_messages = collector2.received_messages
        
        print(f"   Alice收到消息数量: {len(alice_messages)}")
        for msg in alice_messages:
            print(f"     - {msg['sender']}: {msg['content']} (组ID: {msg['chat_group_id']})")
        
        print(f"   Bob收到消息数量: {len(bob_messages)}")
        for msg in bob_messages:
            print(f"     - {msg['sender']}: {msg['content']} (组ID: {msg['chat_group_id']})")
        
        # 验证消息隔离
        public_group_id = client1.current_chat_group['id']
        testroom_group_id = client2.current_chat_group['id']
        
        # Alice应该只收到public聊天组的消息
        alice_public_messages = [msg for msg in alice_messages if msg['chat_group_id'] == public_group_id]
        alice_testroom_messages = [msg for msg in alice_messages if msg['chat_group_id'] == testroom_group_id]
        
        # Bob应该只收到testroom聊天组的消息
        bob_public_messages = [msg for msg in bob_messages if msg['chat_group_id'] == public_group_id]
        bob_testroom_messages = [msg for msg in bob_messages if msg['chat_group_id'] == testroom_group_id]
        
        print("\n📊 消息隔离验证结果:")
        print(f"   Alice收到public组消息: {len(alice_public_messages)}")
        print(f"   Alice收到testroom组消息: {len(alice_testroom_messages)}")
        print(f"   Bob收到public组消息: {len(bob_public_messages)}")
        print(f"   Bob收到testroom组消息: {len(bob_testroom_messages)}")
        
        # 验证结果
        success = True
        
        if len(alice_testroom_messages) > 0:
            print("❌ 错误：Alice收到了testroom聊天组的消息（应该被隔离）")
            success = False
        
        if len(bob_public_messages) > 0:
            print("❌ 错误：Bob收到了public聊天组的消息（应该被隔离）")
            success = False
        
        if len(alice_public_messages) != 2:
            print(f"❌ 错误：Alice应该收到2条public组消息，实际收到{len(alice_public_messages)}条")
            success = False
        
        if len(bob_testroom_messages) != 1:
            print(f"❌ 错误：Bob应该收到1条testroom组消息，实际收到{len(bob_testroom_messages)}条")
            success = False
        
        if success:
            print("✅ 消息隔离测试通过！")
            print("   - 不同聊天组的消息正确隔离")
            print("   - 用户只能看到当前聊天组的消息")
            print("   - 服务器端和客户端过滤都正常工作")
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
    success = test_message_isolation_final()
    
    if success:
        print("\n🎉 消息隔离修复验证成功！")
        print("📝 修复总结:")
        print("- 服务器端只向当前在聊天组中的用户广播消息")
        print("- 客户端消息过滤逻辑正确工作")
        print("- 创建聊天组时不再自动添加其他用户为成员")
        print("- 不同聊天组之间的消息完全隔离")
    else:
        print("\n❌ 消息隔离修复验证失败")
        print("需要进一步检查和修复")
    
    sys.exit(0 if success else 1)
