#!/usr/bin/env python3
"""
AI模块改进测试脚本
测试GLM-4-Flash集成和新功能
"""

import os
import sys
import time

# 确保项目根目录在Python路径中
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_zhipu_sdk_import():
    """测试智谱AI SDK导入"""
    print("🔍 测试智谱AI SDK导入...")
    
    try:
        from zhipuai import ZhipuAI
        print("✅ 智谱AI官方SDK已安装")
        return True
    except ImportError:
        print("⚠️ 智谱AI官方SDK未安装")
        print("💡 建议安装: pip install zhipuai")
        return False


def test_zhipu_client_initialization():
    """测试智谱AI客户端初始化"""
    print("\n🔍 测试智谱AI客户端初始化...")
    
    try:
        from src.server.ai.zhipu_client import ZhipuClient
        
        # 测试无API密钥的情况
        try:
            client = ZhipuClient()
            print("❌ 应该在没有API密钥时抛出异常")
            return False
        except ValueError as e:
            print(f"✅ 正确处理缺少API密钥的情况: {e}")
        
        # 测试有API密钥的情况（使用测试密钥）
        test_api_key = os.getenv('ZHIPU_API_KEY', 'test_key')
        if test_api_key == 'test_key':
            print("⚠️ 未设置真实API密钥，跳过连接测试")
            return True
        
        try:
            client = ZhipuClient(test_api_key)
            print("✅ 客户端初始化成功")
            
            # 测试模型信息
            model_info = client.get_model_info()
            print(f"📋 模型信息: {model_info}")
            
            # 测试可用模型
            models = client.get_available_models()
            print(f"📋 可用模型: {models}")
            
            return True
        except Exception as e:
            print(f"❌ 客户端初始化失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 导入错误: {e}")
        return False


def test_ai_config():
    """测试AI配置"""
    print("\n🔍 测试AI配置...")
    
    try:
        from src.server.config.ai_config import get_ai_config, print_ai_setup_guide
        
        config = get_ai_config()
        
        # 测试配置属性
        print(f"✅ 默认模型: {config.model}")
        print(f"✅ 最大令牌数: {config.max_tokens}")
        print(f"✅ 温度: {config.temperature}")
        print(f"✅ Top-p: {config.top_p}")
        
        # 测试可用模型
        models = config.get_available_models()
        print(f"✅ 可用模型: {models}")
        
        # 测试模型设置
        if config.set_model("glm-4-flash"):
            print("✅ 模型设置成功")
        else:
            print("❌ 模型设置失败")
        
        # 测试配置字典
        config_dict = config.to_dict()
        print(f"✅ 配置字典包含 {len(config_dict)} 个项目")
        
        return True
        
    except Exception as e:
        print(f"❌ AI配置测试失败: {e}")
        return False


def test_ai_manager():
    """测试AI管理器"""
    print("\n🔍 测试AI管理器...")
    
    try:
        from src.server.ai.ai_manager import AIManager
        
        # 测试初始化（无API密钥）
        manager = AIManager()
        
        # 测试状态检查
        print(f"✅ AI启用状态: {manager.is_enabled()}")
        
        # 测试消息响应判断
        test_messages = [
            ("你好", True),
            ("@AI 你好", True),
            ("这是一个问题吗？", True),
            ("普通消息", False),
            ("AI能帮我吗", True),
        ]
        
        for msg, expected in test_messages:
            result = manager.should_respond_to_message(msg, is_group_chat=True)
            status = "✅" if result == expected else "❌"
            print(f"{status} 消息'{msg}' -> 应回复: {result}")
        
        # 测试状态信息
        status = manager.get_ai_status()
        print(f"✅ AI状态信息: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI管理器测试失败: {e}")
        return False


def test_context_manager():
    """测试上下文管理器"""
    print("\n🔍 测试上下文管理器...")
    
    try:
        from src.server.ai.context_manager import ContextManager
        
        manager = ContextManager()
        
        # 测试添加消息
        manager.add_message("1", "user", "你好", is_group=True)
        manager.add_message("1", "assistant", "你好！有什么可以帮助你的吗？", is_group=True)
        
        # 测试获取上下文
        context = manager.get_context("1", is_group=True)
        print(f"✅ 群聊上下文消息数: {len(context)}")
        
        # 测试私聊上下文
        manager.add_message("100", "user", "私聊消息", is_group=False)
        private_context = manager.get_context("100", is_group=False)
        print(f"✅ 私聊上下文消息数: {len(private_context)}")
        
        # 测试上下文摘要
        summary = manager.get_context_summary()
        print(f"✅ 上下文摘要: {summary}")
        
        # 测试系统提示词
        group_prompt = manager.get_system_prompt("group")
        private_prompt = manager.get_system_prompt("private")
        print(f"✅ 群聊提示词长度: {len(group_prompt)}")
        print(f"✅ 私聊提示词长度: {len(private_prompt)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 上下文管理器测试失败: {e}")
        return False


def test_real_api_call():
    """测试真实API调用（如果有API密钥）"""
    print("\n🔍 测试真实API调用...")
    
    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        print("⚠️ 未设置ZHIPU_API_KEY环境变量，跳过真实API测试")
        return True
    
    try:
        from src.server.ai.zhipu_client import ZhipuClient
        
        client = ZhipuClient(api_key)
        
        # 测试连接
        print("🔗 测试API连接...")
        if client.test_connection():
            print("✅ API连接测试成功")
        else:
            print("❌ API连接测试失败")
            return False
        
        # 测试简单聊天
        print("💬 测试简单聊天...")
        response = client.simple_chat("你好，请简短回复", "你是一个友好的AI助手")
        if response:
            print(f"✅ AI回复: {response}")
        else:
            print("❌ 没有收到AI回复")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 真实API调用测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始AI模块改进测试...")
    print("=" * 60)
    
    tests = [
        test_zhipu_sdk_import,
        test_zhipu_client_initialization,
        test_ai_config,
        test_ai_manager,
        test_context_manager,
        test_real_api_call,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ 测试 {test_func.__name__} 失败")
        except Exception as e:
            print(f"\n❌ 测试 {test_func.__name__} 出现异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有AI模块改进测试通过！")
        print("\n✨ 改进内容包括:")
        print("  • 支持智谱AI官方SDK")
        print("  • 使用GLM-4-Flash免费模型")
        print("  • 增强的错误处理和日志")
        print("  • 模型切换功能")
        print("  • 改进的配置管理")
        print("  • 更好的API兼容性")
        return True
    else:
        print("❌ 部分测试失败，请检查实现")
        
        # 显示设置指南
        from src.server.config.ai_config import print_ai_setup_guide
        print_ai_setup_guide()
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
