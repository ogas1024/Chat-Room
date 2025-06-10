#!/usr/bin/env python3
"""
AI功能演示脚本
展示改进后的智谱AI集成功能
"""

import os
import sys
import time

# 确保项目根目录在Python路径中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def demo_ai_setup_guide():
    """演示AI设置指南"""
    print("🤖 智谱AI功能演示")
    print("=" * 60)
    
    from server.config.ai_config import print_ai_setup_guide
    print_ai_setup_guide()


def demo_ai_config():
    """演示AI配置功能"""
    print("\n📋 AI配置演示")
    print("-" * 40)
    
    from server.config.ai_config import get_ai_config
    
    config = get_ai_config()
    
    print(f"当前模型: {config.model}")
    print(f"API密钥已设置: {config.is_enabled()}")
    print(f"可用模型: {', '.join(config.get_available_models())}")
    
    # 演示模型切换
    print("\n🔄 模型切换演示:")
    models_to_test = ["glm-4-flash", "glm-4", "glm-4-plus"]
    
    for model in models_to_test:
        if config.set_model(model):
            print(f"✅ 成功切换到: {model}")
        else:
            print(f"❌ 切换失败: {model}")
    
    # 恢复默认模型
    config.set_model("glm-4-flash")
    print(f"🔄 恢复默认模型: {config.model}")


def demo_zhipu_client():
    """演示智谱AI客户端功能"""
    print("\n🔌 智谱AI客户端演示")
    print("-" * 40)
    
    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        print("⚠️ 未设置ZHIPU_API_KEY环境变量")
        print("💡 请设置API密钥以体验完整功能")
        return
    
    try:
        from server.ai.zhipu_client import ZhipuClient
        
        client = ZhipuClient(api_key)
        
        # 显示客户端信息
        model_info = client.get_model_info()
        print(f"📋 客户端信息:")
        for key, value in model_info.items():
            print(f"   {key}: {value}")
        
        # 测试连接
        print("\n🔗 测试API连接...")
        if client.test_connection():
            print("✅ API连接成功")
            
            # 演示简单对话
            print("\n💬 简单对话演示:")
            test_messages = [
                "你好，请简短介绍一下自己",
                "你能做什么？",
                "请用一句话总结人工智能的作用"
            ]
            
            for i, message in enumerate(test_messages, 1):
                print(f"\n用户 {i}: {message}")
                response = client.simple_chat(message, "你是一个友好的AI助手，请简洁回复。")
                if response:
                    print(f"AI: {response}")
                else:
                    print("AI: [无回复]")
                time.sleep(1)  # 避免请求过快
        else:
            print("❌ API连接失败")
            
    except Exception as e:
        print(f"❌ 客户端演示失败: {e}")


def demo_ai_manager():
    """演示AI管理器功能"""
    print("\n🧠 AI管理器演示")
    print("-" * 40)
    
    api_key = os.getenv('ZHIPU_API_KEY')
    
    try:
        from server.ai.ai_manager import AIManager
        
        manager = AIManager(api_key)
        
        # 显示AI状态
        status = manager.get_ai_status()
        print(f"📊 AI状态:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        if not manager.is_enabled():
            print("⚠️ AI功能未启用，跳过对话演示")
            return
        
        # 演示消息响应判断
        print("\n🎯 消息响应判断演示:")
        test_messages = [
            ("你好", "群聊"),
            ("@AI 你好", "群聊"),
            ("这是一个问题吗？", "群聊"),
            ("普通消息", "群聊"),
            ("AI能帮我吗", "群聊"),
            ("私聊消息", "私聊"),
        ]
        
        for message, chat_type in test_messages:
            is_group = chat_type == "群聊"
            should_respond = manager.should_respond_to_message(message, is_group)
            status = "会回复" if should_respond else "不回复"
            print(f"   {chat_type} '{message}' -> {status}")
        
        # 演示AI对话处理
        print("\n💬 AI对话处理演示:")
        test_conversations = [
            (1, "Alice", "你好，AI助手！", 1),  # 群聊
            (2, "Bob", "你能帮我解释一下Python吗？", None),  # 私聊
        ]
        
        for user_id, username, message, chat_group_id in test_conversations:
            chat_type = "群聊" if chat_group_id else "私聊"
            print(f"\n{chat_type} - {username}: {message}")
            
            response = manager.process_message(user_id, username, message, chat_group_id)
            if response:
                print(f"AI: {response}")
            else:
                print("AI: [不回复]")
            
            time.sleep(1)  # 避免请求过快
            
    except Exception as e:
        print(f"❌ AI管理器演示失败: {e}")


def demo_context_management():
    """演示上下文管理功能"""
    print("\n📚 上下文管理演示")
    print("-" * 40)
    
    try:
        from server.ai.context_manager import ContextManager
        
        manager = ContextManager()
        
        # 模拟群聊对话
        print("🗣️ 模拟群聊对话:")
        group_id = "1"
        
        conversations = [
            ("user", "Alice: 你好，AI助手！"),
            ("assistant", "你好Alice！很高兴见到你，有什么可以帮助你的吗？"),
            ("user", "Bob: 我想了解Python编程"),
            ("assistant", "Python是一门很棒的编程语言！它简洁易学，应用广泛。"),
            ("user", "Alice: 能推荐一些学习资源吗？"),
        ]
        
        for role, content in conversations:
            manager.add_message(group_id, role, content, is_group=True)
            print(f"   {content}")
        
        # 获取上下文
        context = manager.get_context(group_id, is_group=True)
        print(f"\n📋 群聊上下文包含 {len(context)} 条消息")
        
        # 模拟私聊对话
        print("\n💬 模拟私聊对话:")
        user_id = "100"
        
        private_conversations = [
            ("user", "用户私聊: 这是私密问题"),
            ("assistant", "我理解这是私聊，我会保护您的隐私。"),
        ]
        
        for role, content in private_conversations:
            manager.add_message(user_id, role, content, is_group=False)
            print(f"   {content}")
        
        # 获取私聊上下文
        private_context = manager.get_context(user_id, is_group=False)
        print(f"\n📋 私聊上下文包含 {len(private_context)} 条消息")
        
        # 显示上下文摘要
        summary = manager.get_context_summary()
        print(f"\n📊 上下文摘要:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # 显示系统提示词
        group_prompt = manager.get_system_prompt("group")
        private_prompt = manager.get_system_prompt("private")
        print(f"\n📝 系统提示词:")
        print(f"   群聊提示词: {group_prompt[:50]}...")
        print(f"   私聊提示词: {private_prompt[:50]}...")
        
    except Exception as e:
        print(f"❌ 上下文管理演示失败: {e}")


def demo_model_comparison():
    """演示不同模型的对比"""
    print("\n🔬 模型对比演示")
    print("-" * 40)
    
    api_key = os.getenv('ZHIPU_API_KEY')
    if not api_key:
        print("⚠️ 未设置ZHIPU_API_KEY环境变量，跳过模型对比")
        return
    
    try:
        from server.ai.zhipu_client import ZhipuClient
        
        # 测试不同模型
        models_to_test = ["glm-4-flash", "glm-4"]
        test_question = "请用一句话解释什么是人工智能"
        
        for model in models_to_test:
            print(f"\n🤖 测试模型: {model}")
            
            client = ZhipuClient(api_key)
            if client.set_model(model):
                response = client.simple_chat(test_question, "请简洁回复")
                if response:
                    print(f"回复: {response}")
                else:
                    print("回复: [无回复]")
            else:
                print(f"❌ 模型 {model} 不可用")
            
            time.sleep(2)  # 避免请求过快
            
    except Exception as e:
        print(f"❌ 模型对比演示失败: {e}")


def main():
    """主演示函数"""
    print("🎭 智谱AI功能完整演示")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv('ZHIPU_API_KEY')
    if api_key:
        print(f"✅ 检测到API密钥: {api_key[:8]}...")
        print("🚀 将演示完整功能")
    else:
        print("⚠️ 未检测到API密钥")
        print("🔧 将演示基础功能和配置")
    
    # 运行各个演示
    demos = [
        demo_ai_setup_guide,
        demo_ai_config,
        demo_zhipu_client,
        demo_ai_manager,
        demo_context_management,
        demo_model_comparison,
    ]
    
    for demo_func in demos:
        try:
            demo_func()
        except KeyboardInterrupt:
            print("\n\n👋 演示被用户中断")
            break
        except Exception as e:
            print(f"\n❌ 演示 {demo_func.__name__} 出现错误: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 AI功能演示完成！")
    print("\n💡 要在聊天室中使用AI功能:")
    print("   1. 设置环境变量: export ZHIPU_API_KEY='your_key'")
    print("   2. 启动服务器: python -m server.main")
    print("   3. 启动客户端: python -m client.main")
    print("   4. 在群聊中@AI或私聊AI用户")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示出现错误: {e}")
