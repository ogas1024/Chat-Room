"""
消息协议模块
定义消息类型和协议处理函数
"""

import json
from typing import Dict, Any, Union
from enum import Enum

from .messages import (
    BaseMessage, LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    ChatMessage, SystemMessage, ErrorMessage, UserInfoResponse, ListUsersResponse,
    ListChatsResponse, CreateChatRequest, CreateChatResponse, JoinChatRequest,
    JoinChatResponse, EnterChatRequest, EnterChatResponse, FileListRequest,
    FileListResponse, FileUploadRequest, FileUploadResponse, FileDownloadRequest,
    FileDownloadResponse
)


class MessageType(Enum):
    """消息类型枚举"""
    # 认证相关
    LOGIN_REQUEST = "login_request"
    LOGIN_RESPONSE = "login_response"
    REGISTER_REQUEST = "register_request"
    REGISTER_RESPONSE = "register_response"
    LOGOUT_REQUEST = "logout_request"
    
    # 聊天相关
    CHAT_MESSAGE = "chat_message"
    SYSTEM_MESSAGE = "system_message"
    ERROR_MESSAGE = "error_message"
    
    # 用户信息相关
    USER_INFO_REQUEST = "user_info_request"
    USER_INFO_RESPONSE = "user_info_response"
    LIST_USERS_REQUEST = "list_users_request"
    LIST_USERS_RESPONSE = "list_users_response"
    
    # 聊天组相关
    LIST_CHATS_REQUEST = "list_chats_request"
    LIST_CHATS_RESPONSE = "list_chats_response"
    CREATE_CHAT_REQUEST = "create_chat_request"
    CREATE_CHAT_RESPONSE = "create_chat_response"
    JOIN_CHAT_REQUEST = "join_chat_request"
    JOIN_CHAT_RESPONSE = "join_chat_response"
    ENTER_CHAT_REQUEST = "enter_chat_request"
    ENTER_CHAT_RESPONSE = "enter_chat_response"
    
    # 文件传输相关
    FILE_LIST_REQUEST = "file_list_request"
    FILE_LIST_RESPONSE = "file_list_response"
    FILE_UPLOAD_REQUEST = "file_upload_request"
    FILE_UPLOAD_RESPONSE = "file_upload_response"
    FILE_DOWNLOAD_REQUEST = "file_download_request"
    FILE_DOWNLOAD_RESPONSE = "file_download_response"
    
    # AI相关
    AI_CHAT_REQUEST = "ai_chat_request"
    AI_CHAT_RESPONSE = "ai_chat_response"


def create_message(message_type: MessageType, data: Dict[str, Any]) -> str:
    """
    创建消息
    
    Args:
        message_type: 消息类型
        data: 消息数据
        
    Returns:
        JSON格式的消息字符串
    """
    message = {
        "type": message_type.value,
        "data": data
    }
    return json.dumps(message, ensure_ascii=False)


def parse_message(message_str: str) -> Dict[str, Any]:
    """
    解析消息
    
    Args:
        message_str: JSON格式的消息字符串
        
    Returns:
        解析后的消息字典
    """
    try:
        message = json.loads(message_str)
        return {
            "type": message.get("type"),
            "data": message.get("data", {})
        }
    except json.JSONDecodeError:
        return {
            "type": "error",
            "data": {"error": "Invalid JSON format"}
        }


def create_login_request(username: str, password: str) -> str:
    """创建登录请求"""
    return create_message(MessageType.LOGIN_REQUEST, {
        "username": username,
        "password": password
    })


def create_register_request(username: str, password: str) -> str:
    """创建注册请求"""
    return create_message(MessageType.REGISTER_REQUEST, {
        "username": username,
        "password": password
    })


def create_chat_message(content: str, chat_group_id: int = None) -> str:
    """创建聊天消息"""
    return create_message(MessageType.CHAT_MESSAGE, {
        "content": content,
        "chat_group_id": chat_group_id
    })


def create_user_info_request() -> str:
    """创建用户信息请求"""
    return create_message(MessageType.USER_INFO_REQUEST, {})


def create_list_users_request() -> str:
    """创建用户列表请求"""
    return create_message(MessageType.LIST_USERS_REQUEST, {})


def create_list_chats_request(list_type: str = "user_chats") -> str:
    """创建聊天组列表请求"""
    return create_message(MessageType.LIST_CHATS_REQUEST, {
        "list_type": list_type
    })


def create_create_chat_request(chat_name: str, member_usernames: list = None) -> str:
    """创建创建聊天组请求"""
    return create_message(MessageType.CREATE_CHAT_REQUEST, {
        "chat_name": chat_name,
        "member_usernames": member_usernames or []
    })


def create_join_chat_request(chat_name: str) -> str:
    """创建加入聊天组请求"""
    return create_message(MessageType.JOIN_CHAT_REQUEST, {
        "chat_name": chat_name
    })


def create_enter_chat_request(chat_name: str) -> str:
    """创建进入聊天组请求"""
    return create_message(MessageType.ENTER_CHAT_REQUEST, {
        "chat_name": chat_name
    })


def create_file_list_request(chat_group_id: int = None) -> str:
    """创建文件列表请求"""
    return create_message(MessageType.FILE_LIST_REQUEST, {
        "chat_group_id": chat_group_id
    })


def create_file_upload_request(filename: str, file_data: str, chat_group_id: int = None) -> str:
    """创建文件上传请求"""
    return create_message(MessageType.FILE_UPLOAD_REQUEST, {
        "filename": filename,
        "file_data": file_data,
        "chat_group_id": chat_group_id
    })


def create_file_download_request(file_id: str) -> str:
    """创建文件下载请求"""
    return create_message(MessageType.FILE_DOWNLOAD_REQUEST, {
        "file_id": file_id
    })


def create_error_message(error_code: int, error_message: str) -> str:
    """创建错误消息"""
    return create_message(MessageType.ERROR_MESSAGE, {
        "error_code": error_code,
        "error_message": error_message
    })


def create_system_message(content: str) -> str:
    """创建系统消息"""
    return create_message(MessageType.SYSTEM_MESSAGE, {
        "content": content
    })


# 消息类型映射
MESSAGE_TYPE_MAP = {
    MessageType.LOGIN_REQUEST.value: LoginRequest,
    MessageType.LOGIN_RESPONSE.value: LoginResponse,
    MessageType.REGISTER_REQUEST.value: RegisterRequest,
    MessageType.REGISTER_RESPONSE.value: RegisterResponse,
    MessageType.CHAT_MESSAGE.value: ChatMessage,
    MessageType.SYSTEM_MESSAGE.value: SystemMessage,
    MessageType.ERROR_MESSAGE.value: ErrorMessage,
    MessageType.USER_INFO_RESPONSE.value: UserInfoResponse,
    MessageType.LIST_USERS_RESPONSE.value: ListUsersResponse,
    MessageType.LIST_CHATS_RESPONSE.value: ListChatsResponse,
}


def message_from_dict(message_type: str, data: Dict[str, Any]) -> Union[BaseMessage, None]:
    """
    从字典创建消息对象
    
    Args:
        message_type: 消息类型
        data: 消息数据
        
    Returns:
        消息对象或None
    """
    message_class = MESSAGE_TYPE_MAP.get(message_type)
    if message_class:
        try:
            return message_class(**data)
        except Exception:
            return None
    return None
