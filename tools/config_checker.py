#!/usr/bin/env python3
"""
配置管理系统检查工具
用于验证Chat-Room项目的配置管理系统是否正常工作
"""

import sys
import os
from pathlib import Path
import yaml
import json
from typing import Dict, Any, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.config_manager import ConfigManager
from client.config.client_config import get_client_config
from server.config.server_config import get_server_config


class ConfigChecker:
    """配置检查器"""
    
    def __init__(self):
        """初始化配置检查器"""
        self.issues = []
        self.warnings = []
        self.info = []
        
    def add_issue(self, message: str):
        """添加问题"""
        self.issues.append(f"❌ {message}")
        
    def add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(f"⚠️ {message}")
        
    def add_info(self, message: str):
        """添加信息"""
        self.info.append(f"ℹ️ {message}")
    
    def check_config_files_exist(self) -> bool:
        """检查配置文件是否存在"""
        print("🔍 检查配置文件存在性...")
        
        config_files = [
            "config/client_config.yaml",
            "config/server_config.yaml",
            "config/templates/client_config.template.yaml",
            "config/templates/server_config.template.yaml"
        ]
        
        all_exist = True
        for config_file in config_files:
            file_path = project_root / config_file
            if file_path.exists():
                self.add_info(f"配置文件存在: {config_file}")
            else:
                self.add_issue(f"配置文件不存在: {config_file}")
                all_exist = False
        
        return all_exist
    
    def check_config_file_format(self) -> bool:
        """检查配置文件格式"""
        print("🔍 检查配置文件格式...")
        
        config_files = [
            "config/client_config.yaml",
            "config/server_config.yaml"
        ]
        
        all_valid = True
        for config_file in config_files:
            file_path = project_root / config_file
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                self.add_info(f"配置文件格式正确: {config_file}")
            except yaml.YAMLError as e:
                self.add_issue(f"配置文件格式错误 {config_file}: {e}")
                all_valid = False
            except Exception as e:
                self.add_issue(f"读取配置文件失败 {config_file}: {e}")
                all_valid = False
        
        return all_valid
    
    def check_client_config(self) -> bool:
        """检查客户端配置"""
        print("🔍 检查客户端配置...")
        
        try:
            client_config = get_client_config()
            
            # 检查基本配置项
            host = client_config.get_default_host()
            port = client_config.get_default_port()
            ui_mode = client_config.get_ui_mode()
            
            self.add_info(f"客户端默认服务器: {host}:{port}")
            self.add_info(f"客户端UI模式: {ui_mode}")
            
            # 检查配置完整性
            required_sections = ['connection', 'ui', 'user', 'chat', 'logging']
            for section in required_sections:
                if client_config.config_manager.get(section):
                    self.add_info(f"客户端配置节存在: {section}")
                else:
                    self.add_warning(f"客户端配置节缺失: {section}")
            
            return True
            
        except Exception as e:
            self.add_issue(f"客户端配置加载失败: {e}")
            return False
    
    def check_server_config(self) -> bool:
        """检查服务器配置"""
        print("🔍 检查服务器配置...")
        
        try:
            server_config = get_server_config()
            
            # 检查基本配置项
            host = server_config.get_server_host()
            port = server_config.get_server_port()
            max_conn = server_config.get_max_connections()
            ai_enabled = server_config.is_ai_enabled()
            
            self.add_info(f"服务器监听地址: {host}:{port}")
            self.add_info(f"最大连接数: {max_conn}")
            self.add_info(f"AI功能启用: {ai_enabled}")
            
            # 检查AI配置
            if ai_enabled:
                api_key = server_config.get_ai_api_key()
                model = server_config.get_ai_model()
                if api_key:
                    self.add_info(f"AI API密钥已设置 (长度: {len(api_key)})")
                    self.add_info(f"AI模型: {model}")
                else:
                    self.add_warning("AI功能已启用但API密钥未设置")
            
            # 检查配置完整性
            required_sections = ['server', 'database', 'ai', 'logging', 'security']
            for section in required_sections:
                if server_config.config_manager.get(section):
                    self.add_info(f"服务器配置节存在: {section}")
                else:
                    self.add_warning(f"服务器配置节缺失: {section}")
            
            return True
            
        except Exception as e:
            self.add_issue(f"服务器配置加载失败: {e}")
            return False
    
    def check_hardcoded_values(self) -> bool:
        """检查硬编码值"""
        print("🔍 检查硬编码配置值...")
        
        # 检查常量文件
        constants_file = project_root / "shared" / "constants.py"
        if constants_file.exists():
            with open(constants_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'DEFAULT_HOST = "localhost"' in content:
                    self.add_info("常量文件包含默认主机地址（作为备用值）")
                if 'DEFAULT_PORT = 8888' in content:
                    self.add_info("常量文件包含默认端口（作为备用值）")
        
        # 检查主程序是否正确使用配置
        server_main = project_root / "server" / "main.py"
        if server_main.exists():
            with open(server_main, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'get_server_config()' in content:
                    self.add_info("服务器主程序正确使用配置管理器")
                else:
                    self.add_warning("服务器主程序可能未使用配置管理器")
        
        client_main = project_root / "client" / "main.py"
        if client_main.exists():
            with open(client_main, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'get_client_config()' in content:
                    self.add_info("客户端主程序正确使用配置管理器")
                else:
                    self.add_warning("客户端主程序可能未使用配置管理器")
        
        return True
    
    def test_config_modification(self) -> bool:
        """测试配置修改功能"""
        print("🔍 测试配置修改功能...")
        
        try:
            # 测试客户端配置修改
            client_config = get_client_config()
            original_theme = client_config.get_theme()
            
            # 修改主题
            test_theme = "test_theme"
            if client_config.set_theme(test_theme):
                if client_config.get_theme() == test_theme:
                    self.add_info("客户端配置修改功能正常")
                    # 恢复原始值
                    client_config.set_theme(original_theme)
                else:
                    self.add_issue("客户端配置修改后读取值不正确")
            else:
                self.add_issue("客户端配置修改失败")
            
            # 测试服务器配置修改
            server_config = get_server_config()
            original_model = server_config.get_ai_model()
            
            # 修改AI模型
            test_model = "glm-4"
            if server_config.set_ai_model(test_model):
                if server_config.get_ai_model() == test_model:
                    self.add_info("服务器配置修改功能正常")
                    # 恢复原始值
                    server_config.set_ai_model(original_model)
                else:
                    self.add_issue("服务器配置修改后读取值不正确")
            else:
                self.add_warning("服务器配置修改失败（可能是模型不在可用列表中）")
            
            return True
            
        except Exception as e:
            self.add_issue(f"配置修改测试失败: {e}")
            return False
    
    def run_all_checks(self) -> bool:
        """运行所有检查"""
        print("=" * 60)
        print("🔧 Chat-Room 配置管理系统检查")
        print("=" * 60)
        
        checks = [
            self.check_config_files_exist,
            self.check_config_file_format,
            self.check_client_config,
            self.check_server_config,
            self.check_hardcoded_values,
            self.test_config_modification
        ]
        
        all_passed = True
        for check in checks:
            try:
                result = check()
                all_passed = all_passed and result
            except Exception as e:
                self.add_issue(f"检查过程中出错: {e}")
                all_passed = False
            print()
        
        return all_passed
    
    def print_results(self):
        """打印检查结果"""
        print("=" * 60)
        print("📊 检查结果汇总")
        print("=" * 60)
        
        if self.info:
            print("\n✅ 信息:")
            for info in self.info:
                print(f"  {info}")
        
        if self.warnings:
            print("\n⚠️ 警告:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.issues:
            print("\n❌ 问题:")
            for issue in self.issues:
                print(f"  {issue}")
        
        print("\n" + "=" * 60)
        if not self.issues:
            print("🎉 配置管理系统检查通过！")
        else:
            print(f"⚠️ 发现 {len(self.issues)} 个问题需要解决")
        print("=" * 60)


def main():
    """主函数"""
    checker = ConfigChecker()
    success = checker.run_all_checks()
    checker.print_results()
    
    return 0 if success and not checker.issues else 1


if __name__ == "__main__":
    sys.exit(main())
