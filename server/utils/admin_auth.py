"""
管理员权限控制模块
提供管理员权限验证和禁言状态检查功能
"""

import socket
from functools import wraps
from typing import Callable, Dict, Any

from shared.constants import ADMIN_USER_ID, ErrorCode
from shared.logger import get_logger, log_security_event


logger = get_logger(__name__)


def require_admin(func: Callable) -> Callable:
    """
    装饰器：要求管理员权限
    自动验证用户是否为管理员，如果不是则发送错误响应
    """
    @wraps(func)
    def wrapper(self, client_socket: socket.socket, *args, **kwargs):
        # 获取用户信息
        user_info = self.user_manager.get_user_by_socket(client_socket)
        if not user_info:
            self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
            return
        
        # 检查管理员权限
        if user_info['user_id'] != ADMIN_USER_ID:
            self.send_error(client_socket, ErrorCode.PERMISSION_DENIED, "权限不足：需要管理员权限")
            
            # 记录安全事件
            log_security_event(
                "unauthorized_admin_access",
                user_id=user_info['user_id'],
                username=user_info['username'],
                client_ip=client_socket.getpeername()[0] if client_socket else "unknown"
            )
            return
        
        # 将用户信息作为第一个参数传递给原函数
        return func(self, client_socket, user_info, *args, **kwargs)
    
    return wrapper


def check_user_ban_status(db_manager, user_id: int) -> tuple[bool, str]:
    """
    检查用户是否被禁言
    
    Args:
        db_manager: 数据库管理器
        user_id: 用户ID
        
    Returns:
        (是否被禁言, 错误信息)
    """
    try:
        if db_manager.is_user_banned(user_id):
            return True, "您已被禁言，无法发送消息"
        return False, ""
    except Exception as e:
        logger.error(f"检查用户禁言状态失败: {e}")
        return False, ""


def check_chat_group_ban_status(db_manager, group_id: int) -> tuple[bool, str]:
    """
    检查聊天组是否被禁言
    
    Args:
        db_manager: 数据库管理器
        group_id: 聊天组ID
        
    Returns:
        (是否被禁言, 错误信息)
    """
    try:
        if db_manager.is_chat_group_banned(group_id):
            return True, "该聊天组已被禁言，无法发送消息"
        return False, ""
    except Exception as e:
        logger.error(f"检查聊天组禁言状态失败: {e}")
        return False, ""


def validate_admin_command(command: str, action: str) -> tuple[bool, str]:
    """
    验证管理员命令格式（新架构）

    Args:
        command: 操作类型 (add, del, modify, ban, free)
        action: 对象类型 (-u, -g, -f, -l)

    Returns:
        (是否有效, 错误信息)
    """
    valid_commands = {
        "add": ["-u"],  # 新增用户
        "del": ["-u", "-g", "-f"],  # 删除用户, 删除群组, 删除文件
        "modify": ["-u", "-g"],  # 修改用户信息, 修改群组信息
        "ban": ["-u", "-g"],  # 禁言用户, 禁言群组
        "free": ["-u", "-g", "-l"]  # 解除用户禁言, 解除群组禁言, 列出被禁言对象
    }

    if command not in valid_commands:
        return False, f"无效的操作类型: {command}。支持的操作: {', '.join(valid_commands.keys())}"

    if action not in valid_commands[command]:
        return False, f"操作 {command} 不支持对象类型 {action}。支持的对象类型: {', '.join(valid_commands[command])}"

    return True, ""


def parse_admin_command(command_str: str) -> tuple[str, str, list]:
    """
    解析管理员命令字符串（新架构）

    Args:
        command_str: 命令字符串，如 "/del -u 123" 或 "/ban -u username"

    Returns:
        (操作类型, 对象类型, 参数列表)
    """
    parts = command_str.strip().split()

    if len(parts) < 2:
        return "", "", []

    # 移除命令前缀 "/"
    operation = parts[0].lstrip("/")
    object_type = parts[1]
    args = parts[2:] if len(parts) > 2 else []

    return operation, object_type, args


def is_admin_user(user_id: int) -> bool:
    """
    检查用户是否为管理员
    
    Args:
        user_id: 用户ID
        
    Returns:
        是否为管理员
    """
    return user_id == ADMIN_USER_ID


def log_admin_operation(operation: str, operator_id: int, operator_name: str, 
                       target_type: str, target_id: int, target_name: str, 
                       success: bool, error_message: str = ""):
    """
    记录管理员操作日志
    
    Args:
        operation: 操作类型
        operator_id: 操作者ID
        operator_name: 操作者用户名
        target_type: 目标类型 (user/group)
        target_id: 目标ID
        target_name: 目标名称
        success: 操作是否成功
        error_message: 错误信息（如果失败）
    """
    log_data = {
        "operation": operation,
        "operator_id": operator_id,
        "operator_name": operator_name,
        "target_type": target_type,
        "target_id": target_id,
        "target_name": target_name,
        "success": success
    }
    
    if not success and error_message:
        log_data["error_message"] = error_message
    
    if success:
        logger.info(f"管理员操作成功: {operation}", **log_data)
    else:
        logger.warning(f"管理员操作失败: {operation}", **log_data)
    
    # 记录安全事件
    log_security_event(
        f"admin_operation_{operation}",
        **log_data
    )


class AdminPermissionChecker:
    """管理员权限检查器"""
    
    def __init__(self, db_manager):
        """
        初始化权限检查器
        
        Args:
            db_manager: 数据库管理器
        """
        self.db = db_manager
    
    def can_send_message(self, user_id: int, group_id: int) -> tuple[bool, str]:
        """
        检查用户是否可以在指定聊天组发送消息
        
        Args:
            user_id: 用户ID
            group_id: 聊天组ID
            
        Returns:
            (是否可以发送, 错误信息)
        """
        # 管理员不受禁言限制
        if is_admin_user(user_id):
            return True, ""
        
        # 检查用户是否被禁言
        user_banned, user_error = check_user_ban_status(self.db, user_id)
        if user_banned:
            return False, user_error
        
        # 检查聊天组是否被禁言
        group_banned, group_error = check_chat_group_ban_status(self.db, group_id)
        if group_banned:
            return False, group_error
        
        return True, ""
    
    def can_perform_admin_operation(self, user_id: int, operation: str) -> tuple[bool, str]:
        """
        检查用户是否可以执行管理员操作
        
        Args:
            user_id: 用户ID
            operation: 操作类型
            
        Returns:
            (是否可以执行, 错误信息)
        """
        if not is_admin_user(user_id):
            return False, "权限不足：需要管理员权限"
        
        return True, ""
