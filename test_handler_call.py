#!/usr/bin/env python3
"""
测试历史消息处理器是否被调用
"""

import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from client.main import SimpleChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT, MessageType

def test_handler_call():
    """测试历史消息处理器是否被调用"""
    print("测试历史消息处理器是否被调用...")
    
    # 创建SimpleChatClient
    simple_client = SimpleChatClient(DEFAULT_HOST, DEFAULT_PORT)
    
    # 添加调试装饰器
    original_history_handler = simple_client._handle_simple_chat_history
    original_complete_handler = simple_client._handle_simple_chat_history_complete
    
    call_count = {'history': 0, 'complete': 0}
    
    def debug_history_handler(message):
        call_count['history'] += 1
        print(f"🔍 历史消息处理器被调用 #{call_count['history']}")
        print(f"   发送者: {message.sender_username}")
        print(f"   内容: {message.content[:50]}...")
        print(f"   聊天组ID: {getattr(message, 'chat_group_id', 'None')}")
        
        # 调用原始处理器
        return original_history_handler(message)
    
    def debug_complete_handler(message):
        call_count['complete'] += 1
        print(f"🔍 历史消息完成处理器被调用 #{call_count['complete']}")
        print(f"   消息数量: {getattr(message, 'message_count', 'None')}")
        
        # 调用原始处理器
        return original_complete_handler(message)
    
    # 替换处理器
    simple_client._handle_simple_chat_history = debug_history_handler
    simple_client._handle_simple_chat_history_complete = debug_complete_handler
    
    # 重新设置网络客户端的处理器
    simple_client.chat_client.network_client.set_message_handler(
        MessageType.CHAT_HISTORY, debug_history_handler
    )
    simple_client.chat_client.network_client.set_message_handler(
        MessageType.CHAT_HISTORY_COMPLETE, debug_complete_handler
    )
    
    try:
        # 连接
        if not simple_client.chat_client.connect():
            print("❌ 连接失败")
            return False
        
        print("✅ 连接成功")
        
        # 登录
        success, msg = simple_client.chat_client.login("test", "123456qwer")
        if not success:
            print(f"❌ 登录失败: {msg}")
            return False
        
        print(f"✅ 登录成功")
        
        # 进入test聊天组
        print("\n=== 开始进入test聊天组 ===")
        success, msg = simple_client.chat_client.enter_chat_group("test")
        if not success:
            print(f"❌ 进入聊天组失败: {msg}")
            return False
        
        print(f"✅ 进入聊天组成功: {msg}")
        
        # 等待历史消息加载
        print("\n等待历史消息加载...")
        time.sleep(5)
        
        print(f"\n=== 调用统计 ===")
        print(f"历史消息处理器调用次数: {call_count['history']}")
        print(f"历史消息完成处理器调用次数: {call_count['complete']}")
        
        if call_count['history'] > 0:
            print("✅ 历史消息处理器被正确调用")
        else:
            print("❌ 历史消息处理器未被调用")
        
        if call_count['complete'] > 0:
            print("✅ 历史消息完成处理器被正确调用")
        else:
            print("❌ 历史消息完成处理器未被调用")
        
        return call_count['history'] > 0 and call_count['complete'] > 0
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            simple_client.chat_client.disconnect()
        except:
            pass

if __name__ == "__main__":
    success = test_handler_call()
    if success:
        print("\n🎉 测试成功！处理器被正确调用")
    else:
        print("\n❌ 测试失败！处理器未被调用")
