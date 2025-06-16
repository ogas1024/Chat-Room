"""
网络客户端模块
处理与服务器的连接、消息发送和接收
"""

import socket
import threading
import time
from typing import Callable, Optional, Dict, Any, List

from shared.constants import DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE
from shared.messages import BaseMessage, parse_message
from shared.logger import get_logger


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
            logger = get_logger("client.core.network")
            logger.error("连接服务器失败", host=self.host, port=self.port, error=str(e))
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
            logger = get_logger("client.core.network")
            logger.error("发送消息失败", error=str(e))
            self.connected = False
            return False

    def send_file_data(self, file_path: str, chunk_size: int = 8192) -> bool:
        """发送文件数据到服务器"""
        if not self.connected or not self.socket:
            return False

        try:
            import os
            if not os.path.exists(file_path):
                return False

            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    self.socket.send(data)
            return True
        except Exception as e:
            logger = get_logger("client.core.network")
            logger.error("发送文件数据失败", file_path=file_path, error=str(e))
            return False

    def receive_file_data(self, save_path: str, file_size: int, chunk_size: int = 8192) -> bool:
        """接收文件数据并保存到指定路径"""
        if not self.connected or not self.socket:
            return False

        try:
            import os
            import time

            # 确保目录存在
            dir_path = os.path.dirname(save_path)
            if dir_path:  # 只有当目录路径不为空时才创建
                os.makedirs(dir_path, exist_ok=True)

            # 检查save_path是否是目录
            if os.path.isdir(save_path):
                return False

            # 暂停消息处理，避免文件数据被当作消息处理
            old_running = self.running
            self.running = False

            # 等待消息处理线程暂停
            time.sleep(0.2)

            try:
                # 等待文件数据开始标记 - 使用更明确的分隔符
                start_marker = b"===FILE_DATA_START===\n"
                buffer = b""
                timeout_start = time.time()
                timeout_duration = 30.0  # 30秒超时

                while start_marker not in buffer:
                    if time.time() - timeout_start > timeout_duration:
                        return False

                    try:
                        self.socket.settimeout(1.0)  # 设置1秒超时
                        data = self.socket.recv(1024)
                        if not data:
                            return False
                        buffer += data
                    except socket.timeout:
                        continue
                    except socket.error:
                        return False
                    finally:
                        try:
                            self.socket.settimeout(None)
                        except:
                            pass  # 忽略设置超时时的异常

                # 移除开始标记，保留剩余数据
                marker_pos = buffer.find(start_marker)
                remaining_data = buffer[marker_pos + len(start_marker):]

                # 接收文件数据 - 只接收指定大小的数据
                received_size = 0
                end_marker = b"\n===FILE_DATA_END===\n"

                with open(save_path, 'wb') as f:
                    # 先处理剩余数据
                    if remaining_data:
                        # 检查剩余数据中是否包含结束标记
                        if end_marker in remaining_data:
                            # 找到结束标记，只写入结束标记之前的数据
                            end_pos = remaining_data.find(end_marker)
                            file_data = remaining_data[:end_pos]
                            write_size = min(len(file_data), file_size - received_size)
                            f.write(file_data[:write_size])
                            received_size += write_size
                        else:
                            write_size = min(len(remaining_data), file_size - received_size)
                            f.write(remaining_data[:write_size])
                            received_size += write_size

                    # 继续接收直到达到文件大小或遇到结束标记
                    file_buffer = b""
                    while received_size < file_size:
                        remaining = file_size - received_size
                        current_chunk_size = min(chunk_size, remaining + len(end_marker))  # 多接收一些以检测结束标记

                        try:
                            self.socket.settimeout(5.0)  # 设置5秒超时
                            data = self.socket.recv(current_chunk_size)
                            if not data:
                                break
                        except socket.timeout:
                            break
                        except socket.error:
                            break
                        finally:
                            try:
                                self.socket.settimeout(None)
                            except:
                                pass  # 忽略设置超时时的异常

                        file_buffer += data

                        # 检查是否包含结束标记
                        if end_marker in file_buffer:
                            # 找到结束标记，只写入结束标记之前的数据
                            end_pos = file_buffer.find(end_marker)
                            file_data = file_buffer[:end_pos]
                            write_size = min(len(file_data), file_size - received_size)
                            f.write(file_data[:write_size])
                            received_size += write_size
                            break
                        else:
                            # 没有结束标记，写入所有数据（但不超过文件大小）
                            write_size = min(len(file_buffer), file_size - received_size)
                            f.write(file_buffer[:write_size])
                            received_size += write_size
                            file_buffer = file_buffer[write_size:]  # 保留未写入的数据

                        if received_size >= file_size:
                            break

                # 验证文件大小
                if received_size == file_size:
                    return True
                else:
                    return False

            finally:
                # 恢复消息处理
                self.running = old_running

                # 等待一小段时间，让服务器发送完成响应
                time.sleep(0.3)

        except Exception as e:
            logger = get_logger("client.core.network")
            logger.error("接收文件数据失败", save_path=save_path, file_size=file_size, error=str(e))
            return False
    
    def _receive_messages(self):
        """接收消息的线程函数"""
        buffer = b""  # 使用字节缓冲区

        while self.connected:  # 只检查连接状态，不检查running状态
            try:
                # 检查是否需要暂停消息处理（文件传输时）
                if not self.running:
                    time.sleep(0.1)
                    continue

                # 设置非阻塞模式来避免与文件传输的超时设置冲突
                try:
                    self.socket.settimeout(1.0)  # 设置1秒超时
                    data = self.socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                except socket.timeout:
                    continue  # 超时是正常的，继续循环
                finally:
                    # 恢复socket设置，避免影响其他操作
                    try:
                        self.socket.settimeout(None)
                    except:
                        pass

                # 添加到字节缓冲区
                buffer += data

                # 尝试解码并处理完整的消息（以换行符分隔）
                while b'\n' in buffer and self.running:
                    line_bytes, buffer = buffer.split(b'\n', 1)
                    if line_bytes:
                        try:
                            # 解码单条消息
                            line = line_bytes.decode('utf-8').strip()
                            if line:
                                self._handle_received_message(line)
                        except UnicodeDecodeError as e:
                            logger = get_logger("client.core.network")
                            logger.error("消息解码错误", error=str(e), data_preview=str(line_bytes[:100]))
                            continue

            except socket.error as e:
                # 检查是否是由于文件传输导致的临时错误
                if e.errno == 11:  # EAGAIN/EWOULDBLOCK
                    time.sleep(0.1)
                    continue
                elif self.connected:  # 只有在连接状态下才报告其他错误
                    logger = get_logger("client.core.network")
                    logger.error("接收消息时出错", error=str(e))
                    break
                else:
                    break

        # 只有在真正断开连接时才设置connected为False
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
                logger = get_logger("client.core.network")
                logger.debug("未处理的消息类型", message_type=message_type)

        except Exception as e:
            logger = get_logger("client.core.network")
            logger.error("处理接收消息时出错", error=str(e), exc_info=True)
    
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
            # 恢复原来的处理器 - 改进版本，避免覆盖Simple模式的处理器
            if message_types:
                for msg_type in message_types:
                    if msg_type in old_handlers:
                        # 恢复原来的处理器
                        self.message_handlers[msg_type] = old_handlers[msg_type]
                    else:
                        # 如果原来没有处理器，检查当前处理器是否是我们设置的临时处理器
                        # 如果是，才删除；如果不是（可能被其他地方设置了），保留它
                        if (msg_type in self.message_handlers and
                            self.message_handlers[msg_type] == response_handler):
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
        from shared.constants import MessageType

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
            MessageType.CHAT_HISTORY, self._handle_chat_history
        )
        self.network_client.set_message_handler(
            MessageType.CHAT_HISTORY_COMPLETE, self._handle_chat_history_complete
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
        from shared.messages import LoginRequest
        from shared.constants import MessageType

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
                # 设置当前聊天组（如果服务器提供了）
                if hasattr(response, 'current_chat_group') and response.current_chat_group:
                    self.current_chat_group = response.current_chat_group
                return True, "登录成功"
            elif hasattr(response, 'error_message'):
                return False, response.error_message
            elif hasattr(response, 'success'):
                return False, response.error_message or "登录失败"

        return False, "服务器无响应"
    
    def register(self, username: str, password: str) -> tuple[bool, str]:
        """用户注册"""
        from shared.messages import RegisterRequest
        from shared.constants import MessageType

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
        from shared.messages import ChatMessage
        
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
        # 验证消息是否属于当前聊天组
        if not hasattr(message, 'chat_group_id'):
            # 消息没有聊天组ID，忽略显示
            return

        if not self.current_chat_group:
            # 用户没有当前聊天组，忽略显示
            return

        if message.chat_group_id != self.current_chat_group['id']:
            # 消息不属于当前聊天组，忽略显示
            return

        # 这里可以添加消息显示逻辑
        print(f"[{message.sender_username}]: {message.content}")

    def _handle_chat_history(self, message):
        """处理历史聊天消息"""
        # 验证消息是否属于当前聊天组
        if not hasattr(message, 'chat_group_id'):
            return

        if not self.current_chat_group:
            return

        if message.chat_group_id != self.current_chat_group['id']:
            return

        # 历史消息的默认处理（可以被上层应用覆盖）
        print(f"[历史] [{message.sender_username}]: {message.content}")

    def _handle_chat_history_complete(self, message):
        """处理历史消息加载完成通知"""
        # 验证消息是否属于当前聊天组
        if not hasattr(message, 'chat_group_id'):
            return

        if not self.current_chat_group:
            return

        if message.chat_group_id != self.current_chat_group['id']:
            return

        # 历史消息加载完成的默认处理（可以被上层应用覆盖）
        print(f"[系统] 历史消息加载完成，共 {message.message_count} 条消息")

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
        from shared.messages import BaseMessage
        from shared.constants import MessageType

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
        from shared.messages import ListUsersRequest
        from shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录", None

        if not self.network_client.is_connected():
            return False, "未连接到服务器", None

        # 发送用户列表请求
        request = ListUsersRequest(
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
        from shared.messages import ListChatsRequest
        from shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录", None

        if not self.network_client.is_connected():
            return False, "未连接到服务器", None

        # 发送聊天组列表请求
        request = ListChatsRequest(
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
        from shared.messages import CreateChatRequest
        from shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送创建聊天组请求
        request = CreateChatRequest(
            chat_name=group_name,
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
        from shared.messages import JoinChatRequest
        from shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送加入聊天组请求
        request = JoinChatRequest(
            chat_name=group_name
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 等待响应
        response = self.network_client.wait_for_response(
            timeout=10.0,
            message_types=[MessageType.SYSTEM_MESSAGE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.SYSTEM_MESSAGE:
                return True, f"成功加入聊天组 '{group_name}'"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"

    def enter_chat_group(self, group_name: str) -> tuple[bool, str]:
        """进入聊天组（切换当前聊天组）"""
        from shared.messages import EnterChatRequest
        from shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送进入聊天组请求
        request = EnterChatRequest(
            chat_name=group_name
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 创建一个自定义的响应处理器，在接收到响应时立即更新聊天组状态
        response = None

        def custom_response_handler(message):
            nonlocal response
            if message.message_type in [MessageType.ENTER_CHAT_RESPONSE, MessageType.ERROR_MESSAGE]:
                response = message
                # 如果是成功的进入聊天组响应，立即更新当前聊天组信息
                if (message.message_type == MessageType.ENTER_CHAT_RESPONSE and
                    hasattr(message, 'success') and message.success and
                    hasattr(message, 'chat_group_id') and hasattr(message, 'chat_name')):

                    new_chat_group = {
                        'id': message.chat_group_id,
                        'name': message.chat_name,
                        'is_private_chat': False
                    }
                    self.current_chat_group = new_chat_group

        # 使用自定义的wait_for_response逻辑
        import time
        start_time = time.time()
        timeout = 10.0

        # 保存原有的处理器
        old_handlers = {}
        for msg_type in [MessageType.ENTER_CHAT_RESPONSE, MessageType.ERROR_MESSAGE]:
            if msg_type in self.network_client.message_handlers:
                old_handlers[msg_type] = self.network_client.message_handlers[msg_type]
            self.network_client.message_handlers[msg_type] = custom_response_handler

        try:
            # 等待响应
            while time.time() - start_time < timeout and response is None:
                time.sleep(0.1)
        finally:
            # 恢复原来的处理器
            for msg_type in [MessageType.ENTER_CHAT_RESPONSE, MessageType.ERROR_MESSAGE]:
                if msg_type in old_handlers:
                    self.network_client.message_handlers[msg_type] = old_handlers[msg_type]
                else:
                    self.network_client.message_handlers.pop(msg_type, None)

        if response:
            if response.message_type == MessageType.ENTER_CHAT_RESPONSE:
                if hasattr(response, 'success') and response.success:
                    return True, f"已进入聊天组 '{group_name}'"
                else:
                    return False, response.error_message or "进入聊天组失败"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"

    def list_files(self, chat_group_id: int = None) -> tuple[bool, str, Optional[List[Dict[str, Any]]]]:
        """获取聊天组文件列表"""
        from shared.messages import FileListRequest
        from shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录", None

        if not self.network_client.is_connected():
            return False, "未连接到服务器", None

        # 使用当前聊天组ID或指定的ID
        group_id = chat_group_id or (self.current_chat_group['id'] if self.current_chat_group else None)
        if not group_id:
            return False, "请先进入聊天组", None

        # 发送文件列表请求
        request = FileListRequest(
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
        from shared.messages import FileUploadRequest
        from shared.constants import MessageType, MAX_FILE_SIZE, ALLOWED_FILE_EXTENSIONS

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
        request = FileUploadRequest(
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
                    # 服务器准备就绪，开始发送文件数据
                    if self.network_client.send_file_data(file_path):
                        # 等待上传完成确认
                        final_response = self.network_client.wait_for_response(
                            timeout=30.0,
                            message_types=[MessageType.FILE_UPLOAD_RESPONSE, MessageType.ERROR_MESSAGE]
                        )
                        if final_response and hasattr(final_response, 'success') and final_response.success:
                            return True, f"文件 '{filename}' 上传成功"
                        else:
                            return False, final_response.error_message if final_response and hasattr(final_response, 'error_message') else "文件上传失败"
                    else:
                        return False, "文件数据发送失败"
                else:
                    return False, response.error_message or "文件上传失败"
            elif hasattr(response, 'error_message'):
                return False, response.error_message

        return False, "服务器无响应"

    def download_file(self, file_id: int, save_path: str = None) -> tuple[bool, str]:
        """下载文件"""
        import os
        from shared.messages import FileDownloadRequest
        from shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送文件下载请求
        request = FileDownloadRequest(
            file_id=str(file_id)
        )
        if not self.network_client.send_message(request):
            return False, "发送请求失败"

        # 等待第一个响应（开始下载）
        response = self.network_client.wait_for_response(
            timeout=30.0,  # 文件下载可能需要更长时间
            message_types=[MessageType.FILE_DOWNLOAD_RESPONSE, MessageType.ERROR_MESSAGE]
        )

        if response:
            if response.message_type == MessageType.FILE_DOWNLOAD_RESPONSE:
                if hasattr(response, 'success') and response.success:
                    # 检查这是否是开始下载的响应（包含filename和file_size）
                    if hasattr(response, 'filename') and response.filename and hasattr(response, 'file_size') and response.file_size > 0:
                        # 这是开始下载的响应
                        filename = response.filename
                        file_size = response.file_size

                        # 确定保存路径
                        if not save_path:
                            username = self.current_user['username'] if self.current_user else 'unknown'
                            download_dir = os.path.join('client', 'Downloads', username)
                            save_path = os.path.join(download_dir, filename)

                        # 接收文件数据
                        if self.network_client.receive_file_data(save_path, file_size):
                            # 等待下载完成确认
                            self.network_client.wait_for_response(
                                timeout=10.0,
                                message_types=[MessageType.FILE_DOWNLOAD_RESPONSE, MessageType.ERROR_MESSAGE]
                            )
                            return True, f"文件下载成功: {save_path}"
                        else:
                            return False, "文件数据接收失败"
                    else:
                        # 这可能是下载完成的响应，我们需要重新等待开始下载的响应
                        # 重新等待开始下载的响应
                        start_response = self.network_client.wait_for_response(
                            timeout=10.0,
                            message_types=[MessageType.FILE_DOWNLOAD_RESPONSE, MessageType.ERROR_MESSAGE]
                        )

                        if start_response and start_response.message_type == MessageType.FILE_DOWNLOAD_RESPONSE:
                            if (hasattr(start_response, 'filename') and start_response.filename and
                                hasattr(start_response, 'file_size') and start_response.file_size > 0):
                                # 这是开始下载的响应
                                filename = start_response.filename
                                file_size = start_response.file_size

                                # 确定保存路径
                                if not save_path:
                                    username = self.current_user['username'] if self.current_user else 'unknown'
                                    download_dir = os.path.join('client', 'Downloads', username)
                                    save_path = os.path.join(download_dir, filename)

                                # 接收文件数据
                                if self.network_client.receive_file_data(save_path, file_size):
                                    return True, f"文件下载成功: {save_path}"
                                else:
                                    return False, "文件数据接收失败"

                        return False, "无法获取正确的下载响应"
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
        from shared.messages import AIChatRequest
        from shared.constants import MessageType

        if not self.is_logged_in():
            return False, "请先登录"

        if not self.network_client.is_connected():
            return False, "未连接到服务器"

        # 发送AI请求
        request = AIChatRequest(
            command=command,
            message=message or "",
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
