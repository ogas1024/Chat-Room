#!/usr/bin/env python3
"""
直接测试Simple模式历史消息显示问题
避免交互式输入的复杂性
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
from client.core.client import ChatClient
from shared.constants import DEFAULT_HOST, DEFAULT_PORT, MessageType


def test_simple_history_direct():
    """直接测试Simple模式历史消息显示"""
    print("开始直接测试Simple模式历史消息显示...")

    # 不启动新服务器，使用现有的服务器
    print("使用现有服务器...")
    
    try:
        # 创建客户端
        client = ChatClient(DEFAULT_HOST, DEFAULT_PORT)
        
        # 设置历史消息处理器来模拟Simple模式
        history_messages = []
        history_complete = False
        
        def handle_history(message):
            history_messages.append(message)
            
            # 模拟Simple模式的历史消息显示逻辑
            timestamp_str = ""
            if hasattr(message, 'timestamp') and message.timestamp:
                try:
                    from datetime import datetime
                    from shared.constants import TIMESTAMP_FORMAT
                    
                    if isinstance(message.timestamp, str):
                        dt = datetime.strptime(message.timestamp, TIMESTAMP_FORMAT)
                        timestamp_str = dt.strftime("[%H:%M:%S]")
                    else:
                        timestamp_str = f"[{message.timestamp}]"
                except:
                    timestamp_str = ""
            
            # 这里是关键：直接打印历史消息
            print(f"📜 {timestamp_str} [{message.sender_username}]: {message.content}")
        
        def handle_history_complete(message):
            nonlocal history_complete
            history_complete = True
            if hasattr(message, 'message_count'):
                if message.message_count > 0:
                    print(f"✅ 已加载 {message.message_count} 条历史消息")
                else:
                    print("✅ 暂无历史消息")
            print("-" * 50)
        
        # 设置消息处理器
        client.network_client.set_message_handler(MessageType.CHAT_HISTORY, handle_history)
        client.network_client.set_message_handler(MessageType.CHAT_HISTORY_COMPLETE, handle_history_complete)
        
        # 连接
        if not client.connect():
            print("❌ 连接失败")
            return False
        
        print("✅ 连接成功")
        
        # 登录
        success, msg = client.login("test", "123456qwer")
        if not success:
            print(f"❌ 登录失败: {msg}")
            return False
        
        print(f"✅ 登录成功")
        
        # 进入test聊天组
        print("\n=== 开始进入test聊天组 ===")
        success, msg = client.enter_chat_group("test")
        if not success:
            print(f"❌ 进入聊天组失败: {msg}")
            return False
        
        print(f"✅ 进入聊天组成功: {msg}")
        
        # 等待历史消息加载
        print("\n等待历史消息加载...")
        timeout = 10
        start_time = time.time()
        
        while not history_complete and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        if history_complete:
            print(f"\n✅ 历史消息加载测试成功！收到 {len(history_messages)} 条历史消息")
            
            # 显示前几条历史消息的详细信息
            print("\n前3条历史消息详情:")
            for i, msg in enumerate(history_messages[:3]):
                print(f"  {i+1}. 发送者: {msg.sender_username}")
                print(f"     内容: {msg.content}")
                print(f"     时间戳: {msg.timestamp}")
                print(f"     聊天组ID: {getattr(msg, 'chat_group_id', 'None')}")
                print()
        else:
            print("❌ 历史消息加载超时")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            client.disconnect()
        except:
            pass


if __name__ == "__main__":
    success = test_simple_history_direct()
    if success:
        print("\n🎉 测试完成！")
    else:
        print("\n❌ 测试失败！")
