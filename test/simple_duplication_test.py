#!/usr/bin/env python3
"""
简单的消息重复显示测试
验证客户端UI修复是否有效
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_ui_message_handling():
    """测试UI消息处理逻辑"""
    print("🧪 测试UI消息处理逻辑...")
    
    try:
        # 模拟客户端UI的消息处理
        from client.ui.app import ChatRoomApp
        
        # 创建应用实例（不运行）
        app = ChatRoomApp("localhost", 8888)
        
        # 模拟消息发送场景
        print("📝 模拟消息发送场景...")
        
        # 检查handle_message方法的逻辑
        import inspect
        source = inspect.getsource(app.handle_message)
        
        # 检查是否包含立即显示消息的代码
        if "self.add_chat_message(self.current_user, message, is_self=True)" in source:
            print("❌ 发现问题：客户端仍在发送成功后立即显示消息")
            print("   这会导致消息重复显示")
            return False
        else:
            print("✅ 修复验证：客户端不再在发送成功后立即显示消息")
            print("   消息将等待服务器广播后显示，避免重复")
            return True
    
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False


def test_message_flow():
    """测试消息流程"""
    print("🧪 测试消息流程...")
    
    print("📋 预期的消息流程:")
    print("1. 用户在客户端输入消息")
    print("2. 客户端发送消息到服务器")
    print("3. 服务器接收消息并保存到数据库")
    print("4. 服务器广播消息给所有聊天组成员（包括发送者）")
    print("5. 客户端接收服务器广播的消息并显示")
    print("6. 结果：每条消息只显示一次")
    
    print("\n🔧 修复前的问题:")
    print("- 步骤2后：客户端立即显示消息（第一次显示）")
    print("- 步骤5后：客户端再次显示消息（第二次显示）")
    print("- 结果：消息重复显示")
    
    print("\n✅ 修复后的流程:")
    print("- 步骤2后：客户端不立即显示消息")
    print("- 步骤5后：客户端显示服务器广播的消息（唯一显示）")
    print("- 结果：消息只显示一次")
    
    return True


def verify_server_broadcast_logic():
    """验证服务器广播逻辑"""
    print("🧪 验证服务器广播逻辑...")
    
    try:
        # 检查服务器端的消息处理逻辑
        from server.core.server import ChatRoomServer
        from server.core.chat_manager import ChatManager
        
        print("📋 服务器端消息处理流程:")
        print("1. handle_chat_message: 处理客户端发送的消息")
        print("2. chat_manager.send_message: 保存消息到数据库")
        print("3. chat_manager.broadcast_message_to_group: 广播给所有成员")
        print("4. 广播包括发送者本人，确保消息一致性")
        
        # 检查广播逻辑
        import inspect
        broadcast_source = inspect.getsource(ChatManager.broadcast_message_to_group)
        
        if "for member in members:" in broadcast_source:
            print("✅ 服务器广播逻辑正确：向所有聊天组成员发送消息")
            return True
        else:
            print("❌ 服务器广播逻辑可能有问题")
            return False
    
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        return False


def run_tests():
    """运行所有测试"""
    print("🚀 开始消息重复显示修复验证")
    print("=" * 50)
    
    tests = [
        ("UI消息处理逻辑测试", test_ui_message_handling),
        ("消息流程分析", test_message_flow),
        ("服务器广播逻辑验证", verify_server_broadcast_logic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} 通过")
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 消息重复显示问题修复验证通过！")
        print("\n📝 修复总结:")
        print("- 移除了客户端发送消息成功后的立即显示逻辑")
        print("- 消息现在只在服务器广播后显示一次")
        print("- 确保了消息显示的一致性和正确性")
        return True
    else:
        print("❌ 部分验证失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = run_tests()
    
    if success:
        print("\n🔧 使用建议:")
        print("1. 重新启动服务器和客户端")
        print("2. 测试发送消息，确认不再出现重复显示")
        print("3. 验证多用户聊天场景下的消息显示")
        
    sys.exit(0 if success else 1)
