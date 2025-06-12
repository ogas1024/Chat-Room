#!/usr/bin/env python3
"""
验证TUI聊天记录加载修复
测试修复后的TUI界面逻辑是否正常工作
"""

import sys
import os
from unittest.mock import Mock

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from shared.constants import MessageType
from shared.messages import ChatHistoryComplete


def test_tui_history_loading_logic():
    """测试TUI历史消息加载逻辑"""
    print("🧪 测试TUI历史消息加载逻辑...")
    
    try:
        from client.ui.app import ChatRoomApp
        
        # 创建模拟的TUI应用
        app = ChatRoomApp("localhost", 8888)
        
        # 模拟初始化状态
        app.history_loading = False
        app.history_message_count = 0
        
        # 测试清空聊天记录
        print("📝 测试清空聊天记录...")
        
        # 模拟chat_log组件
        app.chat_log = Mock()
        app.chat_log.clear = Mock()
        app.chat_log.write = Mock()
        
        app.clear_chat_log()
        
        # 验证状态
        assert hasattr(app, 'history_loading'), "应该设置history_loading属性"
        assert app.history_loading == True, "清空后应该设置为加载状态"
        assert app.history_message_count == 0, "消息计数应该重置为0"
        
        print("✅ 清空聊天记录逻辑正确")
        
        # 测试历史消息接收
        print("📝 测试历史消息接收...")
        
        # 模拟接收历史消息
        for i in range(3):
            app.on_history_message_received()
        
        assert app.history_message_count == 3, f"应该计数3条消息，实际: {app.history_message_count}"
        
        print("✅ 历史消息计数正确")
        
        # 测试完成历史消息加载
        print("📝 测试完成历史消息加载...")
        
        app.finish_history_loading()
        
        assert app.history_loading == False, "完成后应该设置为非加载状态"
        assert app.history_message_count == 0, "完成后消息计数应该重置"
        
        print("✅ 完成历史消息加载逻辑正确")
        
        return True
        
    except Exception as e:
        print(f"❌ TUI历史消息加载逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_history_complete_handler():
    """测试历史消息完成处理器"""
    print("🧪 测试历史消息完成处理器...")
    
    try:
        from client.ui.app import ChatRoomApp
        from client.core.client import ChatClient
        
        # 创建模拟的TUI应用
        app = ChatRoomApp("localhost", 8888)
        
        # 模拟聊天客户端
        mock_client = Mock(spec=ChatClient)
        mock_client.current_chat_group = {'id': 123, 'name': 'test_group'}
        app.chat_client = mock_client
        
        # 模拟初始化状态
        app.history_loading = True
        app.history_message_count = 5
        
        # 创建历史消息完成通知
        complete_message = ChatHistoryComplete(
            chat_group_id=123,
            message_count=5
        )
        
        # 测试处理器
        print("📝 测试处理历史消息完成通知...")
        
        # 模拟finish_history_loading方法
        original_finish = app.finish_history_loading
        finish_called = False
        
        def mock_finish():
            nonlocal finish_called
            finish_called = True
            original_finish()
        
        app.finish_history_loading = mock_finish
        
        # 调用处理器
        app.handle_chat_history_complete(complete_message)
        
        # 验证结果
        assert finish_called, "应该调用finish_history_loading方法"
        
        print("✅ 历史消息完成处理器工作正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 历史消息完成处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_message_handler_registration():
    """测试消息处理器注册"""
    print("🧪 测试消息处理器注册...")
    
    try:
        from client.ui.app import ChatRoomApp
        
        # 创建TUI应用
        app = ChatRoomApp("localhost", 8888)
        
        # 检查是否有handle_chat_history_complete方法
        assert hasattr(app, 'handle_chat_history_complete'), "应该有handle_chat_history_complete方法"
        
        # 检查方法是否可调用
        assert callable(app.handle_chat_history_complete), "handle_chat_history_complete应该是可调用的"
        
        print("✅ 消息处理器注册正确")
        
        return True
        
    except Exception as e:
        print(f"❌ 消息处理器注册测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始TUI聊天记录加载修复验证...")
    
    tests = [
        ("TUI历史消息加载逻辑", test_tui_history_loading_logic),
        ("历史消息完成处理器", test_history_complete_handler),
        ("消息处理器注册", test_message_handler_registration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行 {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有TUI验证测试通过！聊天记录加载修复在TUI层面工作正常。")
        return True
    else:
        print("💥 部分TUI验证测试失败！需要检查TUI层面的修复。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
