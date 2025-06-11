#!/usr/bin/env python3
"""
简化的最终修复验证脚本
验证核心问题是否已修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    BaseMessage, ListUsersRequest, ListChatsRequest, FileListRequest,
    FileUploadRequest, FileDownloadRequest, EnterChatRequest, AIChatRequest,
    AIChatResponse, FileListResponse, parse_message
)
from shared.constants import MessageType


def test_message_classes():
    """测试所有消息类"""
    print("🧪 测试消息类创建...")
    
    try:
        # 测试所有专用消息类
        messages = [
            ListUsersRequest(list_type="all", chat_group_id=1),
            ListChatsRequest(list_type="joined"),
            FileListRequest(chat_group_id=2),
            FileUploadRequest(filename="test.txt", file_size=1024, chat_group_id=3),
            FileDownloadRequest(file_id="456"),
            EnterChatRequest(chat_name="public"),
            AIChatRequest(command="status", message="hello", chat_group_id=4),
            AIChatResponse(success=True, message="AI response"),
            FileListResponse(files=[])
        ]
        
        for message in messages:
            # 测试序列化
            json_str = message.to_json()
            assert isinstance(json_str, str)
            assert message.message_type in json_str
            
            # 测试反序列化
            parsed = parse_message(json_str)
            assert type(parsed) == type(message)
            assert parsed.message_type == message.message_type
            
            print(f"✅ {type(message).__name__} 测试成功")
        
        return True
    except Exception as e:
        print(f"❌ 消息类测试失败: {e}")
        return False


def test_base_message_restrictions():
    """测试BaseMessage参数限制"""
    print("🧪 测试BaseMessage参数限制...")
    
    try:
        # 这应该成功
        message = BaseMessage(message_type="test")
        assert message.message_type == "test"
        print("✅ BaseMessage基本创建成功")
        
        # 这些应该失败
        invalid_params = [
            {'list_type': 'all'},
            {'chat_group_id': 123},
            {'filename': 'test.txt'},
            {'file_id': '456'},
            {'chat_name': 'test'},
            {'command': 'help'}
        ]
        
        for params in invalid_params:
            try:
                BaseMessage(message_type="test", **params)
                print(f"❌ BaseMessage不应该接受参数: {list(params.keys())[0]}")
                return False
            except TypeError:
                print(f"✅ BaseMessage正确拒绝了参数: {list(params.keys())[0]}")
        
        return True
    except Exception as e:
        print(f"❌ BaseMessage限制测试失败: {e}")
        return False


def test_server_message_handling():
    """测试服务器端消息处理模拟"""
    print("🧪 测试服务器端消息处理...")
    
    try:
        # 模拟客户端发送请求
        requests = [
            ListUsersRequest(list_type="all", chat_group_id=1),
            ListChatsRequest(list_type="joined"),
            FileListRequest(chat_group_id=2),
            EnterChatRequest(chat_name="public"),
            AIChatRequest(command="status", message="hello")
        ]
        
        for request in requests:
            # 模拟网络传输
            json_str = request.to_json()
            
            # 模拟服务器端解析
            parsed_request = parse_message(json_str)
            
            # 验证解析结果
            assert type(parsed_request) == type(request)
            assert parsed_request.message_type == request.message_type
            
            # 验证字段可以直接访问（这是关键修复）
            if hasattr(request, 'list_type'):
                assert parsed_request.list_type == request.list_type
            if hasattr(request, 'chat_group_id'):
                assert parsed_request.chat_group_id == request.chat_group_id
            if hasattr(request, 'chat_name'):
                assert parsed_request.chat_name == request.chat_name
            if hasattr(request, 'command'):
                assert parsed_request.command == request.command
            
            print(f"✅ {type(request).__name__} 服务器端处理成功")
        
        return True
    except Exception as e:
        print(f"❌ 服务器端消息处理测试失败: {e}")
        return False


def test_client_config():
    """测试客户端配置"""
    print("🧪 测试客户端配置...")
    
    try:
        from client.config.client_config import get_client_config
        client_config = get_client_config()
        logging_config = client_config.get_logging_config()
        
        # 检查日志配置
        assert isinstance(logging_config, dict)
        assert 'level' in logging_config
        assert 'file_enabled' in logging_config
        assert logging_config['file_enabled'] == True  # 应该启用文件日志
        print("✅ 客户端配置正确")
        
        return True
    except Exception as e:
        print(f"❌ 客户端配置测试失败: {e}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("🧪 测试错误处理...")
    
    try:
        from shared.messages import ErrorMessage
        
        # 测试无效JSON
        invalid_json = "invalid json"
        result = parse_message(invalid_json)
        assert isinstance(result, ErrorMessage)
        assert "消息解析失败" in result.error_message
        print("✅ 无效JSON正确处理")
        
        return True
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始验证最终修复效果...")
    print("=" * 50)
    
    tests = [
        ("消息类创建", test_message_classes),
        ("BaseMessage参数限制", test_base_message_restrictions),
        ("服务器端消息处理", test_server_message_handling),
        ("客户端配置", test_client_config),
        ("错误处理", test_error_handling)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有核心修复验证通过！")
        print("\n修复内容:")
        print("1. ✅ 解决了所有BaseMessage初始化错误")
        print("2. ✅ 添加了所有缺失的专用消息类")
        print("3. ✅ 修复了服务器端消息处理")
        print("4. ✅ 启用了客户端文件日志")
        print("5. ✅ 确保了消息字段可以直接访问")
        print("\n现在/list命令应该可以正常工作了！")
        print("\n测试方法:")
        print("1. 启动服务器: python server/main.py")
        print("2. 启动客户端: python client/main.py --mode simple")
        print("3. 登录后测试: /list -u, /list -c, /list -f 等命令")
        print("4. 查看日志: tail -f logs/client.log")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
