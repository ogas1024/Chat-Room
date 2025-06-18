"""
服务器端配置管理
统一管理服务器的所有配置项
"""

from typing import Dict, Any
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


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

        # 检查配置文件是否存在
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_file}\n"
                f"请确保配置文件存在，或从模板创建: config/templates/server_config.template.yaml"
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
            "server.host",
            "server.port",
            "database.path",
            "ai",
            "logging"
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
    def get_server_host(self) -> str:
        """获取服务器主机地址"""
        return self.config["server"]["host"]

    def get_server_port(self) -> int:
        """获取服务器端口"""
        return self.config["server"]["port"]

    def get_max_connections(self) -> int:
        """获取最大连接数"""
        return self.config["server"].get("max_connections", 100)

    def get_database_path(self) -> str:
        """获取数据库路径"""
        return self.config["database"]["path"]

    def get_files_storage_path(self) -> str:
        """获取文件存储路径"""
        return self.config.get("file_storage", {}).get("path", "server/data/files")

    def get_max_file_size(self) -> int:
        """获取最大文件大小"""
        return self.config.get("file_storage", {}).get("max_file_size", 104857600)

    def get_allowed_file_extensions(self) -> list:
        """获取允许的文件扩展名"""
        return self.config.get("file_storage", {}).get("allowed_extensions", [])

    def is_ai_enabled(self) -> bool:
        """检查AI功能是否启用"""
        ai_config = self.config.get("ai", {})
        return (ai_config.get("enabled", False) and
                bool(ai_config.get("api_key", "")))

    def get_ai_api_key(self) -> str:
        """获取AI API密钥"""
        return self.config.get("ai", {}).get("api_key", "")

    def get_ai_model(self) -> str:
        """获取AI模型"""
        return self.config.get("ai", {}).get("model", "glm-4-flash")

    def get_ai_config(self) -> Dict[str, Any]:
        """获取完整的AI配置"""
        return self.config.get("ai", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        return self.config.get("logging", {})

    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self.config.get("security", {})
    
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
            "ai_enabled": self.is_ai_enabled(),
            "ai_api_key_set": bool(self.get_ai_api_key()),
            "ai_model": self.get_ai_model(),
            "server_address": f"{self.get_server_host()}:{self.get_server_port()}"
        }


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
