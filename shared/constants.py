"""
全局常量定义
包含网络参数、消息类型、错误代码等常量
注意：具体配置值从配置文件读取，这里只保留必要的默认值
"""

# 网络配置默认值（仅作备用）
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8888
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 100

# 数据库配置默认值（仅作备用）
DATABASE_PATH = "server/data/chatroom.db"
FILES_STORAGE_PATH = "server/data/files"


# 移除可能导致循环导入的函数
# 客户端配置应该直接在客户端模块中处理

# 消息类型常量
class MessageType:
    """消息类型枚举"""
    # 认证相关
    LOGIN_REQUEST = "login_request"
    LOGIN_RESPONSE = "login_response"
    REGISTER_REQUEST = "register_request"
    REGISTER_RESPONSE = "register_response"
    LOGOUT_REQUEST = "logout_request"
    
    # 聊天相关
    CHAT_MESSAGE = "chat_message"
    CHAT_HISTORY = "chat_history"
    CHAT_HISTORY_COMPLETE = "chat_history_complete"  # 历史消息加载完成通知
    USER_STATUS_UPDATE = "user_status_update"
    
    # 聊天组相关
    CREATE_CHAT_REQUEST = "create_chat_request"
    CREATE_CHAT_RESPONSE = "create_chat_response"
    JOIN_CHAT_REQUEST = "join_chat_request"
    JOIN_CHAT_RESPONSE = "join_chat_response"
    ENTER_CHAT_REQUEST = "enter_chat_request"
    ENTER_CHAT_RESPONSE = "enter_chat_response"
    
    # 信息查询相关
    USER_INFO_REQUEST = "user_info_request"
    USER_INFO_RESPONSE = "user_info_response"
    LIST_USERS_REQUEST = "list_users_request"
    LIST_USERS_RESPONSE = "list_users_response"
    LIST_CHATS_REQUEST = "list_chats_request"
    LIST_CHATS_RESPONSE = "list_chats_response"
    
    # 文件传输相关
    FILE_UPLOAD_REQUEST = "file_upload_request"
    FILE_UPLOAD_RESPONSE = "file_upload_response"
    FILE_DOWNLOAD_REQUEST = "file_download_request"
    FILE_DOWNLOAD_RESPONSE = "file_download_response"
    FILE_LIST_REQUEST = "file_list_request"
    FILE_LIST_RESPONSE = "file_list_response"
    FILE_NOTIFICATION = "file_notification"
    
    # AI相关
    AI_CHAT_REQUEST = "ai_chat_request"
    AI_CHAT_RESPONSE = "ai_chat_response"

    # 管理员相关
    ADMIN_COMMAND_REQUEST = "admin_command_request"
    ADMIN_COMMAND_RESPONSE = "admin_command_response"
    ADMIN_OPERATION_NOTIFICATION = "admin_operation_notification"

    # 系统消息
    SYSTEM_MESSAGE = "system_message"
    ERROR_MESSAGE = "error_message"
    HEARTBEAT = "heartbeat"

# 用户状态常量
class UserStatus:
    """用户状态枚举"""
    OFFLINE = 0
    ONLINE = 1

# 聊天组类型常量
class ChatType:
    """聊天组类型枚举"""
    GROUP_CHAT = 0  # 群聊
    PRIVATE_CHAT = 1  # 私聊

# 文件传输常量
FILE_CHUNK_SIZE = 8192  # 文件传输块大小（8KB）
MAX_FILE_SIZE = 100 * 1024 * 1024  # 最大文件大小（100MB）
ALLOWED_FILE_EXTENSIONS = [
    '.txt', '.doc', '.docx', '.pdf', '.jpg', '.jpeg', '.png', '.gif',
    '.mp3', '.mp4', '.avi', '.zip', '.rar', '.py', '.js', '.html', '.css', '.md'
]

# 默认聊天组
DEFAULT_PUBLIC_CHAT = "public"

# AI配置
AI_USERNAME = "AI助手"
AI_USER_ID = -1  # 特殊用户ID，表示AI用户

# 管理员配置
ADMIN_USERNAME = "管理员"
ADMIN_USER_ID = 0  # 特殊用户ID，表示管理员用户

# 命令前缀
COMMAND_PREFIX = "/"

# 时间格式
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_TIME_FORMAT = "<%a %b %d %H:%M:%S %Z %Y>"

# 错误代码
class ErrorCode:
    """错误代码枚举"""
    SUCCESS = 0
    INVALID_CREDENTIALS = 1001
    USER_ALREADY_EXISTS = 1002
    USER_NOT_FOUND = 1003
    CHAT_NOT_FOUND = 1004
    PERMISSION_DENIED = 1005
    FILE_NOT_FOUND = 1006
    FILE_TOO_LARGE = 1007
    INVALID_COMMAND = 1008
    SERVER_ERROR = 1009
    NETWORK_ERROR = 1010
