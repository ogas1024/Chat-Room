#!/usr/bin/env python3
"""
简单验证修复效果的脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_enter_chat_response_parsing():
    """测试EnterChatResponse消息解析"""
    from shared.messages import parse_message, EnterChatResponse
    from shared.constants import MessageType
    
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
    assert response.message_type == MessageType.ENTER_CHAT_RESPONSE
    assert isinstance(response, EnterChatResponse)
    
    # 验证响应数据
    assert response.success == True
    assert response.chat_group_id == 123
    assert response.chat_name == "test_group"
    
    print("✅ EnterChatResponse消息解析测试通过")

def test_enter_chat_response_creation():
    """测试EnterChatResponse消息创建"""
    from shared.messages import EnterChatResponse
    from shared.constants import MessageType
    
    # 创建响应消息
    response = EnterChatResponse(
        success=True,
        chat_group_id=123,
        chat_name="test_group"
    )
    
    # 验证消息属性
    assert response.message_type == MessageType.ENTER_CHAT_RESPONSE
    assert response.success == True
    assert response.chat_group_id == 123
    assert response.chat_name == "test_group"
    
    print("✅ EnterChatResponse消息创建测试通过")

def test_chat_manager_includes_small_groups():
    """测试ChatManager包含小群组"""
    from unittest.mock import Mock
    from server.core.chat_manager import ChatManager
    from shared.messages import ChatGroupInfo
    
    # 创建模拟的用户管理器和数据库
    mock_user_manager = Mock()
    mock_db = Mock()
    
    # 创建聊天管理器
    chat_manager = ChatManager(mock_user_manager)
    chat_manager.db = mock_db
    
    # 模拟数据库返回的聊天组数据
    mock_chats_data = [
        {'id': 1, 'name': 'public', 'is_private_chat': False, 'member_count': 5, 'created_at': '2024-01-01'},
        {'id': 2, 'name': 'test_group', 'is_private_chat': False, 'member_count': 1, 'created_at': '2024-01-02'},
        {'id': 3, 'name': 'small_group', 'is_private_chat': False, 'member_count': 2, 'created_at': '2024-01-03'},
    ]
    
    # 设置模拟数据库方法
    mock_db.get_all_group_chats.return_value = mock_chats_data
    
    # 调用方法
    result = chat_manager.get_all_group_chats()
    
    # 验证结果
    assert len(result) == 3
    
    # 验证包含小群组
    group_names = [chat.group_name for chat in result]
    assert 'test_group' in group_names
    assert 'small_group' in group_names
    
    # 验证对象类型
    for chat in result:
        assert isinstance(chat, ChatGroupInfo)
    
    print("✅ ChatManager包含小群组测试通过")

def test_database_sql_structure():
    """测试数据库SQL查询结构"""
    # 检查修复后的代码文件
    with open('server/database/models.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找get_all_group_chats方法
    method_start = content.find('def get_all_group_chats(self)')
    method_end = content.find('\n    def ', method_start + 1)
    if method_end == -1:
        method_end = len(content)
    
    method_content = content[method_start:method_end]
    
    # 验证不包含HAVING子句
    assert 'HAVING COUNT(gm.user_id) > 2' not in method_content
    assert 'HAVING' not in method_content
    
    print("✅ 数据库SQL查询结构测试通过")

def test_server_imports():
    """测试服务器导入"""
    # 检查服务器文件是否正确导入了EnterChatResponse
    with open('server/core/server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 验证导入了EnterChatResponse
    assert 'EnterChatResponse' in content
    assert 'from shared.messages import' in content
    
    print("✅ 服务器导入测试通过")

def test_server_response_type():
    """测试服务器响应类型"""
    # 检查服务器文件是否使用了正确的响应类型
    with open('server/core/server.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找handle_enter_chat_request方法
    method_start = content.find('def handle_enter_chat_request(self')
    method_end = content.find('\n    def ', method_start + 1)
    if method_end == -1:
        method_end = content.find('\n\n    def ', method_start + 1)
    
    method_content = content[method_start:method_end]
    
    # 验证使用了EnterChatResponse而不是SystemMessage
    assert 'EnterChatResponse(' in method_content
    assert 'success=True' in method_content
    assert 'chat_group_id=group_info[\'id\']' in method_content
    
    print("✅ 服务器响应类型测试通过")

def main():
    """运行所有测试"""
    print("开始验证修复效果...")
    
    try:
        test_enter_chat_response_parsing()
        test_enter_chat_response_creation()
        test_chat_manager_includes_small_groups()
        test_database_sql_structure()
        test_server_imports()
        test_server_response_type()
        
        print("\n🎉 所有测试都通过了！修复效果验证成功！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
