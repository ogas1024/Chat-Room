#!/usr/bin/env python3
"""
测试/list -s命令和/create_chat命令修复效果的验证脚本
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    CreateChatRequest, CreateChatResponse, ListUsersRequest, ListUsersResponse,
    UserInfo, parse_message
)
from shared.constants import MessageType
from server.core.user_manager import UserManager
from client.core.client import ChatClient


class TestListSAndCreateChatFix(unittest.TestCase):
    """测试/list -s命令和/create_chat命令修复效果"""

    def setUp(self):
        """设置测试环境"""
        # 创建模拟的数据库
        self.mock_db = Mock()
        
        # 创建用户管理器
        self.user_manager = UserManager()
        self.user_manager.db = self.mock_db

    def test_user_manager_has_get_chat_group_users_method(self):
        """测试UserManager是否有get_chat_group_users方法"""
        # 验证方法存在
        self.assertTrue(hasattr(self.user_manager, 'get_chat_group_users'))
        self.assertTrue(callable(getattr(self.user_manager, 'get_chat_group_users')))

    def test_get_chat_group_users_method(self):
        """测试get_chat_group_users方法的实现"""
        # 模拟数据库返回的成员数据
        mock_members_data = [
            {'id': 1, 'username': 'alice', 'is_online': True},
            {'id': 2, 'username': 'bob', 'is_online': False},
            {'id': 3, 'username': 'charlie', 'is_online': True}
        ]
        
        # 设置模拟数据库方法
        self.mock_db.get_chat_group_members.return_value = mock_members_data
        
        # 调用方法
        result = self.user_manager.get_chat_group_users(1)
        
        # 验证结果
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], UserInfo)
        
        # 验证第一个用户
        self.assertEqual(result[0].user_id, 1)
        self.assertEqual(result[0].username, 'alice')
        self.assertTrue(result[0].is_online)
        
        # 验证第二个用户
        self.assertEqual(result[1].user_id, 2)
        self.assertEqual(result[1].username, 'bob')
        self.assertFalse(result[1].is_online)
        
        # 验证数据库方法被正确调用
        self.mock_db.get_chat_group_members.assert_called_once_with(1)

    def test_create_chat_request_message_parsing(self):
        """测试CreateChatRequest消息解析"""
        # 模拟客户端发送的JSON数据
        json_data = '''
        {
            "message_type": "create_chat_request",
            "timestamp": 1640995200.0,
            "chat_name": "test_group",
            "member_usernames": ["alice", "bob"]
        }
        '''
        
        # 解析消息
        request = parse_message(json_data)
        
        # 验证消息类型
        self.assertEqual(request.message_type, MessageType.CREATE_CHAT_REQUEST)
        self.assertIsInstance(request, CreateChatRequest)
        
        # 验证请求数据
        self.assertEqual(request.chat_name, "test_group")
        self.assertEqual(request.member_usernames, ["alice", "bob"])

    def test_create_chat_response_message_creation(self):
        """测试CreateChatResponse消息创建"""
        # 创建响应消息
        response = CreateChatResponse(
            success=True,
            chat_group_id=123,
            chat_name="test_group"
        )
        
        # 验证消息属性
        self.assertEqual(response.message_type, MessageType.CREATE_CHAT_RESPONSE)
        self.assertTrue(response.success)
        self.assertEqual(response.chat_group_id, 123)
        self.assertEqual(response.chat_name, "test_group")

    def test_client_create_chat_group_uses_correct_message_type(self):
        """测试客户端create_chat_group方法使用正确的消息类型"""
        # 创建模拟的网络客户端
        mock_network_client = Mock()
        mock_network_client.is_connected.return_value = True
        mock_network_client.send_message.return_value = True
        
        # 创建模拟的响应
        mock_response = CreateChatResponse(
            success=True,
            chat_group_id=123,
            chat_name="test_group"
        )
        mock_network_client.wait_for_response.return_value = mock_response
        
        # 创建聊天客户端
        chat_client = ChatClient()
        chat_client.network_client = mock_network_client
        chat_client.user_id = 1
        chat_client.username = "test_user"

        # 模拟登录状态
        with patch.object(chat_client, 'is_logged_in', return_value=True):
            # 调用create_chat_group方法
            success, message = chat_client.create_chat_group("test_group", ["alice", "bob"])

            # 验证结果
            self.assertTrue(success)
            self.assertIn("创建成功", message)

            # 验证发送的消息类型
            mock_network_client.send_message.assert_called_once()
            sent_message = mock_network_client.send_message.call_args[0][0]
            self.assertIsInstance(sent_message, CreateChatRequest)
            self.assertEqual(sent_message.chat_name, "test_group")
            self.assertEqual(sent_message.member_usernames, ["alice", "bob"])

    def test_empty_member_list_handling(self):
        """测试空成员列表的处理"""
        # 创建模拟的网络客户端
        mock_network_client = Mock()
        mock_network_client.is_connected.return_value = True
        mock_network_client.send_message.return_value = True
        
        # 创建模拟的响应
        mock_response = CreateChatResponse(
            success=True,
            chat_group_id=123,
            chat_name="test_group"
        )
        mock_network_client.wait_for_response.return_value = mock_response
        
        # 创建聊天客户端
        chat_client = ChatClient()
        chat_client.network_client = mock_network_client
        chat_client.user_id = 1
        chat_client.username = "test_user"

        # 模拟登录状态
        with patch.object(chat_client, 'is_logged_in', return_value=True):
            # 调用create_chat_group方法（不传member_usernames）
            success, message = chat_client.create_chat_group("test_group")

            # 验证结果
            self.assertTrue(success)

            # 验证发送的消息
            sent_message = mock_network_client.send_message.call_args[0][0]
            self.assertEqual(sent_message.member_usernames, [])

    def test_user_manager_additional_methods(self):
        """测试UserManager的其他新增方法"""
        # 测试is_user_online方法
        self.user_manager.online_users = {1: Mock(), 2: Mock()}
        self.assertTrue(self.user_manager.is_user_online(1))
        self.assertFalse(self.user_manager.is_user_online(3))
        
        # 测试get_user_socket方法
        mock_socket = Mock()
        self.user_manager.online_users = {1: mock_socket}
        self.assertEqual(self.user_manager.get_user_socket(1), mock_socket)
        self.assertIsNone(self.user_manager.get_user_socket(2))
        
        # 测试set_user_current_chat方法
        self.user_manager.user_sessions = {1: {}}
        self.user_manager.set_user_current_chat(1, 123)
        self.assertEqual(self.user_manager.user_sessions[1]['current_chat_group'], 123)

    def test_error_handling_in_get_chat_group_users(self):
        """测试get_chat_group_users方法的错误处理"""
        # 模拟数据库异常
        self.mock_db.get_chat_group_members.side_effect = Exception("Database error")
        
        # 调用方法应该抛出异常
        with self.assertRaises(Exception):
            self.user_manager.get_chat_group_users(1)

    def test_list_users_request_with_chat_group_id(self):
        """测试带有chat_group_id的ListUsersRequest"""
        # 创建请求消息
        request = ListUsersRequest(
            list_type="current_chat",
            chat_group_id=123
        )
        
        # 验证消息属性
        self.assertEqual(request.message_type, MessageType.LIST_USERS_REQUEST)
        self.assertEqual(request.list_type, "current_chat")
        self.assertEqual(request.chat_group_id, 123)

    def test_create_chat_request_without_members(self):
        """测试不带成员的CreateChatRequest"""
        # 创建请求消息
        request = CreateChatRequest(
            chat_name="test_group"
        )
        
        # 验证消息属性
        self.assertEqual(request.message_type, MessageType.CREATE_CHAT_REQUEST)
        self.assertEqual(request.chat_name, "test_group")
        self.assertEqual(request.member_usernames, [])  # 应该有默认值

    def test_create_chat_response_error_case(self):
        """测试CreateChatResponse错误情况"""
        # 创建错误响应
        response = CreateChatResponse(
            success=False,
            error_message="聊天组名称已存在"
        )
        
        # 验证消息属性
        self.assertEqual(response.message_type, MessageType.CREATE_CHAT_RESPONSE)
        self.assertFalse(response.success)
        self.assertEqual(response.error_message, "聊天组名称已存在")


if __name__ == '__main__':
    print("开始测试/list -s命令和/create_chat命令修复效果...")
    unittest.main(verbosity=2)
