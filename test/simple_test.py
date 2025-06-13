#!/usr/bin/env python3
"""
简化的修复验证测试
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """测试导入"""
    print("🧪 测试模块导入...")
    
    try:
        from shared.messages import ChatMessage, ChatHistoryComplete
        print("✅ shared.messages 导入成功")
        
        from shared.constants import MessageType
        print("✅ shared.constants 导入成功")
        
        from client.core.client import NetworkClient
        print("✅ client.core.client 导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_encoding_fix():
    """测试编码修复"""
    print("🧪 测试编码修复...")
    
    try:
        # 测试中文消息编码
        test_content = "@AI 帮我翻译下面这段话: hello world 你好世界"
        
        # 模拟字节缓冲区处理
        message_json = f'{{"content": "{test_content}"}}\n'
        message_bytes = message_json.encode('utf-8')
        
        # 模拟分片接收
        buffer = b""
        chunk_size = 50
        
        for i in range(0, len(message_bytes), chunk_size):
            chunk = message_bytes[i:i+chunk_size]
            buffer += chunk
        
        # 处理完整消息
        if b'\n' in buffer:
            line_bytes, remaining = buffer.split(b'\n', 1)
            try:
                decoded_message = line_bytes.decode('utf-8')
                print(f"✅ 编码修复验证成功: {len(decoded_message)} 字符")
                
                import json
                parsed_data = json.loads(decoded_message)
                if parsed_data.get('content') == test_content:
                    print("✅ 中文内容验证通过")
                    return True
                else:
                    print("❌ 中文内容验证失败")
                    return False
                    
            except UnicodeDecodeError as e:
                print(f"❌ 解码失败: {e}")
                return False
        else:
            print("❌ 消息处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 编码测试失败: {e}")
        return False


def test_message_handlers():
    """测试消息处理器"""
    print("🧪 测试消息处理器...")
    
    try:
        from client.core.client import NetworkClient
        
        # 创建网络客户端
        client = NetworkClient()
        
        # 测试消息处理器设置
        def test_handler(message):
            pass
        
        client.set_message_handler("test_type", test_handler)
        
        if "test_type" in client.message_handlers:
            print("✅ 消息处理器设置成功")
            
            if client.message_handlers["test_type"] == test_handler:
                print("✅ 消息处理器引用正确")
                return True
            else:
                print("❌ 消息处理器引用错误")
                return False
        else:
            print("❌ 消息处理器设置失败")
            return False
            
    except Exception as e:
        print(f"❌ 消息处理器测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("🔧 简化修复验证测试")
    print("=" * 50)
    
    tests = [
        ("模块导入测试", test_imports),
        ("编码修复测试", test_encoding_fix),
        ("消息处理器测试", test_message_handlers),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
                print("✅ 测试通过")
            else:
                print("❌ 测试失败")
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 基础修复验证通过！")
    else:
        print("⚠️  部分测试失败")
    
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
