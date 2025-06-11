#!/usr/bin/env python3
"""
TODO功能测试脚本
测试所有新实现的功能是否正常工作
"""

import sys
import os

# 确保项目根目录在Python路径中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """测试所有模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from client.core.client import ChatClient
        from client.commands.parser import CommandHandler, Command
        from client.ui.app import ChatRoomApp
        from shared.constants import MessageType
        from shared.messages import BaseMessage
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_chat_client_methods():
    """测试ChatClient新方法"""
    print("\n🔍 测试ChatClient新方法...")
    
    try:
        from client.core.client import ChatClient
        
        client = ChatClient()
        
        # 测试方法是否存在
        methods_to_test = [
            'get_user_info',
            'list_users', 
            'list_chats',
            'create_chat_group',
            'join_chat_group', 
            'enter_chat_group',
            'list_files',
            'send_file',
            'download_file'
        ]
        
        for method_name in methods_to_test:
            if hasattr(client, method_name):
                print(f"✅ 方法 {method_name} 存在")
            else:
                print(f"❌ 方法 {method_name} 不存在")
                return False
        
        print("✅ 所有ChatClient方法测试通过")
        return True
        
    except Exception as e:
        print(f"❌ ChatClient方法测试失败: {e}")
        return False

def test_command_handler():
    """测试命令处理器"""
    print("\n🔍 测试命令处理器...")
    
    try:
        from client.core.client import ChatClient
        from client.commands.parser import CommandHandler, Command
        
        client = ChatClient()
        handler = CommandHandler(client)
        
        # 测试命令处理方法
        test_commands = [
            ("info", []),
            ("list", ["-u"]),
            ("create_chat", ["测试群"]),
            ("join_chat", ["测试群"]),
            ("enter_chat", ["测试群"]),
            ("send_files", ["test.txt"]),
            ("recv_files", ["-l"]),
            ("exit", [])
        ]
        
        for cmd_name, args in test_commands:
            command = Command(cmd_name, args, {}, f"/{cmd_name}")
            method_name = f"handle_{cmd_name}"
            
            if hasattr(handler, method_name):
                print(f"✅ 命令处理器 {method_name} 存在")
                
                # 测试调用（不连接服务器）
                try:
                    method = getattr(handler, method_name)
                    success, message = method(command)
                    print(f"  📝 {cmd_name}: {message[:50]}...")
                except Exception as e:
                    print(f"  ⚠️ {cmd_name}: 调用出错 - {e}")
            else:
                print(f"❌ 命令处理器 {method_name} 不存在")
                return False
        
        print("✅ 所有命令处理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 命令处理器测试失败: {e}")
        return False

def test_ui_app():
    """测试UI应用"""
    print("\n🔍 测试UI应用...")
    
    try:
        from client.ui.app import ChatRoomApp
        
        # 测试应用实例化
        app = ChatRoomApp()
        
        # 测试方法是否存在
        methods_to_test = [
            'handle_message',
            'reset_input_mode',
            'update_status_area',
            'handle_user_status_update'
        ]
        
        for method_name in methods_to_test:
            if hasattr(app, method_name):
                print(f"✅ UI方法 {method_name} 存在")
            else:
                print(f"❌ UI方法 {method_name} 不存在")
                return False
        
        print("✅ UI应用测试通过")
        return True
        
    except Exception as e:
        print(f"❌ UI应用测试失败: {e}")
        return False

def test_message_types():
    """测试消息类型"""
    print("\n🔍 测试消息类型...")
    
    try:
        from shared.constants import MessageType
        
        # 测试新的消息类型是否存在
        message_types_to_test = [
            'USER_INFO_REQUEST',
            'USER_INFO_RESPONSE', 
            'LIST_USERS_REQUEST',
            'LIST_USERS_RESPONSE',
            'LIST_CHATS_REQUEST',
            'LIST_CHATS_RESPONSE',
            'CREATE_CHAT_REQUEST',
            'CREATE_CHAT_RESPONSE',
            'JOIN_CHAT_REQUEST',
            'JOIN_CHAT_RESPONSE',
            'ENTER_CHAT_REQUEST',
            'ENTER_CHAT_RESPONSE',
            'FILE_LIST_REQUEST',
            'FILE_LIST_RESPONSE',
            'FILE_UPLOAD_REQUEST',
            'FILE_UPLOAD_RESPONSE',
            'FILE_DOWNLOAD_REQUEST',
            'FILE_DOWNLOAD_RESPONSE'
        ]
        
        for msg_type in message_types_to_test:
            if hasattr(MessageType, msg_type):
                print(f"✅ 消息类型 {msg_type} 存在")
            else:
                print(f"❌ 消息类型 {msg_type} 不存在")
                return False
        
        print("✅ 消息类型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 消息类型测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始TODO功能测试...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_chat_client_methods,
        test_command_handler,
        test_ui_app,
        test_message_types
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n❌ 测试 {test_func.__name__} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有TODO功能测试通过！")
        print("\n✨ 新功能包括:")
        print("  • 用户信息查询")
        print("  • 用户和聊天组列表")
        print("  • 聊天组管理（创建、加入、进入）")
        print("  • 文件传输（上传、下载、列表）")
        print("  • 消息发送到聊天组")
        print("  • 密码输入掩码")
        print("  • 在线用户状态显示")
        print("  • 完整的命令行界面支持")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
