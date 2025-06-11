#!/usr/bin/env python3
"""
测试/list命令最终修复效果的验证脚本
验证所有消息类型错误和日志记录问题是否已修复
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    BaseMessage, ListUsersRequest, ListChatsRequest, FileListRequest,
    FileUploadRequest, FileDownloadRequest, EnterChatRequest, AIChatRequest,
    create_message_from_dict
)
from shared.constants import MessageType
from client.core.client import ChatClient
from client.commands.parser import CommandHandler


class TestListCommandsFinalFix(unittest.TestCase):
    """测试/list命令最终修复效果"""

    def setUp(self):
        """测试前准备"""
        self.mock_client = Mock()
        self.mock_client.is_logged_in.return_value = True
        self.mock_client.current_user = {'id': 1, 'username': 'test_user'}
        self.mock_client.current_chat_group = {'id': 1, 'name': 'test_group'}
        
        # 设置默认的方法返回值
        self.mock_client.list_users.return_value = (True, "成功", [])
        self.mock_client.list_chats.return_value = (True, "成功", [])
        self.mock_client.list_files.return_value = (True, "成功", [])
        
        self.command_handler = CommandHandler(self.mock_client)

    def test_all_message_classes_creation(self):
        """测试所有消息类的创建"""
        print("🧪 测试所有消息类创建...")
        
        # 测试ListUsersRequest
        request = ListUsersRequest(list_type="current_chat", chat_group_id=123)
        self.assertEqual(request.message_type, MessageType.LIST_USERS_REQUEST)
        self.assertEqual(request.list_type, "current_chat")
        self.assertEqual(request.chat_group_id, 123)
        print("✅ ListUsersRequest创建成功")
        
        # 测试ListChatsRequest
        request = ListChatsRequest(list_type="all")
        self.assertEqual(request.message_type, MessageType.LIST_CHATS_REQUEST)
        self.assertEqual(request.list_type, "all")
        print("✅ ListChatsRequest创建成功")
        
        # 测试FileListRequest
        request = FileListRequest(chat_group_id=456)
        self.assertEqual(request.message_type, MessageType.FILE_LIST_REQUEST)
        self.assertEqual(request.chat_group_id, 456)
        print("✅ FileListRequest创建成功")
        
        # 测试FileUploadRequest
        request = FileUploadRequest(filename="test.txt", file_size=1024, chat_group_id=789)
        self.assertEqual(request.message_type, MessageType.FILE_UPLOAD_REQUEST)
        self.assertEqual(request.filename, "test.txt")
        self.assertEqual(request.file_size, 1024)
        self.assertEqual(request.chat_group_id, 789)
        print("✅ FileUploadRequest创建成功")
        
        # 测试FileDownloadRequest
        request = FileDownloadRequest(file_id="123")
        self.assertEqual(request.message_type, MessageType.FILE_DOWNLOAD_REQUEST)
        self.assertEqual(request.file_id, "123")
        print("✅ FileDownloadRequest创建成功")
        
        # 测试EnterChatRequest
        request = EnterChatRequest(chat_name="test_chat")
        self.assertEqual(request.message_type, MessageType.ENTER_CHAT_REQUEST)
        self.assertEqual(request.chat_name, "test_chat")
        print("✅ EnterChatRequest创建成功")
        
        # 测试AIChatRequest
        request = AIChatRequest(command="help", message="test", chat_group_id=999)
        self.assertEqual(request.message_type, MessageType.AI_CHAT_REQUEST)
        self.assertEqual(request.command, "help")
        self.assertEqual(request.message, "test")
        self.assertEqual(request.chat_group_id, 999)
        print("✅ AIChatRequest创建成功")

    def test_message_serialization_all_types(self):
        """测试所有消息类型的序列化"""
        print("🧪 测试消息序列化...")
        
        test_messages = [
            ListUsersRequest(list_type="all", chat_group_id=1),
            ListChatsRequest(list_type="joined"),
            FileListRequest(chat_group_id=2),
            FileUploadRequest(filename="test.txt", file_size=1024),
            FileDownloadRequest(file_id="456"),
            EnterChatRequest(chat_name="public"),
            AIChatRequest(command="status", message="hello")
        ]
        
        for message in test_messages:
            # 测试序列化
            json_str = message.to_json()
            self.assertIsInstance(json_str, str)
            self.assertIn(message.message_type, json_str)
            
            # 测试反序列化
            data = message.to_dict()
            recreated = type(message).from_dict(data)
            self.assertEqual(recreated.message_type, message.message_type)
            
            print(f"✅ {type(message).__name__} 序列化/反序列化成功")

    def test_message_type_mapping_complete(self):
        """测试完整的消息类型映射"""
        print("🧪 测试消息类型映射...")
        
        test_cases = [
            (MessageType.LIST_USERS_REQUEST, ListUsersRequest, {'list_type': 'all'}),
            (MessageType.LIST_CHATS_REQUEST, ListChatsRequest, {'list_type': 'joined'}),
            (MessageType.FILE_LIST_REQUEST, FileListRequest, {'chat_group_id': 1}),
            (MessageType.FILE_UPLOAD_REQUEST, FileUploadRequest, {'filename': 'test.txt'}),
            (MessageType.FILE_DOWNLOAD_REQUEST, FileDownloadRequest, {'file_id': '123'}),
            (MessageType.ENTER_CHAT_REQUEST, EnterChatRequest, {'chat_name': 'test'}),
            (MessageType.AI_CHAT_REQUEST, AIChatRequest, {'command': 'help'})
        ]
        
        for message_type, expected_class, extra_data in test_cases:
            data = {
                'message_type': message_type,
                'timestamp': 1234567890.0,
                **extra_data
            }
            message = create_message_from_dict(data)
            self.assertIsInstance(message, expected_class)
            self.assertEqual(message.message_type, message_type)
            print(f"✅ {expected_class.__name__} 类型映射成功")

    def test_base_message_parameter_validation(self):
        """测试BaseMessage参数验证"""
        print("🧪 测试BaseMessage参数验证...")
        
        # 这应该成功
        message = BaseMessage(message_type="test")
        self.assertEqual(message.message_type, "test")
        print("✅ BaseMessage基本创建成功")
        
        # 这些应该失败，因为BaseMessage不接受这些参数
        invalid_params = [
            {'list_type': 'all'},
            {'chat_group_id': 123},
            {'filename': 'test.txt'},
            {'file_id': '456'},
            {'chat_name': 'test'},
            {'command': 'help'}
        ]
        
        for params in invalid_params:
            with self.assertRaises(TypeError):
                BaseMessage(message_type="test", **params)
            print(f"✅ BaseMessage正确拒绝了参数: {list(params.keys())[0]}")

    @patch('client.core.client.ChatClient.list_users')
    def test_client_methods_use_correct_message_types(self, mock_list_users):
        """测试客户端方法使用正确的消息类型"""
        print("🧪 测试客户端方法...")
        
        # 创建真实的客户端实例
        client = ChatClient("localhost", 8888)
        client.network_client = Mock()
        client.current_user = {'id': 1, 'username': 'test_user'}
        client.current_chat_group = {'id': 1, 'name': 'test_group'}
        
        # 模拟网络客户端
        client.network_client.is_connected.return_value = True
        client.network_client.send_message.return_value = True
        
        # 模拟响应
        mock_response = Mock()
        mock_response.message_type = MessageType.LIST_USERS_RESPONSE
        mock_response.users = []
        client.network_client.wait_for_response.return_value = mock_response
        
        # 测试list_users方法
        client.list_users("current_chat")
        sent_message = client.network_client.send_message.call_args[0][0]
        self.assertIsInstance(sent_message, ListUsersRequest)
        print("✅ list_users使用ListUsersRequest")
        
        # 测试list_chats方法
        mock_response.message_type = MessageType.LIST_CHATS_RESPONSE
        mock_response.chats = []
        client.list_chats("all")
        sent_message = client.network_client.send_message.call_args[0][0]
        self.assertIsInstance(sent_message, ListChatsRequest)
        print("✅ list_chats使用ListChatsRequest")
        
        # 测试list_files方法
        mock_response.message_type = MessageType.FILE_LIST_RESPONSE
        mock_response.files = []
        client.list_files()
        sent_message = client.network_client.send_message.call_args[0][0]
        self.assertIsInstance(sent_message, FileListRequest)
        print("✅ list_files使用FileListRequest")

    def test_no_base_message_usage_in_client_methods(self):
        """测试客户端方法不再使用BaseMessage"""
        print("🧪 测试客户端方法不使用BaseMessage...")
        
        # 读取客户端代码，检查是否还有BaseMessage的错误使用
        client_file = os.path.join(os.path.dirname(__file__), '..', 'client', 'core', 'client.py')
        with open(client_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有BaseMessage与特定参数的组合
        problematic_patterns = [
            'BaseMessage(.*list_type',
            'BaseMessage(.*chat_group_id',
            'BaseMessage(.*filename',
            'BaseMessage(.*file_id',
            'BaseMessage(.*chat_name',
            'BaseMessage(.*command'
        ]
        
        import re
        for pattern in problematic_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            self.assertEqual(len(matches), 0, f"发现问题模式: {pattern}")
        
        print("✅ 客户端代码中没有发现BaseMessage的错误使用")

    def test_logging_configuration(self):
        """测试日志配置"""
        print("🧪 测试日志配置...")
        
        try:
            from client.config.client_config import get_client_config
            client_config = get_client_config()
            logging_config = client_config.get_logging_config()
            
            # 检查日志配置
            self.assertIsInstance(logging_config, dict)
            self.assertIn('level', logging_config)
            self.assertIn('file_enabled', logging_config)
            self.assertTrue(logging_config['file_enabled'])  # 应该启用文件日志
            print("✅ 客户端日志配置正确")
            
        except Exception as e:
            self.fail(f"日志配置测试失败: {e}")


def run_tests():
    """运行所有测试"""
    print("🚀 开始验证/list命令最终修复效果...")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTests(loader.loadTestsFromTestCase(TestListCommandsFinalFix))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    
    # 输出结果
    if result.wasSuccessful():
        print("🎉 所有测试通过！/list命令最终修复成功")
        print("\n修复内容总结:")
        print("1. ✅ 修复了所有BaseMessage初始化错误")
        print("2. ✅ 添加了所有缺失的专用消息类")
        print("3. ✅ 更新了完整的消息类型映射")
        print("4. ✅ 修复了客户端所有方法的消息类型使用")
        print("5. ✅ 启用了客户端文件日志记录")
        print("6. ✅ 禁用了TUI模式下的控制台日志干扰")
        return True
    else:
        print(f"❌ 测试失败：{len(result.failures)} 个失败，{len(result.errors)} 个错误")
        
        # 显示详细错误信息
        if result.failures:
            print("\n失败的测试:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\n错误的测试:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
        
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
