"""
AI配置文件
用于配置智谱AI API相关设置
"""

import os
from typing import Optional


class AIConfig:
    """AI配置类"""
    
    def __init__(self):
        """初始化AI配置"""
        # 从环境变量获取API密钥
        self.api_key = os.getenv('ZHIPU_API_KEY')
        
        # AI模型配置
        self.model = "glm-4"
        self.max_tokens = 1024
        self.temperature = 0.7
        
        # 上下文管理配置
        self.max_context_length = 10
        self.context_timeout = 3600  # 1小时
        
        # 功能开关
        self.enable_group_chat = True  # 是否在群聊中启用AI
        self.enable_private_chat = True  # 是否在私聊中启用AI
        self.auto_reply = True  # 是否自动回复
        
        # 回复触发条件
        self.trigger_keywords = ["ai", "人工智能", "助手", "机器人", "智能", "问答"]
        self.require_at_mention = False  # 群聊中是否需要@AI才回复
        
    def is_enabled(self) -> bool:
        """检查AI功能是否可用"""
        return bool(self.api_key)
    
    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        return self.api_key
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key
        # 同时设置环境变量
        os.environ['ZHIPU_API_KEY'] = api_key
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "api_key_set": bool(self.api_key),
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "max_context_length": self.max_context_length,
            "context_timeout": self.context_timeout,
            "enable_group_chat": self.enable_group_chat,
            "enable_private_chat": self.enable_private_chat,
            "auto_reply": self.auto_reply,
            "trigger_keywords": self.trigger_keywords,
            "require_at_mention": self.require_at_mention
        }


# 全局配置实例
ai_config = AIConfig()


def get_ai_config() -> AIConfig:
    """获取AI配置实例"""
    return ai_config


def setup_ai_from_env():
    """从环境变量设置AI配置"""
    config = get_ai_config()
    
    # 检查环境变量
    if not config.api_key:
        print("⚠️  未设置智谱AI API密钥")
        print("💡 请设置环境变量 ZHIPU_API_KEY 来启用AI功能")
        print("   例如: export ZHIPU_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ 智谱AI配置已加载，模型: {config.model}")
    return True


def print_ai_setup_guide():
    """打印AI设置指南"""
    print("""
🤖 AI功能设置指南:

1. 获取智谱AI API密钥:
   - 访问 https://open.bigmodel.cn/
   - 注册账号并获取API密钥

2. 设置环境变量:
   - Linux/Mac: export ZHIPU_API_KEY='your-api-key-here'
   - Windows: set ZHIPU_API_KEY=your-api-key-here

3. 重启服务器以应用配置

4. 使用AI功能:
   - 群聊中@AI或使用AI关键词
   - 私聊中直接发送消息
   - 使用 /ai status 查看AI状态
   - 使用 /ai help 获取帮助
""")


if __name__ == "__main__":
    # 测试配置
    config = get_ai_config()
    print("AI配置信息:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
    
    if not config.is_enabled():
        print_ai_setup_guide()
