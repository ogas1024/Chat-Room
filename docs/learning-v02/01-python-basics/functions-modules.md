# 函数与模块深入学习

## 🎯 学习目标

通过本章学习，您将能够：
- 掌握Python函数的高级特性和最佳实践
- 理解装饰器的原理和应用场景
- 学会模块和包的组织管理
- 在Chat-Room项目中应用模块化设计思想

## 🔧 函数高级特性

### 函数参数的灵活使用
```python
# server/utils/auth.py - 认证工具函数
def validate_user_input(username: str, password: str, 
                       email: str = None, 
                       *additional_fields,
                       **validation_options) -> tuple:
    """
    用户输入验证函数
    
    参数类型演示：
    - 位置参数：username, password（必需）
    - 默认参数：email（可选）
    - 可变位置参数：*additional_fields（额外字段）
    - 可变关键字参数：**validation_options（验证选项）
    
    Args:
        username: 用户名
        password: 密码
        email: 邮箱（可选）
        *additional_fields: 额外验证字段
        **validation_options: 验证选项
        
    Returns:
        (is_valid: bool, error_message: str)
    """
    # 获取验证选项（带默认值）
    min_username_length = validation_options.get('min_username_length', 3)
    max_username_length = validation_options.get('max_username_length', 20)
    require_special_char = validation_options.get('require_special_char', False)
    
    # 用户名验证
    if not username or len(username) < min_username_length:
        return False, f"用户名长度不能少于{min_username_length}字符"
    
    if len(username) > max_username_length:
        return False, f"用户名长度不能超过{max_username_length}字符"
    
    # 密码验证
    if not password or len(password) < 6:
        return False, "密码长度不能少于6字符"
    
    if require_special_char:
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(char in special_chars for char in password):
            return False, "密码必须包含特殊字符"
    
    # 邮箱验证（如果提供）
    if email:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "邮箱格式不正确"
    
    # 处理额外字段
    for field in additional_fields:
        if not field or len(field.strip()) == 0:
            return False, "额外字段不能为空"
    
    return True, "验证通过"

# 使用示例
def demo_function_parameters():
    """函数参数使用演示"""
    
    # 基本使用
    result1 = validate_user_input("alice", "password123")
    print(f"基本验证: {result1}")
    
    # 带可选参数
    result2 = validate_user_input("bob", "password123", "bob@example.com")
    print(f"带邮箱验证: {result2}")
    
    # 带额外字段
    result3 = validate_user_input("charlie", "password123", "charlie@example.com", 
                                 "真实姓名", "电话号码")
    print(f"带额外字段: {result3}")
    
    # 带验证选项
    result4 = validate_user_input("dave", "password123", 
                                 min_username_length=5,
                                 require_special_char=True)
    print(f"自定义验证选项: {result4}")
```

### 高阶函数和函数式编程
```python
# server/utils/message_processor.py - 消息处理工具
def create_message_filter(filter_type: str):
    """
    创建消息过滤器（高阶函数）
    
    返回一个函数，用于过滤特定类型的消息
    这是函数式编程的应用：函数作为返回值
    """
    
    def spam_filter(message: str) -> bool:
        """垃圾消息过滤器"""
        spam_keywords = ['广告', '推广', '免费', '中奖', '点击链接']
        return not any(keyword in message for keyword in spam_keywords)
    
    def profanity_filter(message: str) -> bool:
        """不当内容过滤器"""
        profanity_words = ['脏话1', '脏话2', '不当词汇']  # 实际项目中会有更完整的词库
        return not any(word in message for word in profanity_words)
    
    def length_filter(message: str) -> bool:
        """长度过滤器"""
        return 1 <= len(message) <= 1000
    
    # 根据类型返回对应的过滤函数
    filters = {
        'spam': spam_filter,
        'profanity': profanity_filter,
        'length': length_filter
    }
    
    return filters.get(filter_type, lambda msg: True)

def process_messages(messages: list, *filter_types) -> list:
    """
    处理消息列表（函数式编程应用）
    
    使用多个过滤器处理消息
    演示：map, filter, reduce等函数式编程概念
    """
    # 创建过滤器列表
    filters = [create_message_filter(filter_type) for filter_type in filter_types]
    
    def apply_all_filters(message: str) -> bool:
        """应用所有过滤器"""
        return all(filter_func(message) for filter_func in filters)
    
    # 使用filter函数过滤消息
    filtered_messages = list(filter(apply_all_filters, messages))
    
    # 使用map函数处理消息（添加时间戳）
    import time
    processed_messages = list(map(
        lambda msg: {
            'content': msg,
            'processed_at': time.time(),
            'length': len(msg)
        },
        filtered_messages
    ))
    
    return processed_messages

# 使用示例
def demo_higher_order_functions():
    """高阶函数使用演示"""
    test_messages = [
        "Hello everyone!",
        "这是一条广告消息，点击链接获取免费奖品",
        "正常的聊天消息",
        "包含脏话1的消息",
        "a" * 1001,  # 超长消息
        "另一条正常消息"
    ]
    
    # 应用多个过滤器
    result = process_messages(test_messages, 'spam', 'profanity', 'length')
    
    print("过滤后的消息:")
    for msg in result:
        print(f"- {msg['content'][:50]}... (长度: {msg['length']})")
```

## 🎨 装饰器详解

### 基础装饰器
```python
# shared/decorators.py - 项目装饰器集合
import time
import functools
from typing import Callable, Any

def timing_decorator(func: Callable) -> Callable:
    """
    计时装饰器
    
    用于测量函数执行时间，在性能优化时很有用
    """
    @functools.wraps(func)  # 保持原函数的元数据
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print(f"函数 {func.__name__} 执行时间: {end_time - start_time:.4f}秒")
        return result
    
    return wrapper

def retry_decorator(max_attempts: int = 3, delay: float = 1.0):
    """
    重试装饰器（带参数的装饰器）
    
    用于网络请求等可能失败的操作
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        print(f"函数 {func.__name__} 第{attempt + 1}次尝试失败: {e}")
                        time.sleep(delay)
                    else:
                        print(f"函数 {func.__name__} 所有尝试都失败了")
            
            raise last_exception
        
        return wrapper
    return decorator

def permission_required(required_permission: str):
    """
    权限检查装饰器
    
    Chat-Room项目中用于保护需要特定权限的操作
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, user_id: int, *args, **kwargs):
            # 检查用户权限（假设self有权限检查方法）
            if hasattr(self, 'check_user_permission'):
                if not self.check_user_permission(user_id, required_permission):
                    raise PermissionError(f"用户 {user_id} 缺少权限: {required_permission}")
            
            return func(self, user_id, *args, **kwargs)
        
        return wrapper
    return decorator
```

### Chat-Room中的装饰器应用
```python
# server/core/admin_manager.py - 管理员系统中的装饰器应用
class AdminManager:
    def __init__(self):
        self.admin_users = {0}  # 管理员用户ID集合，0是超级管理员
        self.user_permissions = {}
    
    def check_user_permission(self, user_id: int, permission: str) -> bool:
        """检查用户权限"""
        if user_id in self.admin_users:
            return True  # 管理员有所有权限
        
        user_perms = self.user_permissions.get(user_id, set())
        return permission in user_perms
    
    @permission_required('ban_user')
    @timing_decorator
    def ban_user(self, admin_id: int, target_user_id: int, reason: str = ""):
        """
        禁用用户（使用装饰器保护）
        
        装饰器应用：
        1. @permission_required: 检查管理员权限
        2. @timing_decorator: 记录操作耗时
        """
        print(f"管理员 {admin_id} 禁用用户 {target_user_id}, 原因: {reason}")
        # 实际的禁用逻辑...
        return True
    
    @permission_required('delete_message')
    @retry_decorator(max_attempts=3, delay=0.5)
    def delete_message(self, admin_id: int, message_id: str):
        """
        删除消息（带重试机制）
        
        装饰器应用：
        1. @permission_required: 权限检查
        2. @retry_decorator: 失败重试（数据库操作可能失败）
        """
        # 模拟可能失败的数据库操作
        import random
        if random.random() < 0.3:  # 30%的失败率
            raise Exception("数据库连接失败")
        
        print(f"管理员 {admin_id} 删除消息 {message_id}")
        return True

# 使用示例
def demo_decorators():
    """装饰器使用演示"""
    admin_manager = AdminManager()
    
    try:
        # 测试权限装饰器
        admin_manager.ban_user(0, 123, "违规发言")
        
        # 测试重试装饰器
        admin_manager.delete_message(0, "msg_456")
        
    except PermissionError as e:
        print(f"权限错误: {e}")
    except Exception as e:
        print(f"操作失败: {e}")
```

## 📦 模块和包管理

### Chat-Room项目的模块结构
```python
# 项目模块组织示例
"""
Chat-Room项目模块结构分析

server/
├── __init__.py              # 包初始化文件
├── main.py                  # 服务器入口
├── core/                    # 核心业务模块
│   ├── __init__.py
│   ├── server.py           # 服务器主类
│   ├── user_manager.py     # 用户管理
│   └── chat_manager.py     # 聊天管理
├── database/               # 数据库模块
│   ├── __init__.py
│   ├── models.py          # 数据模型
│   └── connection.py      # 数据库连接
└── utils/                 # 工具模块
    ├── __init__.py
    ├── auth.py           # 认证工具
    └── validation.py     # 验证工具

设计原则：
1. 单一职责：每个模块只负责一个功能领域
2. 低耦合：模块间依赖关系最小化
3. 高内聚：模块内部功能紧密相关
4. 分层架构：core -> database -> utils
"""
```

### 模块导入最佳实践
```python
# server/core/__init__.py - 包初始化文件
"""
包初始化文件的作用：
1. 标识目录为Python包
2. 控制包的导入行为
3. 提供包级别的初始化代码
4. 定义包的公共接口
"""

# 导入核心类，方便外部使用
from .server import ChatRoomServer
from .user_manager import UserManager
from .chat_manager import ChatManager

# 定义包的公共接口
__all__ = [
    'ChatRoomServer',
    'UserManager', 
    'ChatManager'
]

# 包级别的配置
PACKAGE_VERSION = "1.0.0"
DEFAULT_CONFIG = {
    'max_connections': 100,
    'timeout': 300
}

# 包初始化代码
def initialize_core_package():
    """包初始化函数"""
    print(f"Chat-Room Core Package v{PACKAGE_VERSION} 已加载")

# 自动执行初始化
initialize_core_package()
```

### 相对导入和绝对导入
```python
# server/core/chat_manager.py - 导入示例
"""
导入方式对比和最佳实践
"""

# 1. 绝对导入（推荐）
from server.database.models import DatabaseManager
from server.utils.auth import validate_username
from shared.messages import ChatMessage
from shared.constants import MessageType

# 2. 相对导入（包内使用）
from .user_manager import UserManager  # 同级模块
from ..database.models import DatabaseManager  # 上级包的模块
from ..utils.validation import sanitize_message  # 上级包的工具

# 3. 条件导入（处理可选依赖）
try:
    from textual.app import App
    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    print("警告: textual库未安装，TUI功能不可用")

class ChatManager:
    def __init__(self, user_manager: UserManager):
        """
        聊天管理器初始化
        
        导入策略：
        1. 在类初始化时导入重要依赖
        2. 延迟导入可选依赖
        3. 使用类型注解提高代码可读性
        """
        self.user_manager = user_manager
        self.db_manager = DatabaseManager()
        
        # 延迟导入（只在需要时导入）
        self._ai_manager = None
    
    @property
    def ai_manager(self):
        """延迟加载AI管理器"""
        if self._ai_manager is None:
            try:
                from server.ai.ai_manager import AIManager
                self._ai_manager = AIManager()
            except ImportError:
                print("AI功能不可用")
                self._ai_manager = None
        return self._ai_manager
```

### 动态导入和插件系统
```python
# server/plugins/plugin_manager.py - 插件系统
import importlib
import os
from typing import Dict, List, Any

class PluginManager:
    """
    插件管理器
    
    演示动态导入的应用：
    1. 运行时加载插件
    2. 插件热加载
    3. 插件依赖管理
    """
    
    def __init__(self, plugin_dir: str = "server/plugins"):
        self.plugin_dir = plugin_dir
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_configs: Dict[str, dict] = {}
    
    def discover_plugins(self) -> List[str]:
        """
        发现可用插件
        
        扫描插件目录，找到所有Python模块
        """
        plugins = []
        
        if not os.path.exists(self.plugin_dir):
            return plugins
        
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]  # 移除.py扩展名
                plugins.append(plugin_name)
        
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        动态加载插件
        
        使用importlib动态导入模块
        """
        try:
            # 构造模块路径
            module_path = f"{self.plugin_dir.replace('/', '.')}.{plugin_name}"
            
            # 动态导入模块
            plugin_module = importlib.import_module(module_path)
            
            # 检查插件接口
            if not hasattr(plugin_module, 'Plugin'):
                print(f"插件 {plugin_name} 缺少Plugin类")
                return False
            
            # 实例化插件
            plugin_instance = plugin_module.Plugin()
            
            # 检查必需方法
            required_methods = ['initialize', 'process_message', 'cleanup']
            for method in required_methods:
                if not hasattr(plugin_instance, method):
                    print(f"插件 {plugin_name} 缺少方法: {method}")
                    return False
            
            # 初始化插件
            plugin_instance.initialize()
            
            # 保存插件实例
            self.loaded_plugins[plugin_name] = plugin_instance
            
            print(f"插件 {plugin_name} 加载成功")
            return True
            
        except Exception as e:
            print(f"加载插件 {plugin_name} 失败: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        重新加载插件（热加载）
        
        用于开发时的插件更新
        """
        # 先卸载插件
        if plugin_name in self.loaded_plugins:
            try:
                self.loaded_plugins[plugin_name].cleanup()
            except:
                pass
            del self.loaded_plugins[plugin_name]
        
        # 重新导入模块
        module_path = f"{self.plugin_dir.replace('/', '.')}.{plugin_name}"
        if module_path in sys.modules:
            importlib.reload(sys.modules[module_path])
        
        # 重新加载插件
        return self.load_plugin(plugin_name)
    
    def process_message_with_plugins(self, message: str, user_id: int) -> str:
        """
        使用插件处理消息
        
        演示插件系统的实际应用
        """
        processed_message = message
        
        for plugin_name, plugin in self.loaded_plugins.items():
            try:
                processed_message = plugin.process_message(processed_message, user_id)
            except Exception as e:
                print(f"插件 {plugin_name} 处理消息失败: {e}")
        
        return processed_message

# 插件接口示例
# server/plugins/spam_filter.py
class Plugin:
    """
    垃圾消息过滤插件
    
    插件必须实现的接口：
    - initialize(): 初始化插件
    - process_message(message, user_id): 处理消息
    - cleanup(): 清理资源
    """
    
    def __init__(self):
        self.spam_keywords = ['广告', '推广', '免费']
    
    def initialize(self):
        """插件初始化"""
        print("垃圾消息过滤插件已初始化")
    
    def process_message(self, message: str, user_id: int) -> str:
        """处理消息"""
        for keyword in self.spam_keywords:
            if keyword in message:
                return f"[消息被过滤] 用户 {user_id} 的消息包含敏感词"
        return message
    
    def cleanup(self):
        """清理资源"""
        print("垃圾消息过滤插件已清理")
```

## 🎯 实践练习

### 练习1：消息处理管道
```python
def create_message_pipeline(*processors):
    """
    创建消息处理管道
    
    要求：
    1. 使用函数式编程思想
    2. 支持链式处理
    3. 错误处理和日志记录
    4. 性能监控
    """
    # TODO: 实现消息处理管道
    pass

# 使用示例
def demo_message_pipeline():
    # 创建处理管道
    pipeline = create_message_pipeline(
        spam_filter,
        profanity_filter,
        length_validator,
        emoji_converter
    )
    
    # 处理消息
    result = pipeline("Hello world! 😊")
    print(result)
```

### 练习2：配置管理模块
```python
class ConfigManager:
    """
    配置管理器
    
    要求：
    1. 支持多种配置源（文件、环境变量、命令行）
    2. 配置热重载
    3. 配置验证
    4. 默认值处理
    """
    
    def __init__(self, config_file: str = None):
        # TODO: 实现配置管理器
        pass
    
    @property
    def database_config(self):
        """数据库配置"""
        # TODO: 返回数据库配置
        pass
    
    def reload_config(self):
        """重新加载配置"""
        # TODO: 实现配置重载
        pass
```

## ✅ 学习检查

完成本章学习后，请确认您能够：

- [ ] 熟练使用函数的各种参数类型
- [ ] 理解和应用高阶函数概念
- [ ] 掌握装饰器的原理和实现
- [ ] 设计合理的模块结构
- [ ] 正确使用导入语句
- [ ] 实现动态导入和插件系统
- [ ] 完成实践练习

## 📚 下一步

函数与模块掌握后，请继续学习：
- [面向对象编程基础](oop-basics.md)
- [第2章：Socket网络编程](../02-socket-programming/tcp-basics.md)

---

**现在您已经掌握了Python函数和模块的高级用法！** 🎉
