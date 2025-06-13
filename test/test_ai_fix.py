#!/usr/bin/env python3
"""
AI功能修复测试脚本
测试AI用户的创建、权限和消息发送功能
"""

import sys
import os
import sqlite3
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.database.models import DatabaseManager
from server.core.chat_manager import ChatManager
from server.core.user_manager import UserManager
from shared.constants import AI_USER_ID, AI_USERNAME, DEFAULT_PUBLIC_CHAT


def test_ai_user_creation():
    """测试AI用户创建"""
    print("🧪 测试AI用户创建...")
    
    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # 初始化数据库
        db = DatabaseManager(db_path)
        
        # 检查AI用户是否存在
        try:
            ai_user = db.get_user_by_id(AI_USER_ID)
            print(f"✅ AI用户已创建: {ai_user}")
            assert ai_user['username'] == AI_USERNAME
            assert ai_user['id'] == AI_USER_ID
        except Exception as e:
            print(f"❌ AI用户创建失败: {e}")
            return False
        
        # 检查AI用户是否在public聊天组中
        try:
            public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
            is_in_group = db.is_user_in_chat_group(public_group['id'], AI_USER_ID)
            print(f"✅ AI用户在public聊天组中: {is_in_group}")
            assert is_in_group
        except Exception as e:
            print(f"❌ AI用户聊天组检查失败: {e}")
            return False
        
        return True
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)


def test_ai_message_sending():
    """测试AI消息发送"""
    print("🧪 测试AI消息发送...")
    
    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # 初始化数据库和管理器
        db = DatabaseManager(db_path)
        user_manager = UserManager()
        user_manager.db = db  # 使用测试数据库
        chat_manager = ChatManager(user_manager)
        chat_manager.db = db  # 使用测试数据库
        
        # 获取public聊天组
        public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
        group_id = public_group['id']
        
        # 测试AI用户发送消息
        try:
            ai_message = chat_manager.send_message(
                AI_USER_ID, group_id, "Hello, this is AI test message!"
            )
            print(f"✅ AI消息发送成功: {ai_message.content}")
            assert ai_message.sender_id == AI_USER_ID
            assert ai_message.sender_username == AI_USERNAME
            assert ai_message.chat_group_id == group_id
        except Exception as e:
            print(f"❌ AI消息发送失败: {e}")
            return False
        
        return True
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)


def test_new_chat_group_ai_addition():
    """测试新聊天组自动添加AI用户"""
    print("🧪 测试新聊天组自动添加AI用户...")
    
    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    
    try:
        # 初始化数据库和管理器
        db = DatabaseManager(db_path)
        user_manager = UserManager()
        user_manager.db = db  # 使用测试数据库
        chat_manager = ChatManager(user_manager)
        chat_manager.db = db  # 使用测试数据库
        
        # 创建测试用户
        test_user_id = db.create_user("testuser", "password123")
        
        # 创建新的群聊
        group_id = chat_manager.create_chat_group("test_group", test_user_id)
        
        # 检查AI用户是否被自动添加
        try:
            is_ai_in_group = db.is_user_in_chat_group(group_id, AI_USER_ID)
            print(f"✅ AI用户自动添加到新群聊: {is_ai_in_group}")
            assert is_ai_in_group
        except Exception as e:
            print(f"❌ AI用户自动添加失败: {e}")
            return False
        
        # 测试AI在新群聊中发送消息
        try:
            ai_message = chat_manager.send_message(
                AI_USER_ID, group_id, "Hello in new group!"
            )
            print(f"✅ AI在新群聊中发送消息成功: {ai_message.content}")
        except Exception as e:
            print(f"❌ AI在新群聊中发送消息失败: {e}")
            return False
        
        return True
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)


def main():
    """主测试函数"""
    print("=" * 50)
    print("🤖 AI功能修复测试")
    print("=" * 50)
    
    tests = [
        test_ai_user_creation,
        test_ai_message_sending,
        test_new_chat_group_ai_addition,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ 测试通过\n")
            else:
                print("❌ 测试失败\n")
        except Exception as e:
            print(f"❌ 测试异常: {e}\n")
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    print("=" * 50)
    
    if passed == total:
        print("🎉 所有测试通过！AI功能修复成功！")
        return True
    else:
        print("⚠️  部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
