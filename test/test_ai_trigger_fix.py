#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI触发逻辑修复测试
测试AI回复只在@AI时触发的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, patch
from server.ai.ai_manager import AIManager
from server.config.ai_config import AIConfig


class TestAITriggerFix:
    """AI触发逻辑修复测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 创建模拟的配置对象
        self.mock_config = Mock(spec=AIConfig)
        self.mock_config.enabled = True
        self.mock_config.require_at_mention = True  # 关键：要求@AI才回复
        self.mock_config.trigger_keywords = ["ai", "人工智能", "助手", "机器人", "智能", "问答"]
        self.mock_config.api_key = "test_api_key"
        self.mock_config.max_context_length = 10
        self.mock_config.context_timeout = 3600

        # 创建AI管理器实例
        with patch('server.ai.ai_manager.ZhipuClient'), \
             patch('server.ai.ai_manager.ContextManager'):
            self.ai_manager = AIManager(config=self.mock_config)
    
    def test_should_respond_with_at_ai_lowercase(self):
        """测试小写@ai应该触发回复"""
        message = "你好@ai，请帮我解答一个问题"
        result = self.ai_manager.should_respond_to_message(message, is_group_chat=True)
        assert result is True, "包含@ai的消息应该触发AI回复"
    
    def test_should_respond_with_at_ai_uppercase(self):
        """测试大写@AI应该触发回复"""
        message = "你好@AI，请帮我解答一个问题"
        result = self.ai_manager.should_respond_to_message(message, is_group_chat=True)
        assert result is True, "包含@AI的消息应该触发AI回复"
    
    def test_should_respond_with_at_ai_mixed_case(self):
        """测试混合大小写@Ai应该触发回复"""
        message = "你好@Ai，请帮我解答一个问题"
        result = self.ai_manager.should_respond_to_message(message, is_group_chat=True)
        assert result is True, "包含@Ai的消息应该触发AI回复"
    
    def test_should_not_respond_without_at_ai(self):
        """测试不包含@AI的普通消息不应该触发回复"""
        test_messages = [
            "这是一个普通的消息",
            "我有一个问题？",  # 以问号结尾
            "人工智能很厉害",  # 包含AI关键词
            "智能助手很有用",  # 包含多个AI关键词
            "ai技术发展很快",  # 包含ai关键词
            "机器人很有趣",    # 包含机器人关键词
        ]
        
        for message in test_messages:
            result = self.ai_manager.should_respond_to_message(message, is_group_chat=True)
            assert result is False, f"消息'{message}'不应该触发AI回复"
    
    def test_should_respond_in_private_chat(self):
        """测试私聊中应该总是回复（不受@AI限制）"""
        message = "这是一个私聊消息"
        result = self.ai_manager.should_respond_to_message(message, is_group_chat=False)
        assert result is True, "私聊消息应该总是触发AI回复"
    
    def test_should_not_respond_when_disabled(self):
        """测试AI禁用时不应该回复"""
        self.mock_config.enabled = False
        message = "你好@AI"
        result = self.ai_manager.should_respond_to_message(message, is_group_chat=True)
        assert result is False, "AI禁用时不应该回复任何消息"
    
    def test_fallback_to_old_logic_when_require_at_mention_false(self):
        """测试当require_at_mention为False时，应该使用原有的多种触发条件"""
        self.mock_config.require_at_mention = False
        
        # 测试关键词触发
        message = "人工智能很厉害"
        result = self.ai_manager.should_respond_to_message(message, is_group_chat=True)
        assert result is True, "require_at_mention为False时，关键词应该触发回复"
        
        # 测试问号触发
        message = "今天天气怎么样？"
        result = self.ai_manager.should_respond_to_message(message, is_group_chat=True)
        assert result is True, "require_at_mention为False时，问号应该触发回复"


def test_integration_with_real_config():
    """集成测试：使用真实配置文件测试"""
    try:
        from server.config.ai_config import get_ai_config

        # 加载真实配置
        ai_config = get_ai_config()

        # 验证配置已正确设置
        assert ai_config.require_at_mention is True, "配置文件中require_at_mention应该为True"

        # 创建AI管理器（使用模拟的依赖）
        with patch('server.ai.ai_manager.ZhipuClient'), \
             patch('server.ai.ai_manager.ContextManager'):
            ai_manager = AIManager(config=ai_config)

        # 测试只有@AI才触发
        assert ai_manager.should_respond_to_message("你好@AI", True) is True
        assert ai_manager.should_respond_to_message("普通消息", True) is False
        assert ai_manager.should_respond_to_message("智能助手很好", True) is False

        print("✅ 集成测试通过：AI触发逻辑修复成功")

    except ImportError as e:
        print(f"⚠️  集成测试跳过：无法导入配置模块 - {e}")


if __name__ == "__main__":
    # 运行单元测试
    pytest.main([__file__, "-v"])
    
    # 运行集成测试
    test_integration_with_real_config()
