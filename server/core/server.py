"""
聊天室服务器核心模块
处理客户端连接、消息路由、协议解析等核心功能
"""

import socket
import threading
import json
import os
import uuid
import time

from server.core.user_manager import UserManager
from server.core.chat_manager import ChatManager
from server.ai.ai_manager import AIManager
from server.config.ai_config import get_ai_config
from server.database.connection import init_database
from server.utils.auth import (
    validate_username, validate_password, validate_chat_group_name,
    sanitize_message_content
)
from server.utils.common import ResponseHelper
from shared.constants import (
    DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE, MAX_CONNECTIONS,
    MessageType, ErrorCode, FILES_STORAGE_PATH, FILE_CHUNK_SIZE,
    MAX_FILE_SIZE, ALLOWED_FILE_EXTENSIONS, AI_USER_ID
)
from shared.logger import (
    get_logger, log_event, log_network_event, log_user_action,
    log_database_operation, log_ai_operation, log_security_event,
    log_performance, log_file_operation, log_function_call
)
from shared.messages import (
    parse_message, BaseMessage, LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse, ChatMessage, SystemMessage,
    ErrorMessage, UserInfoResponse, ListUsersResponse, ListChatsResponse,
    FileInfo, FileUploadResponse, FileDownloadResponse
)
from shared.exceptions import (
    AuthenticationError, UserAlreadyExistsError,
    UserNotFoundError, ChatGroupNotFoundError, PermissionDeniedError
)


class ChatRoomServer:
    """聊天室服务器"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化服务器"""
        self.host = host
        self.port = port
        self.max_connections = MAX_CONNECTIONS
        self.server_socket = None
        self.running = False

        # 初始化日志
        self.logger = get_logger("server.core")

        # 初始化管理器
        self.user_manager = UserManager()
        self.chat_manager = ChatManager(self.user_manager)

        # 初始化AI管理器
        ai_config = get_ai_config()
        self.ai_manager = AIManager(ai_config.get_api_key())

        # 响应助手
        self.response_helper = ResponseHelper()

        self.logger.info("服务器初始化完成", host=host, port=port, max_connections=MAX_CONNECTIONS)
        print(f"聊天室服务器初始化完成 - {host}:{port}")
    
    def start(self):
        """启动服务器"""
        try:
            # 初始化数据库
            self.logger.info("初始化数据库...")
            init_database()
            log_database_operation("init", "all_tables")

            # 创建服务器socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_CONNECTIONS)

            self.running = True
            self.logger.info("服务器启动成功", host=self.host, port=self.port, max_connections=MAX_CONNECTIONS)
            log_network_event("server_started", client_ip=None, host=self.host, port=self.port)

            print(f"服务器启动成功，监听 {self.host}:{self.port}")
            print(f"最大连接数: {MAX_CONNECTIONS}")

            # 接受客户端连接
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_ip = client_address[0]
                    client_port = client_address[1]

                    self.logger.info("新客户端连接", client_ip=client_ip, client_port=client_port)
                    log_network_event("client_connected", client_ip=client_ip, client_port=client_port)
                    print(f"新客户端连接: {client_address}")

                    # 为每个客户端创建处理线程
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()

                except socket.error as e:
                    if self.running:
                        self.logger.error("接受连接时出错", error=str(e))
                        print(f"接受连接时出错: {e}")

        except Exception as e:
            self.logger.error("服务器启动失败", error=str(e), exc_info=True)
            print(f"服务器启动失败: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        print("服务器已停止")
    
    def handle_client(self, client_socket: socket.socket, client_address):
        """处理客户端连接"""
        client_ip = client_address[0]
        client_port = client_address[1]

        try:
            while self.running:
                # 接收消息
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                try:
                    # 解析消息
                    message_str = data.decode('utf-8').strip()
                    if not message_str:
                        continue

                    # 记录接收到的消息
                    self.logger.debug("接收消息", client_ip=client_ip, message_length=len(message_str))

                    # 处理可能的多条消息
                    for line in message_str.split('\n'):
                        if line.strip():
                            self.process_message(client_socket, line.strip())

                except UnicodeDecodeError:
                    self.logger.warning("消息编码错误", client_ip=client_ip)
                    log_security_event("invalid_encoding", client_ip=client_ip)
                    self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "消息编码错误")
                except Exception as e:
                    self.logger.error("处理消息时出错", client_ip=client_ip, error=str(e))
                    print(f"处理消息时出错: {e}")
                    self.send_error(client_socket, ErrorCode.SERVER_ERROR, "服务器内部错误")

        except ConnectionResetError:
            self.logger.info("客户端连接重置", client_ip=client_ip, client_port=client_port)
            log_network_event("client_connection_reset", client_ip=client_ip)
            print(f"客户端 {client_address} 连接重置")
        except Exception as e:
            self.logger.error("处理客户端时出错", client_ip=client_ip, error=str(e), exc_info=True)
            print(f"处理客户端 {client_address} 时出错: {e}")
        finally:
            # 清理连接
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if user_info:
                log_user_action(user_info['user_id'], user_info['username'], "disconnect")

            self.user_manager.disconnect_user(client_socket)
            try:
                client_socket.close()
            except:
                pass

            self.logger.info("客户端连接已关闭", client_ip=client_ip, client_port=client_port)
            log_network_event("client_disconnected", client_ip=client_ip)
            print(f"客户端 {client_address} 连接已关闭")
    
    def process_message(self, client_socket: socket.socket, message_str: str):
        """处理单条消息"""
        try:
            # 解析消息
            message = parse_message(message_str)
            
            if isinstance(message, ErrorMessage):
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "消息格式错误")
                return
            
            # 根据消息类型处理
            if message.message_type == MessageType.LOGIN_REQUEST:
                self.handle_login(client_socket, message)
            elif message.message_type == MessageType.REGISTER_REQUEST:
                self.handle_register(client_socket, message)
            elif message.message_type == MessageType.CHAT_MESSAGE:
                self.handle_chat_message(client_socket, message)
            elif message.message_type == MessageType.USER_INFO_REQUEST:
                self.handle_user_info_request(client_socket)
            elif message.message_type == MessageType.LIST_USERS_REQUEST:
                self.handle_list_users_request(client_socket, message)
            elif message.message_type == MessageType.LIST_CHATS_REQUEST:
                self.handle_list_chats_request(client_socket, message)
            elif message.message_type == MessageType.CREATE_CHAT_REQUEST:
                self.handle_create_chat_request(client_socket, message)
            elif message.message_type == MessageType.JOIN_CHAT_REQUEST:
                self.handle_join_chat_request(client_socket, message)
            elif message.message_type == MessageType.ENTER_CHAT_REQUEST:
                self.handle_enter_chat_request(client_socket, message)
            elif message.message_type == MessageType.FILE_UPLOAD_REQUEST:
                self.handle_file_upload_request(client_socket, message)
            elif message.message_type == MessageType.FILE_DOWNLOAD_REQUEST:
                self.handle_file_download_request(client_socket, message)
            elif message.message_type == MessageType.FILE_LIST_REQUEST:
                self.handle_file_list_request(client_socket, message)
            elif message.message_type == MessageType.AI_CHAT_REQUEST:
                self.handle_ai_chat_request(client_socket, message)
            elif message.message_type == MessageType.LOGOUT_REQUEST:
                self.handle_logout(client_socket)
            else:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, f"未知的消息类型: {message.message_type}")
                
        except json.JSONDecodeError:
            self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "JSON格式错误")
        except Exception as e:
            print(f"处理消息时出错: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "服务器内部错误")
    
    def handle_login(self, client_socket: socket.socket, message: LoginRequest):
        """处理登录请求"""
        client_ip = client_socket.getpeername()[0] if client_socket else "unknown"

        try:
            # 验证用户名和密码格式
            valid, error_msg = validate_username(message.username)
            if not valid:
                self.logger.warning("登录失败：用户名格式不正确", username=message.username, client_ip=client_ip)
                log_security_event("invalid_username_format", username=message.username, client_ip=client_ip)
                self.send_login_response(client_socket, False, error_message=error_msg)
                return

            valid, error_msg = validate_password(message.password)
            if not valid:
                self.logger.warning("登录失败：密码格式不正确", username=message.username, client_ip=client_ip)
                log_security_event("invalid_password_format", username=message.username, client_ip=client_ip)
                self.send_login_response(client_socket, False, error_message=error_msg)
                return

            # 认证用户
            self.logger.info("用户认证中", username=message.username, client_ip=client_ip)
            user_info = self.user_manager.authenticate_user(message.username, message.password)

            # 登录用户
            self.user_manager.login_user(user_info['id'], client_socket)

            # 自动进入公频聊天组
            public_chat_id = self.chat_manager.get_public_chat_id()
            self.user_manager.set_user_current_chat(user_info['id'], public_chat_id)

            # 获取公频聊天组信息
            public_chat_info = self.chat_manager.db.get_chat_group_by_id(public_chat_id)

            # 记录成功登录
            self.logger.info("用户登录成功",
                           user_id=user_info['id'],
                           username=user_info['username'],
                           client_ip=client_ip)
            log_user_action(user_info['id'], user_info['username'], "login", client_ip=client_ip)
            log_security_event("login_success",
                             user_id=user_info['id'],
                             username=user_info['username'],
                             client_ip=client_ip)

            # 发送成功响应（包含当前聊天组信息）
            self.send_login_response(
                client_socket, True,
                user_id=user_info['id'],
                username=user_info['username'],
                current_chat_group={
                    'id': public_chat_id,
                    'name': public_chat_info['name']
                }
            )

        except AuthenticationError as e:
            self.logger.warning("用户认证失败", username=message.username, client_ip=client_ip, error=str(e))
            log_security_event("login_failed", username=message.username, client_ip=client_ip, reason=str(e))
            self.send_login_response(client_socket, False, error_message=str(e))
        except Exception as e:
            self.logger.error("登录处理错误", username=message.username, client_ip=client_ip, error=str(e), exc_info=True)
            print(f"登录处理错误: {e}")
            self.send_login_response(client_socket, False, error_message="登录失败")
    
    def handle_register(self, client_socket: socket.socket, message: RegisterRequest):
        """处理注册请求"""
        try:
            # 验证用户名和密码格式
            valid, error_msg = validate_username(message.username)
            if not valid:
                self.send_register_response(client_socket, False, error_message=error_msg)
                return
            
            valid, error_msg = validate_password(message.password)
            if not valid:
                self.send_register_response(client_socket, False, error_message=error_msg)
                return
            
            # 注册用户
            user_id = self.user_manager.register_user(message.username, message.password)
            
            # 发送成功响应
            self.send_register_response(
                client_socket, True,
                user_id=user_id,
                username=message.username
            )
            
        except UserAlreadyExistsError as e:
            self.send_register_response(client_socket, False, error_message=str(e))
        except Exception as e:
            print(f"注册处理错误: {e}")
            self.send_register_response(client_socket, False, error_message="注册失败")

    def handle_chat_message(self, client_socket: socket.socket, message: ChatMessage):
        """处理聊天消息"""
        try:
            # 获取发送者信息
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if not user_info:
                self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
                return

            # 清理消息内容
            content = sanitize_message_content(message.content)
            if not content:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "消息内容不能为空")
                return

            # 记录消息发送
            self.logger.info("用户发送消息",
                           user_id=user_info['user_id'],
                           username=user_info['username'],
                           chat_group_id=message.chat_group_id,
                           message_length=len(content))
            log_user_action(user_info['user_id'], user_info['username'], "send_message",
                          chat_group_id=message.chat_group_id, message_length=len(content))

            # 发送消息
            chat_message = self.chat_manager.send_message(
                user_info['user_id'], message.chat_group_id, content
            )

            # 广播消息到聊天组
            self.chat_manager.broadcast_message_to_group(chat_message)

            # 检查是否需要AI回复
            if self.ai_manager.is_enabled():
                start_time = time.time()
                ai_reply = self.ai_manager.process_message(
                    user_info['user_id'],
                    user_info['username'],
                    content,
                    message.chat_group_id
                )
                ai_response_time = time.time() - start_time

                if ai_reply:
                    # 记录AI回复
                    self.logger.info("AI生成回复",
                                   user_id=user_info['user_id'],
                                   chat_group_id=message.chat_group_id,
                                   response_time=ai_response_time,
                                   reply_length=len(ai_reply))
                    log_ai_operation("generate_reply", "glm-4-flash",
                                   user_id=user_info['user_id'],
                                   chat_group_id=message.chat_group_id,
                                   response_time=ai_response_time)

                    # 创建AI回复消息
                    ai_message = self.chat_manager.send_message(
                        AI_USER_ID, message.chat_group_id, ai_reply
                    )
                    # 广播AI回复
                    self.chat_manager.broadcast_message_to_group(ai_message)

        except PermissionDeniedError as e:
            self.logger.warning("消息发送权限被拒绝",
                              user_id=user_info.get('user_id') if user_info else None,
                              error=str(e))
            self.send_error(client_socket, ErrorCode.PERMISSION_DENIED, str(e))
        except Exception as e:
            self.logger.error("聊天消息处理错误",
                            user_id=user_info.get('user_id') if user_info else None,
                            error=str(e), exc_info=True)
            print(f"聊天消息处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "消息发送失败")

    def handle_user_info_request(self, client_socket: socket.socket):
        """处理用户信息请求"""
        try:
            # 验证用户登录
            user_info = self.verify_user_login(client_socket)
            if not user_info:
                return

            # 获取详细信息
            detailed_info = self.user_manager.get_user_info(user_info['user_id'])

            # 发送响应
            response = UserInfoResponse(**detailed_info)
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"用户信息请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "获取用户信息失败")

    def handle_list_users_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理用户列表请求"""
        try:
            # 验证用户登录
            user_info = self.verify_user_login(client_socket)
            if not user_info:
                return

            # 获取用户列表
            users = self.user_manager.get_all_users()

            # 发送响应
            response = ListUsersResponse(users=users)
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"用户列表请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "获取用户列表失败")

    def handle_list_chats_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理聊天组列表请求"""
        try:
            # 验证用户登录
            user_info = self.verify_user_login(client_socket)
            if not user_info:
                return

            # 根据请求类型获取不同的聊天组列表
            request_data = getattr(message, 'to_dict', lambda: {})()
            list_type = request_data.get('list_type', 'user_chats')

            if list_type == 'user_chats':
                # 用户加入的聊天组
                chats = self.chat_manager.get_user_chat_groups(user_info['user_id'])
            elif list_type == 'group_chats':
                # 所有群聊
                chats = self.chat_manager.get_all_group_chats()
            else:
                chats = self.chat_manager.get_user_chat_groups(user_info['user_id'])

            # 发送响应
            response = ListChatsResponse(chats=chats)
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"聊天组列表请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "获取聊天组列表失败")

    def handle_create_chat_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理创建聊天组请求"""
        try:
            # 验证用户登录
            user_info = self.verify_user_login(client_socket)
            if not user_info:
                return

            # 获取请求数据
            request_data, error_msg = self.get_request_data(message, ['chat_name'])
            if error_msg:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, error_msg)
                return

            chat_name = request_data['chat_name']
            member_usernames = request_data.get('member_usernames', [])

            # 验证聊天组名称
            valid, error_msg = validate_chat_group_name(chat_name)
            if not valid:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, error_msg)
                return

            # 获取成员用户ID
            member_ids = []
            for username in member_usernames:
                try:
                    member_info = self.user_manager.db.get_user_by_username(username)
                    member_ids.append(member_info['id'])
                except UserNotFoundError:
                    self.send_error(client_socket, ErrorCode.USER_NOT_FOUND, f"用户 '{username}' 不存在")
                    return

            # 创建聊天组
            self.chat_manager.create_chat_group(
                chat_name, user_info['user_id'], member_ids
            )

            # 发送成功响应
            response = SystemMessage(content=f"聊天组 '{chat_name}' 创建成功")
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"创建聊天组请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "创建聊天组失败")

    def handle_join_chat_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理加入聊天组请求"""
        try:
            # 验证用户登录
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if not user_info:
                self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
                return

            # 获取请求数据
            request_data = getattr(message, 'to_dict', lambda: {})()
            chat_name = request_data.get('chat_name', '')

            if not chat_name:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "聊天组名称不能为空")
                return

            # 加入聊天组
            self.chat_manager.join_chat_group(chat_name, user_info['user_id'])

            # 发送成功响应
            response = SystemMessage(content=f"成功加入聊天组 '{chat_name}'")
            self.send_message(client_socket, response)

        except ChatGroupNotFoundError as e:
            self.send_error(client_socket, ErrorCode.CHAT_NOT_FOUND, str(e))
        except Exception as e:
            print(f"加入聊天组请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "加入聊天组失败")

    def handle_enter_chat_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理进入聊天组请求"""
        try:
            # 验证用户登录
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if not user_info:
                self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
                return

            # 获取请求数据
            request_data = getattr(message, 'to_dict', lambda: {})()
            chat_name = request_data.get('chat_name', '')

            if not chat_name:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "聊天组名称不能为空")
                return

            # 进入聊天组
            self.chat_manager.enter_chat_group(chat_name, user_info['user_id'])

            # 发送成功响应
            response = SystemMessage(content=f"已进入聊天组 '{chat_name}'")
            self.send_message(client_socket, response)

        except ChatGroupNotFoundError as e:
            self.send_error(client_socket, ErrorCode.CHAT_NOT_FOUND, str(e))
        except PermissionDeniedError as e:
            self.send_error(client_socket, ErrorCode.PERMISSION_DENIED, str(e))
        except Exception as e:
            print(f"进入聊天组请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "进入聊天组失败")

    def handle_logout(self, client_socket: socket.socket):
        """处理登出请求"""
        try:
            # 获取用户信息
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if user_info:
                self.user_manager.logout_user(user_info['user_id'])

            # 发送成功响应
            response = SystemMessage(content="已成功登出")
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"登出处理错误: {e}")

    # 辅助方法
    def send_message(self, client_socket: socket.socket, message: BaseMessage):
        """发送消息到客户端"""
        ResponseHelper.send_message(client_socket, message)

    def send_error(self, client_socket: socket.socket, error_code: int, error_message: str):
        """发送错误消息"""
        ResponseHelper.send_error(client_socket, error_code, error_message)

    def verify_user_login(self, client_socket: socket.socket):
        """验证用户登录状态，返回用户信息或None"""
        user_info = self.user_manager.get_user_by_socket(client_socket)
        if not user_info:
            self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
            return None
        return user_info

    def get_request_data(self, message: BaseMessage, required_fields: list = None):
        """获取并验证请求数据"""
        try:
            request_data = getattr(message, 'to_dict', lambda: {})()

            # 检查必需字段
            if required_fields:
                for field in required_fields:
                    if field not in request_data or not request_data[field]:
                        return None, f"缺少必需字段: {field}"

            return request_data, None

        except Exception as e:
            return None, f"请求数据格式错误: {e}"

    def send_login_response(self, client_socket: socket.socket, success: bool,
                           user_id: int = None, username: str = None,
                           error_message: str = None, current_chat_group: dict = None):
        """发送登录响应"""
        response = LoginResponse(
            success=success,
            user_id=user_id,
            username=username,
            error_message=error_message,
            current_chat_group=current_chat_group
        )
        self.send_message(client_socket, response)

    def send_register_response(self, client_socket: socket.socket, success: bool,
                              user_id: int = None, username: str = None,
                              error_message: str = None):
        """发送注册响应"""
        response = RegisterResponse(
            success=success,
            user_id=user_id,
            username=username,
            error_message=error_message
        )
        self.send_message(client_socket, response)

    # 文件传输处理方法
    def handle_file_upload_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理文件上传请求"""
        try:
            # 验证用户登录
            user_info = self.verify_user_login(client_socket)
            if not user_info:
                return

            # 获取请求数据
            request_data, error_msg = self.get_request_data(message, ['chat_group_id', 'filename', 'file_size'])
            if error_msg:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, error_msg)
                return

            chat_group_id = request_data['chat_group_id']
            filename = request_data['filename']
            file_size = request_data['file_size']

            # 验证文件大小
            if file_size > MAX_FILE_SIZE:
                self.send_error(client_socket, ErrorCode.FILE_TOO_LARGE,
                              f"文件过大，最大支持 {MAX_FILE_SIZE // (1024*1024)}MB")
                return

            # 验证文件扩展名
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in ALLOWED_FILE_EXTENSIONS:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND,
                              f"不支持的文件类型: {file_ext}")
                return

            # 验证用户是否在聊天组中
            if not self.chat_manager.db.is_user_in_chat_group(chat_group_id, user_info['user_id']):
                self.send_error(client_socket, ErrorCode.PERMISSION_DENIED, "您不在此聊天组中")
                return

            # 生成唯一的服务器文件名
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            server_filepath = os.path.join(FILES_STORAGE_PATH, str(chat_group_id), unique_filename)

            # 确保目录存在
            os.makedirs(os.path.dirname(server_filepath), exist_ok=True)

            # 发送上传准备就绪响应
            response = FileUploadResponse(
                success=True,
                message="准备接收文件"
            )
            self.send_message(client_socket, response)

            # 接收文件数据
            self._receive_file_data(client_socket, server_filepath, file_size,
                                  filename, user_info['user_id'], chat_group_id)

        except Exception as e:
            print(f"文件上传请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "文件上传失败")

    def _receive_file_data(self, client_socket: socket.socket, server_filepath: str,
                          file_size: int, original_filename: str, uploader_id: int,
                          chat_group_id: int):
        """接收文件数据"""
        try:
            received_size = 0
            with open(server_filepath, 'wb') as f:
                while received_size < file_size:
                    # 计算本次接收的数据大小
                    chunk_size = min(FILE_CHUNK_SIZE, file_size - received_size)

                    # 接收数据
                    data = client_socket.recv(chunk_size)
                    if not data:
                        break

                    f.write(data)
                    received_size += len(data)

            # 验证文件大小
            if received_size != file_size:
                os.remove(server_filepath)
                self.send_error(client_socket, ErrorCode.SERVER_ERROR, "文件传输不完整")
                return

            # 保存文件元数据到数据库
            file_id = self.chat_manager.db.save_file_metadata(
                original_filename, server_filepath, file_size,
                uploader_id, chat_group_id
            )

            # 创建文件通知消息
            uploader_username = self.user_manager.db.get_user_by_id(uploader_id)['username']
            file_message_content = f"📎 {uploader_username} 上传了文件: {original_filename} ({file_size // 1024}KB)"

            # 保存文件通知消息
            message_id = self.chat_manager.db.save_message(
                chat_group_id, uploader_id, file_message_content, 'file_notification'
            )

            # 更新文件元数据中的消息ID
            self.chat_manager.db.update_file_message_id(file_id, message_id)

            # 广播文件通知到聊天组
            file_notification = ChatMessage(
                message_type=MessageType.FILE_NOTIFICATION,
                sender_id=uploader_id,
                sender_username=uploader_username,
                chat_group_id=chat_group_id,
                content=file_message_content,
                message_id=message_id
            )
            self.chat_manager.broadcast_message_to_group(file_notification)

            # 发送上传成功响应
            response = FileUploadResponse(
                success=True,
                message=f"文件 '{original_filename}' 上传成功",
                file_id=file_id
            )
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"文件数据接收错误: {e}")
            # 清理失败的文件
            if os.path.exists(server_filepath):
                os.remove(server_filepath)
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "文件接收失败")

    def handle_file_download_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理文件下载请求"""
        try:
            # 验证用户登录
            user_info = self.verify_user_login(client_socket)
            if not user_info:
                return

            # 获取请求数据
            request_data, error_msg = self.get_request_data(message, ['file_id'])
            if error_msg:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, error_msg)
                return

            file_id = request_data['file_id']

            # 获取文件元数据
            try:
                file_metadata = self.chat_manager.db.get_file_metadata_by_id(file_id)
            except Exception:
                self.send_error(client_socket, ErrorCode.FILE_NOT_FOUND, "文件不存在")
                return

            # 验证用户是否在文件所属的聊天组中
            if not self.chat_manager.db.is_user_in_chat_group(
                file_metadata['chat_group_id'], user_info['user_id']
            ):
                self.send_error(client_socket, ErrorCode.PERMISSION_DENIED, "您无权下载此文件")
                return

            # 检查文件是否存在
            server_filepath = file_metadata['server_filepath']
            if not os.path.exists(server_filepath):
                self.send_error(client_socket, ErrorCode.FILE_NOT_FOUND, "服务器上的文件不存在")
                return

            # 发送下载开始响应
            response = FileDownloadResponse(
                success=True,
                message="开始下载文件",
                filename=file_metadata['original_filename'],
                file_size=file_metadata['file_size']
            )
            self.send_message(client_socket, response)

            # 发送文件数据
            self._send_file_data(client_socket, server_filepath, file_metadata['original_filename'])

        except Exception as e:
            print(f"文件下载请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "文件下载失败")

    def _send_file_data(self, client_socket: socket.socket, server_filepath: str, filename: str):
        """发送文件数据"""
        try:
            with open(server_filepath, 'rb') as f:
                while True:
                    data = f.read(FILE_CHUNK_SIZE)
                    if not data:
                        break
                    client_socket.send(data)

            # 发送下载完成响应
            response = FileDownloadResponse(
                success=True,
                message=f"文件 '{filename}' 下载完成"
            )
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"文件数据发送错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "文件发送失败")

    def handle_file_list_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理文件列表请求"""
        try:
            # 验证用户登录
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if not user_info:
                self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
                return

            # 获取请求数据
            request_data = getattr(message, 'to_dict', lambda: {})()
            chat_group_id = request_data.get('chat_group_id')

            if not chat_group_id:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "聊天组ID不能为空")
                return

            # 验证用户是否在聊天组中
            if not self.chat_manager.db.is_user_in_chat_group(chat_group_id, user_info['user_id']):
                self.send_error(client_socket, ErrorCode.PERMISSION_DENIED, "您不在此聊天组中")
                return

            # 获取文件列表
            files_data = self.chat_manager.db.get_chat_group_files(chat_group_id)

            # 转换为FileInfo对象列表
            files = [
                FileInfo(
                    file_id=file_data['id'],
                    original_filename=file_data['original_filename'],
                    file_size=file_data['file_size'],
                    uploader_username=file_data['uploader_username'],
                    upload_time=file_data['upload_timestamp']
                )
                for file_data in files_data
            ]

            # 发送文件列表响应
            response = BaseMessage(
                message_type=MessageType.FILE_LIST_RESPONSE,
                success=True,
                files=files
            )
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"文件列表请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "获取文件列表失败")

    def handle_ai_chat_request(self, client_socket: socket.socket, message: BaseMessage):
        """处理AI聊天请求"""
        try:
            # 验证用户登录
            user_info = self.verify_user_login(client_socket)
            if not user_info:
                return

            # 检查AI功能是否启用
            if not self.ai_manager.is_enabled():
                self.send_error(client_socket, ErrorCode.SERVER_ERROR, "AI功能未启用")
                return

            # 获取请求数据
            request_data, error_msg = self.get_request_data(message)
            if error_msg:
                self.send_error(client_socket, ErrorCode.INVALID_COMMAND, error_msg)
                return

            user_message = request_data.get('message', '')
            chat_group_id = request_data.get('chat_group_id')  # None表示私聊
            command = request_data.get('command', '')

            # 处理AI命令
            if command:
                ai_response = self.ai_manager.handle_ai_command(
                    command, user_info['user_id'], chat_group_id
                )
            else:
                # 处理普通AI聊天
                if not user_message:
                    self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "消息内容不能为空")
                    return

                ai_response = self.ai_manager.process_message(
                    user_info['user_id'],
                    user_info['username'],
                    user_message,
                    chat_group_id
                )

                if not ai_response:
                    ai_response = "抱歉，我现在无法回复您的消息。"

            # 发送AI响应
            response = BaseMessage(
                message_type=MessageType.AI_CHAT_RESPONSE,
                success=True,
                message=ai_response
            )
            self.send_message(client_socket, response)

        except Exception as e:
            print(f"AI聊天请求处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "AI聊天处理失败")
