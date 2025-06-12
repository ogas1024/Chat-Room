#!/usr/bin/env python3
"""
消息解析修复测试
验证ChatMessage和CHAT_HISTORY类型的消息解析是否正常工作
"""

import sys
import os
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shared.messages import parse_message, ChatMessage, create_message_from_dict
from shared.constants import MessageType


def test_chat_message_parsing():
    """测试ChatMessage解析"""
    print("🧪 测试ChatMessage解析...")
    
    try:
        # 创建一个ChatMessage对象
        original_message = ChatMessage(
            message_type=MessageType.CHAT_MESSAGE,
            sender_id=123,
            sender_username="testuser",
            chat_group_id=456,
            chat_group_name="testgroup",
            content="Hello, world!",
            message_id=789
        )
        
        print(f"✅ 创建ChatMessage成功: {original_message.content}")
        
        # 序列化为JSON
        json_str = original_message.to_json()
        print(f"✅ 序列化为JSON成功")
        
        # 解析JSON
        parsed_message = parse_message(json_str)
        print(f"✅ 解析JSON成功: {type(parsed_message).__name__}")
        
        # 验证解析结果
        assert isinstance(parsed_message, ChatMessage), f"解析结果应该是ChatMessage，实际是{type(parsed_message)}"
        assert parsed_message.sender_id == 123, f"sender_id不匹配: {parsed_message.sender_id}"
        assert parsed_message.sender_username == "testuser", f"sender_username不匹配: {parsed_message.sender_username}"
        assert parsed_message.content == "Hello, world!", f"content不匹配: {parsed_message.content}"
        
        print("✅ ChatMessage解析测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ ChatMessage解析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_history_parsing():
    """测试CHAT_HISTORY类型消息解析"""
    print("🧪 测试CHAT_HISTORY消息解析...")
    
    try:
        # 创建一个CHAT_HISTORY类型的ChatMessage对象
        original_message = ChatMessage(
            message_type=MessageType.CHAT_HISTORY,
            sender_id=123,
            sender_username="testuser",
            chat_group_id=456,
            chat_group_name="testgroup",
            content="Historical message",
            message_id=789
        )
        
        print(f"✅ 创建CHAT_HISTORY消息成功: {original_message.content}")
        
        # 序列化为JSON
        json_str = original_message.to_json()
        print(f"✅ 序列化为JSON成功")
        
        # 解析JSON
        parsed_message = parse_message(json_str)
        print(f"✅ 解析JSON成功: {type(parsed_message).__name__}")
        
        # 验证解析结果
        assert isinstance(parsed_message, ChatMessage), f"解析结果应该是ChatMessage，实际是{type(parsed_message)}"
        assert parsed_message.message_type == MessageType.CHAT_HISTORY, f"message_type不匹配: {parsed_message.message_type}"
        assert parsed_message.sender_id == 123, f"sender_id不匹配: {parsed_message.sender_id}"
        assert parsed_message.content == "Historical message", f"content不匹配: {parsed_message.content}"
        
        print("✅ CHAT_HISTORY消息解析测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ CHAT_HISTORY消息解析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_message_from_dict():
    """测试create_message_from_dict函数"""
    print("🧪 测试create_message_from_dict函数...")
    
    try:
        # 测试CHAT_MESSAGE类型
        chat_data = {
            'message_type': MessageType.CHAT_MESSAGE,
            'sender_id': 123,
            'sender_username': 'testuser',
            'chat_group_id': 456,
            'content': 'Test message'
        }
        
        message = create_message_from_dict(chat_data)
        assert isinstance(message, ChatMessage), f"应该返回ChatMessage，实际返回{type(message)}"
        print("✅ CHAT_MESSAGE类型处理正确")
        
        # 测试CHAT_HISTORY类型
        history_data = {
            'message_type': MessageType.CHAT_HISTORY,
            'sender_id': 123,
            'sender_username': 'testuser',
            'chat_group_id': 456,
            'content': 'Historical message'
        }
        
        message = create_message_from_dict(history_data)
        assert isinstance(message, ChatMessage), f"应该返回ChatMessage，实际返回{type(message)}"
        print("✅ CHAT_HISTORY类型处理正确")
        
        print("✅ create_message_from_dict函数测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ create_message_from_dict函数测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_problematic_scenario():
    """测试之前出现问题的场景"""
    print("🧪 测试之前出现问题的场景...")
    
    try:
        # 模拟服务器端创建历史消息的场景
        history_data = {
            'id': 1,
            'sender_id': 123,
            'sender_username': 'testuser',
            'content': 'Hello from history',
            'timestamp': 1234567890.0
        }
        
        # 模拟chat_manager.py中的逻辑
        message = ChatMessage(
            message_type=MessageType.CHAT_HISTORY,
            message_id=history_data['id'],
            sender_id=history_data['sender_id'],
            sender_username=history_data['sender_username'],
            chat_group_id=456,
            chat_group_name="",
            content=history_data['content'],
            timestamp=history_data['timestamp']
        )
        
        print(f"✅ 创建历史消息成功: {message.content}")
        
        # 序列化（模拟网络传输）
        json_str = message.to_json()
        print(f"✅ 序列化成功")
        
        # 解析（模拟客户端接收）
        parsed_message = parse_message(json_str)
        print(f"✅ 解析成功: {type(parsed_message).__name__}")
        
        # 验证结果
        assert isinstance(parsed_message, ChatMessage), "解析结果应该是ChatMessage"
        assert parsed_message.message_type == MessageType.CHAT_HISTORY, "消息类型应该是CHAT_HISTORY"
        assert parsed_message.sender_id == 123, "sender_id应该正确"
        assert parsed_message.content == "Hello from history", "内容应该正确"
        
        print("✅ 问题场景测试通过！修复成功。")
        return True
        
    except Exception as e:
        print(f"❌ 问题场景测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始消息解析修复测试...")
    
    tests = [
        test_chat_message_parsing,
        test_chat_history_parsing,
        test_create_message_from_dict,
        test_problematic_scenario
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # 空行分隔
    
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！消息解析问题已修复。")
        return True
    else:
        print("❌ 部分测试失败，需要进一步修复。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
