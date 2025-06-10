"""
AI对话上下文管理器
管理AI对话的上下文和历史记录
"""

import time
from typing import Dict, List, Optional
from collections import defaultdict, deque
from server.ai.zhipu_client import AIMessage


class ContextManager:
    """AI对话上下文管理器"""
    
    def __init__(self, max_context_length: int = 10, context_timeout: int = 3600):
        """
        初始化上下文管理器
        
        Args:
            max_context_length: 每个对话的最大上下文长度
            context_timeout: 上下文超时时间（秒）
        """
        self.max_context_length = max_context_length
        self.context_timeout = context_timeout
        
        # 存储每个聊天组的对话上下文
        # 格式: {chat_group_id: deque([AIMessage, ...])}
        self.group_contexts: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=self.max_context_length)
        )
        
        # 存储每个用户的私聊上下文
        # 格式: {user_id: deque([AIMessage, ...])}
        self.private_contexts: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=self.max_context_length)
        )
        
        # 记录最后活动时间
        self.last_activity: Dict[str, float] = {}
    
    def add_message(self, context_id: str, role: str, content: str, 
                   is_group: bool = True):
        """
        添加消息到上下文
        
        Args:
            context_id: 上下文ID（聊天组ID或用户ID）
            role: 消息角色（user/assistant）
            content: 消息内容
            is_group: 是否为群聊上下文
        """
        message = AIMessage(
            role=role,
            content=content,
            timestamp=time.time()
        )
        
        if is_group:
            context_key = f"group_{context_id}"
            self.group_contexts[int(context_id)].append(message)
        else:
            context_key = f"private_{context_id}"
            self.private_contexts[int(context_id)].append(message)
        
        # 更新活动时间
        self.last_activity[context_key] = time.time()
    
    def get_context(self, context_id: str, is_group: bool = True) -> List[AIMessage]:
        """
        获取对话上下文
        
        Args:
            context_id: 上下文ID
            is_group: 是否为群聊上下文
            
        Returns:
            对话上下文消息列表
        """
        if is_group:
            context = self.group_contexts.get(int(context_id), deque())
        else:
            context = self.private_contexts.get(int(context_id), deque())
        
        # 过滤过期消息
        current_time = time.time()
        valid_messages = [
            msg for msg in context 
            if msg.timestamp and (current_time - msg.timestamp) < self.context_timeout
        ]
        
        return valid_messages
    
    def clear_context(self, context_id: str, is_group: bool = True):
        """
        清除对话上下文
        
        Args:
            context_id: 上下文ID
            is_group: 是否为群聊上下文
        """
        if is_group:
            if int(context_id) in self.group_contexts:
                self.group_contexts[int(context_id)].clear()
            context_key = f"group_{context_id}"
        else:
            if int(context_id) in self.private_contexts:
                self.private_contexts[int(context_id)].clear()
            context_key = f"private_{context_id}"
        
        # 清除活动时间记录
        if context_key in self.last_activity:
            del self.last_activity[context_key]
    
    def cleanup_expired_contexts(self):
        """清理过期的上下文"""
        current_time = time.time()
        expired_keys = []
        
        # 查找过期的上下文
        for context_key, last_time in self.last_activity.items():
            if current_time - last_time > self.context_timeout:
                expired_keys.append(context_key)
        
        # 清理过期上下文
        for key in expired_keys:
            if key.startswith("group_"):
                group_id = int(key.split("_")[1])
                if group_id in self.group_contexts:
                    self.group_contexts[group_id].clear()
            elif key.startswith("private_"):
                user_id = int(key.split("_")[1])
                if user_id in self.private_contexts:
                    self.private_contexts[user_id].clear()
            
            del self.last_activity[key]
    
    def get_context_summary(self) -> Dict[str, int]:
        """
        获取上下文摘要信息
        
        Returns:
            包含各种统计信息的字典
        """
        return {
            "active_group_contexts": len([
                k for k in self.last_activity.keys() 
                if k.startswith("group_")
            ]),
            "active_private_contexts": len([
                k for k in self.last_activity.keys() 
                if k.startswith("private_")
            ]),
            "total_group_messages": sum(
                len(context) for context in self.group_contexts.values()
            ),
            "total_private_messages": sum(
                len(context) for context in self.private_contexts.values()
            )
        }
    
    def get_system_prompt(self, context_type: str = "group") -> str:
        """
        获取系统提示词
        
        Args:
            context_type: 上下文类型（group/private）
            
        Returns:
            系统提示词
        """
        if context_type == "group":
            return """你是Chat-Room聊天室的AI助手。你的职责是：
1. 友好地回答用户的问题
2. 参与群聊讨论，提供有用的信息
3. 保持对话的连贯性和上下文理解
4. 使用简洁、自然的中文回复
5. 避免重复或冗长的回答

请根据聊天上下文，给出恰当的回复。"""
        else:
            return """你是Chat-Room聊天室的AI助手。你正在与用户进行私聊对话。请：
1. 提供个性化的帮助和建议
2. 保持友好和专业的态度
3. 根据对话历史提供连贯的回复
4. 使用自然、亲切的中文交流
5. 尊重用户隐私，不记录敏感信息

请根据对话上下文，给出有帮助的回复。"""
