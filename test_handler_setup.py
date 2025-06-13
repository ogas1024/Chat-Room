#!/usr/bin/env python3
"""
测试消息处理器设置
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from client.main import SimpleChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT, MessageType

def test_handler_setup():
    """测试消息处理器设置"""
    print("测试消息处理器设置...")
    
    # 创建SimpleChatClient
    simple_client = SimpleChatClient(DEFAULT_HOST, DEFAULT_PORT)
    
    # 检查消息处理器
    network_client = simple_client.chat_client.network_client
    
    print("当前设置的消息处理器:")
    for msg_type, handler in network_client.message_handlers.items():
        print(f"  {msg_type}: {handler.__name__ if hasattr(handler, '__name__') else handler}")
    
    # 特别检查历史消息处理器
    history_handler = network_client.message_handlers.get(MessageType.CHAT_HISTORY)
    history_complete_handler = network_client.message_handlers.get(MessageType.CHAT_HISTORY_COMPLETE)
    
    print(f"\n历史消息处理器: {history_handler}")
    print(f"历史消息完成处理器: {history_complete_handler}")
    
    # 检查是否是SimpleChatClient的处理器
    if history_handler == simple_client._handle_simple_chat_history:
        print("✅ 历史消息处理器设置正确")
    else:
        print("❌ 历史消息处理器设置错误")
        print(f"期望: {simple_client._handle_simple_chat_history}")
        print(f"实际: {history_handler}")
    
    if history_complete_handler == simple_client._handle_simple_chat_history_complete:
        print("✅ 历史消息完成处理器设置正确")
    else:
        print("❌ 历史消息完成处理器设置错误")
        print(f"期望: {simple_client._handle_simple_chat_history_complete}")
        print(f"实际: {history_complete_handler}")

if __name__ == "__main__":
    test_handler_setup()
