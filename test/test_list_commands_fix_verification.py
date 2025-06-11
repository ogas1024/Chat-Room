#!/usr/bin/env python3
"""
测试/list命令修复效果的验证脚本
验证BaseMessage初始化错误是否已修复
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    BaseMessage, ListUsersRequest, ListChatsRequest, 
    ListUsersResponse, ListChatsResponse, create_message_from_dict
)
from shared.constants import MessageType
from client.core.client import ChatClient
from client.commands.parser import CommandHandler


class TestListCommandsFix(unittest.TestCase):
    """测试/list命令修复效果"""

    def setUp(self):
        """测试前准备"""
        self.mock_client = Mock()
        self.mock_client.is_logged_in.return_value = True
        self.mock_client.current_user = {'id': 1, 'username': 'test_user'}
        self.mock_client.current_chat_group = {'id': 1, 'name': 'test_group'}

        # 设置默认的list方法返回值
        self.mock_client.list_users.return_value = (True, "成功", [])
        self.mock_client.list_chats.return_value = (True, "成功", [])
        self.mock_client.list_files.return_value = (True, "成功", [])

        self.command_handler = CommandHandler(self.mock_client)

    def test_list_users_request_creation(self):
        """测试ListUsersRequest消息创建"""
        # 测试基本创建
        request = ListUsersRequest()
        self.assertEqual(request.message_type, MessageType.LIST_USERS_REQUEST)
        self.assertEqual(request.list_type, "all")
        self.assertIsNone(request.chat_group_id)
        
        # 测试带参数创建
        request = ListUsersRequest(list_type="current_chat", chat_group_id=123)
        self.assertEqual(request.list_type, "current_chat")
        self.assertEqual(request.chat_group_id, 123)

    def test_list_chats_request_creation(self):
        """测试ListChatsRequest消息创建"""
        # 测试基本创建
        request = ListChatsRequest()
        self.assertEqual(request.message_type, MessageType.LIST_CHATS_REQUEST)
        self.assertEqual(request.list_type, "joined")
        
        # 测试带参数创建
        request = ListChatsRequest(list_type="all")
        self.assertEqual(request.list_type, "all")

    def test_message_serialization(self):
        """测试消息序列化和反序列化"""
        # 测试ListUsersRequest
        request = ListUsersRequest(list_type="current_chat", chat_group_id=456)
        json_str = request.to_json()
        self.assertIn("list_type", json_str)
        self.assertIn("current_chat", json_str)
        self.assertIn("456", json_str)
        
        # 测试从字典创建
        data = request.to_dict()
        recreated = ListUsersRequest.from_dict(data)
        self.assertEqual(recreated.list_type, "current_chat")
        self.assertEqual(recreated.chat_group_id, 456)

    def test_message_type_mapping(self):
        """测试消息类型映射"""
        # 测试ListUsersRequest映射
        data = {
            'message_type': MessageType.LIST_USERS_REQUEST,
            'list_type': 'all',
            'chat_group_id': None,
            'timestamp': 1234567890.0
        }
        message = create_message_from_dict(data)
        self.assertIsInstance(message, ListUsersRequest)
        self.assertEqual(message.list_type, 'all')
        
        # 测试ListChatsRequest映射
        data = {
            'message_type': MessageType.LIST_CHATS_REQUEST,
            'list_type': 'joined',
            'timestamp': 1234567890.0
        }
        message = create_message_from_dict(data)
        self.assertIsInstance(message, ListChatsRequest)
        self.assertEqual(message.list_type, 'joined')

    @patch('client.core.client.ChatClient.list_users')
    def test_list_users_command_handling(self, mock_list_users):
        """测试/list -u命令处理"""
        # 模拟成功响应
        mock_list_users.return_value = (True, "获取用户列表成功", [
            {'user_id': 1, 'username': 'alice', 'is_online': True},
            {'user_id': 2, 'username': 'bob', 'is_online': False}
        ])
        
        # 执行命令
        success, message = self.command_handler.handle_command("/list -u")
        
        # 验证结果
        self.assertTrue(success)
        self.assertIn("所有用户列表", message)
        self.assertIn("alice", message)
        self.assertIn("bob", message)
        self.assertIn("在线", message)
        self.assertIn("离线", message)
        
        # 验证调用参数
        mock_list_users.assert_called_once_with("all")

    @patch('client.core.client.ChatClient.list_chats')
    def test_list_chats_command_handling(self, mock_list_chats):
        """测试/list -c命令处理"""
        # 模拟成功响应
        mock_list_chats.return_value = (True, "获取聊天组列表成功", [
            {'group_id': 1, 'group_name': 'public', 'is_private_chat': False, 'member_count': 5, 'created_at': '2024-01-01'},
            {'group_id': 2, 'group_name': 'private_chat', 'is_private_chat': True, 'member_count': 2, 'created_at': '2024-01-02'}
        ])
        
        # 执行命令
        success, message = self.command_handler.handle_command("/list -c")
        
        # 验证结果
        self.assertTrue(success)
        self.assertIn("已加入的聊天组", message)
        self.assertIn("public", message)
        self.assertIn("private_chat", message)
        self.assertIn("群聊", message)
        self.assertIn("私聊", message)
        
        # 验证调用参数
        mock_list_chats.assert_called_once_with("joined")

    @patch('client.core.client.ChatClient.list_users')
    def test_list_users_error_handling(self, mock_list_users):
        """测试/list -u命令错误处理"""
        # 模拟错误响应
        mock_list_users.return_value = (False, "服务器连接失败", None)
        
        # 执行命令
        success, message = self.command_handler.handle_command("/list -u")
        
        # 验证结果
        self.assertFalse(success)
        self.assertEqual(message, "服务器连接失败")

    def test_list_command_invalid_option(self):
        """测试/list命令无效选项"""
        # 测试无效选项
        success, message = self.command_handler.handle_command("/list -x")
        self.assertFalse(success)
        self.assertIn("未知选项", message)
        self.assertIn("-x", message)

    def test_list_command_no_option(self):
        """测试/list命令无选项"""
        # 测试无选项
        success, message = self.command_handler.handle_command("/list")
        self.assertFalse(success)
        self.assertIn("请指定列表类型", message)

    @patch('shared.logger.get_logger')
    def test_command_logging(self, mock_get_logger):
        """测试命令执行日志记录"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # 重新创建命令处理器以使用模拟的logger
        handler = CommandHandler(self.mock_client)
        handler.logger = mock_logger
        
        # 模拟成功的list_users调用
        self.mock_client.list_users.return_value = (True, "成功", [])
        
        # 执行命令
        handler.handle_command("/list -u")
        
        # 验证日志记录
        mock_logger.info.assert_called()
        mock_logger.warning.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_base_message_no_extra_params(self):
        """测试BaseMessage不接受额外参数"""
        # 这应该不会抛出异常
        message = BaseMessage(message_type="test")
        self.assertEqual(message.message_type, "test")
        
        # 这应该抛出TypeError，因为BaseMessage不接受list_type参数
        with self.assertRaises(TypeError):
            BaseMessage(message_type="test", list_type="all")


class TestClientListMethods(unittest.TestCase):
    """测试客户端list方法"""

    def setUp(self):
        """测试前准备"""
        self.client = ChatClient("localhost", 8888)
        self.client.network_client = Mock()
        self.client.current_user = {'id': 1, 'username': 'test_user'}
        self.client.current_chat_group = {'id': 1, 'name': 'test_group'}

    def test_list_users_creates_correct_request(self):
        """测试list_users方法创建正确的请求"""
        # 模拟网络客户端
        self.client.network_client.is_connected.return_value = True
        self.client.network_client.send_message.return_value = True
        
        # 模拟响应
        mock_response = Mock()
        mock_response.message_type = MessageType.LIST_USERS_RESPONSE
        mock_response.users = []
        self.client.network_client.wait_for_response.return_value = mock_response
        
        # 调用方法
        self.client.list_users("current_chat")
        
        # 验证发送的消息
        sent_message = self.client.network_client.send_message.call_args[0][0]
        self.assertIsInstance(sent_message, ListUsersRequest)
        self.assertEqual(sent_message.list_type, "current_chat")
        self.assertEqual(sent_message.chat_group_id, 1)

    def test_list_chats_creates_correct_request(self):
        """测试list_chats方法创建正确的请求"""
        # 模拟网络客户端
        self.client.network_client.is_connected.return_value = True
        self.client.network_client.send_message.return_value = True
        
        # 模拟响应
        mock_response = Mock()
        mock_response.message_type = MessageType.LIST_CHATS_RESPONSE
        mock_response.chats = []
        self.client.network_client.wait_for_response.return_value = mock_response
        
        # 调用方法
        self.client.list_chats("all")
        
        # 验证发送的消息
        sent_message = self.client.network_client.send_message.call_args[0][0]
        self.assertIsInstance(sent_message, ListChatsRequest)
        self.assertEqual(sent_message.list_type, "all")


def run_tests():
    """运行所有测试"""
    print("🧪 开始验证/list命令修复效果...")

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试用例
    suite.addTests(loader.loadTestsFromTestCase(TestListCommandsFix))
    suite.addTests(loader.loadTestsFromTestCase(TestClientListMethods))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出结果
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！/list命令修复成功")
        return True
    else:
        print(f"\n❌ 测试失败：{len(result.failures)} 个失败，{len(result.errors)} 个错误")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
