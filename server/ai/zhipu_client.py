"""
智谱AI API客户端
负责与智谱AI API进行通信，使用官方SDK
"""

import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from zhipuai import ZhipuAI
    ZHIPU_SDK_AVAILABLE = True
except ImportError:
    ZHIPU_SDK_AVAILABLE = False
    print("⚠️ 智谱AI官方SDK未安装，将使用HTTP API方式")
    print("💡 建议安装官方SDK: pip install zhipuai")

    # 备用HTTP API实现
    import json
    import requests


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
            api_key: 智谱AI API密钥，如果为None则从配置文件获取
        """
        if api_key:
            self.api_key = api_key
        else:
            # 从配置文件获取API密钥
            try:
                from .config.server_config import get_server_config
                server_config = get_server_config()
                self.api_key = server_config.get_ai_api_key()
            except Exception:
                # 备用方案：从环境变量获取
                self.api_key = os.getenv('ZHIPU_API_KEY', '')

        if not self.api_key:
            raise ValueError("智谱AI API密钥未设置，请在配置文件 config/server_config.yaml 中设置 ai.api_key 或传入api_key参数")

        # 模型配置 - 使用GLM-4-Flash免费模型
        self.model = "glm-4-flash"  # 使用免费的GLM-4-Flash模型
        self.max_tokens = 1024
        self.temperature = 0.7
        self.top_p = 0.9

        # 初始化客户端
        if ZHIPU_SDK_AVAILABLE:
            self.client = ZhipuAI(api_key=self.api_key)
            self.use_sdk = True
            print("✅ 使用智谱AI官方SDK")
        else:
            # 备用HTTP API配置
            self.base_url = "https://open.bigmodel.cn/api/paas/v4"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.use_sdk = False
            print("⚠️ 使用HTTP API方式调用智谱AI")
    
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

            if self.use_sdk:
                # 使用官方SDK调用
                return self._chat_completion_sdk(api_messages)
            else:
                # 使用HTTP API调用
                return self._chat_completion_http(api_messages)

        except Exception as e:
            print(f"智谱AI API调用错误: {e}")
            return None

    def _chat_completion_sdk(self, api_messages: List[Dict]) -> Optional[str]:
        """
        使用官方SDK调用聊天完成API

        Args:
            api_messages: API消息列表

        Returns:
            AI回复内容
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                stream=False
            )

            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                print("智谱AI SDK响应格式错误：没有choices")
                return None

        except Exception as e:
            print(f"智谱AI SDK调用错误: {e}")
            return None

    def _chat_completion_http(self, api_messages: List[Dict]) -> Optional[str]:
        """
        使用HTTP API调用聊天完成API

        Args:
            api_messages: API消息列表

        Returns:
            AI回复内容
        """
        try:
            # 构建请求数据
            request_data = {
                "model": self.model,
                "messages": api_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
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
            print(f"智谱AI HTTP API调用错误: {e}")
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
        messages = [AIMessage(role="user", content=user_message, timestamp=time.time())]
        return self.chat_completion(messages, system_prompt)

    def test_connection(self) -> bool:
        """
        测试API连接

        Returns:
            连接是否成功
        """
        try:
            response = self.simple_chat("你好", "你是一个友好的AI助手，请简短回复。")
            return response is not None and len(response.strip()) > 0
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
            "top_p": self.top_p,
            "api_key_set": bool(self.api_key),
            "use_sdk": self.use_sdk,
            "sdk_available": ZHIPU_SDK_AVAILABLE
        }

    def get_available_models(self) -> List[str]:
        """
        获取可用的模型列表

        Returns:
            模型名称列表
        """
        # GLM-4系列模型
        return [
            "glm-4-flash",      # 免费模型，速度快
            "glm-4",            # 标准模型
            "glm-4-plus",       # 增强模型
            "glm-4-air",        # 轻量模型
            "glm-4-airx",       # 轻量增强模型
            "glm-4-long",       # 长文本模型
        ]

    def set_model(self, model_name: str) -> bool:
        """
        设置使用的模型

        Args:
            model_name: 模型名称

        Returns:
            设置是否成功
        """
        available_models = self.get_available_models()
        if model_name in available_models:
            self.model = model_name
            print(f"✅ 已切换到模型: {model_name}")
            return True
        else:
            print(f"❌ 不支持的模型: {model_name}")
            print(f"💡 可用模型: {', '.join(available_models)}")
            return False
