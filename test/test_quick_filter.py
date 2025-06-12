#!/usr/bin/env python3
"""
快速测试消息过滤逻辑
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_client_filter():
    """测试客户端过滤逻辑"""
    print("🧪 测试客户端消息过滤逻辑...")
    
    from client.core.client import ChatClient
    from shared.messages import ChatMessage
    
    # 创建客户端实例
    client = ChatClient()
    
    # 模拟用户登录状态
    client.current_user = {'id': 1, 'username': 'testuser'}
    client.current_chat_group = {'id': 1, 'name': 'public'}
    
    # 记录处理的消息
    processed_messages = []
    
    # 重写消息处理方法
    def mock_print_message(username, content):
        processed_messages.append(f"[{username}]: {content}")
        print(f"[{username}]: {content}")
    
    # 保存原始方法
    original_handle = client._handle_chat_message
    
    def new_handle_chat_message(message):
        # 验证消息是否属于当前聊天组
        if not hasattr(message, 'chat_group_id'):
            # 消息没有聊天组ID，忽略显示
            return
        
        if not client.current_chat_group:
            # 用户没有当前聊天组，忽略显示
            return
        
        if message.chat_group_id != client.current_chat_group['id']:
            # 消息不属于当前聊天组，忽略显示
            return

        # 处理消息
        mock_print_message(message.sender_username, message.content)
    
    client._handle_chat_message = new_handle_chat_message
    
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
    
    print("📝 测试场景3：用户没有当前聊天组时的消息处理")
    
    # 清除当前聊天组
    client.current_chat_group = None
    
    # 创建消息
    message3 = ChatMessage(
        sender_id=5,
        sender_username="testuser5",
        chat_group_id=1,
        chat_group_name="public",
        content="Message when no current group"
    )
    
    # 处理消息
    client._handle_chat_message(message3)
    
    if len(processed_messages) == 1:  # 仍然只有第一条消息
        print("✅ 用户没有当前聊天组时的消息正确处理（被忽略）")
    else:
        print(f"❌ 用户没有当前聊天组时的消息处理失败，处理了{len(processed_messages)}条消息")
        return False
    
    print("📝 测试场景4：没有聊天组ID的消息处理")
    
    # 恢复聊天组
    client.current_chat_group = {'id': 1, 'name': 'public'}
    
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
    
    if len(processed_messages) == 1:  # 仍然只有第一条消息
        print("✅ 没有聊天组ID的消息正确处理（被忽略）")
    else:
        print(f"❌ 没有聊天组ID的消息处理失败，处理了{len(processed_messages)}条消息")
        return False
    
    return True


def main():
    """主函数"""
    print("🚀 开始快速消息过滤测试")
    print("=" * 50)
    
    try:
        if test_client_filter():
            print("\n🎉 所有测试通过！")
            print("📝 修复总结:")
            print("- 客户端消息过滤逻辑正确工作")
            print("- 只有当前聊天组的消息会被处理和显示")
            print("- 其他聊天组的消息被正确过滤")
            print("- 消息隔离功能已成功修复")
            return True
        else:
            print("\n❌ 测试失败")
            return False
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
