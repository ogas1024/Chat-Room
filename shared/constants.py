"""
全局常量定义
包含服务器配置、网络参数、消息类型等常量
注意：网络和数据库配置现在从配置文件读取，这里保留默认值作为备用
"""

# 默认网络配置（备用值）
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8888
BUFFER_SIZE = 4096
MAX_CONNECTIONS = 100

# 默认数据库配置（备用值）
DATABASE_PATH = "server/data/chatroom.db"
FILES_STORAGE_PATH = "server/data/files"


def get_server_constants():
    """
    从配置文件获取服务器常量
    如果配置文件不可用，返回默认值
    """
    try:
        from server.config.server_config import get_server_config
        config = get_server_config()
        return {
            'HOST': config.get_server_host(),
            'PORT': config.get_server_port(),
            'MAX_CONNECTIONS': config.get_max_connections(),
            'DATABASE_PATH': config.get_database_path(),
            'FILES_STORAGE_PATH': config.get_files_storage_path(),
            'BUFFER_SIZE': config.config_manager.get("server.buffer_size", BUFFER_SIZE)
        }
    except Exception:
        # 配置文件不可用时使用默认值
        return {
            'HOST': DEFAULT_HOST,
            'PORT': DEFAULT_PORT,
            'MAX_CONNECTIONS': MAX_CONNECTIONS,
            'DATABASE_PATH': DATABASE_PATH,
            'FILES_STORAGE_PATH': FILES_STORAGE_PATH,
            'BUFFER_SIZE': BUFFER_SIZE
        }


def get_client_constants():
    """
    从配置文件获取客户端常量
    如果配置文件不可用，返回默认值
    """
    try:
        from client.config.client_config import get_client_config
        config = get_client_config()
        return {
            'DEFAULT_HOST': config.get_default_host(),
            'DEFAULT_PORT': config.get_default_port(),
            'CONNECTION_TIMEOUT': config.get_connection_timeout(),
            'BUFFER_SIZE': config.config_manager.get("performance.buffer_size", BUFFER_SIZE)
        }
    except Exception:
        # 配置文件不可用时使用默认值
        return {
            'DEFAULT_HOST': DEFAULT_HOST,
            'DEFAULT_PORT': DEFAULT_PORT,
            'CONNECTION_TIMEOUT': 10,
            'BUFFER_SIZE': BUFFER_SIZE
        }

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
FILE_CHUNK_SIZE = 8192  # 文件传输块大小
MAX_FILE_SIZE = 100 * 1024 * 1024  # 最大文件大小 100MB
ALLOWED_FILE_EXTENSIONS = [
    '.txt', '.doc', '.docx', '.pdf', '.jpg', '.jpeg', '.png', '.gif',
    '.mp3', '.mp4', '.avi', '.zip', '.rar', '.py', '.js', '.html', '.css'
]

# 默认聊天组
DEFAULT_PUBLIC_CHAT = "public"

# AI配置
AI_USERNAME = "AI助手"
AI_USER_ID = -1  # 特殊用户ID，表示AI用户

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
