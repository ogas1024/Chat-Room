#!/usr/bin/env python3
"""
基础消息隔离测试
验证重构后的核心功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_database_isolation():
    """测试数据库层面的消息隔离"""
    print("🔍 测试数据库层面的消息隔离...")
    
    from server.database.connection import DatabaseConnection
    import tempfile
    import os
    
    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_isolation.db")
    DatabaseConnection.set_database_path(db_path)
    
    db = DatabaseConnection.get_instance()
    
    try:
        # 创建测试用户
        user1_id = db.create_user("user1", "password123")
        user2_id = db.create_user("user2", "password123")
        print(f"✅ 创建用户: user1({user1_id}), user2({user2_id})")
        
        # 创建两个聊天组
        group1_id = db.create_chat_group("group1", False)
        group2_id = db.create_chat_group("group2", False)
        print(f"✅ 创建聊天组: group1({group1_id}), group2({group2_id})")
        
        # 用户加入聊天组
        db.add_user_to_chat_group(group1_id, user1_id)
        db.add_user_to_chat_group(group2_id, user2_id)
        print("✅ 用户加入聊天组")
        
        # 在不同聊天组发送消息
        msg1_id = db.save_message(group1_id, user1_id, "Message in group1")
        msg2_id = db.save_message(group2_id, user2_id, "Message in group2")
        print(f"✅ 发送消息: msg1({msg1_id}), msg2({msg2_id})")
        
        # 验证消息隔离
        group1_history = db.get_chat_history(group1_id, 10)
        group2_history = db.get_chat_history(group2_id, 10)
        
        print(f"📊 Group1历史消息数量: {len(group1_history)}")
        print(f"📊 Group2历史消息数量: {len(group2_history)}")
        
        # 检查消息内容
        group1_contents = [msg['content'] for msg in group1_history]
        group2_contents = [msg['content'] for msg in group2_history]
        
        print(f"📝 Group1消息内容: {group1_contents}")
        print(f"📝 Group2消息内容: {group2_contents}")
        
        # 验证隔离
        assert "Message in group1" in group1_contents, "Group1应该包含自己的消息"
        assert "Message in group2" not in group1_contents, "Group1不应该包含Group2的消息"
        assert "Message in group2" in group2_contents, "Group2应该包含自己的消息"
        assert "Message in group1" not in group2_contents, "Group2不应该包含Group1的消息"
        
        print("✅ 数据库层面的消息隔离测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理
        DatabaseConnection.close()
        try:
            os.remove(db_path)
        except:
            pass


def test_chat_manager_isolation():
    """测试聊天管理器的消息隔离"""
    print("🔍 测试聊天管理器的消息隔离...")
    
    from server.core.chat_manager import ChatManager
    from server.core.user_manager import UserManager
    from server.database.connection import DatabaseConnection
    import tempfile
    import os
    
    # 创建临时数据库
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_chat_manager.db")
    DatabaseConnection.set_database_path(db_path)
    
    try:
        # 创建管理器
        user_manager = UserManager()
        chat_manager = ChatManager(user_manager)
        
        # 注册用户
        user1_id = user_manager.register_user("chatuser1", "password123")
        user2_id = user_manager.register_user("chatuser2", "password123")
        print(f"✅ 注册用户: chatuser1({user1_id}), chatuser2({user2_id})")
        
        # 创建聊天组
        group1_id = chat_manager.create_chat_group("chatgroup1", user1_id)
        group2_id = chat_manager.create_chat_group("chatgroup2", user2_id)
        print(f"✅ 创建聊天组: chatgroup1({group1_id}), chatgroup2({group2_id})")
        
        # 发送消息
        msg1 = chat_manager.send_message(user1_id, group1_id, "Hello from chatgroup1")
        msg2 = chat_manager.send_message(user2_id, group2_id, "Hello from chatgroup2")
        print(f"✅ 发送消息: {msg1.content}, {msg2.content}")
        
        # 验证消息隔离
        history1 = chat_manager.get_chat_history(group1_id, user1_id, 10)
        history2 = chat_manager.get_chat_history(group2_id, user2_id, 10)
        
        print(f"📊 Chatgroup1历史消息数量: {len(history1)}")
        print(f"📊 Chatgroup2历史消息数量: {len(history2)}")
        
        # 检查消息内容
        contents1 = [msg['content'] for msg in history1]
        contents2 = [msg['content'] for msg in history2]
        
        print(f"📝 Chatgroup1消息内容: {contents1}")
        print(f"📝 Chatgroup2消息内容: {contents2}")
        
        # 验证隔离
        assert "Hello from chatgroup1" in contents1, "Chatgroup1应该包含自己的消息"
        assert "Hello from chatgroup2" not in contents1, "Chatgroup1不应该包含Chatgroup2的消息"
        assert "Hello from chatgroup2" in contents2, "Chatgroup2应该包含自己的消息"
        assert "Hello from chatgroup1" not in contents2, "Chatgroup2不应该包含Chatgroup1的消息"
        
        print("✅ 聊天管理器的消息隔离测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 聊天管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理
        DatabaseConnection.close()
        try:
            os.remove(db_path)
        except:
            pass


def main():
    """主测试函数"""
    print("🚀 开始基础消息隔离测试...")
    
    success1 = test_database_isolation()
    success2 = test_chat_manager_isolation()
    
    if success1 and success2:
        print("🎉 所有基础测试通过！消息隔离功能正常工作。")
        return True
    else:
        print("❌ 部分测试失败，请检查代码。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
