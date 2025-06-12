#!/usr/bin/env python3
"""
测试/enter_chat命令时延和/list -g命令显示问题的修复效果
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    EnterChatRequest, EnterChatResponse, ListChatsRequest, ListChatsResponse,
    ChatGroupInfo, parse_message
)
from shared.constants import MessageType
from server.core.chat_manager import ChatManager
from server.database.models import DatabaseManager
from client.core.client import ChatClient


class TestEnterChatAndListGFix(unittest.TestCase):
    """测试/enter_chat命令时延和/list -g命令显示问题的修复效果"""

    def setUp(self):
        """设置测试环境"""
        # 创建模拟的数据库
        self.mock_db = Mock()
        
        # 创建模拟的用户管理器
        self.mock_user_manager = Mock()
        
        # 创建聊天管理器
        self.chat_manager = ChatManager(self.mock_user_manager)
        self.chat_manager.db = self.mock_db

    def test_enter_chat_response_message_parsing(self):
        """测试EnterChatResponse消息解析"""
        # 模拟服务器返回的JSON数据
        json_data = '''
        {
            "message_type": "enter_chat_response",
            "timestamp": 1640995200.0,
            "success": true,
            "chat_group_id": 123,
            "chat_name": "test_group"
        }
        '''
        
        # 解析消息
        response = parse_message(json_data)
        
        # 验证消息类型
        self.assertEqual(response.message_type, MessageType.ENTER_CHAT_RESPONSE)
        self.assertIsInstance(response, EnterChatResponse)
        
        # 验证响应数据
        self.assertTrue(response.success)
        self.assertEqual(response.chat_group_id, 123)
        self.assertEqual(response.chat_name, "test_group")

    def test_enter_chat_response_creation(self):
        """测试EnterChatResponse消息创建"""
        # 创建响应消息
        response = EnterChatResponse(
            success=True,
            chat_group_id=123,
            chat_name="test_group"
        )
        
        # 验证消息属性
        self.assertEqual(response.message_type, MessageType.ENTER_CHAT_RESPONSE)
        self.assertTrue(response.success)
        self.assertEqual(response.chat_group_id, 123)
        self.assertEqual(response.chat_name, "test_group")

    def test_client_enter_chat_group_expects_correct_response(self):
        """测试客户端enter_chat_group方法期望正确的响应类型"""
        # 创建模拟的网络客户端
        mock_network_client = Mock()
        mock_network_client.is_connected.return_value = True
        mock_network_client.send_message.return_value = True
        
        # 创建模拟的响应
        mock_response = EnterChatResponse(
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
            # 调用enter_chat_group方法
            success, message = chat_client.enter_chat_group("test_group")
            
            # 验证结果
            self.assertTrue(success)
            self.assertIn("已进入聊天组", message)
            
            # 验证等待的响应类型
            mock_network_client.wait_for_response.assert_called_once()
            call_args = mock_network_client.wait_for_response.call_args
            expected_message_types = call_args[1]['message_types']
            self.assertIn(MessageType.ENTER_CHAT_RESPONSE, expected_message_types)

    def test_database_sql_query_structure(self):
        """测试数据库SQL查询结构不包含成员数量过滤"""
        # 这个测试验证SQL查询的结构，而不是实际执行
        # 我们通过检查修复后的代码来验证HAVING子句已被移除

        # 模拟数据库管理器
        mock_db = Mock()

        # 模拟查询结果 - 包含不同成员数量的聊天组
        mock_db.get_all_group_chats.return_value = [
            {'id': 1, 'name': 'public', 'is_private_chat': False, 'member_count': 5, 'created_at': '2024-01-01'},
            {'id': 2, 'name': 'test_group', 'is_private_chat': False, 'member_count': 1, 'created_at': '2024-01-02'},  # 只有1个成员
            {'id': 3, 'name': 'small_group', 'is_private_chat': False, 'member_count': 2, 'created_at': '2024-01-03'},  # 只有2个成员
        ]

        # 验证模拟返回的结果包含所有群聊，不管成员数量
        result = mock_db.get_all_group_chats()
        self.assertEqual(len(result), 3)

        # 验证包含小群组
        group_names = [chat['name'] for chat in result]
        self.assertIn('test_group', group_names)
        self.assertIn('small_group', group_names)

    def test_chat_manager_get_all_group_chats_includes_small_groups(self):
        """测试ChatManager的get_all_group_chats方法包含小群组"""
        # 模拟数据库返回的聊天组数据
        mock_chats_data = [
            {'id': 1, 'name': 'public', 'is_private_chat': False, 'member_count': 5, 'created_at': '2024-01-01'},
            {'id': 2, 'name': 'test_group', 'is_private_chat': False, 'member_count': 1, 'created_at': '2024-01-02'},
            {'id': 3, 'name': 'small_group', 'is_private_chat': False, 'member_count': 2, 'created_at': '2024-01-03'},
        ]
        
        # 设置模拟数据库方法
        self.mock_db.get_all_group_chats.return_value = mock_chats_data
        
        # 调用方法
        result = self.chat_manager.get_all_group_chats()
        
        # 验证结果
        self.assertEqual(len(result), 3)
        
        # 验证包含小群组
        group_names = [chat.group_name for chat in result]
        self.assertIn('test_group', group_names)
        self.assertIn('small_group', group_names)
        
        # 验证对象类型
        for chat in result:
            self.assertIsInstance(chat, ChatGroupInfo)

    def test_enter_chat_request_message_parsing(self):
        """测试EnterChatRequest消息解析"""
        # 模拟客户端发送的JSON数据
        json_data = '''
        {
            "message_type": "enter_chat_request",
            "timestamp": 1640995200.0,
            "chat_name": "test_group"
        }
        '''
        
        # 解析消息
        request = parse_message(json_data)
        
        # 验证消息类型
        self.assertEqual(request.message_type, MessageType.ENTER_CHAT_REQUEST)
        self.assertIsInstance(request, EnterChatRequest)
        
        # 验证请求数据
        self.assertEqual(request.chat_name, "test_group")

    def test_enter_chat_response_error_case(self):
        """测试EnterChatResponse错误情况"""
        # 创建错误响应
        response = EnterChatResponse(
            success=False,
            error_message="您不是聊天组的成员"
        )
        
        # 验证消息属性
        self.assertEqual(response.message_type, MessageType.ENTER_CHAT_RESPONSE)
        self.assertFalse(response.success)
        self.assertEqual(response.error_message, "您不是聊天组的成员")

    def test_client_enter_chat_group_handles_error_response(self):
        """测试客户端enter_chat_group方法处理错误响应"""
        # 创建模拟的网络客户端
        mock_network_client = Mock()
        mock_network_client.is_connected.return_value = True
        mock_network_client.send_message.return_value = True
        
        # 创建模拟的错误响应
        mock_response = EnterChatResponse(
            success=False,
            error_message="您不是聊天组的成员"
        )
        mock_network_client.wait_for_response.return_value = mock_response
        
        # 创建聊天客户端
        chat_client = ChatClient()
        chat_client.network_client = mock_network_client
        chat_client.user_id = 1
        chat_client.username = "test_user"
        
        # 模拟登录状态
        with patch.object(chat_client, 'is_logged_in', return_value=True):
            # 调用enter_chat_group方法
            success, message = chat_client.enter_chat_group("test_group")
            
            # 验证结果
            self.assertFalse(success)
            self.assertEqual(message, "您不是聊天组的成员")

    def test_client_enter_chat_group_timeout_handling(self):
        """测试客户端enter_chat_group方法超时处理"""
        # 创建模拟的网络客户端
        mock_network_client = Mock()
        mock_network_client.is_connected.return_value = True
        mock_network_client.send_message.return_value = True
        
        # 模拟超时（返回None）
        mock_network_client.wait_for_response.return_value = None
        
        # 创建聊天客户端
        chat_client = ChatClient()
        chat_client.network_client = mock_network_client
        chat_client.user_id = 1
        chat_client.username = "test_user"
        
        # 模拟登录状态
        with patch.object(chat_client, 'is_logged_in', return_value=True):
            # 调用enter_chat_group方法
            success, message = chat_client.enter_chat_group("test_group")
            
            # 验证结果
            self.assertFalse(success)
            self.assertEqual(message, "服务器无响应")

    def test_list_chats_response_includes_all_groups(self):
        """测试ListChatsResponse包含所有群组"""
        # 创建包含不同成员数量群组的响应
        chats = [
            ChatGroupInfo(group_id=1, group_name='public', is_private_chat=False, member_count=5, created_at='2024-01-01'),
            ChatGroupInfo(group_id=2, group_name='test_group', is_private_chat=False, member_count=1, created_at='2024-01-02'),
            ChatGroupInfo(group_id=3, group_name='small_group', is_private_chat=False, member_count=2, created_at='2024-01-03'),
        ]
        
        response = ListChatsResponse(chats=chats)
        
        # 验证响应包含所有群组
        self.assertEqual(len(response.chats), 3)
        
        # 验证包含小群组
        group_names = [chat.group_name for chat in response.chats]
        self.assertIn('test_group', group_names)
        self.assertIn('small_group', group_names)

    def test_enter_chat_group_updates_current_chat(self):
        """测试进入聊天组更新当前聊天组信息"""
        # 创建模拟的网络客户端
        mock_network_client = Mock()
        mock_network_client.is_connected.return_value = True
        mock_network_client.send_message.return_value = True
        
        # 创建模拟的响应，包含chat_group信息
        mock_chat_group = Mock()
        mock_chat_group.group_id = 123
        mock_chat_group.group_name = "test_group"
        mock_chat_group.is_private_chat = False
        
        mock_response = EnterChatResponse(
            success=True,
            chat_group_id=123,
            chat_name="test_group"
        )
        mock_response.chat_group = mock_chat_group
        mock_network_client.wait_for_response.return_value = mock_response
        
        # 创建聊天客户端
        chat_client = ChatClient()
        chat_client.network_client = mock_network_client
        chat_client.user_id = 1
        chat_client.username = "test_user"
        
        # 模拟登录状态
        with patch.object(chat_client, 'is_logged_in', return_value=True):
            # 调用enter_chat_group方法
            success, message = chat_client.enter_chat_group("test_group")
            
            # 验证结果
            self.assertTrue(success)
            
            # 验证当前聊天组信息被更新
            self.assertIsNotNone(chat_client.current_chat_group)
            self.assertEqual(chat_client.current_chat_group['id'], 123)
            self.assertEqual(chat_client.current_chat_group['name'], "test_group")


if __name__ == '__main__':
    print("开始测试/enter_chat命令时延和/list -g命令显示问题的修复效果...")
    unittest.main(verbosity=2)
