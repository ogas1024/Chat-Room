#!/usr/bin/env python3
"""
核心消息修复验证脚本
验证BaseMessage错误和消息类型问题是否已修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.messages import (
    BaseMessage, ListUsersRequest, ListChatsRequest, FileListRequest,
    FileUploadRequest, FileDownloadRequest, EnterChatRequest, AIChatRequest,
    create_message_from_dict
)
from shared.constants import MessageType


def test_base_message_fix():
    """测试BaseMessage修复"""
    print("🧪 测试BaseMessage修复...")
    
    try:
        # 这应该成功
        message = BaseMessage(message_type="test")
        print("✅ BaseMessage基本创建成功")
        
        # 这些应该失败
        error_count = 0
        test_params = [
            {'list_type': 'all'},
            {'chat_group_id': 123},
            {'filename': 'test.txt'},
            {'file_id': '456'},
            {'chat_name': 'test'},
            {'command': 'help'}
        ]
        
        for params in test_params:
            try:
                BaseMessage(message_type="test", **params)
                print(f"❌ BaseMessage不应该接受参数: {list(params.keys())[0]}")
                error_count += 1
            except TypeError:
                print(f"✅ BaseMessage正确拒绝了参数: {list(params.keys())[0]}")
        
        return error_count == 0
    except Exception as e:
        print(f"❌ BaseMessage测试失败: {e}")
        return False


def test_specialized_message_classes():
    """测试专用消息类"""
    print("🧪 测试专用消息类...")
    
    try:
        # 测试所有专用消息类
        test_cases = [
            (ListUsersRequest, {'list_type': 'current_chat', 'chat_group_id': 123}),
            (ListChatsRequest, {'list_type': 'all'}),
            (FileListRequest, {'chat_group_id': 456}),
            (FileUploadRequest, {'filename': 'test.txt', 'file_size': 1024, 'chat_group_id': 789}),
            (FileDownloadRequest, {'file_id': '123'}),
            (EnterChatRequest, {'chat_name': 'test_chat'}),
            (AIChatRequest, {'command': 'help', 'message': 'test', 'chat_group_id': 999})
        ]
        
        for message_class, params in test_cases:
            message = message_class(**params)

            # 验证消息类型 - 直接使用消息实例的message_type
            if not hasattr(message, 'message_type') or not message.message_type:
                print(f"❌ {message_class.__name__} 消息类型缺失")
                return False
            
            # 验证序列化
            json_str = message.to_json()
            if not isinstance(json_str, str) or message.message_type not in json_str:
                print(f"❌ {message_class.__name__} 序列化失败")
                return False
            
            # 验证反序列化
            data = message.to_dict()
            recreated = message_class.from_dict(data)
            if recreated.message_type != message.message_type:
                print(f"❌ {message_class.__name__} 反序列化失败")
                return False
            
            print(f"✅ {message_class.__name__} 测试成功")
        
        return True
    except Exception as e:
        print(f"❌ 专用消息类测试失败: {e}")
        return False


def test_message_type_mapping():
    """测试消息类型映射"""
    print("🧪 测试消息类型映射...")
    
    try:
        test_cases = [
            (MessageType.LIST_USERS_REQUEST, ListUsersRequest, {'list_type': 'all'}),
            (MessageType.LIST_CHATS_REQUEST, ListChatsRequest, {'list_type': 'joined'}),
            (MessageType.FILE_LIST_REQUEST, FileListRequest, {'chat_group_id': 1}),
            (MessageType.FILE_UPLOAD_REQUEST, FileUploadRequest, {'filename': 'test.txt', 'file_size': 1024}),
            (MessageType.FILE_DOWNLOAD_REQUEST, FileDownloadRequest, {'file_id': '123'}),
            (MessageType.ENTER_CHAT_REQUEST, EnterChatRequest, {'chat_name': 'test'}),
            (MessageType.AI_CHAT_REQUEST, AIChatRequest, {'command': 'help', 'message': 'test'})
        ]
        
        for message_type, expected_class, extra_data in test_cases:
            data = {
                'message_type': message_type,
                'timestamp': 1234567890.0,
                **extra_data
            }
            message = create_message_from_dict(data)
            
            if not isinstance(message, expected_class):
                print(f"❌ {expected_class.__name__} 类型映射失败")
                return False
            
            if message.message_type != message_type:
                print(f"❌ {expected_class.__name__} 消息类型不匹配")
                return False
            
            print(f"✅ {expected_class.__name__} 类型映射成功")
        
        return True
    except Exception as e:
        print(f"❌ 消息类型映射测试失败: {e}")
        return False


def test_client_code_analysis():
    """分析客户端代码，检查是否还有BaseMessage的错误使用"""
    print("🧪 分析客户端代码...")
    
    try:
        client_file = os.path.join(os.path.dirname(__file__), '..', 'client', 'core', 'client.py')
        with open(client_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有问题的BaseMessage使用
        problematic_lines = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'BaseMessage(' in line and any(param in line for param in [
                'list_type', 'chat_group_id', 'filename', 'file_id', 'chat_name', 'command'
            ]):
                problematic_lines.append((i, line.strip()))
        
        if problematic_lines:
            print("❌ 发现问题的BaseMessage使用:")
            for line_num, line in problematic_lines:
                print(f"  第{line_num}行: {line}")
            return False
        else:
            print("✅ 客户端代码中没有发现BaseMessage的错误使用")
            return True
            
    except Exception as e:
        print(f"❌ 客户端代码分析失败: {e}")
        return False


def test_import_statements():
    """测试导入语句"""
    print("🧪 测试导入语句...")
    
    try:
        # 测试所有消息类是否可以正确导入
        from shared.messages import (
            ListUsersRequest, ListChatsRequest, FileListRequest,
            FileUploadRequest, FileDownloadRequest, EnterChatRequest, 
            AIChatRequest, AIChatResponse
        )
        print("✅ 所有消息类导入成功")
        
        # 测试消息类型常量
        from shared.constants import MessageType
        required_types = [
            'LIST_USERS_REQUEST', 'LIST_CHATS_REQUEST', 'FILE_LIST_REQUEST',
            'FILE_UPLOAD_REQUEST', 'FILE_DOWNLOAD_REQUEST', 'ENTER_CHAT_REQUEST',
            'AI_CHAT_REQUEST', 'AI_CHAT_RESPONSE'
        ]
        
        for type_name in required_types:
            if not hasattr(MessageType, type_name):
                print(f"❌ 缺少消息类型: {type_name}")
                return False
        
        print("✅ 所有消息类型常量存在")
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始验证核心消息修复效果...")
    print("=" * 50)
    
    tests = [
        ("BaseMessage修复", test_base_message_fix),
        ("专用消息类", test_specialized_message_classes),
        ("消息类型映射", test_message_type_mapping),
        ("客户端代码分析", test_client_code_analysis),
        ("导入语句", test_import_statements)
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
        print("1. ✅ 解决了BaseMessage初始化时的参数错误")
        print("2. ✅ 添加了所有缺失的专用消息类")
        print("3. ✅ 更新了完整的消息类型映射")
        print("4. ✅ 修复了客户端方法的消息类型使用")
        print("5. ✅ 确保了所有导入语句正确")
        print("\n现在/list命令应该可以正常工作了！")
        return True
    else:
        print("❌ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
