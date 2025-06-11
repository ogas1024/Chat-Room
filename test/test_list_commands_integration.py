#!/usr/bin/env python3
"""
/list命令集成测试
验证消息解析修复后的实际效果
"""

import sys
import os
import unittest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    ListUsersResponse, ListChatsResponse, UserInfo, ChatGroupInfo, parse_message
)
from shared.constants import MessageType


class TestListCommandsIntegration(unittest.TestCase):
    """测试/list命令集成效果"""

    def test_parse_real_server_response_users(self):
        """测试解析真实的服务器用户列表响应"""
        # 模拟服务器实际返回的JSON响应
        server_response = '''
        {
            "message_type": "list_users_response",
            "timestamp": 1640995200.0,
            "users": [
                {
                    "user_id": 1,
                    "username": "test",
                    "is_online": true
                },
                {
                    "user_id": 2,
                    "username": "alice",
                    "is_online": false
                }
            ]
        }
        '''
        
        # 解析消息
        response = parse_message(server_response)
        
        # 验证解析结果
        self.assertIsInstance(response, ListUsersResponse)
        self.assertEqual(response.message_type, MessageType.LIST_USERS_RESPONSE)
        self.assertEqual(len(response.users), 2)
        
        # 验证第一个用户
        user1 = response.users[0]
        self.assertIsInstance(user1, UserInfo)
        self.assertEqual(user1.user_id, 1)
        self.assertEqual(user1.username, "test")
        self.assertTrue(user1.is_online)
        
        # 验证第二个用户
        user2 = response.users[1]
        self.assertIsInstance(user2, UserInfo)
        self.assertEqual(user2.user_id, 2)
        self.assertEqual(user2.username, "alice")
        self.assertFalse(user2.is_online)
        
        # 验证可以正常访问属性（这是之前失败的地方）
        try:
            for user in response.users:
                _ = user.user_id
                _ = user.username
                _ = user.is_online
        except AttributeError as e:
            self.fail(f"访问用户属性时出错: {e}")

    def test_parse_real_server_response_chats(self):
        """测试解析真实的服务器聊天组列表响应"""
        # 模拟服务器实际返回的JSON响应
        server_response = '''
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
        response = parse_message(server_response)
        
        # 验证解析结果
        self.assertIsInstance(response, ListChatsResponse)
        self.assertEqual(response.message_type, MessageType.LIST_CHATS_RESPONSE)
        self.assertEqual(len(response.chats), 2)
        
        # 验证第一个聊天组
        chat1 = response.chats[0]
        self.assertIsInstance(chat1, ChatGroupInfo)
        self.assertEqual(chat1.group_id, 1)
        self.assertEqual(chat1.group_name, "General")
        self.assertFalse(chat1.is_private_chat)
        self.assertEqual(chat1.member_count, 5)
        
        # 验证第二个聊天组
        chat2 = response.chats[1]
        self.assertIsInstance(chat2, ChatGroupInfo)
        self.assertEqual(chat2.group_id, 2)
        self.assertEqual(chat2.group_name, "Private Chat")
        self.assertTrue(chat2.is_private_chat)
        self.assertEqual(chat2.member_count, 2)
        
        # 验证可以正常访问属性（这是之前失败的地方）
        try:
            for chat in response.chats:
                _ = chat.group_id
                _ = chat.group_name
                _ = chat.is_private_chat
                _ = chat.member_count
        except AttributeError as e:
            self.fail(f"访问聊天组属性时出错: {e}")

    def test_empty_lists_parsing(self):
        """测试空列表的解析"""
        # 测试空用户列表
        empty_users_response = '''
        {
            "message_type": "list_users_response",
            "timestamp": 1640995200.0,
            "users": []
        }
        '''
        
        response = parse_message(empty_users_response)
        self.assertIsInstance(response, ListUsersResponse)
        self.assertEqual(len(response.users), 0)
        
        # 测试空聊天组列表
        empty_chats_response = '''
        {
            "message_type": "list_chats_response",
            "timestamp": 1640995200.0,
            "chats": []
        }
        '''
        
        response = parse_message(empty_chats_response)
        self.assertIsInstance(response, ListChatsResponse)
        self.assertEqual(len(response.chats), 0)

    def test_missing_fields_handling(self):
        """测试缺少字段时的处理"""
        # 测试缺少users字段
        response_without_users = '''
        {
            "message_type": "list_users_response",
            "timestamp": 1640995200.0
        }
        '''
        
        response = parse_message(response_without_users)
        self.assertIsInstance(response, ListUsersResponse)
        self.assertEqual(len(response.users), 0)  # 应该初始化为空列表
        
        # 测试缺少chats字段
        response_without_chats = '''
        {
            "message_type": "list_chats_response",
            "timestamp": 1640995200.0
        }
        '''
        
        response = parse_message(response_without_chats)
        self.assertIsInstance(response, ListChatsResponse)
        self.assertEqual(len(response.chats), 0)  # 应该初始化为空列表

    def test_data_conversion_consistency(self):
        """测试数据转换的一致性"""
        # 创建一个包含用户数据的响应
        server_response = '''
        {
            "message_type": "list_users_response",
            "timestamp": 1640995200.0,
            "users": [
                {
                    "user_id": 123,
                    "username": "testuser",
                    "is_online": true
                }
            ]
        }
        '''
        
        # 解析消息
        response = parse_message(server_response)
        
        # 验证数据类型和值
        user = response.users[0]
        self.assertIsInstance(user.user_id, int)
        self.assertIsInstance(user.username, str)
        self.assertIsInstance(user.is_online, bool)
        
        self.assertEqual(user.user_id, 123)
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.is_online)

    def test_attribute_access_patterns(self):
        """测试不同的属性访问模式"""
        server_response = '''
        {
            "message_type": "list_users_response",
            "timestamp": 1640995200.0,
            "users": [
                {
                    "user_id": 1,
                    "username": "test",
                    "is_online": true
                }
            ]
        }
        '''
        
        response = parse_message(server_response)
        user = response.users[0]
        
        # 测试直接属性访问（这是修复的关键）
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.username, "test")
        self.assertTrue(user.is_online)
        
        # 测试getattr访问
        self.assertEqual(getattr(user, 'user_id'), 1)
        self.assertEqual(getattr(user, 'username'), "test")
        self.assertTrue(getattr(user, 'is_online'))
        
        # 测试hasattr检查
        self.assertTrue(hasattr(user, 'user_id'))
        self.assertTrue(hasattr(user, 'username'))
        self.assertTrue(hasattr(user, 'is_online'))


if __name__ == '__main__':
    print("开始/list命令集成测试...")
    unittest.main(verbosity=2)
