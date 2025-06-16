"""
配置管理系统测试
测试配置文件的加载、保存、修改等功能
"""

import pytest
import tempfile
import os
import yaml
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.config_manager import ConfigManager
from client.config.client_config import ClientConfig, get_client_config
from server.config.server_config import ServerConfig, get_server_config


class TestConfigManager:
    """配置管理器基础测试"""
    
    def test_config_manager_creation(self):
        """测试配置管理器创建"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            default_config = {"test": {"value": 123}}
            manager = ConfigManager(config_file, default_config)
            
            assert manager.config_file.exists()
            assert manager.config == default_config
        finally:
            os.unlink(config_file)
    
    def test_config_get_set(self):
        """测试配置获取和设置"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            default_config = {"section": {"key": "value"}}
            manager = ConfigManager(config_file, default_config)
            
            # 测试获取
            assert manager.get("section.key") == "value"
            assert manager.get("nonexistent", "default") == "default"
            
            # 测试设置
            assert manager.set("section.new_key", "new_value")
            assert manager.get("section.new_key") == "new_value"
            
        finally:
            os.unlink(config_file)
    
    def test_config_save_load(self):
        """测试配置保存和加载"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            default_config = {"test": {"value": 123}}
            manager = ConfigManager(config_file, default_config)
            
            # 修改配置
            manager.set("test.value", 456)
            manager.save_config()
            
            # 创建新的管理器实例，验证配置被正确保存
            new_manager = ConfigManager(config_file, default_config)
            assert new_manager.get("test.value") == 456
            
        finally:
            os.unlink(config_file)


class TestClientConfig:
    """客户端配置测试"""
    
    def test_client_config_creation(self):
        """测试客户端配置创建"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            client_config = ClientConfig(config_file)
            
            # 验证默认值
            assert client_config.get_default_host() == "localhost"
            assert client_config.get_default_port() == 8888
            assert client_config.get_ui_mode() == "tui"
            
        finally:
            os.unlink(config_file)
    
    def test_client_config_modification(self):
        """测试客户端配置修改"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            client_config = ClientConfig(config_file)
            
            # 修改配置
            assert client_config.set_ui_mode("cli")
            assert client_config.get_ui_mode() == "cli"
            
            assert client_config.set_theme("dark")
            assert client_config.get_theme() == "dark"
            
        finally:
            os.unlink(config_file)


class TestServerConfig:
    """服务器配置测试"""
    
    def test_server_config_creation(self):
        """测试服务器配置创建"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            server_config = ServerConfig(config_file)
            
            # 验证默认值
            assert server_config.get_server_host() == "localhost"
            assert server_config.get_server_port() == 8888
            assert server_config.get_max_connections() == 100
            
        finally:
            os.unlink(config_file)
    
    def test_server_ai_config(self):
        """测试服务器AI配置"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            server_config = ServerConfig(config_file)
            
            # 测试AI配置
            assert server_config.set_ai_api_key("test_key")
            assert server_config.get_ai_api_key() == "test_key"
            
            assert server_config.set_ai_model("glm-4")
            assert server_config.get_ai_model() == "glm-4"
            
        finally:
            os.unlink(config_file)


class TestConfigIntegration:
    """配置系统集成测试"""
    
    def test_config_file_modification_effect(self):
        """测试修改配置文件后的效果"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
            config_file = f.name
        
        try:
            # 创建初始配置
            default_config = {"server": {"host": "localhost", "port": 8888}}
            manager = ConfigManager(config_file, default_config)
            
            # 直接修改配置文件
            new_config = {"server": {"host": "0.0.0.0", "port": 9999}}
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f)
            
            # 重新加载配置
            manager.load_config()
            
            # 验证配置已更新
            assert manager.get("server.host") == "0.0.0.0"
            assert manager.get("server.port") == 9999
            
        finally:
            os.unlink(config_file)
    
    def test_config_template_export(self):
        """测试配置模板导出"""
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as config_file, \
             tempfile.NamedTemporaryFile(suffix='.template.yaml', delete=False) as template_file:
            
            config_path = config_file.name
            template_path = template_file.name
        
        try:
            default_config = {"test": {"value": 123, "description": "测试配置"}}
            manager = ConfigManager(config_path, default_config)
            
            # 导出模板
            assert manager.export_template(template_path)
            
            # 验证模板文件存在且包含正确内容
            assert os.path.exists(template_path)
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Chat-Room 配置文件模板" in content
                assert "test:" in content
                
        finally:
            os.unlink(config_path)
            os.unlink(template_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
