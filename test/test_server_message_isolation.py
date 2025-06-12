#!/usr/bin/env python3
"""
测试服务器端消息隔离逻辑
验证服务器是否正确处理聊天组成员关系和消息广播
"""

import os
import sys
import time
import threading
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from server.core.server import ChatRoomServer
from client.core.client import ChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT
from shared.logger import init_logger, get_logger
from server.database.connection import DatabaseConnection


def check_database_state(db_path: str, test_name: str):
    """检查数据库状态"""
    print(f"\n🔍 检查数据库状态 - {test_name}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查用户表
        cursor.execute("SELECT id, username, is_online FROM users")
        users = cursor.fetchall()
        print("👥 用户列表:")
        for user in users:
            print(f"   ID: {user[0]}, 用户名: {user[1]}, 在线: {user[2]}")
        
        # 检查聊天组表
        cursor.execute("SELECT id, name, is_private_chat FROM chat_groups")
        groups = cursor.fetchall()
        print("💬 聊天组列表:")
        for group in groups:
            print(f"   ID: {group[0]}, 名称: {group[1]}, 私聊: {group[2]}")
        
        # 检查聊天组成员关系
        cursor.execute("""
            SELECT cgm.chat_group_id, cg.name, cgm.user_id, u.username 
            FROM chat_group_members cgm
            JOIN chat_groups cg ON cgm.chat_group_id = cg.id
            JOIN users u ON cgm.user_id = u.id
            ORDER BY cgm.chat_group_id, cgm.user_id
        """)
        memberships = cursor.fetchall()
        print("🔗 聊天组成员关系:")
        for membership in memberships:
            print(f"   聊天组 '{membership[1]}' (ID: {membership[0]}) - 用户 '{membership[3]}' (ID: {membership[2]})")
        
        # 检查消息表
        cursor.execute("""
            SELECT m.id, m.chat_group_id, cg.name, m.sender_id, u.username, m.content
            FROM messages m
            JOIN chat_groups cg ON m.chat_group_id = cg.id
            JOIN users u ON m.sender_id = u.id
            ORDER BY m.id
        """)
        messages = cursor.fetchall()
        print("📝 消息列表:")
        for message in messages:
            print(f"   消息ID: {message[0]}, 聊天组: '{message[2]}' (ID: {message[1]}), 发送者: '{message[4]}' (ID: {message[3]}), 内容: {message[5]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据库状态失败: {e}")


def test_server_message_isolation():
    """测试服务器端消息隔离"""
    print("🧪 开始测试服务器端消息隔离...")
    
    # 使用测试端口和数据库
    test_port = 9998
    test_db_path = "test/test_server_isolation.db"
    
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
    init_logger(logging_config, "test_server_isolation")
    
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
        
        # 客户端1 (testuser1)
        client1 = ChatClient()
        client1.network_client.port = test_port
        
        # 客户端2 (testuser2)
        client2 = ChatClient()
        client2.network_client.port = test_port
        
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
        
        # 检查初始数据库状态
        check_database_state(test_db_path, "用户登录后")
        
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
        
        print("✅ 聊天组设置完成")
        print(f"   用户1在聊天组: {client1.current_chat_group['name'] if client1.current_chat_group else 'None'}")
        print(f"   用户2在聊天组: {client2.current_chat_group['name'] if client2.current_chat_group else 'None'}")
        
        # 检查聊天组创建后的数据库状态
        check_database_state(test_db_path, "聊天组创建后")
        
        # 等待状态更新
        time.sleep(1)
        
        # 测试消息发送
        print("💬 测试消息发送...")
        
        # 用户1在public聊天组发送消息
        print("📤 用户1在public聊天组发送消息...")
        if client1.current_chat_group:
            group_id = client1.current_chat_group['id']
            print(f"   发送到聊天组ID: {group_id}")
            success = client1.send_chat_message("hello from public", group_id)
            if not success:
                print("❌ 用户1消息发送失败")
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
            print(f"   发送到聊天组ID: {group_id}")
            success = client2.send_chat_message("hello from testgroup", group_id)
            if not success:
                print("❌ 用户2消息发送失败")
                return False
        else:
            print("❌ 用户2未在聊天组中")
            return False
        
        # 等待消息传播
        time.sleep(1)
        
        # 检查消息发送后的数据库状态
        check_database_state(test_db_path, "消息发送后")
        
        print("✅ 服务器端消息隔离测试完成")
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
        
        # 保留测试数据库以供分析
        print(f"📁 测试数据库保存在: {test_db_path}")


if __name__ == "__main__":
    success = test_server_message_isolation()
    
    if success:
        print("\n🎉 服务器端消息隔离测试完成！")
        print("📝 请检查数据库状态和日志以分析问题")
    else:
        print("\n❌ 服务器端消息隔离测试失败")
    
    sys.exit(0 if success else 1)
