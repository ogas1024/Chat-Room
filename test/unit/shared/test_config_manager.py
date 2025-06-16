"""
测试共享配置管理模块
测试配置文件加载、验证和管理功能
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from shared.config_manager import ConfigManager
from shared.exceptions import ConfigError


class TestConfigManager:
    """测试配置管理器"""
    
    def test_config_manager_creation(self):
        """测试配置管理器创建"""
        config_manager = ConfigManager()
        assert config_manager is not None
        assert hasattr(config_manager, 'config')
        assert isinstance(config_manager.config, dict)
    
    def test_load_valid_yaml_config(self, temp_dir):
        """测试加载有效的YAML配置"""
        config_data = {
            "server": {
                "host": "localhost",
                "port": 8888,
                "max_connections": 100
            },
            "database": {
                "path": "test.db",
                "backup_enabled": True
            }
        }
        
        config_file = temp_dir / "test_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
        
        config_manager = ConfigManager()
        config_manager.load_config(str(config_file))
        
        assert config_manager.get("server.host") == "localhost"
        assert config_manager.get("server.port") == 8888
        assert config_manager.get("database.backup_enabled") is True
    
    def test_load_invalid_yaml_config(self, temp_dir):
        """测试加载无效的YAML配置"""
        config_file = temp_dir / "invalid_config.yaml"
        with open(config_file, 'w') as f:
            f.write("invalid: yaml: content: [")
        
        config_manager = ConfigManager()
        with pytest.raises(ConfigError):
            config_manager.load_config(str(config_file))
    
    def test_load_nonexistent_config(self):
        """测试加载不存在的配置文件"""
        config_manager = ConfigManager()
        with pytest.raises(ConfigError):
            config_manager.load_config("nonexistent_config.yaml")
    
    def test_get_config_value(self):
        """测试获取配置值"""
        config_manager = ConfigManager()
        config_manager.config = {
            "server": {
                "host": "localhost",
                "port": 8888,
                "settings": {
                    "debug": True
                }
            }
        }
        
        # 测试简单键
        assert config_manager.get("server") == config_manager.config["server"]
        
        # 测试嵌套键
        assert config_manager.get("server.host") == "localhost"
        assert config_manager.get("server.port") == 8888
        assert config_manager.get("server.settings.debug") is True
        
        # 测试不存在的键
        assert config_manager.get("nonexistent") is None
        assert config_manager.get("server.nonexistent") is None
        
        # 测试默认值
        assert config_manager.get("nonexistent", "default") == "default"
        assert config_manager.get("server.nonexistent", 9999) == 9999
    
    def test_set_config_value(self):
        """测试设置配置值"""
        config_manager = ConfigManager()
        config_manager.config = {}
        
        # 设置简单值
        config_manager.set("host", "localhost")
        assert config_manager.get("host") == "localhost"
        
        # 设置嵌套值
        config_manager.set("server.port", 8888)
        assert config_manager.get("server.port") == 8888
        assert config_manager.get("server") == {"port": 8888}
        
        # 设置深层嵌套值
        config_manager.set("database.connection.timeout", 30)
        assert config_manager.get("database.connection.timeout") == 30
        
        # 覆盖现有值
        config_manager.set("server.port", 9999)
        assert config_manager.get("server.port") == 9999
    
    def test_has_config_key(self):
        """测试检查配置键是否存在"""
        config_manager = ConfigManager()
        config_manager.config = {
            "server": {
                "host": "localhost",
                "port": 8888
            }
        }
        
        # 测试存在的键
        assert config_manager.has("server") is True
        assert config_manager.has("server.host") is True
        assert config_manager.has("server.port") is True
        
        # 测试不存在的键
        assert config_manager.has("nonexistent") is False
        assert config_manager.has("server.nonexistent") is False
        assert config_manager.has("server.host.nonexistent") is False
    
    def test_update_config(self):
        """测试更新配置"""
        config_manager = ConfigManager()
        config_manager.config = {
            "server": {
                "host": "localhost",
                "port": 8888
            }
        }
        
        # 更新配置
        update_data = {
            "server": {
                "port": 9999,
                "max_connections": 100
            },
            "database": {
                "path": "new.db"
            }
        }
        
        config_manager.update(update_data)
        
        # 验证更新结果
        assert config_manager.get("server.host") == "localhost"  # 保持原值
        assert config_manager.get("server.port") == 9999  # 更新值
        assert config_manager.get("server.max_connections") == 100  # 新增值
        assert config_manager.get("database.path") == "new.db"  # 新增节点
    
    def test_validate_config_schema(self):
        """测试配置模式验证"""
        config_manager = ConfigManager()
        
        # 定义配置模式
        schema = {
            "server": {
                "host": str,
                "port": int,
                "max_connections": int
            },
            "database": {
                "path": str,
                "backup_enabled": bool
            }
        }
        
        # 有效配置
        valid_config = {
            "server": {
                "host": "localhost",
                "port": 8888,
                "max_connections": 100
            },
            "database": {
                "path": "test.db",
                "backup_enabled": True
            }
        }
        
        config_manager.config = valid_config
        assert config_manager.validate_schema(schema) is True
        
        # 无效配置 - 类型错误
        invalid_config = {
            "server": {
                "host": "localhost",
                "port": "8888",  # 应该是int
                "max_connections": 100
            },
            "database": {
                "path": "test.db",
                "backup_enabled": True
            }
        }
        
        config_manager.config = invalid_config
        assert config_manager.validate_schema(schema) is False
    
    def test_get_section(self):
        """测试获取配置节"""
        config_manager = ConfigManager()
        config_manager.config = {
            "server": {
                "host": "localhost",
                "port": 8888,
                "settings": {
                    "debug": True,
                    "log_level": "INFO"
                }
            },
            "database": {
                "path": "test.db"
            }
        }
        
        # 获取顶级节
        server_config = config_manager.get_section("server")
        assert server_config["host"] == "localhost"
        assert server_config["port"] == 8888
        
        # 获取嵌套节
        settings_config = config_manager.get_section("server.settings")
        assert settings_config["debug"] is True
        assert settings_config["log_level"] == "INFO"
        
        # 获取不存在的节
        nonexistent = config_manager.get_section("nonexistent")
        assert nonexistent == {}
    
    def test_merge_configs(self):
        """测试合并配置"""
        config_manager = ConfigManager()
        
        base_config = {
            "server": {
                "host": "localhost",
                "port": 8888,
                "settings": {
                    "debug": False,
                    "timeout": 30
                }
            },
            "database": {
                "path": "base.db"
            }
        }
        
        override_config = {
            "server": {
                "port": 9999,
                "settings": {
                    "debug": True,
                    "max_connections": 100
                }
            },
            "logging": {
                "level": "DEBUG"
            }
        }
        
        merged = config_manager.merge_configs(base_config, override_config)
        
        # 验证合并结果
        assert merged["server"]["host"] == "localhost"  # 保持base值
        assert merged["server"]["port"] == 9999  # 使用override值
        assert merged["server"]["settings"]["debug"] is True  # 使用override值
        assert merged["server"]["settings"]["timeout"] == 30  # 保持base值
        assert merged["server"]["settings"]["max_connections"] == 100  # 新增值
        assert merged["database"]["path"] == "base.db"  # 保持base值
        assert merged["logging"]["level"] == "DEBUG"  # 新增节点
    
    def test_save_config(self, temp_dir):
        """测试保存配置"""
        config_manager = ConfigManager()
        config_manager.config = {
            "server": {
                "host": "localhost",
                "port": 8888
            },
            "database": {
                "path": "test.db",
                "backup_enabled": True
            }
        }
        
        config_file = temp_dir / "saved_config.yaml"
        config_manager.save_config(str(config_file))
        
        # 验证文件存在
        assert config_file.exists()
        
        # 验证文件内容
        with open(config_file, 'r', encoding='utf-8') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data["server"]["host"] == "localhost"
        assert saved_data["server"]["port"] == 8888
        assert saved_data["database"]["backup_enabled"] is True
    
    def test_config_with_chinese_content(self, temp_dir):
        """测试包含中文内容的配置"""
        config_data = {
            "应用": {
                "名称": "聊天室",
                "版本": "1.0.0"
            },
            "服务器": {
                "主机": "本地主机",
                "端口": 8888
            }
        }
        
        config_file = temp_dir / "chinese_config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True)
        
        config_manager = ConfigManager()
        config_manager.load_config(str(config_file))
        
        assert config_manager.get("应用.名称") == "聊天室"
        assert config_manager.get("服务器.主机") == "本地主机"
        assert config_manager.get("服务器.端口") == 8888
    
    def test_environment_variable_substitution(self):
        """测试环境变量替换"""
        config_manager = ConfigManager()
        
        with patch.dict('os.environ', {'TEST_HOST': 'test.example.com', 'TEST_PORT': '9999'}):
            config_data = {
                "server": {
                    "host": "${TEST_HOST}",
                    "port": "${TEST_PORT}",
                    "fallback": "${NONEXISTENT:localhost}"
                }
            }
            
            config_manager.config = config_data
            config_manager.substitute_env_vars()
            
            assert config_manager.get("server.host") == "test.example.com"
            assert config_manager.get("server.port") == "9999"
            assert config_manager.get("server.fallback") == "localhost"
