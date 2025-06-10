"""
智谱AI API客户端
负责与智谱AI API进行通信
"""

import os
import json
import requests
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class AIMessage:
    """AI消息数据类"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[float] = None


class ZhipuClient:
    """智谱AI API客户端"""
    
    def __init__(self, api_key: str = None):
        """
        初始化智谱AI客户端
        
        Args:
            api_key: 智谱AI API密钥，如果为None则从环境变量获取
        """
        self.api_key = api_key or os.getenv('ZHIPU_API_KEY')
        if not self.api_key:
            raise ValueError("智谱AI API密钥未设置，请设置环境变量 ZHIPU_API_KEY 或传入api_key参数")
        
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
        self.model = "glm-4"  # 默认使用GLM-4模型
        self.max_tokens = 1024
        self.temperature = 0.7
        
        # 请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: List[AIMessage], 
                       system_prompt: str = None) -> Optional[str]:
        """
        调用智谱AI聊天完成API
        
        Args:
            messages: 对话消息列表
            system_prompt: 系统提示词
            
        Returns:
            AI回复内容，失败时返回None
        """
        try:
            # 构建请求消息
            api_messages = []
            
            # 添加系统提示词
            if system_prompt:
                api_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # 添加对话消息
            for msg in messages:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # 构建请求数据
            request_data = {
                "model": self.model,
                "messages": api_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=request_data,
                timeout=30
            )
            
            # 检查响应状态
            if response.status_code != 200:
                print(f"智谱AI API请求失败: {response.status_code} - {response.text}")
                return None
            
            # 解析响应
            response_data = response.json()
            
            if "choices" not in response_data or not response_data["choices"]:
                print("智谱AI API响应格式错误")
                return None
            
            # 提取AI回复
            ai_reply = response_data["choices"][0]["message"]["content"]
            return ai_reply.strip()
            
        except requests.exceptions.RequestException as e:
            print(f"智谱AI API网络请求错误: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"智谱AI API响应解析错误: {e}")
            return None
        except Exception as e:
            print(f"智谱AI API调用错误: {e}")
            return None
    
    def simple_chat(self, user_message: str, system_prompt: str = None) -> Optional[str]:
        """
        简单聊天接口
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            
        Returns:
            AI回复内容
        """
        messages = [AIMessage(role="user", content=user_message)]
        return self.chat_completion(messages, system_prompt)
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        try:
            response = self.simple_chat("你好", "你是一个友好的AI助手")
            return response is not None
        except Exception as e:
            print(f"智谱AI连接测试失败: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "api_key_set": bool(self.api_key)
        }
