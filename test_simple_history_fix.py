#!/usr/bin/env python3
"""
简单的聊天记录加载修复测试
验证新增的CHAT_HISTORY_COMPLETE消息类型是否正常工作
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_message_types():
    """测试新增的消息类型"""
    print("🧪 测试新增的消息类型...")
    
    try:
        from shared.constants import MessageType
        from shared.messages import ChatHistoryComplete, create_message_from_dict
        
        # 测试新的消息类型常量
        print(f"✅ CHAT_HISTORY_COMPLETE 常量: {MessageType.CHAT_HISTORY_COMPLETE}")
        
        # 测试新的消息类
        complete_msg = ChatHistoryComplete(
            chat_group_id=123,
            message_count=5
        )
        print(f"✅ ChatHistoryComplete 消息创建成功: {complete_msg}")
        
        # 测试消息序列化
        msg_dict = complete_msg.to_dict()
        print(f"✅ 消息序列化: {msg_dict}")
        
        # 测试消息反序列化
        reconstructed_msg = create_message_from_dict(msg_dict)
        print(f"✅ 消息反序列化: {reconstructed_msg}")
        
        # 验证消息类型
        assert reconstructed_msg.message_type == MessageType.CHAT_HISTORY_COMPLETE
        assert reconstructed_msg.chat_group_id == 123
        assert reconstructed_msg.message_count == 5
        
        print("✅ 所有消息类型测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 消息类型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_server_imports():
    """测试服务器端的导入"""
    print("🧪 测试服务器端导入...")
    
    try:
        from shared.messages import ChatHistoryComplete
        from server.core.server import ChatRoomServer
        
        print("✅ 服务器端导入成功")
        
        # 测试创建完成通知消息
        notification = ChatHistoryComplete(
            chat_group_id=1,
            message_count=10
        )
        
        print(f"✅ 服务器端可以创建完成通知: {notification}")
        return True
        
    except Exception as e:
        print(f"❌ 服务器端导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_client_imports():
    """测试客户端的导入"""
    print("🧪 测试客户端导入...")
    
    try:
        from client.core.client import ChatClient
        from client.ui.app import ChatRoomApp
        
        print("✅ 客户端导入成功")
        return True
        
    except Exception as e:
        print(f"❌ 客户端导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("🚀 开始聊天记录加载修复的基础测试...")
    
    tests = [
        ("消息类型测试", test_message_types),
        ("服务器端导入测试", test_server_imports),
        ("客户端导入测试", test_client_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 运行 {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基础测试通过！修复的基础结构正常工作。")
        return True
    else:
        print("💥 部分测试失败！需要检查修复。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
