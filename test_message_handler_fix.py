#!/usr/bin/env python3
"""
消息处理器修复测试
验证ChatClient和TUI的消息处理器设置是否正确
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from client.core.client import ChatClient
from shared.constants import MessageType, DEFAULT_HOST


def test_chat_client_handlers():
    """测试ChatClient的消息处理器设置"""
    print("🧪 测试ChatClient消息处理器...")
    
    try:
        # 创建ChatClient实例
        client = ChatClient(DEFAULT_HOST, 8888)
        
        # 检查网络客户端的消息处理器
        handlers = client.network_client.message_handlers
        
        print(f"📋 ChatClient设置的消息处理器:")
        for msg_type, handler in handlers.items():
            print(f"   {msg_type}: {handler.__name__}")
        
        # 验证关键处理器是否存在
        required_handlers = [
            MessageType.LOGIN_RESPONSE,
            MessageType.REGISTER_RESPONSE,
            MessageType.CHAT_MESSAGE,
            MessageType.CHAT_HISTORY,
            MessageType.ERROR_MESSAGE,
            MessageType.SYSTEM_MESSAGE
        ]
        
        for msg_type in required_handlers:
            assert msg_type in handlers, f"缺少处理器: {msg_type}"
            print(f"✅ {msg_type} 处理器已设置")
        
        print("✅ ChatClient消息处理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ ChatClient测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_handler_override():
    """测试消息处理器覆盖功能"""
    print("🧪 测试消息处理器覆盖...")
    
    try:
        # 创建ChatClient实例
        client = ChatClient(DEFAULT_HOST, 8888)
        
        # 记录原始处理器
        original_handler = client.network_client.message_handlers.get(MessageType.CHAT_HISTORY)
        print(f"📝 原始CHAT_HISTORY处理器: {original_handler.__name__}")
        
        # 定义新的处理器
        def custom_history_handler(message):
            print(f"自定义历史消息处理器: {message}")
        
        # 覆盖处理器
        client.network_client.set_message_handler(MessageType.CHAT_HISTORY, custom_history_handler)
        
        # 验证处理器已被覆盖
        new_handler = client.network_client.message_handlers.get(MessageType.CHAT_HISTORY)
        assert new_handler == custom_history_handler, "处理器覆盖失败"
        
        print(f"📝 新CHAT_HISTORY处理器: {new_handler.__name__}")
        print("✅ 消息处理器覆盖测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 处理器覆盖测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_parsing():
    """测试消息解析功能"""
    print("🧪 测试消息解析...")
    
    try:
        from shared.messages import ChatMessage, parse_message
        
        # 创建历史消息
        history_msg = ChatMessage(
            message_type=MessageType.CHAT_HISTORY,
            sender_id=123,
            sender_username="testuser",
            chat_group_id=456,
            content="历史消息测试"
        )
        
        print(f"📝 创建历史消息: {history_msg.content}")
        
        # 序列化
        json_str = history_msg.to_json()
        print(f"📝 序列化成功")
        
        # 解析
        parsed_msg = parse_message(json_str)
        print(f"📝 解析成功: {type(parsed_msg).__name__}")
        
        # 验证解析结果
        assert isinstance(parsed_msg, ChatMessage), "解析结果类型错误"
        assert parsed_msg.message_type == MessageType.CHAT_HISTORY, "消息类型错误"
        assert parsed_msg.content == "历史消息测试", "消息内容错误"
        
        print("✅ 消息解析测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 消息解析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unhandled_message_detection():
    """测试未处理消息类型检测"""
    print("🧪 测试未处理消息类型检测...")
    
    try:
        from client.core.client import NetworkClient
        
        # 创建网络客户端
        network_client = NetworkClient(DEFAULT_HOST, 8888)
        
        # 创建一个未知类型的消息
        unknown_message_json = '{"message_type": "unknown_type", "content": "test"}'
        
        # 捕获print输出
        import io
        from contextlib import redirect_stdout
        
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            network_client._handle_received_message(unknown_message_json)
        
        output = captured_output.getvalue()
        print(f"📝 捕获的输出: {output.strip()}")
        
        # 验证是否输出了"未处理的消息类型"
        assert "未处理的消息类型" in output, "应该输出未处理消息类型的警告"
        
        print("✅ 未处理消息类型检测正常")
        return True
        
    except Exception as e:
        print(f"❌ 未处理消息检测测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始消息处理器修复测试...")
    
    tests = [
        test_chat_client_handlers,
        test_message_handler_override,
        test_message_parsing,
        test_unhandled_message_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # 空行分隔
    
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！消息处理器修复成功。")
        return True
    else:
        print("❌ 部分测试失败，需要进一步修复。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
