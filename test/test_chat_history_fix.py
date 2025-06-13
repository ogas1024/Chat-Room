#!/usr/bin/env python3
"""
聊天历史记录修复测试脚本
测试Simple模式下的历史消息接收和显示
"""

import sys
import os
import time
import threading
from unittest.mock import Mock, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from client.main import SimpleChatClient
from shared.messages import ChatMessage, ChatHistoryComplete
from shared.constants import MessageType, DEFAULT_HOST, DEFAULT_PORT


def test_message_handler_setup():
    """测试消息处理器设置"""
    print("🧪 测试消息处理器设置...")
    
    try:
        # 创建Simple客户端
        client = SimpleChatClient()
        
        # 检查消息处理器是否正确设置
        handlers = client.chat_client.network_client.message_handlers
        
        # 检查关键的消息处理器
        required_handlers = [
            MessageType.CHAT_HISTORY,
            MessageType.CHAT_HISTORY_COMPLETE,
            MessageType.CHAT_MESSAGE
        ]
        
        for handler_type in required_handlers:
            if handler_type in handlers:
                print(f"✅ {handler_type} 处理器已设置")
            else:
                print(f"❌ {handler_type} 处理器未设置")
                return False
        
        # 检查处理器是否指向Simple模式的方法
        if handlers[MessageType.CHAT_HISTORY] == client._handle_simple_chat_history:
            print("✅ CHAT_HISTORY 处理器指向正确的Simple模式方法")
        else:
            print("❌ CHAT_HISTORY 处理器未指向Simple模式方法")
            return False
        
        if handlers[MessageType.CHAT_HISTORY_COMPLETE] == client._handle_simple_chat_history_complete:
            print("✅ CHAT_HISTORY_COMPLETE 处理器指向正确的Simple模式方法")
        else:
            print("❌ CHAT_HISTORY_COMPLETE 处理器未指向Simple模式方法")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 消息处理器设置测试失败: {e}")
        return False


def test_force_override_handlers():
    """测试强制覆盖消息处理器"""
    print("🧪 测试强制覆盖消息处理器...")
    
    try:
        # 创建Simple客户端
        client = SimpleChatClient()
        
        # 模拟其他地方设置了不同的处理器
        def dummy_handler(message):
            pass
        
        client.chat_client.network_client.message_handlers[MessageType.CHAT_HISTORY] = dummy_handler
        client.chat_client.network_client.message_handlers[MessageType.CHAT_HISTORY_COMPLETE] = dummy_handler
        
        print("✅ 模拟设置了错误的处理器")
        
        # 调用强制覆盖方法
        client._force_override_message_handlers()
        
        # 检查处理器是否被正确覆盖
        handlers = client.chat_client.network_client.message_handlers
        
        if handlers[MessageType.CHAT_HISTORY] == client._handle_simple_chat_history:
            print("✅ CHAT_HISTORY 处理器被正确覆盖")
        else:
            print("❌ CHAT_HISTORY 处理器覆盖失败")
            return False
        
        if handlers[MessageType.CHAT_HISTORY_COMPLETE] == client._handle_simple_chat_history_complete:
            print("✅ CHAT_HISTORY_COMPLETE 处理器被正确覆盖")
        else:
            print("❌ CHAT_HISTORY_COMPLETE 处理器覆盖失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 强制覆盖处理器测试失败: {e}")
        return False


def test_history_message_collection():
    """测试历史消息收集"""
    print("🧪 测试历史消息收集...")
    
    try:
        # 创建Simple客户端
        client = SimpleChatClient()
        
        # 模拟当前聊天组
        client.chat_client.current_chat_group = {'id': 1, 'name': 'test_group'}
        
        # 创建测试历史消息
        test_messages = [
            ChatMessage(
                message_type=MessageType.CHAT_HISTORY,
                sender_id=1,
                sender_username="user1",
                chat_group_id=1,
                content="第一条历史消息",
                timestamp="2025-06-13 10:00:00"
            ),
            ChatMessage(
                message_type=MessageType.CHAT_HISTORY,
                sender_id=2,
                sender_username="user2",
                chat_group_id=1,
                content="第二条历史消息",
                timestamp="2025-06-13 10:01:00"
            ),
            ChatMessage(
                message_type=MessageType.CHAT_HISTORY,
                sender_id=-1,
                sender_username="AI助手",
                chat_group_id=1,
                content="这是AI的回复消息",
                timestamp="2025-06-13 10:02:00"
            )
        ]
        
        # 清空历史消息收集器
        client.history_messages = []
        client.current_chat_group_id = None
        
        # 模拟接收历史消息
        for message in test_messages:
            client._handle_simple_chat_history(message)
        
        # 检查消息是否被正确收集
        if len(client.history_messages) == len(test_messages):
            print(f"✅ 历史消息收集数量正确: {len(client.history_messages)}")
        else:
            print(f"❌ 历史消息收集数量错误: 期望 {len(test_messages)}, 实际 {len(client.history_messages)}")
            return False
        
        # 检查消息内容
        for i, collected_msg in enumerate(client.history_messages):
            expected_content = test_messages[i].content
            if collected_msg['content'] == expected_content:
                print(f"✅ 历史消息 {i+1} 内容正确")
            else:
                print(f"❌ 历史消息 {i+1} 内容错误: 期望 '{expected_content}', 实际 '{collected_msg['content']}'")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 历史消息收集测试失败: {e}")
        return False


def test_history_complete_handling():
    """测试历史消息完成处理"""
    print("🧪 测试历史消息完成处理...")
    
    try:
        # 创建Simple客户端
        client = SimpleChatClient()
        
        # 模拟当前聊天组
        client.chat_client.current_chat_group = {'id': 1, 'name': 'test_group'}
        
        # 准备一些历史消息
        client.history_messages = [
            {
                'username': 'user1',
                'timestamp': 'Today 10:00:00',
                'content': '测试消息1'
            },
            {
                'username': 'user2',
                'timestamp': 'Today 10:01:00',
                'content': '测试消息2'
            }
        ]
        
        # 创建历史消息完成通知
        complete_message = ChatHistoryComplete(
            chat_group_id=1,
            message_count=2
        )
        
        # 重定向stdout来捕获输出
        import io
        from contextlib import redirect_stdout
        
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer):
            client._handle_simple_chat_history_complete(complete_message)
        
        output = output_buffer.getvalue()
        
        # 检查输出是否包含预期内容
        if "已加载 2 条历史消息" in output:
            print("✅ 历史消息数量显示正确")
        else:
            print("❌ 历史消息数量显示错误")
            return False
        
        if "测试消息1" in output and "测试消息2" in output:
            print("✅ 历史消息内容显示正确")
        else:
            print("❌ 历史消息内容显示错误")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 历史消息完成处理测试失败: {e}")
        return False


def test_command_handler_integration():
    """测试命令处理器集成"""
    print("🧪 测试命令处理器集成...")
    
    try:
        # 创建Simple客户端
        client = SimpleChatClient()
        
        # 检查命令处理器是否有Simple客户端引用
        if hasattr(client.command_handler, 'simple_client'):
            if client.command_handler.simple_client == client:
                print("✅ 命令处理器Simple客户端引用设置正确")
            else:
                print("❌ 命令处理器Simple客户端引用不正确")
                return False
        else:
            print("❌ 命令处理器缺少Simple客户端引用")
            return False
        
        # 模拟enter_chat命令处理
        from client.commands.parser import Command
        
        # 创建模拟命令
        command = Command("enter_chat", ["test_group"])
        
        # 模拟登录状态
        client.chat_client.current_user = {'username': 'test_user', 'user_id': 1}
        
        # 模拟enter_chat_group方法
        def mock_enter_chat_group(group_name):
            return True, f"成功进入聊天组 '{group_name}'"
        
        client.chat_client.enter_chat_group = mock_enter_chat_group
        
        # 记录初始状态
        initial_messages_count = len(client.history_messages)
        
        # 调用enter_chat处理
        success, message = client.command_handler.handle_enter_chat(command)
        
        if success:
            print("✅ enter_chat命令处理成功")
        else:
            print(f"❌ enter_chat命令处理失败: {message}")
            return False
        
        # 检查历史消息是否被清空
        if len(client.history_messages) == 0:
            print("✅ 历史消息收集器被正确清空")
        else:
            print("❌ 历史消息收集器未被清空")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 命令处理器集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("📜 聊天历史记录修复测试")
    print("=" * 60)
    
    tests = [
        ("消息处理器设置测试", test_message_handler_setup),
        ("强制覆盖处理器测试", test_force_override_handlers),
        ("历史消息收集测试", test_history_message_collection),
        ("历史消息完成处理测试", test_history_complete_handling),
        ("命令处理器集成测试", test_command_handler_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print("✅ 测试通过")
            else:
                print("❌ 测试失败")
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有历史记录测试通过！聊天历史记录修复成功！")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
