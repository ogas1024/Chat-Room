#!/usr/bin/env python3
"""
调试Simple模式历史消息显示问题
"""

import sys
import os
import time
import threading
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from server.main import ChatRoomServer
from client.main import SimpleChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT, MessageType


def debug_simple_history():
    """调试Simple模式历史消息显示问题"""
    print("开始调试Simple模式历史消息显示问题...")
    
    # 启动服务器
    server = ChatRoomServer(DEFAULT_HOST, DEFAULT_PORT)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(2)
    
    try:
        # 创建Simple模式客户端
        simple_client = SimpleChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 添加调试信息到历史消息处理器
        original_history_handler = simple_client._handle_simple_chat_history
        original_complete_handler = simple_client._handle_simple_chat_history_complete
        
        def debug_history_handler(message):
            print(f"🔍 DEBUG: 历史消息处理器被调用")
            print(f"🔍 DEBUG: 消息类型: {message.message_type}")
            print(f"🔍 DEBUG: 发送者: {message.sender_username}")
            print(f"🔍 DEBUG: 内容: {message.content}")
            print(f"🔍 DEBUG: 聊天组ID: {getattr(message, 'chat_group_id', 'None')}")
            print(f"🔍 DEBUG: 当前聊天组: {simple_client.chat_client.current_chat_group}")
            
            # 调用原始处理器
            original_history_handler(message)
            
        def debug_complete_handler(message):
            print(f"🔍 DEBUG: 历史消息完成处理器被调用")
            print(f"🔍 DEBUG: 消息数量: {getattr(message, 'message_count', 'None')}")
            
            # 调用原始处理器
            original_complete_handler(message)
        
        # 替换处理器
        simple_client._handle_simple_chat_history = debug_history_handler
        simple_client._handle_simple_chat_history_complete = debug_complete_handler
        
        # 重新设置消息处理器
        simple_client.chat_client.network_client.set_message_handler(
            MessageType.CHAT_HISTORY, debug_history_handler
        )
        simple_client.chat_client.network_client.set_message_handler(
            MessageType.CHAT_HISTORY_COMPLETE, debug_complete_handler
        )
        
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
        print(f"🔍 当前聊天组: {simple_client.chat_client.current_chat_group}")
        
        # 等待历史消息加载
        print("\n等待历史消息加载...")
        time.sleep(5)
        
        print("\n=== 历史消息加载完成 ===")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            simple_client.chat_client.disconnect()
        except:
            pass
        
        try:
            server.stop()
        except:
            pass


if __name__ == "__main__":
    success = debug_simple_history()
    if success:
        print("\n🎉 调试完成！")
    else:
        print("\n❌ 调试失败！")
