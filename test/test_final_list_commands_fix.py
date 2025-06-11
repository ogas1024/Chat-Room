#!/usr/bin/env python3
"""
最终/list命令修复验证脚本
验证所有消息格式错误和日志记录问题是否已修复
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
    AIChatResponse, FileListResponse, create_message_from_dict
)
from shared.constants import MessageType


class TestFinalListCommandsFix(unittest.TestCase):
    """测试最终/list命令修复效果"""

    def test_all_message_classes_creation(self):
        """测试所有消息类的创建"""
        print("🧪 测试所有消息类创建...")
        
        # 测试所有专用消息类
        test_cases = [
            (ListUsersRequest, {'list_type': 'current_chat', 'chat_group_id': 123}),
            (ListChatsRequest, {'list_type': 'all'}),
            (FileListRequest, {'chat_group_id': 456}),
            (FileUploadRequest, {'filename': 'test.txt', 'file_size': 1024, 'chat_group_id': 789}),
            (FileDownloadRequest, {'file_id': '123'}),
            (EnterChatRequest, {'chat_name': 'test_chat'}),
            (AIChatRequest, {'command': 'help', 'message': 'test', 'chat_group_id': 999}),
            (AIChatResponse, {'success': True, 'message': 'AI response'}),
            (FileListResponse, {'files': []})
        ]
        
        for message_class, params in test_cases:
            message = message_class(**params)
            
            # 验证消息类型
            self.assertIsNotNone(message.message_type)
            
            # 验证序列化
            json_str = message.to_json()
            self.assertIsInstance(json_str, str)
            self.assertIn(message.message_type, json_str)
            
            # 验证反序列化
            data = message.to_dict()
            recreated = message_class.from_dict(data)
            self.assertEqual(recreated.message_type, message.message_type)
            
            print(f"✅ {message_class.__name__} 创建和序列化成功")

    def test_message_type_mapping_complete(self):
        """测试完整的消息类型映射"""
        print("🧪 测试消息类型映射...")
        
        test_cases = [
            (MessageType.LIST_USERS_REQUEST, ListUsersRequest, {'list_type': 'all'}),
            (MessageType.LIST_CHATS_REQUEST, ListChatsRequest, {'list_type': 'joined'}),
            (MessageType.FILE_LIST_REQUEST, FileListRequest, {'chat_group_id': 1}),
            (MessageType.FILE_UPLOAD_REQUEST, FileUploadRequest, {'filename': 'test.txt', 'file_size': 1024}),
            (MessageType.FILE_DOWNLOAD_REQUEST, FileDownloadRequest, {'file_id': '123'}),
            (MessageType.ENTER_CHAT_REQUEST, EnterChatRequest, {'chat_name': 'test'}),
            (MessageType.AI_CHAT_REQUEST, AIChatRequest, {'command': 'help', 'message': 'test'}),
            (MessageType.AI_CHAT_RESPONSE, AIChatResponse, {'success': True, 'message': 'response'}),
            (MessageType.FILE_LIST_RESPONSE, FileListResponse, {'files': []})
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
            {'command': 'help'},
            {'success': True},
            {'files': []}
        ]
        
        for params in invalid_params:
            with self.assertRaises(TypeError):
                BaseMessage(message_type="test", **params)
            print(f"✅ BaseMessage正确拒绝了参数: {list(params.keys())[0]}")

    def test_server_message_handling_simulation(self):
        """模拟服务器端消息处理"""
        print("🧪 测试服务器端消息处理模拟...")
        
        # 模拟服务器端处理不同类型的请求
        test_messages = [
            ListUsersRequest(list_type="all", chat_group_id=1),
            ListChatsRequest(list_type="joined"),
            FileListRequest(chat_group_id=2),
            FileUploadRequest(filename="test.txt", file_size=1024, chat_group_id=3),
            FileDownloadRequest(file_id="456"),
            EnterChatRequest(chat_name="public"),
            AIChatRequest(command="status", message="hello", chat_group_id=4)
        ]
        
        for message in test_messages:
            # 模拟消息序列化传输
            json_str = message.to_json()
            
            # 模拟服务器端解析
            from shared.messages import parse_message
            parsed_message = parse_message(json_str)
            
            # 验证解析结果
            self.assertIsInstance(parsed_message, type(message))
            self.assertEqual(parsed_message.message_type, message.message_type)
            
            # 验证专用属性可以正确访问
            if hasattr(message, 'list_type'):
                self.assertEqual(parsed_message.list_type, message.list_type)
            if hasattr(message, 'chat_group_id'):
                self.assertEqual(parsed_message.chat_group_id, message.chat_group_id)
            if hasattr(message, 'filename'):
                self.assertEqual(parsed_message.filename, message.filename)
            if hasattr(message, 'file_id'):
                self.assertEqual(parsed_message.file_id, message.file_id)
            if hasattr(message, 'chat_name'):
                self.assertEqual(parsed_message.chat_name, message.chat_name)
            if hasattr(message, 'command'):
                self.assertEqual(parsed_message.command, message.command)
            
            print(f"✅ {type(message).__name__} 服务器端处理模拟成功")

    def test_client_config_import(self):
        """测试客户端配置导入"""
        print("🧪 测试客户端配置导入...")
        
        try:
            from client.config.client_config import get_client_config
            client_config = get_client_config()
            logging_config = client_config.get_logging_config()
            
            # 检查日志配置
            self.assertIsInstance(logging_config, dict)
            self.assertIn('level', logging_config)
            self.assertIn('file_enabled', logging_config)
            self.assertTrue(logging_config['file_enabled'])  # 应该启用文件日志
            print("✅ 客户端配置导入和日志配置正确")
            
        except Exception as e:
            self.fail(f"客户端配置导入测试失败: {e}")

    def test_no_base_message_usage_in_server(self):
        """测试服务器端代码不再错误使用BaseMessage"""
        print("🧪 测试服务器端代码...")
        
        # 读取服务器端代码，检查是否还有BaseMessage的错误使用
        server_file = os.path.join(os.path.dirname(__file__), '..', 'server', 'core', 'server.py')
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有问题的BaseMessage使用模式
        problematic_patterns = [
            'BaseMessage(\n.*message_type=MessageType.AI_CHAT_RESPONSE',
            'BaseMessage(\n.*message_type=MessageType.FILE_LIST_RESPONSE',
            'getattr(message, \'to_dict\', lambda: {})()'
        ]
        
        import re
        for pattern in problematic_patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            self.assertEqual(len(matches), 0, f"发现问题模式: {pattern}")
        
        print("✅ 服务器端代码中没有发现BaseMessage的错误使用")

    def test_message_field_access(self):
        """测试消息字段直接访问"""
        print("🧪 测试消息字段直接访问...")
        
        # 测试各种消息类的字段访问
        test_cases = [
            (ListUsersRequest(list_type="all", chat_group_id=1), ['list_type', 'chat_group_id']),
            (ListChatsRequest(list_type="joined"), ['list_type']),
            (FileListRequest(chat_group_id=2), ['chat_group_id']),
            (FileUploadRequest(filename="test.txt", file_size=1024), ['filename', 'file_size']),
            (FileDownloadRequest(file_id="456"), ['file_id']),
            (EnterChatRequest(chat_name="public"), ['chat_name']),
            (AIChatRequest(command="status", message="hello"), ['command', 'message'])
        ]
        
        for message, fields in test_cases:
            for field in fields:
                # 验证字段可以直接访问
                value = getattr(message, field)
                self.assertIsNotNone(value)
                print(f"✅ {type(message).__name__}.{field} = {value}")

    def test_error_message_handling(self):
        """测试错误消息处理"""
        print("🧪 测试错误消息处理...")
        
        # 测试无效JSON的处理
        from shared.messages import parse_message, ErrorMessage
        
        invalid_json = "invalid json string"
        result = parse_message(invalid_json)
        self.assertIsInstance(result, ErrorMessage)
        self.assertIn("消息解析失败", result.error_message)
        print("✅ 无效JSON正确处理为ErrorMessage")
        
        # 测试缺少字段的处理
        incomplete_data = '{"message_type": "LIST_USERS_REQUEST"}'
        result = parse_message(incomplete_data)
        self.assertIsInstance(result, ListUsersRequest)
        # 应该使用默认值
        self.assertEqual(result.list_type, "all")
        print("✅ 缺少字段使用默认值正确处理")


def run_tests():
    """运行所有测试"""
    print("🚀 开始验证最终/list命令修复效果...")
    print("=" * 60)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试用例
    suite.addTests(loader.loadTestsFromTestCase(TestFinalListCommandsFix))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    
    # 输出结果
    if result.wasSuccessful():
        print("🎉 所有测试通过！最终/list命令修复成功")
        print("\n修复内容总结:")
        print("1. ✅ 修复了所有服务器端BaseMessage错误使用")
        print("2. ✅ 添加了所有缺失的专用消息类和响应类")
        print("3. ✅ 更新了服务器端方法签名使用正确的消息类型")
        print("4. ✅ 修复了客户端配置导入路径问题")
        print("5. ✅ 启用了客户端文件日志记录")
        print("6. ✅ 确保了消息字段可以直接访问")
        print("7. ✅ 完善了错误消息处理")
        print("\n现在所有/list命令应该可以正常工作了！")
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
