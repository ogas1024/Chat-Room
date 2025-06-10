"""
认证工具模块
提供密码验证、用户权限检查等认证相关功能
"""

import re
from typing import Optional


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    验证用户名格式
    
    Args:
        username: 用户名
        
    Returns:
        (是否有效, 错误信息)
    """
    if not username:
        return False, "用户名不能为空"
    
    if len(username) < 3:
        return False, "用户名长度不能少于3个字符"
    
    if len(username) > 20:
        return False, "用户名长度不能超过20个字符"
    
    # 只允许字母、数字、下划线、中文
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
        return False, "用户名只能包含字母、数字、下划线和中文字符"
    
    # 不能以数字开头
    if username[0].isdigit():
        return False, "用户名不能以数字开头"
    
    return True, None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    验证密码格式
    
    Args:
        password: 密码
        
    Returns:
        (是否有效, 错误信息)
    """
    if not password:
        return False, "密码不能为空"
    
    if len(password) < 6:
        return False, "密码长度不能少于6个字符"
    
    if len(password) > 50:
        return False, "密码长度不能超过50个字符"
    
    # 检查是否包含至少一个字母和一个数字
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_letter and has_digit):
        return False, "密码必须包含至少一个字母和一个数字"
    
    return True, None


def validate_chat_group_name(name: str) -> tuple[bool, Optional[str]]:
    """
    验证聊天组名称格式
    
    Args:
        name: 聊天组名称
        
    Returns:
        (是否有效, 错误信息)
    """
    if not name:
        return False, "聊天组名称不能为空"
    
    if len(name) < 2:
        return False, "聊天组名称长度不能少于2个字符"
    
    if len(name) > 30:
        return False, "聊天组名称长度不能超过30个字符"
    
    # 只允许字母、数字、下划线、中文、空格
    if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5\s]+$', name):
        return False, "聊天组名称只能包含字母、数字、下划线、中文字符和空格"
    
    # 去除首尾空格后检查
    name = name.strip()
    if not name:
        return False, "聊天组名称不能只包含空格"
    
    return True, None


def sanitize_message_content(content: str) -> str:
    """
    清理消息内容，移除危险字符
    
    Args:
        content: 原始消息内容
        
    Returns:
        清理后的消息内容
    """
    if not content:
        return ""
    
    # 移除控制字符（除了换行符和制表符）
    content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\t')
    
    # 限制消息长度
    max_length = 1000
    if len(content) > max_length:
        content = content[:max_length] + "..."
    
    return content.strip()


def validate_file_name(filename: str) -> tuple[bool, Optional[str]]:
    """
    验证文件名格式
    
    Args:
        filename: 文件名
        
    Returns:
        (是否有效, 错误信息)
    """
    if not filename:
        return False, "文件名不能为空"
    
    if len(filename) > 255:
        return False, "文件名长度不能超过255个字符"
    
    # 检查是否包含非法字符
    illegal_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in illegal_chars:
        if char in filename:
            return False, f"文件名不能包含字符: {char}"
    
    # 检查是否为保留名称
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    name_without_ext = filename.split('.')[0].upper()
    if name_without_ext in reserved_names:
        return False, f"文件名不能使用保留名称: {name_without_ext}"
    
    return True, None


def is_safe_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    检查文件扩展名是否安全
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表
        
    Returns:
        是否为安全的文件扩展名
    """
    if not filename or '.' not in filename:
        return False
    
    extension = '.' + filename.split('.')[-1].lower()
    return extension in [ext.lower() for ext in allowed_extensions]


def generate_safe_filename(original_filename: str, user_id: int, timestamp: str) -> str:
    """
    生成安全的服务器端文件名
    
    Args:
        original_filename: 原始文件名
        user_id: 用户ID
        timestamp: 时间戳
        
    Returns:
        安全的文件名
    """
    # 获取文件扩展名
    if '.' in original_filename:
        name, ext = original_filename.rsplit('.', 1)
        ext = '.' + ext.lower()
    else:
        name = original_filename
        ext = ''
    
    # 清理文件名
    safe_name = re.sub(r'[^\w\-_\u4e00-\u9fa5]', '_', name)
    safe_name = safe_name[:50]  # 限制长度
    
    # 生成唯一文件名
    safe_filename = f"{user_id}_{timestamp}_{safe_name}{ext}"
    
    return safe_filename
