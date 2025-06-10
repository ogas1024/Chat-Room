"""
自定义异常类定义
定义项目中使用的各种异常类型
"""


class ChatRoomException(Exception):
    """聊天室基础异常类"""
    def __init__(self, message: str, error_code: int = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class AuthenticationError(ChatRoomException):
    """认证相关异常"""
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, error_code=1001)


class UserAlreadyExistsError(ChatRoomException):
    """用户已存在异常"""
    def __init__(self, username: str):
        message = f"用户名 '{username}' 已存在"
        super().__init__(message, error_code=1002)


class UserNotFoundError(ChatRoomException):
    """用户不存在异常"""
    def __init__(self, username: str = None, user_id: int = None):
        if username:
            message = f"用户 '{username}' 不存在"
        elif user_id:
            message = f"用户ID '{user_id}' 不存在"
        else:
            message = "用户不存在"
        super().__init__(message, error_code=1003)


class ChatGroupNotFoundError(ChatRoomException):
    """聊天组不存在异常"""
    def __init__(self, chat_name: str = None, chat_id: int = None):
        if chat_name:
            message = f"聊天组 '{chat_name}' 不存在"
        elif chat_id:
            message = f"聊天组ID '{chat_id}' 不存在"
        else:
            message = "聊天组不存在"
        super().__init__(message, error_code=1004)


class PermissionDeniedError(ChatRoomException):
    """权限不足异常"""
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, error_code=1005)


class FileNotFoundError(ChatRoomException):
    """文件不存在异常"""
    def __init__(self, filename: str = None):
        if filename:
            message = f"文件 '{filename}' 不存在"
        else:
            message = "文件不存在"
        super().__init__(message, error_code=1006)


class FileTooLargeError(ChatRoomException):
    """文件过大异常"""
    def __init__(self, filename: str, max_size: int):
        message = f"文件 '{filename}' 超过最大大小限制 {max_size} 字节"
        super().__init__(message, error_code=1007)


class InvalidCommandError(ChatRoomException):
    """无效命令异常"""
    def __init__(self, command: str):
        message = f"无效的命令: '{command}'"
        super().__init__(message, error_code=1008)


class ServerError(ChatRoomException):
    """服务器内部错误"""
    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(message, error_code=1009)


class NetworkError(ChatRoomException):
    """网络连接错误"""
    def __init__(self, message: str = "网络连接错误"):
        super().__init__(message, error_code=1010)


class DatabaseError(ChatRoomException):
    """数据库操作错误"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, error_code=1011)


class AIServiceError(ChatRoomException):
    """AI服务错误"""
    def __init__(self, message: str = "AI服务调用失败"):
        super().__init__(message, error_code=1012)


def get_error_message(error_code: int) -> str:
    """根据错误代码获取错误消息"""
    error_messages = {
        1001: "认证失败",
        1002: "用户已存在",
        1003: "用户不存在",
        1004: "聊天组不存在",
        1005: "权限不足",
        1006: "文件不存在",
        1007: "文件过大",
        1008: "无效命令",
        1009: "服务器内部错误",
        1010: "网络连接错误",
        1011: "数据库操作失败",
        1012: "AI服务调用失败",
    }
    return error_messages.get(error_code, "未知错误")
