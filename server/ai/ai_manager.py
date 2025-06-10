"""
AI管理器
统一管理AI功能，包括消息处理、上下文管理等
"""

import re
import time
import threading
from typing import Optional, Dict, Any, List
from .zhipu_client import ZhipuClient, AIMessage
from .context_manager import ContextManager
from shared.constants import AI_USERNAME, AI_USER_ID


class AIManager:
    """AI管理器"""
    
    def __init__(self, api_key: str = None):
        """
        初始化AI管理器
        
        Args:
            api_key: 智谱AI API密钥
        """
        self.zhipu_client = None
        self.context_manager = ContextManager()
        self.enabled = False
        
        # 尝试初始化智谱客户端
        try:
            self.zhipu_client = ZhipuClient(api_key)
            if self.zhipu_client.test_connection():
                self.enabled = True
                print("✅ AI功能已启用")
            else:
                print("❌ AI连接测试失败，AI功能已禁用")
        except Exception as e:
            print(f"❌ AI初始化失败: {e}")
            print("💡 请设置环境变量 ZHIPU_API_KEY 或在配置中提供API密钥")
        
        # 启动定期清理任务
        if self.enabled:
            self._start_cleanup_task()
    
    def is_enabled(self) -> bool:
        """检查AI功能是否启用"""
        return self.enabled and self.zhipu_client is not None
    
    def should_respond_to_message(self, message_content: str, 
                                 is_group_chat: bool = True) -> bool:
        """
        判断是否应该回复消息
        
        Args:
            message_content: 消息内容
            is_group_chat: 是否为群聊
            
        Returns:
            是否应该回复
        """
        if not self.is_enabled():
            return False
        
        # 私聊中总是回复
        if not is_group_chat:
            return True
        
        # 群聊中检查是否@AI或包含AI关键词
        message_lower = message_content.lower()
        
        # 检查@AI
        if f"@{AI_USERNAME.lower()}" in message_lower or "@ai" in message_lower:
            return True
        
        # 检查AI相关关键词
        ai_keywords = ["ai", "人工智能", "助手", "机器人", "智能", "问答"]
        for keyword in ai_keywords:
            if keyword in message_lower:
                return True
        
        # 检查问号结尾的问题
        if message_content.strip().endswith("?") or message_content.strip().endswith("？"):
            return True
        
        return False
    
    def process_message(self, user_id: int, username: str, message_content: str,
                       chat_group_id: int = None) -> Optional[str]:
        """
        处理用户消息并生成AI回复
        
        Args:
            user_id: 用户ID
            username: 用户名
            message_content: 消息内容
            chat_group_id: 聊天组ID，None表示私聊
            
        Returns:
            AI回复内容，None表示不回复
        """
        if not self.is_enabled():
            return None
        
        is_group_chat = chat_group_id is not None
        
        # 判断是否应该回复
        if not self.should_respond_to_message(message_content, is_group_chat):
            return None
        
        try:
            # 清理消息内容（移除@AI标记）
            cleaned_message = self._clean_message(message_content)
            
            # 获取上下文ID
            context_id = str(chat_group_id) if is_group_chat else str(user_id)
            
            # 添加用户消息到上下文
            self.context_manager.add_message(
                context_id, "user", f"{username}: {cleaned_message}", is_group_chat
            )
            
            # 获取对话上下文
            context_messages = self.context_manager.get_context(context_id, is_group_chat)
            
            # 获取系统提示词
            context_type = "group" if is_group_chat else "private"
            system_prompt = self.context_manager.get_system_prompt(context_type)
            
            # 调用AI生成回复
            ai_reply = self.zhipu_client.chat_completion(context_messages, system_prompt)
            
            if ai_reply:
                # 添加AI回复到上下文
                self.context_manager.add_message(
                    context_id, "assistant", ai_reply, is_group_chat
                )
                
                return ai_reply
            
        except Exception as e:
            print(f"AI消息处理错误: {e}")
            return "抱歉，我现在无法回复，请稍后再试。"
        
        return None
    
    def _clean_message(self, message: str) -> str:
        """
        清理消息内容，移除@AI标记等
        
        Args:
            message: 原始消息
            
        Returns:
            清理后的消息
        """
        # 移除@AI标记
        cleaned = re.sub(r'@(ai|AI|助手|智能助手)', '', message, flags=re.IGNORECASE)
        
        # 移除多余的空格
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def clear_context(self, context_id: str, is_group: bool = True):
        """
        清除指定的对话上下文
        
        Args:
            context_id: 上下文ID
            is_group: 是否为群聊上下文
        """
        self.context_manager.clear_context(context_id, is_group)
    
    def get_ai_status(self) -> Dict[str, Any]:
        """
        获取AI状态信息
        
        Returns:
            AI状态字典
        """
        status = {
            "enabled": self.enabled,
            "api_connected": False,
            "model_info": {},
            "context_summary": {}
        }
        
        if self.zhipu_client:
            status["api_connected"] = self.zhipu_client.test_connection()
            status["model_info"] = self.zhipu_client.get_model_info()
        
        if self.context_manager:
            status["context_summary"] = self.context_manager.get_context_summary()
        
        return status
    
    def _start_cleanup_task(self):
        """启动定期清理任务"""
        def cleanup_worker():
            while self.enabled:
                try:
                    time.sleep(3600)  # 每小时清理一次
                    self.context_manager.cleanup_expired_contexts()
                except Exception as e:
                    print(f"AI上下文清理错误: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def handle_ai_command(self, command: str, user_id: int, 
                         chat_group_id: int = None) -> str:
        """
        处理AI相关命令
        
        Args:
            command: 命令内容
            user_id: 用户ID
            chat_group_id: 聊天组ID
            
        Returns:
            命令执行结果
        """
        if not self.is_enabled():
            return "❌ AI功能未启用"
        
        command_lower = command.lower().strip()
        
        if command_lower == "status":
            # 显示AI状态
            status = self.get_ai_status()
            return f"""AI状态信息:
• 功能状态: {'启用' if status['enabled'] else '禁用'}
• API连接: {'正常' if status['api_connected'] else '异常'}
• 模型: {status['model_info'].get('model', 'N/A')}
• 活跃群聊上下文: {status['context_summary'].get('active_group_contexts', 0)}
• 活跃私聊上下文: {status['context_summary'].get('active_private_contexts', 0)}"""
        
        elif command_lower == "clear":
            # 清除当前上下文
            is_group = chat_group_id is not None
            context_id = str(chat_group_id) if is_group else str(user_id)
            self.clear_context(context_id, is_group)
            return "✅ AI对话上下文已清除"
        
        elif command_lower == "help":
            # 显示AI帮助
            return """AI助手使用说明:
• 在群聊中@AI或使用AI关键词来呼叫助手
• 在私聊中直接发送消息即可与AI对话
• 使用 /ai status 查看AI状态
• 使用 /ai clear 清除对话上下文
• 使用 /ai help 显示此帮助信息"""
        
        else:
            return f"❌ 未知的AI命令: {command}\n使用 /ai help 查看可用命令"
