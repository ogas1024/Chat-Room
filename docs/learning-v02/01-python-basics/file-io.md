# Python文件操作和I/O

## 🎯 学习目标

通过本章学习，您将能够：
- 掌握Python文件读写的基本操作
- 理解不同文件模式的使用场景
- 学会处理文件路径和目录操作
- 在Chat-Room项目中应用文件I/O技术
- 实现配置文件读取和日志文件写入
- 掌握文件传输的基础知识

## 📁 文件操作基础

### 文件操作概述

在Chat-Room项目中，文件操作无处不在：配置文件读取、日志记录、用户数据存储、文件传输等。

```mermaid
graph TD
    A[文件操作] --> B[读取操作]
    A --> C[写入操作]
    A --> D[路径操作]
    A --> E[目录操作]
    
    B --> B1[读取配置文件]
    B --> B2[读取用户数据]
    B --> B3[读取传输文件]
    
    C --> C1[写入日志文件]
    C --> C2[保存用户设置]
    C --> C3[创建备份文件]
    
    D --> D1[路径拼接]
    D --> D2[路径验证]
    D --> D3[相对/绝对路径]
    
    E --> E1[创建目录]
    E --> E2[遍历目录]
    E --> E3[删除目录]
    
    style A fill:#e8f5e8
    style B fill:#fff3cd
    style C fill:#f8d7da
```

### 基本文件读写

```python
# shared/utils/file_manager.py - 文件管理工具类
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from shared.exceptions import FileOperationException

class FileManager:
    """文件管理工具类，封装常用的文件操作"""
    
    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
        """
        读取文本文件内容
        
        Args:
            file_path: 文件路径
            encoding: 文件编码，默认utf-8
            
        Returns:
            文件内容字符串
            
        Raises:
            FileOperationException: 文件操作失败
        """
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                content = file.read()
                print(f"✅ 成功读取文件: {file_path}")
                return content
                
        except FileNotFoundError:
            raise FileOperationException(f"文件不存在: {file_path}")
        except PermissionError:
            raise FileOperationException(f"没有读取权限: {file_path}")
        except UnicodeDecodeError as e:
            raise FileOperationException(f"文件编码错误: {e}")
        except Exception as e:
            raise FileOperationException(f"读取文件失败: {e}")
    
    @staticmethod
    def write_text_file(file_path: str, content: str, encoding: str = 'utf-8', 
                       mode: str = 'w') -> None:
        """
        写入文本文件
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            encoding: 文件编码，默认utf-8
            mode: 写入模式，'w'覆盖，'a'追加
            
        Raises:
            FileOperationException: 文件操作失败
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, mode, encoding=encoding) as file:
                file.write(content)
                print(f"✅ 成功写入文件: {file_path}")
                
        except PermissionError:
            raise FileOperationException(f"没有写入权限: {file_path}")
        except OSError as e:
            if e.errno == 28:  # No space left on device
                raise FileOperationException("磁盘空间不足")
            else:
                raise FileOperationException(f"写入文件失败: {e}")
        except Exception as e:
            raise FileOperationException(f"写入文件失败: {e}")

# 配置文件操作示例
class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def load_server_config(self) -> Dict[str, Any]:
        """
        加载服务器配置文件
        
        Returns:
            配置字典
        """
        config_file = self.config_dir / "server_config.yaml"
        
        # 默认配置
        default_config = {
            "server": {
                "host": "localhost",
                "port": 8888,
                "max_connections": 100,
                "timeout": 30
            },
            "database": {
                "path": "data/chatroom.db",
                "backup_interval": 3600
            },
            "logging": {
                "level": "INFO",
                "file": "logs/server.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
        
        try:
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    print(f"✅ 加载配置文件: {config_file}")
                    return config
            else:
                # 创建默认配置文件
                self.save_server_config(default_config)
                return default_config
                
        except yaml.YAMLError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return default_config
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return default_config
    
    def save_server_config(self, config: Dict[str, Any]) -> None:
        """保存服务器配置文件"""
        config_file = self.config_dir / "server_config.yaml"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as file:
                yaml.dump(config, file, default_flow_style=False, 
                         allow_unicode=True, indent=2)
                print(f"✅ 保存配置文件: {config_file}")
                
        except Exception as e:
            raise FileOperationException(f"保存配置文件失败: {e}")

# 使用示例
def demo_config_operations():
    """演示配置文件操作"""
    config_manager = ConfigManager()
    
    # 加载配置
    config = config_manager.load_server_config()
    print("当前服务器配置:")
    print(f"  主机: {config['server']['host']}")
    print(f"  端口: {config['server']['port']}")
    print(f"  最大连接数: {config['server']['max_connections']}")
    
    # 修改配置
    config['server']['port'] = 9999
    config['server']['max_connections'] = 200
    
    # 保存配置
    config_manager.save_server_config(config)
    print("配置已更新并保存")
```

### 日志文件操作

```python
# shared/utils/logger.py - 日志文件管理
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

class SimpleLogger:
    """简单的日志记录器，演示文件写入操作"""
    
    def __init__(self, log_dir: str = "logs", log_file: str = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        if log_file is None:
            # 使用日期作为日志文件名
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = f"chatroom_{today}.log"
        
        self.log_file = self.log_dir / log_file
    
    def log(self, level: str, message: str, module: str = None) -> None:
        """
        写入日志记录
        
        Args:
            level: 日志级别（INFO, WARNING, ERROR）
            message: 日志消息
            module: 模块名称
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        module_info = f"[{module}]" if module else ""
        log_entry = f"{timestamp} [{level}] {module_info} {message}\n"
        
        try:
            # 使用追加模式写入日志
            with open(self.log_file, 'a', encoding='utf-8') as file:
                file.write(log_entry)
                file.flush()  # 立即刷新到磁盘
                
        except Exception as e:
            print(f"写入日志失败: {e}")
    
    def info(self, message: str, module: str = None):
        """记录信息日志"""
        self.log("INFO", message, module)
    
    def warning(self, message: str, module: str = None):
        """记录警告日志"""
        self.log("WARNING", message, module)
    
    def error(self, message: str, module: str = None):
        """记录错误日志"""
        self.log("ERROR", message, module)
    
    def get_recent_logs(self, lines: int = 50) -> List[str]:
        """
        获取最近的日志记录
        
        Args:
            lines: 要获取的行数
            
        Returns:
            日志行列表
        """
        try:
            if not self.log_file.exists():
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as file:
                all_lines = file.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
                
        except Exception as e:
            print(f"读取日志失败: {e}")
            return []

# 使用示例
def demo_logging_operations():
    """演示日志操作"""
    logger = SimpleLogger()
    
    # 记录不同级别的日志
    logger.info("服务器启动", "server")
    logger.info("用户 alice 连接成功", "connection")
    logger.warning("连接数接近上限", "server")
    logger.error("数据库连接失败", "database")
    
    # 读取最近的日志
    recent_logs = logger.get_recent_logs(10)
    print("最近的日志记录:")
    for log_line in recent_logs:
        print(log_line.strip())
```

### 文件传输基础

```python
# shared/utils/file_transfer.py - 文件传输工具
import os
import hashlib
from pathlib import Path
from typing import Generator, Tuple

class FileTransferHelper:
    """文件传输辅助工具"""
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """
        计算文件哈希值，用于验证文件完整性
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法（md5, sha1, sha256）
            
        Returns:
            文件哈希值
        """
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as file:
                # 分块读取，避免大文件占用过多内存
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            raise FileOperationException(f"计算文件哈希失败: {e}")
    
    @staticmethod
    def read_file_chunks(file_path: str, chunk_size: int = 4096) -> Generator[bytes, None, None]:
        """
        分块读取文件，用于大文件传输
        
        Args:
            file_path: 文件路径
            chunk_size: 块大小（字节）
            
        Yields:
            文件数据块
        """
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
                    
        except Exception as e:
            raise FileOperationException(f"读取文件块失败: {e}")
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典
        """
        try:
            file_stat = os.stat(file_path)
            file_path_obj = Path(file_path)
            
            return {
                "name": file_path_obj.name,
                "size": file_stat.st_size,
                "modified_time": file_stat.st_mtime,
                "is_file": file_path_obj.is_file(),
                "extension": file_path_obj.suffix,
                "parent_dir": str(file_path_obj.parent)
            }
            
        except Exception as e:
            raise FileOperationException(f"获取文件信息失败: {e}")

# 使用示例
def demo_file_transfer_operations():
    """演示文件传输操作"""
    helper = FileTransferHelper()
    
    # 创建测试文件
    test_file = "test_data.txt"
    test_content = "这是一个测试文件\n" * 1000
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # 获取文件信息
        file_info = helper.get_file_info(test_file)
        print(f"文件名: {file_info['name']}")
        print(f"文件大小: {file_info['size']} 字节")
        
        # 计算文件哈希
        file_hash = helper.calculate_file_hash(test_file)
        print(f"文件哈希: {file_hash}")
        
        # 分块读取文件
        print("分块读取文件:")
        chunk_count = 0
        for chunk in helper.read_file_chunks(test_file, chunk_size=1024):
            chunk_count += 1
            print(f"  块 {chunk_count}: {len(chunk)} 字节")
            if chunk_count >= 3:  # 只显示前3块
                break
        
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
```

## 🎯 实践练习

### 练习1：配置文件管理器
```python
def practice_config_manager():
    """
    配置文件管理练习
    
    要求：
    1. 支持JSON和YAML格式
    2. 提供配置验证功能
    3. 支持配置热重载
    4. 处理配置文件损坏的情况
    """
    # TODO: 实现完整的配置文件管理器
    pass
```

### 练习2：日志轮转系统
```python
def practice_log_rotation():
    """
    日志轮转系统练习
    
    要求：
    1. 按文件大小轮转日志
    2. 按时间轮转日志
    3. 压缩旧日志文件
    4. 自动清理过期日志
    """
    # TODO: 实现日志轮转系统
    pass
```

## ✅ 学习检查

完成本章学习后，请确认您能够：

- [ ] 熟练进行文件读写操作
- [ ] 处理不同的文件编码问题
- [ ] 管理配置文件的读取和保存
- [ ] 实现日志文件的写入和管理
- [ ] 进行文件传输的基础操作
- [ ] 处理文件操作中的异常情况
- [ ] 完成实践练习

## 📚 下一步

文件操作基础掌握后，请继续学习：
- [常用内置库介绍](builtin-libraries.md) - 学习Python常用的内置库

---

**文件操作是程序与外部数据交互的重要技能！** 📁
