"""
客户端配置管理
统一管理客户端的所有配置项
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.config_manager import ConfigManager


class ClientConfig:
    """客户端配置管理类"""
    
    def __init__(self, config_file: str = "config/client_config.yaml"):
        """
        初始化客户端配置
        
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
            # 连接配置
            "connection": {
                "default_host": "localhost",
                "default_port": 8888,
                "connection_timeout": 10,
                "reconnect_attempts": 3,
                "reconnect_delay": 5,
                "heartbeat_interval": 30,
                "auto_reconnect": True
            },
            
            # 用户界面配置
            "ui": {
                "mode": "tui",  # tui 或 cli
                "theme": "default",
                "language": "zh_CN",
                "show_timestamps": True,
                "timestamp_format": "%H:%M:%S",
                "max_chat_history": 1000,
                "auto_scroll": True,
                "sound_enabled": False,
                "notifications_enabled": True
            },
            
            # TUI界面特定配置
            "tui": {
                "refresh_rate": 10,  # 每秒刷新次数
                "input_history_size": 100,
                "show_user_list": True,
                "show_status_bar": True,
                "chat_area_height": 20,
                "input_area_height": 3,
                "sidebar_width": 20,
                "color_scheme": {
                    "background": "default",
                    "text": "white",
                    "accent": "cyan",
                    "error": "red",
                    "success": "green",
                    "warning": "yellow"
                }
            },
            
            # 用户偏好设置
            "user": {
                "remember_credentials": False,
                "auto_login": False,
                "default_username": "",
                "save_chat_history": True,
                "chat_history_path": "data/chat_history",
                "download_path": "downloads",
                "auto_accept_files": False,
                "max_download_size": 104857600  # 100MB
            },
            
            # 聊天行为配置
            "chat": {
                "auto_join_public": True,
                "show_join_leave_messages": True,
                "show_typing_indicators": True,
                "message_send_key": "Enter",  # Enter 或 Ctrl+Enter
                "enable_emoji": True,
                "enable_markdown": False,
                "max_message_length": 2048,
                "typing_timeout": 3
            },
            
            # 文件传输配置
            "file_transfer": {
                "auto_create_download_dir": True,
                "show_transfer_progress": True,
                "parallel_downloads": 3,
                "chunk_size": 8192,
                "resume_downloads": True,
                "verify_checksums": True
            },
            
            # 命令配置
            "commands": {
                "enable_autocomplete": True,
                "show_command_help": True,
                "command_history_size": 50,
                "case_sensitive": False,
                "custom_aliases": {}
            },
            
            # 日志配置
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "file_path": "logs/client.log",
                "file_max_size": 5242880,  # 5MB
                "file_backup_count": 3,
                "console_enabled": False  # TUI模式下禁用控制台日志
            },
            
            # 性能配置
            "performance": {
                "buffer_size": 4096,
                "message_queue_size": 1000,
                "ui_update_interval": 100,  # 毫秒
                "enable_compression": True,
                "lazy_loading": True
            },
            
            # 调试配置
            "debug": {
                "enabled": False,
                "show_raw_messages": False,
                "log_network_traffic": False,
                "performance_monitoring": False
            }
        }
    
    def _get_config_schema(self) -> Dict[str, Any]:
        """获取配置验证模式"""
        return {
            "type": "object",
            "properties": {
                "connection": {
                    "type": "object",
                    "properties": {
                        "default_host": {"type": "string"},
                        "default_port": {"type": "integer", "minimum": 1, "maximum": 65535},
                        "connection_timeout": {"type": "integer", "minimum": 1},
                        "reconnect_attempts": {"type": "integer", "minimum": 0}
                    },
                    "required": ["default_host", "default_port"]
                },
                "ui": {
                    "type": "object",
                    "properties": {
                        "mode": {"type": "string", "enum": ["tui", "cli"]},
                        "theme": {"type": "string"},
                        "language": {"type": "string"}
                    }
                }
            },
            "required": ["connection", "ui", "user", "chat"]
        }
    
    # 便捷访问方法
    def get_default_host(self) -> str:
        """获取默认服务器主机"""
        return self.config_manager.get("connection.default_host", "localhost")
    
    def get_default_port(self) -> int:
        """获取默认服务器端口"""
        return self.config_manager.get("connection.default_port", 8888)
    
    def get_connection_timeout(self) -> int:
        """获取连接超时时间"""
        return self.config_manager.get("connection.connection_timeout", 10)
    
    def get_ui_mode(self) -> str:
        """获取UI模式"""
        return self.config_manager.get("ui.mode", "tui")
    
    def set_ui_mode(self, mode: str) -> bool:
        """设置UI模式"""
        if mode in ["tui", "cli"]:
            success = self.config_manager.set("ui.mode", mode)
            if success:
                self.config_manager.save_config()
            return success
        return False
    
    def get_theme(self) -> str:
        """获取主题"""
        return self.config_manager.get("ui.theme", "default")
    
    def set_theme(self, theme: str) -> bool:
        """设置主题"""
        success = self.config_manager.set("ui.theme", theme)
        if success:
            self.config_manager.save_config()
        return success
    
    def get_download_path(self) -> str:
        """获取下载路径"""
        return self.config_manager.get("user.download_path", "downloads")
    
    def set_download_path(self, path: str) -> bool:
        """设置下载路径"""
        success = self.config_manager.set("user.download_path", path)
        if success:
            self.config_manager.save_config()
        return success
    
    def is_auto_login_enabled(self) -> bool:
        """检查是否启用自动登录"""
        return self.config_manager.get("user.auto_login", False)
    
    def get_default_username(self) -> str:
        """获取默认用户名"""
        return self.config_manager.get("user.default_username", "")
    
    def set_user_credentials(self, username: str, remember: bool = False) -> bool:
        """设置用户凭据"""
        success = True
        success &= self.config_manager.set("user.default_username", username)
        success &= self.config_manager.set("user.remember_credentials", remember)
        if success:
            self.config_manager.save_config()
        return success
    
    def get_tui_config(self) -> Dict[str, Any]:
        """获取TUI配置"""
        return self.config_manager.get("tui", {})
    
    def get_chat_config(self) -> Dict[str, Any]:
        """获取聊天配置"""
        return self.config_manager.get("chat", {})
    
    def get_file_transfer_config(self) -> Dict[str, Any]:
        """获取文件传输配置"""
        return self.config_manager.get("file_transfer", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config_manager.get("logging", {})
    
    def is_debug_enabled(self) -> bool:
        """检查是否启用调试模式"""
        return self.config_manager.get("debug.enabled", False)
    
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
    
    def export_template(self, template_file: str = "config/client_config.template.yaml") -> bool:
        """导出配置模板"""
        template_path = project_root / template_file
        return self.config_manager.export_template(str(template_path))
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        info = self.config_manager.get_config_info()
        info.update({
            "ui_mode": self.get_ui_mode(),
            "theme": self.get_theme(),
            "default_server": f"{self.get_default_host()}:{self.get_default_port()}",
            "auto_login": self.is_auto_login_enabled(),
            "debug_enabled": self.is_debug_enabled()
        })
        return info


# 全局客户端配置实例
_client_config = None


def get_client_config() -> ClientConfig:
    """获取客户端配置实例（单例模式）"""
    global _client_config
    if _client_config is None:
        _client_config = ClientConfig()
    return _client_config


def reload_client_config() -> bool:
    """重新加载客户端配置"""
    global _client_config
    if _client_config is not None:
        return _client_config.reload_config()
    return False
