#!/usr/bin/env python3
"""
集成测试：验证聊天组邀请功能的完整流程
测试从创建聊天组到用户进入聊天组的完整过程
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from server.database.models import DatabaseManager
from server.core.chat_manager import ChatManager
from server.core.user_manager import UserManager
from shared.constants import AI_USER_ID


def setup_test_environment():
    """设置测试环境"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    # 初始化数据库和管理器
    db_manager = DatabaseManager(db_path)
    db_manager.init_database()

    user_manager = UserManager()
    chat_manager = ChatManager(user_manager)

    return db_manager, user_manager, chat_manager, db_path


def create_test_users(db_manager):
    """创建测试用户"""
    test_user_id = db_manager.create_user("test", "test123")
    test1_user_id = db_manager.create_user("test1", "test123")
    return test_user_id, test1_user_id


def test_complete_invite_flow():
    """测试完整的邀请流程"""
    print("🧪 开始集成测试：聊天组邀请功能完整流程")
    print("=" * 60)
    
    # 设置测试环境
    db_manager, user_manager, chat_manager, db_path = setup_test_environment()
    
    try:
        # 创建测试用户
        test_user_id, test1_user_id = create_test_users(db_manager)
        print(f"✅ 创建测试用户:")
        print(f"   - test (ID: {test_user_id})")
        print(f"   - test1 (ID: {test1_user_id})")
        print(f"   - AI助手 (ID: {AI_USER_ID})")
        
        # 步骤1: 创建聊天组并邀请用户
        print(f"\n📝 步骤1: test用户创建聊天组并邀请test1用户")
        group_id = chat_manager.create_chat_group(
            name="test_invite_group",
            creator_id=test_user_id,
            initial_members=[test_user_id, test1_user_id],  # 邀请test和test1
            is_private_chat=False
        )
        print(f"✅ 创建聊天组 'test_invite_group' (ID: {group_id})")
        
        # 步骤2: 验证创建者在聊天组中
        print(f"\n📝 步骤2: 验证创建者test是否在聊天组中")
        is_creator_in_group = chat_manager.db.is_user_in_chat_group(group_id, test_user_id)
        print(f"✅ 创建者test在聊天组中: {is_creator_in_group}")
        assert is_creator_in_group, "创建者应该在聊天组中"

        # 步骤3: 验证被邀请用户在聊天组中（这是修复的关键）
        print(f"\n📝 步骤3: 验证被邀请用户test1是否在聊天组中")
        is_test1_in_group = chat_manager.db.is_user_in_chat_group(group_id, test1_user_id)
        print(f"✅ 被邀请用户test1在聊天组中: {is_test1_in_group}")
        assert is_test1_in_group, "被邀请用户应该在聊天组中"

        # 步骤4: 验证AI用户在聊天组中
        print(f"\n📝 步骤4: 验证AI用户是否在聊天组中")
        is_ai_in_group = chat_manager.db.is_user_in_chat_group(group_id, AI_USER_ID)
        print(f"✅ AI用户在聊天组中: {is_ai_in_group}")
        assert is_ai_in_group, "AI用户应该在聊天组中"

        # 步骤5: 获取聊天组成员列表
        print(f"\n📝 步骤5: 获取聊天组成员列表")
        members = chat_manager.db.get_chat_group_members(group_id)
        print(f"✅ 聊天组成员数量: {len(members)}")
        print("聊天组成员:")
        for member in members:
            print(f"   - {member['username']} (ID: {member['id']})")

        # 验证成员数量
        expected_members = 3  # test, test1, AI助手
        assert len(members) == expected_members, f"聊天组应该有{expected_members}个成员，实际有{len(members)}个"
        
        # 步骤6: 测试test1用户能否进入聊天组
        print(f"\n📝 步骤6: 测试test1用户能否进入聊天组")
        try:
            group_info = chat_manager.enter_chat_group("test_invite_group", test1_user_id)
            print(f"✅ test1用户成功进入聊天组: {group_info['name']}")
        except Exception as e:
            print(f"❌ test1用户进入聊天组失败: {e}")
            raise
        
        # 步骤7: 测试获取聊天组成员（从test1用户的角度）
        print(f"\n📝 步骤7: 从test1用户角度获取聊天组成员")
        try:
            members_from_test1 = chat_manager.get_chat_group_members(group_id, test1_user_id)
            print(f"✅ test1用户可以查看聊天组成员，数量: {len(members_from_test1)}")
            print("从test1用户角度看到的成员:")
            for member in members_from_test1:
                status = "在线" if member.is_online else "离线"
                print(f"   - {member.username} - {status}")
        except Exception as e:
            print(f"❌ test1用户获取聊天组成员失败: {e}")
            raise
        
        print(f"\n🎉 集成测试通过！聊天组邀请功能完全正常！")
        return True
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理测试数据库
        try:
            os.unlink(db_path)
            print(f"🧹 清理测试数据库: {db_path}")
        except:
            pass


def test_edge_cases():
    """测试边界情况"""
    print(f"\n🧪 测试边界情况")
    print("=" * 60)

    # 设置测试环境
    db_manager, user_manager, chat_manager, db_path = setup_test_environment()

    try:
        # 创建测试用户
        test_user_id, test1_user_id = create_test_users(db_manager)

        # 测试1: 创建聊天组时重复邀请创建者
        print(f"\n📝 测试1: 创建聊天组时重复邀请创建者")
        group_id = chat_manager.create_chat_group(
            name="test_duplicate_edge",
            creator_id=test_user_id,
            initial_members=[test_user_id, test_user_id, test1_user_id],  # 重复邀请test
            is_private_chat=False
        )

        members = chat_manager.db.get_chat_group_members(group_id)
        test_count = sum(1 for m in members if m['username'] == 'test')
        print(f"✅ 创建者test在聊天组中的数量: {test_count} (应该为1)")
        assert test_count == 1, "创建者不应该被重复添加"

        # 测试2: 邀请不存在的用户
        print(f"\n📝 测试2: 邀请不存在的用户")
        group_id2 = chat_manager.create_chat_group(
            name="test_nonexistent_edge",
            creator_id=test_user_id,
            initial_members=[test1_user_id, 999],  # 999是不存在的用户ID
            is_private_chat=False
        )

        members2 = chat_manager.db.get_chat_group_members(group_id2)
        print(f"✅ 聊天组成员数量: {len(members2)} (不存在的用户应该被忽略)")
        # 应该包含：test(创建者), test1(有效邀请), AI助手
        assert len(members2) == 3, "不存在的用户应该被忽略"

        print(f"\n🎉 边界情况测试通过！")
        return True

    except Exception as e:
        print(f"\n❌ 边界情况测试失败: {e}")
        return False

    finally:
        try:
            os.unlink(db_path)
        except:
            pass


if __name__ == "__main__":
    print("=" * 60)
    print("聊天组邀请功能集成测试")
    print("=" * 60)
    
    # 运行测试
    test1_passed = test_complete_invite_flow()
    test2_passed = test_edge_cases()
    
    print("\n" + "=" * 60)
    print("📊 集成测试结果总结")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("🎉 所有集成测试通过！")
        print("✅ 聊天组用户邀请功能修复完全成功！")
        print("✅ 现在用户可以正常使用 /create_chat 命令邀请其他用户")
        print("✅ 被邀请的用户可以直接进入聊天组，无需额外操作")
        sys.exit(0)
    else:
        print("❌ 部分集成测试失败！")
        sys.exit(1)
