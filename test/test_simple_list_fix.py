#!/usr/bin/env python3
"""
简单测试验证/list命令修复效果
主要验证BaseMessage初始化错误是否已修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    BaseMessage, ListUsersRequest, ListChatsRequest, 
    create_message_from_dict
)
from shared.constants import MessageType


def test_base_message_fix():
    """测试BaseMessage修复"""
    print("🧪 测试BaseMessage修复...")
    
    try:
        # 这应该成功，因为BaseMessage只接受message_type和timestamp
        message = BaseMessage(message_type="test")
        print("✅ BaseMessage基本创建成功")
        
        # 这应该失败，因为BaseMessage不接受list_type参数
        try:
            BaseMessage(message_type="test", list_type="all")
            print("❌ BaseMessage不应该接受list_type参数")
            return False
        except TypeError:
            print("✅ BaseMessage正确拒绝了list_type参数")
        
        return True
    except Exception as e:
        print(f"❌ BaseMessage测试失败: {e}")
        return False


def test_list_users_request():
    """测试ListUsersRequest"""
    print("🧪 测试ListUsersRequest...")
    
    try:
        # 基本创建
        request = ListUsersRequest()
        assert request.message_type == MessageType.LIST_USERS_REQUEST
        assert request.list_type == "all"
        assert request.chat_group_id is None
        print("✅ ListUsersRequest基本创建成功")
        
        # 带参数创建
        request = ListUsersRequest(list_type="current_chat", chat_group_id=123)
        assert request.list_type == "current_chat"
        assert request.chat_group_id == 123
        print("✅ ListUsersRequest带参数创建成功")
        
        # 序列化测试
        json_str = request.to_json()
        assert "list_type" in json_str
        assert "current_chat" in json_str
        print("✅ ListUsersRequest序列化成功")
        
        # 反序列化测试
        data = request.to_dict()
        recreated = ListUsersRequest.from_dict(data)
        assert recreated.list_type == "current_chat"
        assert recreated.chat_group_id == 123
        print("✅ ListUsersRequest反序列化成功")
        
        return True
    except Exception as e:
        print(f"❌ ListUsersRequest测试失败: {e}")
        return False


def test_list_chats_request():
    """测试ListChatsRequest"""
    print("🧪 测试ListChatsRequest...")
    
    try:
        # 基本创建
        request = ListChatsRequest()
        assert request.message_type == MessageType.LIST_CHATS_REQUEST
        assert request.list_type == "joined"
        print("✅ ListChatsRequest基本创建成功")
        
        # 带参数创建
        request = ListChatsRequest(list_type="all")
        assert request.list_type == "all"
        print("✅ ListChatsRequest带参数创建成功")
        
        # 序列化测试
        json_str = request.to_json()
        assert "list_type" in json_str
        assert "all" in json_str
        print("✅ ListChatsRequest序列化成功")
        
        return True
    except Exception as e:
        print(f"❌ ListChatsRequest测试失败: {e}")
        return False


def test_message_type_mapping():
    """测试消息类型映射"""
    print("🧪 测试消息类型映射...")
    
    try:
        # 测试ListUsersRequest映射
        data = {
            'message_type': MessageType.LIST_USERS_REQUEST,
            'list_type': 'all',
            'chat_group_id': None,
            'timestamp': 1234567890.0
        }
        message = create_message_from_dict(data)
        assert isinstance(message, ListUsersRequest)
        assert message.list_type == 'all'
        print("✅ ListUsersRequest类型映射成功")
        
        # 测试ListChatsRequest映射
        data = {
            'message_type': MessageType.LIST_CHATS_REQUEST,
            'list_type': 'joined',
            'timestamp': 1234567890.0
        }
        message = create_message_from_dict(data)
        assert isinstance(message, ListChatsRequest)
        assert message.list_type == 'joined'
        print("✅ ListChatsRequest类型映射成功")
        
        return True
    except Exception as e:
        print(f"❌ 消息类型映射测试失败: {e}")
        return False


def test_client_methods():
    """测试客户端方法能正确创建请求"""
    print("🧪 测试客户端方法...")
    
    try:
        from client.core.client import ChatClient
        from unittest.mock import Mock
        
        # 创建模拟客户端
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
        result = client.list_users("current_chat")
        assert result[0] == True  # success
        
        # 验证发送的消息类型
        sent_message = client.network_client.send_message.call_args[0][0]
        assert isinstance(sent_message, ListUsersRequest)
        assert sent_message.list_type == "current_chat"
        assert sent_message.chat_group_id == 1
        print("✅ list_users方法测试成功")
        
        # 测试list_chats方法
        mock_response.message_type = MessageType.LIST_CHATS_RESPONSE
        mock_response.chats = []
        client.network_client.wait_for_response.return_value = mock_response
        
        result = client.list_chats("all")
        assert result[0] == True  # success
        
        # 验证发送的消息类型
        sent_message = client.network_client.send_message.call_args[0][0]
        assert isinstance(sent_message, ListChatsRequest)
        assert sent_message.list_type == "all"
        print("✅ list_chats方法测试成功")
        
        return True
    except Exception as e:
        print(f"❌ 客户端方法测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始验证/list命令修复效果...")
    print("=" * 50)
    
    tests = [
        test_base_message_fix,
        test_list_users_request,
        test_list_chats_request,
        test_message_type_mapping,
        test_client_methods
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            print()
    
    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！/list命令修复成功")
        print("\n修复内容:")
        print("1. ✅ 添加了ListUsersRequest和ListChatsRequest消息类")
        print("2. ✅ 更新了消息类型映射")
        print("3. ✅ 修复了客户端list_users和list_chats方法")
        print("4. ✅ 解决了BaseMessage初始化时的list_type参数错误")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
