"""
服务器端配置管理
统一管理服务器的所有配置项
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.config_manager import ConfigManager


class ServerConfig:
    """服务器配置管理类"""
    
    def __init__(self, config_file: str = "config/server_config.yaml"):
        """
        初始化服务器配置
        
        Args:
            config_file: 配置文件路径（相对于项目根目录）
        """
        # 配置文件路径（相对于项目根目录）
        self.config_file = project_root / config_file
        
        # 默认配置
        self.default_config = self._get_default_config()
        
        # 配置验证模式
        self.config_schema = self._get_config_schema()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager(
            str(self.config_file),
            self.default_config,
            self.config_schema
        )
        
        # 加载配置
        self.config = self.config_manager.config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # 服务器网络配置
            "server": {
                "host": "localhost",
                "port": 8888,
                "max_connections": 100,
                "buffer_size": 4096,
                "heartbeat_interval": 30,
                "connection_timeout": 300
            },
            
            # 数据库配置
            "database": {
                "path": "server/data/chatroom.db",
                "backup_enabled": True,
                "backup_interval": 3600,
                "backup_count": 5,
                "auto_vacuum": True
            },
            
            # 文件存储配置
            "file_storage": {
                "path": "server/data/files",
                "max_file_size": 104857600,  # 100MB
                "allowed_extensions": [
                    ".txt", ".doc", ".docx", ".pdf", ".jpg", ".jpeg", ".png", ".gif",
                    ".mp3", ".mp4", ".avi", ".zip", ".rar", ".py", ".js", ".html", ".css"
                ],
                "chunk_size": 8192,
                "auto_cleanup": True,
                "cleanup_interval": 86400  # 24小时
            },
            
            # AI配置
            "ai": {
                "enabled": True,
                "api_key": "",  # 智谱AI API密钥
                "model": "glm-4-flash",
                "max_tokens": 1024,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_context_length": 10,
                "context_timeout": 3600,
                "enable_group_chat": True,
                "enable_private_chat": True,
                "auto_reply": True,
                "trigger_keywords": ["ai", "人工智能", "助手", "机器人", "智能", "问答"],
                "require_at_mention": False,
                "available_models": [
                    "glm-4-flash", "glm-4", "glm-4-plus", 
                    "glm-4-air", "glm-4-airx", "glm-4-long"
                ]
            },
            
            # 日志配置
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file_enabled": True,
                "file_path": "logs/server/server.log",
                "file_max_size": 10485760,  # 10MB
                "file_backup_count": 5,
                "console_enabled": True,
                # 详细日志配置
                "categories": {
                    "database": {
                        "enabled": True,
                        "level": "DEBUG",
                        "file_path": "logs/server/database.log"
                    },
                    "ai": {
                        "enabled": True,
                        "level": "INFO",
                        "file_path": "logs/server/ai.log"
                    },
                    "security": {
                        "enabled": True,
                        "level": "WARNING",
                        "file_path": "logs/server/security.log"
                    },
                    "performance": {
                        "enabled": True,
                        "level": "INFO",
                        "file_path": "logs/server/performance.log"
                    },
                    "network": {
                        "enabled": True,
                        "level": "INFO",
                        "file_path": "logs/server/network.log"
                    }
                },
                # 日志保留策略
                "retention": {
                    "days": 30,
                    "max_size_gb": 1.0
                },
                # 敏感信息脱敏
                "sanitization": {
                    "enabled": True,
                    "patterns": ["password", "api_key", "token", "secret", "auth"]
                }
            },
            
            # 安全配置
            "security": {
                "password_min_length": 6,
                "password_hash_rounds": 12,
                "session_timeout": 86400,  # 24小时
                "max_login_attempts": 5,
                "login_cooldown": 300,  # 5分钟
                "enable_rate_limiting": True,
                "rate_limit_requests": 100,
                "rate_limit_window": 60
            },
            
            # 聊天配置
            "chat": {
                "default_public_chat": "public",
                "max_message_length": 2048,
                "message_history_limit": 1000,
                "auto_create_public_chat": True,
                "allow_private_chat": True,
                "max_chat_members": 100
            },
            
            # 性能配置
            "performance": {
                "enable_compression": True,
                "compression_level": 6,
                "enable_caching": True,
                "cache_size": 1000,
                "cache_ttl": 300,
                "worker_threads": 4
            }
        }
    
    def _get_config_schema(self) -> Dict[str, Any]:
        """获取配置验证模式"""
        return {
            "type": "object",
            "properties": {
                "server": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                        "max_connections": {"type": "integer", "minimum": 1},
                        "buffer_size": {"type": "integer", "minimum": 1024}
                    },
                    "required": ["host", "port"]
                },
                "ai": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "api_key": {"type": "string"},
                        "model": {"type": "string"},
                        "max_tokens": {"type": "integer", "minimum": 1},
                        "temperature": {"type": "number", "minimum": 0, "maximum": 2}
                    }
                }
            },
            "required": ["server", "database", "ai", "logging"]
        }
    
    # 便捷访问方法
    def get_server_host(self) -> str:
        """获取服务器主机地址"""
        return self.config_manager.get("server.host", "localhost")
    
    def get_server_port(self) -> int:
        """获取服务器端口"""
        return self.config_manager.get("server.port", 8888)
    
    def get_max_connections(self) -> int:
        """获取最大连接数"""
        return self.config_manager.get("server.max_connections", 100)
    
    def get_database_path(self) -> str:
        """获取数据库路径"""
        return self.config_manager.get("database.path", "server/data/chatroom.db")
    
    def get_files_storage_path(self) -> str:
        """获取文件存储路径"""
        return self.config_manager.get("file_storage.path", "server/data/files")
    
    def get_max_file_size(self) -> int:
        """获取最大文件大小"""
        return self.config_manager.get("file_storage.max_file_size", 104857600)
    
    def get_allowed_file_extensions(self) -> list:
        """获取允许的文件扩展名"""
        return self.config_manager.get("file_storage.allowed_extensions", [])
    
    def is_ai_enabled(self) -> bool:
        """检查AI功能是否启用"""
        return (self.config_manager.get("ai.enabled", False) and 
                bool(self.config_manager.get("ai.api_key", "")))
    
    def get_ai_api_key(self) -> str:
        """获取AI API密钥"""
        return self.config_manager.get("ai.api_key", "")
    
    def set_ai_api_key(self, api_key: str) -> bool:
        """设置AI API密钥"""
        success = self.config_manager.set("ai.api_key", api_key)
        if success:
            self.config_manager.save_config()
        return success
    
    def get_ai_model(self) -> str:
        """获取AI模型"""
        return self.config_manager.get("ai.model", "glm-4-flash")
    
    def set_ai_model(self, model: str) -> bool:
        """设置AI模型"""
        available_models = self.config_manager.get("ai.available_models", [])
        if model in available_models:
            success = self.config_manager.set("ai.model", model)
            if success:
                self.config_manager.save_config()
            return success
        return False
    
    def get_ai_config(self) -> Dict[str, Any]:
        """获取完整的AI配置"""
        return self.config_manager.get("ai", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config_manager.get("logging", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.config_manager.get("security", {})
    
    def save_config(self) -> bool:
        """保存配置"""
        return self.config_manager.save_config()
    
    def reload_config(self) -> bool:
        """重新加载配置"""
        try:
            self.config = self.config_manager.load_config()
            return True
        except Exception as e:
            print(f"❌ 重新加载配置失败: {e}")
            return False
    
    def export_template(self, template_file: str = "config/server_config.template.yaml") -> bool:
        """导出配置模板"""
        template_path = project_root / template_file
        return self.config_manager.export_template(str(template_path))
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        info = self.config_manager.get_config_info()
        info.update({
            "ai_enabled": self.is_ai_enabled(),
            "ai_api_key_set": bool(self.get_ai_api_key()),
            "ai_model": self.get_ai_model(),
            "server_address": f"{self.get_server_host()}:{self.get_server_port()}"
        })
        return info


# 全局服务器配置实例
_server_config = None


def get_server_config() -> ServerConfig:
    """获取服务器配置实例（单例模式）"""
    global _server_config
    if _server_config is None:
        _server_config = ServerConfig()
    return _server_config


def reload_server_config() -> bool:
    """重新加载服务器配置"""
    global _server_config
    if _server_config is not None:
        return _server_config.reload_config()
    return False
