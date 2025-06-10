"""
服务器端公共工具函数
提供统一的验证、错误处理和响应发送功能
"""

import socket
from typing import Optional, Dict, Any, Callable
from functools import wraps

from ...shared.constants import ErrorCode
from ...shared.messages import BaseMessage, ErrorMessage
from ...shared.exceptions import AuthenticationError, PermissionDeniedError


def require_login(func: Callable) -> Callable:
    """
    装饰器：要求用户登录
    自动验证用户是否已登录，如果未登录则发送错误响应
    """
    @wraps(func)
    def wrapper(self, client_socket: socket.socket, *args, **kwargs):
        # 获取用户信息
        user_info = self.user_manager.get_user_by_socket(client_socket)
        if not user_info:
            self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
            return
        
        # 将用户信息作为第一个参数传递给原函数
        return func(self, client_socket, user_info, *args, **kwargs)
    
    return wrapper


def handle_exceptions(func: Callable) -> Callable:
    """
    装饰器：统一异常处理
    捕获常见异常并发送适当的错误响应
    """
    @wraps(func)
    def wrapper(self, client_socket: socket.socket, *args, **kwargs):
        try:
            return func(self, client_socket, *args, **kwargs)
        except AuthenticationError as e:
            self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, str(e))
        except PermissionDeniedError as e:
            self.send_error(client_socket, ErrorCode.PERMISSION_DENIED, str(e))
        except Exception as e:
            print(f"{func.__name__} 处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "服务器内部错误")
    
    return wrapper


class ResponseHelper:
    """响应发送辅助类"""
    
    @staticmethod
    def send_message(client_socket: socket.socket, message: BaseMessage):
        """发送消息到客户端"""
        try:
            message_json = message.to_json() + '\n'
            client_socket.send(message_json.encode('utf-8'))
        except Exception as e:
            print(f"发送消息失败: {e}")
    
    @staticmethod
    def send_error(client_socket: socket.socket, error_code: int, error_message: str):
        """发送错误消息"""
        error_msg = ErrorMessage(error_code=error_code, error_message=error_message)
        ResponseHelper.send_message(client_socket, error_msg)
    
    @staticmethod
    def send_success_response(client_socket: socket.socket, message: str):
        """发送成功响应"""
        from ...shared.messages import SystemMessage
        response = SystemMessage(content=message)
        ResponseHelper.send_message(client_socket, response)


class ValidationHelper:
    """验证辅助类"""
    
    @staticmethod
    def validate_request_data(message: BaseMessage, required_fields: list) -> tuple[bool, str, Dict[str, Any]]:
        """
        验证请求数据
        
        Args:
            message: 请求消息对象
            required_fields: 必需字段列表
            
        Returns:
            (是否有效, 错误信息, 请求数据字典)
        """
        try:
            request_data = getattr(message, 'to_dict', lambda: {})()
            
            # 检查必需字段
            for field in required_fields:
                if field not in request_data or not request_data[field]:
                    return False, f"缺少必需字段: {field}", {}
            
            return True, "", request_data
            
        except Exception as e:
            return False, f"请求数据格式错误: {e}", {}
    
    @staticmethod
    def validate_chat_group_access(chat_manager, user_id: int, chat_group_id: int) -> tuple[bool, str]:
        """
        验证用户是否有权限访问聊天组
        
        Returns:
            (是否有权限, 错误信息)
        """
        try:
            if not chat_manager.db.is_user_in_chat_group(chat_group_id, user_id):
                return False, "您不在此聊天组中"
            return True, ""
        except Exception:
            return False, "聊天组不存在"


def log_operation(operation_name: str):
    """
    装饰器：记录操作日志
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                print(f"✅ {operation_name} 执行成功")
                return result
            except Exception as e:
                print(f"❌ {operation_name} 执行失败: {e}")
                raise
        return wrapper
    return decorator
