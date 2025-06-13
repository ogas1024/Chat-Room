#!/usr/bin/env python3
"""
不使用日志系统的测试
"""

import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("测试开始...")

try:
    from client.core.client import ChatClient
    from shared.constants import DEFAULT_HOST, DEFAULT_PORT, MessageType
    
    print("导入成功")
    
    # 创建客户端
    client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
    print("客户端创建成功")
    
    # 设置历史消息处理器
    def simple_history_handler(message):
        print(f"📜 [{message.sender_username}]: {message.content}")
    
    def simple_complete_handler(message):
        print(f"✅ 已加载 {message.message_count} 条历史消息")
        print("-" * 50)
    
    client.network_client.set_message_handler(MessageType.CHAT_HISTORY, simple_history_handler)
    client.network_client.set_message_handler(MessageType.CHAT_HISTORY_COMPLETE, simple_complete_handler)
    
    # 连接
    if client.connect():
        print("✅ 连接成功")
        
        # 登录
        success, msg = client.login("test", "123456qwer")
        if success:
            print(f"✅ 登录成功: {msg}")
            
            # 进入test聊天组
            success, msg = client.enter_chat_group("test")
            if success:
                print(f"✅ 进入聊天组成功: {msg}")
                print(f"当前聊天组: {client.current_chat_group}")
                
                # 等待历史消息
                print("\n等待历史消息...")
                time.sleep(5)
                print("等待结束")
                
            else:
                print(f"❌ 进入聊天组失败: {msg}")
        else:
            print(f"❌ 登录失败: {msg}")
        
        client.disconnect()
    else:
        print("❌ 连接失败")

except Exception as e:
    print(f"异常: {e}")
    import traceback
    traceback.print_exc()

print("测试结束")
