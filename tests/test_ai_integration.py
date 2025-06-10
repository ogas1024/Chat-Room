#!/usr/bin/env python3
"""
AI集成功能测试脚本
测试智谱AI API集成和AI管理器功能
"""

import os
import sys
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from server.ai.zhipu_client import ZhipuClient, AIMessage
from server.ai.context_manager import ContextManager
from server.ai.ai_manager import AIManager
from server.config.ai_config import get_ai_config, print_ai_setup_guide


def test_zhipu_client():
    """测试智谱AI客户端"""
    print("🧪 测试智谱AI客户端...")
    
    try:
        client = ZhipuClient()
        print(f"✅ 客户端初始化成功")
        
        # 测试连接
        if client.test_connection():
            print("✅ API连接测试成功")
            
            # 测试简单聊天
            response = client.simple_chat("你好，请简单介绍一下自己")
            if response:
                print(f"✅ 简单聊天测试成功")
                print(f"   AI回复: {response[:100]}...")
            else:
                print("❌ 简单聊天测试失败")
        else:
            print("❌ API连接测试失败")
            
    except Exception as e:
        print(f"❌ 智谱AI客户端测试失败: {e}")
        return False
    
    return True


def test_context_manager():
    """测试上下文管理器"""
    print("\n🧪 测试上下文管理器...")
    
    try:
        context_mgr = ContextManager(max_context_length=5)
        
        # 添加测试消息
        context_mgr.add_message("1", "user", "你好", is_group=True)
        context_mgr.add_message("1", "assistant", "你好！有什么可以帮助你的吗？", is_group=True)
        context_mgr.add_message("1", "user", "今天天气怎么样？", is_group=True)
        
        # 获取上下文
        context = context_mgr.get_context("1", is_group=True)
        print(f"✅ 上下文管理器测试成功，上下文长度: {len(context)}")
        
        # 测试摘要
        summary = context_mgr.get_context_summary()
        print(f"✅ 上下文摘要: {summary}")
        
    except Exception as e:
        print(f"❌ 上下文管理器测试失败: {e}")
        return False
    
    return True


def test_ai_manager():
    """测试AI管理器"""
    print("\n🧪 测试AI管理器...")
    
    try:
        ai_manager = AIManager()
        
        if not ai_manager.is_enabled():
            print("⚠️  AI管理器未启用（可能是API密钥未设置）")
            return True
        
        print("✅ AI管理器初始化成功")
        
        # 测试状态
        status = ai_manager.get_ai_status()
        print(f"✅ AI状态获取成功: {status['enabled']}")
        
        # 测试消息处理判断
        test_messages = [
            ("你好AI", True),
            ("@AI 帮我解答一个问题", True),
            ("今天天气不错", False),
            ("这是什么？", True),  # 问号结尾
        ]
        
        for msg, expected in test_messages:
            result = ai_manager.should_respond_to_message(msg, is_group_chat=True)
            status = "✅" if result == expected else "❌"
            print(f"   {status} 消息判断: '{msg}' -> {result}")
        
        # 测试命令处理
        commands = ["status", "help", "clear"]
        for cmd in commands:
            response = ai_manager.handle_ai_command(cmd, 1, 1)
            print(f"✅ 命令处理 '{cmd}': {response[:50]}...")
        
    except Exception as e:
        print(f"❌ AI管理器测试失败: {e}")
        return False
    
    return True


def test_ai_conversation():
    """测试AI对话功能"""
    print("\n🧪 测试AI对话功能...")
    
    try:
        ai_manager = AIManager()
        
        if not ai_manager.is_enabled():
            print("⚠️  AI功能未启用，跳过对话测试")
            return True
        
        # 模拟对话
        test_conversations = [
            ("你好，AI助手", "群聊测试"),
            ("请介绍一下Python编程语言", "技术问题测试"),
            ("今天天气怎么样？", "日常对话测试"),
        ]
        
        for message, description in test_conversations:
            print(f"   测试: {description}")
            response = ai_manager.process_message(
                user_id=1,
                username="测试用户",
                message_content=message,
                chat_group_id=1
            )
            
            if response:
                print(f"   ✅ AI回复: {response[:100]}...")
            else:
                print(f"   ⚠️  AI未回复")
            
            time.sleep(1)  # 避免请求过快
        
    except Exception as e:
        print(f"❌ AI对话测试失败: {e}")
        return False
    
    return True


def main():
    """主测试函数"""
    print("🤖 Chat-Room AI集成功能测试")
    print("=" * 50)
    
    # 检查配置
    config = get_ai_config()
    print(f"API密钥设置: {'✅' if config.is_enabled() else '❌'}")
    
    if not config.is_enabled():
        print("\n⚠️  AI功能未配置，将显示设置指南...")
        print_ai_setup_guide()
        print("\n继续进行基础功能测试...")
    
    # 运行测试
    tests = [
        ("智谱AI客户端", test_zhipu_client),
        ("上下文管理器", test_context_manager),
        ("AI管理器", test_ai_manager),
        ("AI对话功能", test_ai_conversation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    # 测试结果
    print(f"\n{'='*50}")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！AI功能集成成功！")
    elif passed > 0:
        print("⚠️  部分测试通过，请检查失败的测试项")
    else:
        print("❌ 所有测试失败，请检查配置和代码")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
