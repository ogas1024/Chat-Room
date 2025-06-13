#!/usr/bin/env python3
"""
AI功能集成测试
模拟完整的AI消息处理流程
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.core.server import ChatRoomServer
from server.core.user_manager import UserManager
from server.core.chat_manager import ChatManager
from server.ai.ai_manager import AIManager
from server.config.ai_config import get_ai_config
from server.database.connection import get_db
from shared.constants import AI_USER_ID, DEFAULT_PUBLIC_CHAT
from shared.messages import ChatMessage


def test_ai_message_processing():
    """测试AI消息处理流程"""
    print("🧪 测试AI消息处理流程...")
    
    try:
        # 初始化管理器
        db = get_db()
        user_manager = UserManager()
        chat_manager = ChatManager(user_manager)
        
        # 创建一个简化的AI管理器用于测试
        class TestAIManager:
            def __init__(self):
                self.enabled = True

            def is_enabled(self):
                return self.enabled

            def should_respond_to_message(self, message_content, is_group_chat=True):
                """简化的消息响应判断"""
                if not self.is_enabled():
                    return False

                message_lower = message_content.lower()
                # 检查@AI
                if "@ai" in message_lower:
                    return True
                return False

        ai_manager = TestAIManager()
        
        # 获取测试用户和聊天组
        try:
            test_user = db.get_user_by_username("test1")
            public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
        except Exception as e:
            print(f"❌ 获取测试数据失败: {e}")
            print("💡 请确保数据库中存在test1用户和public聊天组")
            return False
        
        # 模拟用户发送@AI消息
        user_message_content = "@AI hello"
        print(f"📝 模拟用户消息: {user_message_content}")
        
        # 保存用户消息
        user_message_id = db.save_message(
            public_group['id'], 
            test_user['id'], 
            user_message_content
        )
        print(f"✅ 用户消息已保存，ID: {user_message_id}")
        
        # 检查AI是否应该回复
        should_respond = ai_manager.should_respond_to_message(
            user_message_content, 
            is_group_chat=True
        )
        print(f"🤖 AI应该回复: {should_respond}")
        
        if should_respond:
            # 模拟AI回复（不调用真实API）
            ai_reply = "Hello! This is a test AI reply."
            print(f"💬 模拟AI回复: {ai_reply}")
            
            # 测试AI消息发送权限
            try:
                ai_message = chat_manager.send_message(
                    AI_USER_ID, 
                    public_group['id'], 
                    ai_reply
                )
                print(f"✅ AI消息发送成功:")
                print(f"   - 消息ID: {ai_message.message_id}")
                print(f"   - 发送者: {ai_message.sender_username}")
                print(f"   - 内容: {ai_message.content}")
                print(f"   - 聊天组: {ai_message.chat_group_name}")
                
                return True
                
            except Exception as e:
                print(f"❌ AI消息发送失败: {e}")
                return False
        else:
            print("❌ AI不应该回复此消息")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False


def test_ai_user_permissions():
    """测试AI用户权限"""
    print("🧪 测试AI用户权限...")
    
    try:
        db = get_db()
        
        # 检查AI用户是否存在
        try:
            ai_user = db.get_user_by_id(AI_USER_ID)
            print(f"✅ AI用户存在: {ai_user}")
        except Exception as e:
            print(f"❌ AI用户不存在: {e}")
            return False
        
        # 检查AI用户在public聊天组中的权限
        try:
            public_group = db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
            is_member = db.is_user_in_chat_group(public_group['id'], AI_USER_ID)
            print(f"✅ AI用户在public聊天组中: {is_member}")
            
            if not is_member:
                print("❌ AI用户不在public聊天组中")
                return False
                
        except Exception as e:
            print(f"❌ 检查AI用户聊天组权限失败: {e}")
            return False
        
        # 检查AI用户在所有聊天组中的成员资格
        try:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) as count FROM group_members WHERE user_id = ?",
                    (AI_USER_ID,)
                )
                group_count = cursor.fetchone()['count']
                print(f"✅ AI用户是 {group_count} 个聊天组的成员")

                if group_count == 0:
                    print("❌ AI用户不在任何聊天组中")
                    return False

        except Exception as e:
            print(f"❌ 检查AI用户聊天组成员资格失败: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🤖 AI功能集成测试")
    print("=" * 60)
    
    tests = [
        ("AI用户权限测试", test_ai_user_permissions),
        ("AI消息处理测试", test_ai_message_processing),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print("✅ 测试通过")
            else:
                print("❌ 测试失败")
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI功能权限修复成功！")
        print("💡 现在可以启动服务器测试完整的AI功能")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
