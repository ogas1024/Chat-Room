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

        # 检查配置文件是否存在
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_file}\n"
                f"请确保配置文件存在，或从模板创建: config/templates/client_config.template.yaml"
            )

        # 直接加载配置文件
        try:
            import yaml
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            print(f"✅ 配置文件已加载: {self.config_file}")
        except Exception as e:
            raise RuntimeError(f"配置文件加载失败: {e}")

        # 验证必需的配置项
        self._validate_required_config()

    def _validate_required_config(self):
        """验证必需的配置项"""
        required_keys = [
            "connection.default_host",
            "connection.default_port",
            "ui.mode",
            "user",
            "chat"
        ]

        missing_keys = []
        for key in required_keys:
            if not self._has_nested_key(self.config, key):
                missing_keys.append(key)

        if missing_keys:
            raise ValueError(f"配置文件缺少必需项: {missing_keys}")

    def _has_nested_key(self, config: Dict[str, Any], key: str) -> bool:
        """检查嵌套键是否存在"""
        keys = key.split('.')
        current = config

        try:
            for k in keys:
                current = current[k]
            return True
        except (KeyError, TypeError):
            return False


    
    # 便捷访问方法
    def get_default_host(self) -> str:
        """获取默认服务器主机"""
        return self.config["connection"]["default_host"]

    def get_default_port(self) -> int:
        """获取默认服务器端口"""
        return self.config["connection"]["default_port"]

    def get_connection_timeout(self) -> int:
        """获取连接超时时间"""
        return self.config["connection"].get("connection_timeout", 10)

    def get_ui_mode(self) -> str:
        """获取UI模式"""
        return self.config["ui"]["mode"]
    
    def get_theme(self) -> str:
        """获取主题"""
        return self.config["ui"].get("theme", "default")

    def get_download_path(self) -> str:
        """获取下载路径"""
        return self.config["user"].get("download_path", "downloads")

    def is_auto_login_enabled(self) -> bool:
        """检查是否启用自动登录"""
        return self.config["user"].get("auto_login", False)

    def get_default_username(self) -> str:
        """获取默认用户名"""
        return self.config["user"].get("default_username", "")

    def get_tui_config(self) -> Dict[str, Any]:
        """获取TUI配置"""
        return self.config.get("tui", {})

    def get_chat_config(self) -> Dict[str, Any]:
        """获取聊天配置"""
        return self.config.get("chat", {})

    def get_file_transfer_config(self) -> Dict[str, Any]:
        """获取文件传输配置"""
        return self.config.get("file_transfer", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get("logging", {})

    def is_debug_enabled(self) -> bool:
        """检查是否启用调试模式"""
        return self.config.get("debug", {}).get("enabled", False)
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            import yaml
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False,
                         allow_unicode=True, indent=2, sort_keys=False)
            print(f"✅ 配置已保存: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False

    def reload_config(self) -> bool:
        """重新加载配置"""
        try:
            import yaml
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            self._validate_required_config()
            print(f"✅ 配置已重新加载: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ 重新加载配置失败: {e}")
            return False

    def get_config_info(self) -> Dict[str, Any]:
        """获取配置信息"""
        return {
            "config_file": str(self.config_file),
            "file_exists": self.config_file.exists(),
            "file_size": self.config_file.stat().st_size if self.config_file.exists() else 0,
            "ui_mode": self.get_ui_mode(),
            "theme": self.get_theme(),
            "default_server": f"{self.get_default_host()}:{self.get_default_port()}",
            "auto_login": self.is_auto_login_enabled(),
            "debug_enabled": self.is_debug_enabled()
        }


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
