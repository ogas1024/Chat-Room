#!/usr/bin/env python3
"""
测试消息解析修复效果的验证脚本
验证消息解析和数据结构访问是否正确
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    ListUsersResponse, ListChatsResponse, FileListResponse,
    UserInfo, ChatGroupInfo, FileInfo, parse_message
)
from shared.constants import MessageType
from client.commands.parser import CommandHandler, Command


class TestMessageParsingFix(unittest.TestCase):
    """测试消息解析修复效果"""

    def setUp(self):
        """设置测试环境"""
        # 创建模拟的聊天客户端
        self.mock_chat_client = Mock()
        self.mock_chat_client.is_logged_in.return_value = True
        self.mock_chat_client.current_chat_group = {'id': 1, 'name': 'test_group'}
        
        # 创建命令处理器
        self.command_handler = CommandHandler(self.mock_chat_client)

    def test_list_users_response_parsing(self):
        """测试用户列表响应解析"""
        # 模拟服务器返回的JSON数据
        json_data = '''
        {
            "message_type": "list_users_response",
            "timestamp": 1640995200.0,
            "users": [
                {
                    "user_id": 1,
                    "username": "alice",
                    "is_online": true
                },
                {
                    "user_id": 2,
                    "username": "bob",
                    "is_online": false
                }
            ]
        }
        '''
        
        # 解析消息
        response = parse_message(json_data)
        
        # 验证消息类型
        self.assertEqual(response.message_type, MessageType.LIST_USERS_RESPONSE)
        self.assertIsInstance(response, ListUsersResponse)
        
        # 验证用户数据
        self.assertEqual(len(response.users), 2)
        self.assertIsInstance(response.users[0], UserInfo)
        self.assertEqual(response.users[0].user_id, 1)
        self.assertEqual(response.users[0].username, "alice")
        self.assertTrue(response.users[0].is_online)

    def test_list_chats_response_parsing(self):
        """测试聊天组列表响应解析"""
        # 模拟服务器返回的JSON数据
        json_data = '''
        {
            "message_type": "list_chats_response",
            "timestamp": 1640995200.0,
            "chats": [
                {
                    "group_id": 1,
                    "group_name": "General",
                    "is_private_chat": false,
                    "member_count": 5,
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "group_id": 2,
                    "group_name": "Private Chat",
                    "is_private_chat": true,
                    "member_count": 2,
                    "created_at": "2024-01-02T00:00:00Z"
                }
            ]
        }
        '''
        
        # 解析消息
        response = parse_message(json_data)
        
        # 验证消息类型
        self.assertEqual(response.message_type, MessageType.LIST_CHATS_RESPONSE)
        self.assertIsInstance(response, ListChatsResponse)
        
        # 验证聊天组数据
        self.assertEqual(len(response.chats), 2)
        self.assertIsInstance(response.chats[0], ChatGroupInfo)
        self.assertEqual(response.chats[0].group_id, 1)
        self.assertEqual(response.chats[0].group_name, "General")
        self.assertFalse(response.chats[0].is_private_chat)

    def test_list_users_command_with_mock_data(self):
        """测试/list -u命令处理"""
        # 模拟list_users方法返回字典格式数据
        mock_users = [
            {'user_id': 1, 'username': 'alice', 'is_online': True},
            {'user_id': 2, 'username': 'bob', 'is_online': False}
        ]
        self.mock_chat_client.list_users.return_value = (True, "成功", mock_users)
        
        # 创建命令对象
        command = Command(name="list", args=[], options={"-u": True}, raw_input="/list -u")
        
        # 执行命令
        success, message = self.command_handler.handle_list(command)
        
        # 验证结果
        self.assertTrue(success)
        self.assertIn("所有用户列表", message)
        self.assertIn("alice", message)
        self.assertIn("bob", message)
        self.assertIn("ID: 1", message)
        self.assertIn("在线", message)
        self.assertIn("离线", message)

    def test_list_chats_command_with_mock_data(self):
        """测试/list -c命令处理"""
        # 模拟list_chats方法返回字典格式数据
        mock_chats = [
            {'group_id': 1, 'group_name': 'General', 'is_private_chat': False, 'member_count': 5},
            {'group_id': 2, 'group_name': 'Private', 'is_private_chat': True, 'member_count': 2}
        ]
        self.mock_chat_client.list_chats.return_value = (True, "成功", mock_chats)
        
        # 创建命令对象
        command = Command(name="list", args=[], options={"-c": True}, raw_input="/list -c")
        
        # 执行命令
        success, message = self.command_handler.handle_list(command)
        
        # 验证结果
        self.assertTrue(success)
        self.assertIn("已加入的聊天组", message)
        self.assertIn("General", message)
        self.assertIn("Private", message)
        self.assertIn("ID: 1", message)
        self.assertIn("群聊", message)
        self.assertIn("私聊", message)

    def test_list_groups_command_with_mock_data(self):
        """测试/list -g命令处理"""
        # 模拟list_chats方法返回字典格式数据
        mock_chats = [
            {'group_id': 1, 'group_name': 'General', 'is_private_chat': False, 'member_count': 5},
            {'group_id': 2, 'group_name': 'Private', 'is_private_chat': True, 'member_count': 2},
            {'group_id': 3, 'group_name': 'Public', 'is_private_chat': False, 'member_count': 10}
        ]
        self.mock_chat_client.list_chats.return_value = (True, "成功", mock_chats)
        
        # 创建命令对象
        command = Command(name="list", args=[], options={"-g": True}, raw_input="/list -g")
        
        # 执行命令
        success, message = self.command_handler.handle_list(command)
        
        # 验证结果
        self.assertTrue(success)
        self.assertIn("所有群聊列表", message)
        self.assertIn("General", message)
        self.assertIn("Public", message)
        # 私聊应该被过滤掉
        self.assertNotIn("Private", message)

    def test_list_session_users_command_with_mock_data(self):
        """测试/list -s命令处理"""
        # 模拟list_users方法返回字典格式数据
        mock_users = [
            {'user_id': 1, 'username': 'alice', 'is_online': True},
            {'user_id': 2, 'username': 'bob', 'is_online': False}
        ]
        self.mock_chat_client.list_users.return_value = (True, "成功", mock_users)
        
        # 创建命令对象
        command = Command(name="list", args=[], options={"-s": True}, raw_input="/list -s")
        
        # 执行命令
        success, message = self.command_handler.handle_list(command)
        
        # 验证结果
        self.assertTrue(success)
        self.assertIn("聊天组 'test_group' 成员列表", message)
        self.assertIn("alice", message)
        self.assertIn("bob", message)

    def test_empty_lists(self):
        """测试空列表的处理"""
        # 测试空用户列表
        self.mock_chat_client.list_users.return_value = (True, "成功", [])
        command = Command(name="list", args=[], options={"-u": True}, raw_input="/list -u")
        success, message = self.command_handler.handle_list(command)
        self.assertTrue(success)
        self.assertEqual(message, "暂无用户")

        # 测试空聊天组列表
        self.mock_chat_client.list_chats.return_value = (True, "成功", [])
        command = Command(name="list", args=[], options={"-c": True}, raw_input="/list -c")
        success, message = self.command_handler.handle_list(command)
        self.assertTrue(success)
        self.assertEqual(message, "您还没有加入任何聊天组")

    def test_error_handling(self):
        """测试错误处理"""
        # 测试服务器错误
        self.mock_chat_client.list_users.return_value = (False, "服务器错误", None)
        command = Command(name="list", args=[], options={"-u": True}, raw_input="/list -u")
        success, message = self.command_handler.handle_list(command)
        self.assertFalse(success)
        self.assertEqual(message, "服务器错误")


if __name__ == '__main__':
    print("开始测试消息解析修复效果...")
    unittest.main(verbosity=2)
