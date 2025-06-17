#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI触发逻辑修复演示
演示AI回复只在@AI时触发的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch
from server.ai.ai_manager import AIManager
from server.config.ai_config import get_ai_config


def demo_ai_trigger_fix():
    """演示AI触发逻辑修复效果"""
    print("🤖 AI触发逻辑修复演示")
    print("=" * 50)
    
    # 加载真实配置
    ai_config = get_ai_config()
    print(f"📋 当前配置: require_at_mention = {ai_config.require_at_mention}")
    
    # 创建AI管理器（使用模拟的依赖以避免实际API调用）
    with patch('server.ai.ai_manager.ZhipuClient'), \
         patch('server.ai.ai_manager.ContextManager'):
        ai_manager = AIManager(config=ai_config)
    
    # 测试消息列表
    test_messages = [
        # 应该触发AI回复的消息
        ("你好@AI，请帮我解答一个问题", True, "✅ 应该回复"),
        ("@ai 今天天气怎么样？", True, "✅ 应该回复"),
        ("请问@Ai能帮我写代码吗？", True, "✅ 应该回复"),
        
        # 不应该触发AI回复的消息
        ("这是一个普通的消息", False, "❌ 不应该回复"),
        ("我有一个问题？", False, "❌ 不应该回复（问号触发已禁用）"),
        ("人工智能很厉害", False, "❌ 不应该回复（关键词触发已禁用）"),
        ("智能助手很有用", False, "❌ 不应该回复（关键词触发已禁用）"),
        ("ai技术发展很快", False, "❌ 不应该回复（关键词触发已禁用）"),
        ("机器人很有趣", False, "❌ 不应该回复（关键词触发已禁用）"),
    ]
    
    print("\n🧪 群聊消息测试:")
    print("-" * 30)
    
    all_passed = True
    for message, expected, description in test_messages:
        result = ai_manager.should_respond_to_message(message, is_group_chat=True)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        if result != expected:
            all_passed = False
        
        print(f"{status} | {description}")
        print(f"     消息: '{message}'")
        print(f"     结果: {'会回复' if result else '不会回复'}")
        print()
    
    print("\n🔒 私聊消息测试:")
    print("-" * 30)
    # 私聊中应该总是回复
    private_messages = [
        "这是一个私聊消息",
        "普通问题",
        "没有@AI的消息"
    ]
    
    for message in private_messages:
        result = ai_manager.should_respond_to_message(message, is_group_chat=False)
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        
        print(f"{status} | 私聊消息应该总是回复")
        print(f"     消息: '{message}'")
        print(f"     结果: {'会回复' if result else '不会回复'}")
        print()
    
    print("\n📊 测试总结:")
    print("-" * 30)
    if all_passed:
        print("🎉 所有测试通过！AI触发逻辑修复成功！")
        print("\n✨ 修复效果:")
        print("• 群聊中只有包含@AI（大小写不敏感）的消息才会触发AI回复")
        print("• 不再对包含AI关键词的消息自动回复")
        print("• 不再对以问号结尾的消息自动回复")
        print("• 私聊中仍然对所有消息回复")
        print("• 配置文件中的 require_at_mention: true 生效")
    else:
        print("❌ 部分测试失败，请检查实现")
    
    return all_passed


def demo_config_flexibility():
    """演示配置灵活性"""
    print("\n\n🔧 配置灵活性演示")
    print("=" * 50)
    
    # 模拟配置对象
    from unittest.mock import Mock
    from server.config.ai_config import AIConfig
    
    # 测试 require_at_mention = False 的情况
    mock_config = Mock(spec=AIConfig)
    mock_config.enabled = True
    mock_config.require_at_mention = False  # 使用原有的多种触发条件
    mock_config.trigger_keywords = ["ai", "人工智能", "助手"]
    mock_config.api_key = "test_key"
    mock_config.max_context_length = 10
    mock_config.context_timeout = 3600
    
    with patch('server.ai.ai_manager.ZhipuClient'), \
         patch('server.ai.ai_manager.ContextManager'):
        ai_manager = AIManager(config=mock_config)
    
    print("📋 配置: require_at_mention = False")
    print("🧪 测试结果:")
    
    test_cases = [
        ("你好@AI", True, "@AI触发"),
        ("人工智能很厉害", True, "关键词触发"),
        ("今天天气怎么样？", True, "问号触发"),
        ("普通消息", False, "无触发条件"),
    ]
    
    for message, expected, trigger_type in test_cases:
        result = ai_manager.should_respond_to_message(message, is_group_chat=True)
        status = "✅" if result == expected else "❌"
        print(f"{status} {trigger_type}: '{message}' -> {'会回复' if result else '不会回复'}")
    
    print("\n💡 说明: 当 require_at_mention = False 时，保持原有的多种触发条件")


if __name__ == "__main__":
    # 运行演示
    success = demo_ai_trigger_fix()
    demo_config_flexibility()
    
    print("\n" + "=" * 50)
    if success:
        print("🎯 AI触发逻辑修复完成！")
        print("📝 配置文件: config/server_config.yaml")
        print("🔧 关键配置: ai.require_at_mention = true")
    else:
        print("⚠️  演示过程中发现问题，请检查实现")
