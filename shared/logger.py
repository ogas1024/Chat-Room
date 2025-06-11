"""
Chat-Room 统一日志系统
提供结构化日志记录、敏感信息脱敏、日志轮转等功能
"""

import os
import json
import re
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from loguru import logger
from functools import wraps

# 敏感信息脱敏模式
SENSITIVE_PATTERNS = {
    'password': re.compile(r'("password"\s*:\s*")[^"]*(")', re.IGNORECASE),
    'api_key': re.compile(r'("api_key"\s*:\s*")[^"]*(")', re.IGNORECASE),
    'token': re.compile(r'("token"\s*:\s*")[^"]*(")', re.IGNORECASE),
    'secret': re.compile(r'("secret"\s*:\s*")[^"]*(")', re.IGNORECASE),
    'auth': re.compile(r'("auth"\s*:\s*")[^"]*(")', re.IGNORECASE),
}


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self.loggers = {}
        self.initialized = False
        
    def initialize(self, config: Dict[str, Any], component: str = "server"):
        """
        初始化日志系统
        
        Args:
            config: 日志配置
            component: 组件名称 (server/client)
        """
        if self.initialized:
            return
            
        # 移除默认的logger配置
        logger.remove()
        
        # 创建日志目录
        log_dir = Path("logs") / component
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取配置
        level = config.get('level', 'INFO')
        file_enabled = config.get('file_enabled', True)
        console_enabled = config.get('console_enabled', True)
        file_max_size = config.get('file_max_size', 10485760)  # 10MB
        file_backup_count = config.get('file_backup_count', 5)
        
        # 配置控制台日志
        if console_enabled:
            logger.add(
                sys.stdout,
                level=level,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                       "<level>{message}</level>",
                colorize=True,
                filter=self._console_filter
            )
        
        # 配置文件日志 - 主日志
        if file_enabled:
            main_log_file = log_dir / f"{component}.log"
            logger.add(
                str(main_log_file),
                level=level,
                format="{message}",
                rotation=file_max_size,
                retention=file_backup_count,
                compression="gz",
                serialize=True,  # 使用loguru内置的JSON序列化
                enqueue=True
            )

            # 错误日志单独记录
            error_log_file = log_dir / f"{component}_error.log"
            logger.add(
                str(error_log_file),
                level="ERROR",
                format="{message}",
                rotation=file_max_size,
                retention=file_backup_count,
                compression="gz",
                serialize=True,
                enqueue=True
            )

            # 数据库操作日志
            db_log_file = log_dir / f"{component}_database.log"
            logger.add(
                str(db_log_file),
                level="DEBUG",
                format="{message}",
                rotation=file_max_size,
                retention=file_backup_count,
                compression="gz",
                serialize=True,
                enqueue=True,
                filter=lambda record: "database" in record["extra"]
            )

            # AI功能日志
            ai_log_file = log_dir / f"{component}_ai.log"
            logger.add(
                str(ai_log_file),
                level="DEBUG",
                format="{message}",
                rotation=file_max_size,
                retention=file_backup_count,
                compression="gz",
                serialize=True,
                enqueue=True,
                filter=lambda record: "ai" in record["extra"]
            )

            # 安全相关日志
            security_log_file = log_dir / f"{component}_security.log"
            logger.add(
                str(security_log_file),
                level="INFO",
                format="{message}",
                rotation=file_max_size,
                retention=file_backup_count,
                compression="gz",
                serialize=True,
                enqueue=True,
                filter=lambda record: "security" in record["extra"]
            )
        
        self.initialized = True
        logger.info("日志系统初始化完成", component=component)
    
    def _console_filter(self, record):
        """控制台日志过滤器 - 简化输出"""
        # 过滤掉过于详细的调试信息
        if record["level"].name == "DEBUG":
            return False
        return True
    
    def _json_formatter(self, record):
        """JSON格式化器"""
        # 基础日志信息
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
        }

        # 添加额外信息
        if record["extra"]:
            # 过滤掉一些内部字段
            filtered_extra = {k: v for k, v in record["extra"].items()
                            if k not in ['name']}  # name字段已经在module中了
            log_entry.update(filtered_extra)

        # 添加异常信息
        if record["exception"]:
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback.format()
            }

        # 脱敏处理
        try:
            log_json = json.dumps(log_entry, ensure_ascii=False, default=str)
            log_json = self._sanitize_sensitive_data(log_json)
            return log_json
        except Exception as e:
            # 如果JSON序列化失败，返回简单格式
            return json.dumps({
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "message": str(record["message"]),
                "error": f"JSON formatting error: {str(e)}"
            })
    
    def _sanitize_sensitive_data(self, log_text: str) -> str:
        """脱敏处理敏感信息"""
        for pattern_name, pattern in SENSITIVE_PATTERNS.items():
            log_text = pattern.sub(r'\1***\2', log_text)
        return log_text
    
    def get_logger(self, name: str):
        """获取指定名称的logger"""
        return logger.bind(name=name)


# 全局日志管理器实例
log_manager = LoggerManager()


def init_logger(config: Dict[str, Any], component: str = "server"):
    """初始化日志系统"""
    log_manager.initialize(config, component)


def get_logger(name: str = None):
    """获取logger实例"""
    if name:
        return logger.bind(name=name)
    return logger


def log_event(event_type: str, **kwargs):
    """记录事件日志"""
    logger.info(f"事件: {event_type}", event=event_type, **kwargs)


def log_database_operation(operation: str, table: str, **kwargs):
    """记录数据库操作日志"""
    logger.debug(
        f"数据库操作: {operation} - {table}",
        database=True,
        operation=operation,
        table=table,
        **kwargs
    )


def log_ai_operation(operation: str, model: str, **kwargs):
    """记录AI操作日志"""
    logger.info(
        f"AI操作: {operation} - {model}",
        ai=True,
        operation=operation,
        model=model,
        **kwargs
    )


def log_security_event(event: str, **kwargs):
    """记录安全事件日志"""
    logger.warning(
        f"安全事件: {event}",
        security=True,
        event=event,
        **kwargs
    )


def log_performance(operation: str, duration: float, **kwargs):
    """记录性能日志"""
    logger.info(
        f"性能: {operation} 耗时 {duration:.3f}s",
        performance=True,
        operation=operation,
        duration=duration,
        **kwargs
    )


def log_user_action(user_id: int, username: str, action: str, **kwargs):
    """记录用户操作日志"""
    logger.info(
        f"用户操作: {username}({user_id}) - {action}",
        user_id=user_id,
        username=username,
        action=action,
        **kwargs
    )


def log_network_event(event: str, client_ip: str = None, **kwargs):
    """记录网络事件日志"""
    logger.info(
        f"网络事件: {event}",
        network=True,
        event=event,
        client_ip=client_ip,
        **kwargs
    )


def log_file_operation(operation: str, filename: str, **kwargs):
    """记录文件操作日志"""
    logger.info(
        f"文件操作: {operation} - {filename}",
        file=True,
        operation=operation,
        filename=filename,
        **kwargs
    )


# 装饰器：自动记录函数调用日志
def log_function_call(event_type: str = None, log_args: bool = False, log_result: bool = False):
    """
    装饰器：自动记录函数调用日志
    
    Args:
        event_type: 事件类型，默认使用函数名
        log_args: 是否记录函数参数
        log_result: 是否记录函数返回值
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            event = event_type or func_name
            
            # 记录函数开始
            log_data = {"function": func_name}
            if log_args:
                log_data["args"] = str(args)
                log_data["kwargs"] = str(kwargs)
            
            logger.debug(f"函数调用开始: {func_name}", **log_data)
            
            try:
                # 执行函数
                start_time = datetime.now()
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # 记录成功日志
                success_data = {
                    "function": func_name,
                    "duration": duration,
                    "status": "success"
                }
                if log_result:
                    success_data["result"] = str(result)
                
                logger.debug(f"函数调用成功: {func_name}", **success_data)
                return result
                
            except Exception as e:
                # 记录错误日志
                logger.error(
                    f"函数调用失败: {func_name} - {str(e)}",
                    function=func_name,
                    error=str(e),
                    status="error",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


# 装饰器：记录性能日志
def log_performance_decorator(operation_name: str = None):
    """
    装饰器：记录性能日志
    
    Args:
        operation_name: 操作名称，默认使用函数名
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation = operation_name or func.__name__
            start_time = datetime.now()
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                log_performance(operation, duration)
                return result
                
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                logger.error(
                    f"性能监控: {operation} 执行失败，耗时 {duration:.3f}s - {str(e)}",
                    performance=True,
                    operation=operation,
                    duration=duration,
                    error=str(e),
                    status="error"
                )
                raise
        
        return wrapper
    return decorator
