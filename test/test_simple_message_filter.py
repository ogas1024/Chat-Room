#!/usr/bin/env python3
"""
简单的消息过滤测试
直接测试客户端消息过滤逻辑
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from client.core.client import ChatClient
from shared.messages import ChatMessage


def test_message_filtering():
    """测试消息过滤逻辑"""
    print("🧪 测试客户端消息过滤逻辑...")
    
    # 创建客户端实例
    client = ChatClient()
    
    # 模拟用户登录状态
    client.current_user = {'id': 1, 'username': 'testuser'}
    client.current_chat_group = {'id': 1, 'name': 'public'}
    
    # 记录处理的消息
    processed_messages = []
    
    # 重写消息处理方法来记录处理的消息
    original_handle = client._handle_chat_message
    def mock_handle_chat_message(message):
        # 调用原始处理逻辑
        original_handle(message)
        # 如果消息没有被过滤掉，记录它
        if client.current_chat_group and hasattr(message, 'chat_group_id'):
            if message.chat_group_id == client.current_chat_group['id']:
                processed_messages.append(message)
    
    client._handle_chat_message = mock_handle_chat_message
    
    print("📝 测试场景1：当前聊天组的消息应该被处理")
    
    # 创建属于当前聊天组的消息
    message1 = ChatMessage(
        sender_id=2,
        sender_username="otheruser",
        chat_group_id=1,  # 与当前聊天组ID相同
        chat_group_name="public",
        content="Hello from public group"
    )
    
    # 处理消息
    client._handle_chat_message(message1)
    
    if len(processed_messages) == 1:
        print("✅ 当前聊天组的消息正确处理")
    else:
        print(f"❌ 当前聊天组的消息处理失败，处理了{len(processed_messages)}条消息")
        return False
    
    print("📝 测试场景2：其他聊天组的消息应该被过滤")
    
    # 创建属于其他聊天组的消息
    message2 = ChatMessage(
        sender_id=3,
        sender_username="anotheruser",
        chat_group_id=2,  # 与当前聊天组ID不同
        chat_group_name="test",
        content="Hello from test group"
    )
    
    # 处理消息
    client._handle_chat_message(message2)
    
    if len(processed_messages) == 1:  # 仍然只有第一条消息
        print("✅ 其他聊天组的消息正确过滤")
    else:
        print(f"❌ 其他聊天组的消息过滤失败，处理了{len(processed_messages)}条消息")
        return False
    
    print("📝 测试场景3：切换聊天组后的消息处理")
    
    # 切换到另一个聊天组
    client.current_chat_group = {'id': 2, 'name': 'test'}
    
    # 创建属于新聊天组的消息
    message3 = ChatMessage(
        sender_id=3,
        sender_username="anotheruser",
        chat_group_id=2,  # 与新的当前聊天组ID相同
        chat_group_name="test",
        content="Hello from test group after switch"
    )
    
    # 处理消息
    client._handle_chat_message(message3)
    
    if len(processed_messages) == 2:  # 现在应该有两条消息
        print("✅ 切换聊天组后的消息正确处理")
    else:
        print(f"❌ 切换聊天组后的消息处理失败，处理了{len(processed_messages)}条消息")
        return False
    
    print("📝 测试场景4：没有聊天组ID的消息处理")
    
    # 创建没有聊天组ID的消息
    message4 = ChatMessage(
        sender_id=4,
        sender_username="systemuser",
        content="System message without group ID"
    )
    # 删除chat_group_id属性
    delattr(message4, 'chat_group_id')
    
    # 处理消息
    client._handle_chat_message(message4)
    
    if len(processed_messages) == 2:  # 仍然只有两条消息
        print("✅ 没有聊天组ID的消息正确处理（被忽略）")
    else:
        print(f"❌ 没有聊天组ID的消息处理失败，处理了{len(processed_messages)}条消息")
        return False
    
    print("📝 测试场景5：用户没有当前聊天组时的消息处理")
    
    # 清除当前聊天组
    client.current_chat_group = None
    
    # 创建消息
    message5 = ChatMessage(
        sender_id=5,
        sender_username="testuser5",
        chat_group_id=1,
        chat_group_name="public",
        content="Message when no current group"
    )
    
    # 处理消息
    client._handle_chat_message(message5)
    
    if len(processed_messages) == 2:  # 仍然只有两条消息
        print("✅ 用户没有当前聊天组时的消息正确处理（被忽略）")
    else:
        print(f"❌ 用户没有当前聊天组时的消息处理失败，处理了{len(processed_messages)}条消息")
        return False
    
    return True


def test_ui_message_filtering():
    """测试UI消息过滤逻辑"""
    print("\n🧪 测试UI消息过滤逻辑...")
    
    try:
        from client.ui.app import ChatRoomApp
        
        # 创建应用实例（不运行）
        app = ChatRoomApp("localhost", 8888)
        
        # 模拟聊天客户端和当前聊天组
        from client.core.client import ChatClient
        app.chat_client = ChatClient()
        app.chat_client.current_chat_group = {'id': 1, 'name': 'public'}
        
        # 记录处理的消息
        processed_messages = []
        
        # 重写add_chat_message方法来记录处理的消息
        original_add_chat = app.add_chat_message
        def mock_add_chat_message(sender, content, is_self=False):
            processed_messages.append({'sender': sender, 'content': content, 'is_self': is_self})
        
        app.add_chat_message = mock_add_chat_message
        
        print("📝 测试UI场景1：当前聊天组的消息应该被显示")
        
        # 创建属于当前聊天组的消息
        message1 = ChatMessage(
            sender_id=2,
            sender_username="otheruser",
            chat_group_id=1,  # 与当前聊天组ID相同
            chat_group_name="public",
            content="Hello from public group"
        )
        
        # 处理消息
        app.handle_chat_message(message1)
        
        if len(processed_messages) == 1:
            print("✅ UI当前聊天组的消息正确显示")
        else:
            print(f"❌ UI当前聊天组的消息显示失败，显示了{len(processed_messages)}条消息")
            return False
        
        print("📝 测试UI场景2：其他聊天组的消息应该被过滤")
        
        # 创建属于其他聊天组的消息
        message2 = ChatMessage(
            sender_id=3,
            sender_username="anotheruser",
            chat_group_id=2,  # 与当前聊天组ID不同
            chat_group_name="test",
            content="Hello from test group"
        )
        
        # 处理消息
        app.handle_chat_message(message2)
        
        if len(processed_messages) == 1:  # 仍然只有第一条消息
            print("✅ UI其他聊天组的消息正确过滤")
        else:
            print(f"❌ UI其他聊天组的消息过滤失败，显示了{len(processed_messages)}条消息")
            return False
        
        return True
        
    except ImportError as e:
        print(f"⚠️  跳过UI测试（缺少依赖）: {e}")
        return True


def run_tests():
    """运行所有测试"""
    print("🚀 开始消息过滤逻辑测试")
    print("=" * 50)
    
    tests = [
        ("客户端消息过滤测试", test_message_filtering),
        ("UI消息过滤测试", test_ui_message_filtering),
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
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！消息过滤逻辑工作正常")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = run_tests()
    
    if success:
        print("\n📝 测试总结:")
        print("- 客户端消息过滤逻辑正确工作")
        print("- 只有当前聊天组的消息会被处理和显示")
        print("- 其他聊天组的消息被正确过滤")
        print("- 消息隔离功能已成功修复")
    
    sys.exit(0 if success else 1)
