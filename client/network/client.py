"""
网络客户端模块
处理与服务器的连接、消息发送和接收
"""

import socket
import threading
import time
from typing import Callable, Optional, Dict, Any, List

from ...shared.constants import DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE
from ...shared.messages import BaseMessage, parse_message


class NetworkClient:
    """网络客户端"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化网络客户端"""
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False
        
        # 消息处理回调函数
        self.message_handlers: Dict[str, Callable] = {}
        self.default_message_handler: Optional[Callable] = None
        
        # 接收线程
        self.receive_thread: Optional[threading.Thread] = None
    
    def connect(self) -> bool:
        """连接到服务器"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 设置连接超时
            self.socket.connect((self.host, self.port))
            
            self.connected = True
            self.running = True
            
            # 启动接收线程
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            return True
            
        except socket.error as e:
            print(f"连接服务器失败: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
    
    def send_message(self, message: BaseMessage) -> bool:
        """发送消息到服务器"""
        if not self.connected or not self.socket:
            return False
        
        try:
            message_json = message.to_json() + '\n'
            self.socket.send(message_json.encode('utf-8'))
            return True
        except socket.error as e:
            print(f"发送消息失败: {e}")
            self.connected = False
            return False
    
    def _receive_messages(self):
        """接收消息的线程函数"""
        buffer = ""
        
        while self.running and self.connected:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                # 解码数据
                buffer += data.decode('utf-8')
                
                # 处理完整的消息（以换行符分隔）
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self._handle_received_message(line.strip())
                        
            except socket.timeout:
                continue
            except socket.error as e:
                if self.running:
                    print(f"接收消息时出错: {e}")
                break
            except UnicodeDecodeError as e:
                print(f"消息解码错误: {e}")
                continue
        
        self.connected = False
    
    def _handle_received_message(self, message_str: str):
        """处理接收到的消息"""
        try:
            # 解析消息
            message = parse_message(message_str)
            
            # 根据消息类型调用对应的处理器
            message_type = message.message_type
            if message_type in self.message_handlers:
                self.message_handlers[message_type](message)
            elif self.default_message_handler:
                self.default_message_handler(message)
            else:
                print(f"未处理的消息类型: {message_type}")
                
        except Exception as e:
            print(f"处理接收消息时出错: {e}")
    
    def set_message_handler(self, message_type: str, handler: Callable):
        """设置特定消息类型的处理器"""
        self.message_handlers[message_type] = handler
    
    def set_default_message_handler(self, handler: Callable):
        """设置默认消息处理器"""
        self.default_message_handler = handler
    
    def remove_message_handler(self, message_type: str):
        """移除消息处理器"""
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.connected and self.socket is not None
    
    def wait_for_response(self, timeout: float = 5.0, message_types: list = None) -> Optional[BaseMessage]:
        """等待服务器响应（阻塞式）"""
        if not self.connected:
            return None

        start_time = time.time()
        response = None

        def response_handler(message):
            nonlocal response
            # 如果指定了消息类型，只接受这些类型的消息
            if message_types is None or message.message_type in message_types:
                response = message

        # 保存原有的处理器
        old_handlers = {}
        old_default_handler = self.default_message_handler

        # 如果指定了消息类型，临时替换这些类型的处理器
        if message_types:
            for msg_type in message_types:
                if msg_type in self.message_handlers:
                    old_handlers[msg_type] = self.message_handlers[msg_type]
                self.message_handlers[msg_type] = response_handler
        else:
            # 否则替换默认处理器
            self.default_message_handler = response_handler

        try:
            # 等待响应
            while time.time() - start_time < timeout and response is None:
                time.sleep(0.1)

            return response

        finally:
            # 恢复原来的处理器
            if message_types:
                for msg_type in message_types:
                    if msg_type in old_handlers:
                        self.message_handlers[msg_type] = old_handlers[msg_type]
                    else:
                        self.message_handlers.pop(msg_type, None)
            else:
                self.default_message_handler = old_default_handler


class ChatClient:
    """聊天客户端（高级封装）"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化聊天客户端"""
        self.network_client = NetworkClient(host, port)
        self.current_user: Optional[Dict[str, Any]] = None
        self.current_chat_group: Optional[Dict[str, Any]] = None
        
        # 设置消息处理器
        self._setup_message_handlers()
    
    def _setup_message_handlers(self):
        """设置消息处理器"""
        from ...shared.constants import MessageType
        
        # 设置各种消息类型的处理器
        self.network_client.set_message_handler(
            MessageType.LOGIN_RESPONSE, self._handle_login_response
        )
        self.network_client.set_message_handler(
            MessageType.REGISTER_RESPONSE, self._handle_register_response
        )
        self.network_client.set_message_handler(
            MessageType.CHAT_MESSAGE, self._handle_chat_message
        )
        self.network_client.set_message_handler(
            MessageType.ERROR_MESSAGE, self._handle_error_message
        )
        self.network_client.set_message_handler(
            MessageType.SYSTEM_MESSAGE, self._handle_system_message
        )
    
    def connect(self) -> bool:
        """连接到服务器"""
        return self.network_client.connect()
    
    def disconnect(self):
        """断开连接"""
        self.network_client.disconnect()
        self.current_user = None
        self.current_chat_group = None
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """用户登录"""
        from ...shared.messages import LoginRequest
        from ...shared.constants import MessageType

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送登录请求
        login_request = LoginRequest(username=username, password=password)
        if not self.network_client.send_message(login_request):
            return False, "发送登录请求失败"

        # 等待登录响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.LOGIN_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if hasattr(response, 'success') and response.success:
                self.current_user = {
                    'id': response.user_id,
                    'username': response.username
                }
                return True, "登录成功"
            elif hasattr(response, 'error_message'):
                return False, response.error_message
            elif hasattr(response, 'success'):
                return False, response.error_message or "登录失败"

        return False, "服务器无响应"
    
    def register(self, username: str, password: str) -> tuple[bool, str]:
        """用户注册"""
        from ...shared.messages import RegisterRequest
        from ...shared.constants import MessageType

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送注册请求
        register_request = RegisterRequest(username=username, password=password)
        if not self.network_client.send_message(register_request):
            return False, "发送注册请求失败"

        # 等待注册响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.REGISTER_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if hasattr(response, 'success') and response.success:
                return True, "注册成功"
            elif hasattr(response, 'error_message'):
                return False, response.error_message
            elif hasattr(response, 'success'):
                return False, response.error_message or "注册失败"

        return False, "服务器无响应"
    
    def send_chat_message(self, content: str, group_id: int) -> bool:
        """发送聊天消息"""
        from ...shared.messages import ChatMessage
        
        if not self.current_user:
            return False
        
        message = ChatMessage(
            sender_id=self.current_user['id'],
            sender_username=self.current_user['username'],
            chat_group_id=group_id,
            chat_group_name="",  # 服务器会填充
            content=content
        )
        
        return self.network_client.send_message(message)
    
    # 消息处理器
    def _handle_login_response(self, message):
        """处理登录响应"""
        pass  # 由wait_for_response处理
    
    def _handle_register_response(self, message):
        """处理注册响应"""
        pass  # 由wait_for_response处理
    
    def _handle_chat_message(self, message):
        """处理聊天消息"""
        # 这里可以添加消息显示逻辑
        print(f"[{message.sender_username}]: {message.content}")
    
    def _handle_error_message(self, message):
        """处理错误消息"""
        print(f"错误: {message.error_message}")
    
    def _handle_system_message(self, message):
        """处理系统消息"""
        print(f"系统: {message.content}")
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.network_client.is_connected()
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self.current_user is not None

    def get_user_info(self) -> tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取用户信息"""
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录", None

        if not self.network_client.is_connected():
            return False, "未连接到服务器", None

        # 发送用户信息请求
        request = BaseMessage(message_type=MessageType.USER_INFO_REQUEST)
        if not self.network_client.send_message(request):
            return False, "发送请求失败", None

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.USER_INFO_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.USER_INFO_RESPONSE:
                user_info = {
                    'user_id': response.user_info.user_id if response.user_info else None,
                    'username': response.user_info.username if response.user_info else None,
                    'is_online': response.user_info.is_online if response.user_info else None,
                    'joined_chats_count': response.joined_chats_count,
                    'private_chats_count': response.private_chats_count,
                    'group_chats_count': response.group_chats_count,
                    'total_users_count': response.total_users_count,
                    'online_users_count': response.online_users_count,
                    'total_chats_count': response.total_chats_count
                }
                return True, "获取用户信息成功", user_info
            elif hasattr(response, 'error_message'):
                return False, response.error_message, None

        return False, "服务器无响应", None

    def list_users(self, list_type: str = "all") -> tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """获取用户列表

        Args:
            list_type: 列表类型 ("all", "current_chat")
        """
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录", None

        if not self.network_client.is_connected():
            return False, "未连接到服务器", None

        # 发送用户列表请求
        request = BaseMessage(
            message_type=MessageType.LIST_USERS_REQUEST,
            list_type=list_type,
            chat_group_id=self.current_chat_group['id'] if self.current_chat_group else None
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败", None

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.LIST_USERS_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.LIST_USERS_RESPONSE:
                users = []
                for user in response.users:
                    users.append({
                        'user_id': user.user_id,
                        'username': user.username,
                        'is_online': user.is_online
                    })
                return True, "获取用户列表成功", users
            elif hasattr(response, 'error_message'):
                return False, response.error_message, None

        return False, "服务器无响应", None

    def list_chats(self, list_type: str = "joined") -> tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """获取聊天组列表

        Args:
            list_type: 列表类型 ("joined", "all")
        """
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录", None

        if not self.network_client.is_connected():
            return False, "未连接到服务器", None

        # 发送聊天组列表请求
        request = BaseMessage(
            message_type=MessageType.LIST_CHATS_REQUEST,
            list_type=list_type
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败", None

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.LIST_CHATS_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.LIST_CHATS_RESPONSE:
                chats = []
                for chat in response.chats:
                    chats.append({
                        'group_id': chat.group_id,
                        'group_name': chat.group_name,
                        'is_private_chat': chat.is_private_chat,
                        'member_count': chat.member_count,
                        'created_at': chat.created_at
                    })
                return True, "获取聊天组列表成功", chats
            elif hasattr(response, 'error_message'):
                return False, response.error_message, None

        return False, "服务器无响应", None

    def create_chat_group(self, group_name: str, member_usernames: List[str] = None) -> tuple[bool, str]:
        """创建聊天组

        Args:
            group_name: 聊天组名称
            member_usernames: 初始成员用户名列表
        """
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送创建聊天组请求
        request = BaseMessage(
            message_type=MessageType.CREATE_CHAT_REQUEST,
            group_name=group_name,
            member_usernames=member_usernames or []
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.CREATE_CHAT_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.CREATE_CHAT_RESPONSE:
                if hasattr(response, 'success') and response.success:
                    return True, f"聊天组 '{group_name}' 创建成功"
                else:
                    return False, response.error_message or "创建聊天组失败"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"

    def join_chat_group(self, group_name: str) -> tuple[bool, str]:
        """加入聊天组"""
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送加入聊天组请求
        request = BaseMessage(
            message_type=MessageType.JOIN_CHAT_REQUEST,
            group_name=group_name
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.JOIN_CHAT_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.JOIN_CHAT_RESPONSE:
                if hasattr(response, 'success') and response.success:
                    return True, f"成功加入聊天组 '{group_name}'"
                else:
                    return False, response.error_message or "加入聊天组失败"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"

    def enter_chat_group(self, group_name: str) -> tuple[bool, str]:
        """进入聊天组（切换当前聊天组）"""
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送进入聊天组请求
        request = BaseMessage(
            message_type=MessageType.ENTER_CHAT_REQUEST,
            group_name=group_name
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.ENTER_CHAT_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.ENTER_CHAT_RESPONSE:
                if hasattr(response, 'success') and response.success:
                    # 更新当前聊天组信息
                    if hasattr(response, 'chat_group'):
                        self.current_chat_group = {
                            'id': response.chat_group.group_id,
                            'name': response.chat_group.group_name,
                            'is_private_chat': response.chat_group.is_private_chat
                        }
                    return True, f"已进入聊天组 '{group_name}'"
                else:
                    return False, response.error_message or "进入聊天组失败"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"

    def list_files(self, chat_group_id: int = None) -> tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """获取聊天组文件列表"""
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录", None

        if not self.network_client.is_connected():
            return False, "未连接到服务器", None

        # 使用当前聊天组ID或指定的ID
        group_id = chat_group_id or (self.current_chat_group['id'] if self.current_chat_group else None)
        if not group_id:
            return False, "请先进入聊天组", None

        # 发送文件列表请求
        request = BaseMessage(
            message_type=MessageType.FILE_LIST_REQUEST,
            chat_group_id=group_id
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败", None

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.FILE_LIST_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.FILE_LIST_RESPONSE:
                files = []
                for file_info in response.files:
                    files.append({
                        'file_id': file_info.file_id,
                        'original_filename': file_info.original_filename,
                        'file_size': file_info.file_size,
                        'uploader_username': file_info.uploader_username,
                        'upload_time': file_info.upload_time
                    })
                return True, "获取文件列表成功", files
            elif hasattr(response, 'error_message'):
                return False, response.error_message, None

        return False, "服务器无响应", None

    def send_file(self, file_path: str) -> tuple[bool, str]:
        """发送文件到当前聊天组"""
        import os
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType, MAX_FILE_SIZE, ALLOWED_FILE_EXTENSIONS

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        if not self.current_chat_group:
            return False, "请先进入聊天组"

        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False, f"文件不存在: {file_path}"

        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > MAX_FILE_SIZE:
            return False, f"文件过大，最大支持 {MAX_FILE_SIZE // (1024*1024)}MB"

        # 检查文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in ALLOWED_FILE_EXTENSIONS:
            return False, f"不支持的文件类型: {file_ext}"

        filename = os.path.basename(file_path)

        # 发送文件上传请求
        request = BaseMessage(
            message_type=MessageType.FILE_UPLOAD_REQUEST,
            chat_group_id=self.current_chat_group['id'],
            filename=filename,
            file_size=file_size
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.FILE_UPLOAD_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.FILE_UPLOAD_RESPONSE:
                if hasattr(response, 'success') and response.success:
                    return True, f"文件 '{filename}' 上传成功"
                else:
                    return False, response.error_message or "文件上传失败"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"

    def download_file(self, file_id: int, save_path: str = None) -> tuple[bool, str]:
        """下载文件"""
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送文件下载请求
        request = BaseMessage(
            message_type=MessageType.FILE_DOWNLOAD_REQUEST,
            file_id=file_id,
            save_path=save_path
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=30.0,  # 文件下载可能需要更长时间
            message_types=[MessageType.FILE_DOWNLOAD_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.FILE_DOWNLOAD_RESPONSE:
                if hasattr(response, 'success') and response.success:
                    return True, f"文件下载成功: {response.file_path if hasattr(response, 'file_path') else save_path}"
                else:
                    return False, response.error_message or "文件下载失败"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"

    def send_ai_request(self, command: str, message: str = None,
                       chat_group_id: int = None) -> tuple[bool, str]:
        """发送AI请求

        Args:
            command: AI命令 (status, clear, help)
            message: AI聊天消息 (可选)
            chat_group_id: 聊天组ID (None表示私聊)
        """
        from ...shared.messages import BaseMessage
        from ...shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送AI请求
        request = BaseMessage(
            message_type=MessageType.AI_CHAT_REQUEST,
            command=command,
            message=message,
            chat_group_id=chat_group_id
        )

        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=30.0,  # AI响应可能需要更长时间
            message_types=[MessageType.AI_CHAT_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.AI_CHAT_RESPONSE:
                if hasattr(response, 'success') and response.success:
                    return True, response.message or "AI响应成功"
                else:
                    return False, response.message or "AI响应失败"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"
