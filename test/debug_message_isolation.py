#!/usr/bin/env python3
"""
调试消息隔离问题
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def debug_client_message_handling():
    """调试客户端消息处理"""
    print("🔍 调试客户端消息处理逻辑...")
    
    from client.core.client import ChatClient
    from shared.messages import ChatMessage
    
    # 创建客户端实例
    client = ChatClient()
    
    # 模拟用户登录状态
    client.current_user = {'id': 1, 'username': 'testuser'}
    client.current_chat_group = {'id': 1, 'name': 'public'}
    
    print(f"当前用户: {client.current_user}")
    print(f"当前聊天组: {client.current_chat_group}")
    
    # 测试消息处理
    print("\n📝 测试1: 当前聊天组的消息")
    message1 = ChatMessage(
        sender_id=2,
        sender_username='otheruser',
        chat_group_id=1,  # 与当前聊天组ID相同
        chat_group_name='public',
        content='Hello from public group'
    )
    
    print(f"消息聊天组ID: {message1.chat_group_id}")
    print(f"当前聊天组ID: {client.current_chat_group['id']}")
    print(f"消息有chat_group_id属性: {hasattr(message1, 'chat_group_id')}")
    
    # 手动执行过滤逻辑
    if not hasattr(message1, 'chat_group_id'):
        print("❌ 消息没有聊天组ID，应该被忽略")
    elif not client.current_chat_group:
        print("❌ 用户没有当前聊天组，应该被忽略")
    elif message1.chat_group_id != client.current_chat_group['id']:
        print("❌ 消息不属于当前聊天组，应该被忽略")
    else:
        print("✅ 消息应该被显示")
    
    print("调用处理器...")
    client._handle_chat_message(message1)
    
    print("\n📝 测试2: 其他聊天组的消息")
    message2 = ChatMessage(
        sender_id=3,
        sender_username='anotheruser',
        chat_group_id=2,  # 与当前聊天组ID不同
        chat_group_name='test',
        content='Hello from test group'
    )
    
    print(f"消息聊天组ID: {message2.chat_group_id}")
    print(f"当前聊天组ID: {client.current_chat_group['id']}")
    
    # 手动执行过滤逻辑
    if not hasattr(message2, 'chat_group_id'):
        print("❌ 消息没有聊天组ID，应该被忽略")
    elif not client.current_chat_group:
        print("❌ 用户没有当前聊天组，应该被忽略")
    elif message2.chat_group_id != client.current_chat_group['id']:
        print("❌ 消息不属于当前聊天组，应该被忽略")
    else:
        print("✅ 消息应该被显示")
    
    print("调用处理器...")
    client._handle_chat_message(message2)
    
    print("\n📝 测试3: 没有聊天组ID的消息")
    message3 = ChatMessage(
        sender_id=4,
        sender_username='systemuser',
        content='System message without group ID'
    )
    # 删除chat_group_id属性
    delattr(message3, 'chat_group_id')
    
    print(f"消息有chat_group_id属性: {hasattr(message3, 'chat_group_id')}")
    
    # 手动执行过滤逻辑
    if not hasattr(message3, 'chat_group_id'):
        print("❌ 消息没有聊天组ID，应该被忽略")
    elif not client.current_chat_group:
        print("❌ 用户没有当前聊天组，应该被忽略")
    elif message3.chat_group_id != client.current_chat_group['id']:
        print("❌ 消息不属于当前聊天组，应该被忽略")
    else:
        print("✅ 消息应该被显示")
    
    print("调用处理器...")
    client._handle_chat_message(message3)


def debug_tui_message_handling():
    """调试TUI消息处理"""
    print("\n🔍 调试TUI消息处理逻辑...")
    
    try:
        from client.ui.app import ChatRoomApp
        from client.core.client import ChatClient
        from shared.messages import ChatMessage
        
        # 创建应用实例（不运行）
        app = ChatRoomApp("localhost", 8888)
        
        # 模拟聊天客户端和当前聊天组
        app.chat_client = ChatClient()
        app.chat_client.current_chat_group = {'id': 1, 'name': 'public'}
        
        print(f"TUI当前聊天组: {app.chat_client.current_chat_group}")
        
        # 测试消息处理
        print("\n📝 TUI测试1: 当前聊天组的消息")
        message1 = ChatMessage(
            sender_id=2,
            sender_username='otheruser',
            chat_group_id=1,  # 与当前聊天组ID相同
            chat_group_name='public',
            content='Hello from public group'
        )
        
        print(f"消息聊天组ID: {message1.chat_group_id}")
        print(f"当前聊天组ID: {app.chat_client.current_chat_group['id']}")
        
        # 手动执行过滤逻辑
        if not hasattr(message1, 'chat_group_id'):
            print("❌ 消息没有聊天组ID，应该被忽略")
        elif not app.chat_client or not app.chat_client.current_chat_group:
            print("❌ 没有聊天客户端或用户没有当前聊天组，应该被忽略")
        elif message1.chat_group_id != app.chat_client.current_chat_group['id']:
            print("❌ 消息不属于当前聊天组，应该被忽略")
        else:
            print("✅ 消息应该被显示")
        
        # 模拟add_chat_message方法
        def mock_add_chat_message(sender, content, is_self=False):
            print(f"📨 TUI显示消息: [{sender}]: {content}")
        
        app.add_chat_message = mock_add_chat_message
        
        print("调用TUI处理器...")
        app.handle_chat_message(message1)
        
        print("\n📝 TUI测试2: 其他聊天组的消息")
        message2 = ChatMessage(
            sender_id=3,
            sender_username='anotheruser',
            chat_group_id=2,  # 与当前聊天组ID不同
            chat_group_name='test',
            content='Hello from test group'
        )
        
        print(f"消息聊天组ID: {message2.chat_group_id}")
        print(f"当前聊天组ID: {app.chat_client.current_chat_group['id']}")
        
        # 手动执行过滤逻辑
        if not hasattr(message2, 'chat_group_id'):
            print("❌ 消息没有聊天组ID，应该被忽略")
        elif not app.chat_client or not app.chat_client.current_chat_group:
            print("❌ 没有聊天客户端或用户没有当前聊天组，应该被忽略")
        elif message2.chat_group_id != app.chat_client.current_chat_group['id']:
            print("❌ 消息不属于当前聊天组，应该被忽略")
        else:
            print("✅ 消息应该被显示")
        
        print("调用TUI处理器...")
        app.handle_chat_message(message2)
        
    except ImportError as e:
        print(f"⚠️  跳过TUI测试（缺少依赖）: {e}")


def debug_message_handlers():
    """调试消息处理器设置"""
    print("\n🔍 调试消息处理器设置...")
    
    from client.core.client import ChatClient
    from shared.constants import MessageType
    
    # 创建客户端实例
    client = ChatClient()
    
    print("📋 检查消息处理器设置:")
    print(f"网络客户端消息处理器: {client.network_client.message_handlers}")
    
    # 检查CHAT_MESSAGE处理器
    chat_handler = client.network_client.message_handlers.get(MessageType.CHAT_MESSAGE)
    print(f"CHAT_MESSAGE处理器: {chat_handler}")
    print(f"处理器是否为ChatClient的方法: {chat_handler == client._handle_chat_message}")
    
    # 检查默认处理器
    default_handler = client.network_client.default_message_handler
    print(f"默认消息处理器: {default_handler}")


def main():
    """主函数"""
    print("🚀 开始调试消息隔离问题")
    print("=" * 60)
    
    debug_client_message_handling()
    debug_tui_message_handling()
    debug_message_handlers()
    
    print("\n" + "=" * 60)
    print("🎯 调试总结:")
    print("1. 检查客户端消息过滤逻辑是否正确执行")
    print("2. 检查TUI消息过滤逻辑是否正确执行")
    print("3. 检查消息处理器是否正确设置")
    print("4. 如果以上都正确，问题可能在服务器端或网络传输")


if __name__ == "__main__":
    main()
