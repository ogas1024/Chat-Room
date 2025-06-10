"""
统一配置管理模块
提供YAML/JSON配置文件的读取、验证和管理功能
"""

import os
import yaml
import json
import copy
from typing import Dict, Any, Optional, Union
from pathlib import Path


class ConfigManager:
    """配置管理器基类"""
    
    def __init__(self, config_file: str, default_config: Dict[str, Any], 
                 config_schema: Optional[Dict[str, Any]] = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
            default_config: 默认配置字典
            config_schema: 配置验证模式（可选）
        """
        self.config_file = Path(config_file)
        self.default_config = default_config
        self.config_schema = config_schema
        self.config = {}
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        try:
            if self.config_file.exists():
                # 读取现有配置文件
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.suffix.lower() == '.yaml' or self.config_file.suffix.lower() == '.yml':
                        loaded_config = yaml.safe_load(f) or {}
                    elif self.config_file.suffix.lower() == '.json':
                        loaded_config = json.load(f) or {}
                    else:
                        raise ValueError(f"不支持的配置文件格式: {self.config_file.suffix}")
                
                # 合并默认配置和加载的配置
                self.config = self._merge_configs(self.default_config, loaded_config)
                print(f"✅ 配置文件已加载: {self.config_file}")
            else:
                # 使用默认配置并创建配置文件
                self.config = copy.deepcopy(self.default_config)
                self.save_config()
                print(f"📝 已创建默认配置文件: {self.config_file}")
            
            # 验证配置
            if self.config_schema:
                self._validate_config()
            
            return self.config
            
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            print(f"💡 使用默认配置")
            self.config = copy.deepcopy(self.default_config)
            return self.config
    
    def save_config(self) -> bool:
        """
        保存配置到文件
        
        Returns:
            保存是否成功
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.suffix.lower() == '.yaml' or self.config_file.suffix.lower() == '.yml':
                    yaml.dump(self.config, f, default_flow_style=False, 
                             allow_unicode=True, indent=2, sort_keys=False)
                elif self.config_file.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"不支持的配置文件格式: {self.config_file.suffix}")
            
            print(f"✅ 配置已保存: {self.config_file}")
            return True
            
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号分隔的嵌套键）
        
        Args:
            key: 配置键，支持 'section.subsection.key' 格式
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值（支持点号分隔的嵌套键）
        
        Args:
            key: 配置键
            value: 配置值
            
        Returns:
            设置是否成功
        """
        keys = key.split('.')
        config = self.config
        
        try:
            # 导航到最后一级的父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            return True
            
        except Exception as e:
            print(f"❌ 设置配置失败: {e}")
            return False
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """
        批量更新配置
        
        Args:
            updates: 更新的配置字典
            
        Returns:
            更新是否成功
        """
        try:
            self.config = self._merge_configs(self.config, updates)
            return True
        except Exception as e:
            print(f"❌ 批量更新配置失败: {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """
        重置为默认配置
        
        Returns:
            重置是否成功
        """
        try:
            self.config = copy.deepcopy(self.default_config)
            return self.save_config()
        except Exception as e:
            print(f"❌ 重置配置失败: {e}")
            return False
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归合并配置字典
        
        Args:
            base: 基础配置
            override: 覆盖配置
            
        Returns:
            合并后的配置
        """
        result = copy.deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _validate_config(self) -> bool:
        """
        验证配置格式
        
        Returns:
            验证是否通过
        """
        if not self.config_schema:
            return True
        
        try:
            import jsonschema
            jsonschema.validate(self.config, self.config_schema)
            return True
        except ImportError:
            print("⚠️ jsonschema未安装，跳过配置验证")
            return True
        except Exception as e:
            print(f"❌ 配置验证失败: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置信息
        
        Returns:
            配置信息字典
        """
        return {
            "config_file": str(self.config_file),
            "file_exists": self.config_file.exists(),
            "file_size": self.config_file.stat().st_size if self.config_file.exists() else 0,
            "config_keys": list(self.config.keys()),
            "has_schema": bool(self.config_schema)
        }
    
    def export_template(self, template_file: str) -> bool:
        """
        导出配置模板文件
        
        Args:
            template_file: 模板文件路径
            
        Returns:
            导出是否成功
        """
        try:
            template_path = Path(template_file)
            template_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建带注释的模板
            template_config = copy.deepcopy(self.default_config)
            
            with open(template_path, 'w', encoding='utf-8') as f:
                if template_path.suffix.lower() in ['.yaml', '.yml']:
                    # 添加YAML注释
                    f.write("# Chat-Room 配置文件模板\n")
                    f.write("# 请根据需要修改以下配置项\n\n")
                    yaml.dump(template_config, f, default_flow_style=False, 
                             allow_unicode=True, indent=2, sort_keys=False)
                elif template_path.suffix.lower() == '.json':
                    # JSON格式
                    f.write("{\n")
                    f.write('  "_comment": "Chat-Room 配置文件模板，请根据需要修改以下配置项",\n')
                    json_str = json.dumps(template_config, indent=2, ensure_ascii=False)
                    # 移除第一个和最后一个大括号
                    json_content = json_str[2:-2]
                    f.write(json_content)
                    f.write("\n}")
            
            print(f"✅ 配置模板已导出: {template_path}")
            return True
            
        except Exception as e:
            print(f"❌ 导出配置模板失败: {e}")
            return False


def create_config_directory(config_dir: str) -> bool:
    """
    创建配置目录
    
    Args:
        config_dir: 配置目录路径
        
    Returns:
        创建是否成功
    """
    try:
        Path(config_dir).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ 创建配置目录失败: {e}")
        return False
