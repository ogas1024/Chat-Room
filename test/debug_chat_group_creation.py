#!/usr/bin/env python3
"""
调试聊天组创建和进入问题
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
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 检查数据库状态失败: {e}")


def test_chat_group_creation():
    """测试聊天组创建和进入"""
    print("🧪 开始测试聊天组创建和进入...")
    
    # 使用测试端口和数据库
    test_port = 9996
    test_db_path = "test/test_debug_creation.db"
    
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
    init_logger(logging_config, "test_debug_creation")
    
    # 启动服务器
    print(f"🚀 启动测试服务器 (端口: {test_port})...")
    server = ChatRoomServer(DEFAULT_HOST, test_port)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    try:
        # 创建客户端
        print("👤 创建测试客户端...")
        
        client = ChatClient()
        client.network_client.port = test_port
        
        # 连接到服务器
        print(f"🔗 连接到服务器 (端口: {test_port})...")
        if not client.connect():
            print("❌ 客户端连接失败")
            return False
        
        # 注册和登录用户
        print("👤 注册和登录用户...")
        
        success, message = client.register("testuser", "password123")
        if not success:
            print(f"❌ 用户注册失败: {message}")
            return False
        
        success, message = client.login("testuser", "password123")
        if not success:
            print(f"❌ 用户登录失败: {message}")
            return False
        
        print("✅ 用户登录成功")
        print(f"   当前聊天组: {client.current_chat_group}")
        
        # 检查登录后的数据库状态
        check_database_state(test_db_path, "用户登录后")
        
        # 创建测试聊天组
        print("🏗️ 创建测试聊天组...")
        success, message = client.create_chat_group("testroom", [])
        if not success:
            print(f"❌ 创建聊天组失败: {message}")
            return False
        
        print("✅ 聊天组创建成功")
        
        # 检查聊天组创建后的数据库状态
        check_database_state(test_db_path, "聊天组创建后")
        
        # 尝试进入聊天组
        print("🚪 尝试进入聊天组...")
        success, message = client.enter_chat_group("testroom")
        if not success:
            print(f"❌ 进入聊天组失败: {message}")
            return False
        
        print("✅ 成功进入聊天组")
        print(f"   当前聊天组: {client.current_chat_group}")
        
        # 检查进入聊天组后的数据库状态
        check_database_state(test_db_path, "进入聊天组后")
        
        # 尝试发送消息
        print("💬 尝试发送消息...")
        if client.current_chat_group:
            group_id = client.current_chat_group['id']
            success = client.send_chat_message("Hello from testroom!", group_id)
            if not success:
                print("❌ 消息发送失败")
                return False
            print("✅ 消息发送成功")
        else:
            print("❌ 用户未在聊天组中")
            return False
        
        # 等待消息传播
        time.sleep(1)
        
        # 检查消息发送后的数据库状态
        check_database_state(test_db_path, "消息发送后")
        
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
            if 'client' in locals():
                client.disconnect()
        except:
            pass
        
        try:
            server.stop()
        except:
            pass
        
        # 保留测试数据库以供分析
        print(f"📁 测试数据库保存在: {test_db_path}")


if __name__ == "__main__":
    success = test_chat_group_creation()
    
    if success:
        print("\n🎉 聊天组创建和进入测试完成！")
    else:
        print("\n❌ 聊天组创建和进入测试失败")
    
    sys.exit(0 if success else 1)
