"""
聊天室服务器核心模块
处理客户端连接、消息路由、协议解析等核心功能
"""

import socket
import threading
import json
import time
from typing import Dict, Any, Optional

from server.core.user_manager import UserManager
from server.core.chat_manager import ChatManager
from server.database.connection import init_database
from server.utils.auth import (
    validate_username, validate_password, validate_chat_group_name,
    sanitize_message_content
)
from shared.constants import (
    DEFAULT_HOST, DEFAULT_PORT, BUFFER_SIZE, MAX_CONNECTIONS,
    MessageType, ErrorCode
)
from shared.messages import (
    parse_message, BaseMessage, LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse, ChatMessage, SystemMessage,
    ErrorMessage, UserInfoResponse, ListUsersResponse, ListChatsResponse
)
from shared.exceptions import (
    ChatRoomException, AuthenticationError, UserAlreadyExistsError,
    UserNotFoundError, ChatGroupNotFoundError, PermissionDeniedError
)


class ChatRoomServer:
    """聊天室服务器"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化服务器"""
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        
        # 初始化管理器
        self.user_manager = UserManager()
        self.chat_manager = ChatManager(self.user_manager)
        
        print(f"聊天室服务器初始化完成 - {host}:{port}")
    
    def start(self):
        """启动服务器"""
        try:
            # 初始化数据库
            init_database()
            
            # 创建服务器socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_CONNECTIONS)
            
            self.running = True
            print(f"服务器启动成功，监听 {self.host}:{self.port}")
            print(f"最大连接数: {MAX_CONNECTIONS}")
            
            # 接受客户端连接
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
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
                        print(f"接受连接时出错: {e}")
                    
        except Exception as e:
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
                    
                    # 处理可能的多条消息
                    for line in message_str.split('\n'):
                        if line.strip():
                            self.process_message(client_socket, line.strip())
                            
                except UnicodeDecodeError:
                    self.send_error(client_socket, ErrorCode.INVALID_COMMAND, "消息编码错误")
                except Exception as e:
                    print(f"处理消息时出错: {e}")
                    self.send_error(client_socket, ErrorCode.SERVER_ERROR, "服务器内部错误")
                    
        except ConnectionResetError:
            print(f"客户端 {client_address} 连接重置")
        except Exception as e:
            print(f"处理客户端 {client_address} 时出错: {e}")
        finally:
            # 清理连接
            self.user_manager.disconnect_user(client_socket)
            try:
                client_socket.close()
            except:
                pass
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
        try:
            # 验证用户名和密码格式
            valid, error_msg = validate_username(message.username)
            if not valid:
                self.send_login_response(client_socket, False, error_message=error_msg)
                return
            
            valid, error_msg = validate_password(message.password)
            if not valid:
                self.send_login_response(client_socket, False, error_message=error_msg)
                return
            
            # 认证用户
            user_info = self.user_manager.authenticate_user(message.username, message.password)
            
            # 登录用户
            self.user_manager.login_user(user_info['id'], client_socket)
            
            # 发送成功响应
            self.send_login_response(
                client_socket, True,
                user_id=user_info['id'],
                username=user_info['username']
            )
            
            # 自动进入公频聊天组
            public_chat_id = self.chat_manager.get_public_chat_id()
            self.user_manager.set_user_current_chat(user_info['id'], public_chat_id)
            
        except AuthenticationError as e:
            self.send_login_response(client_socket, False, error_message=str(e))
        except Exception as e:
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

            # 发送消息
            chat_message = self.chat_manager.send_message(
                user_info['user_id'], message.chat_group_id, content
            )

            # 广播消息到聊天组
            self.chat_manager.broadcast_message_to_group(chat_message)

        except PermissionDeniedError as e:
            self.send_error(client_socket, ErrorCode.PERMISSION_DENIED, str(e))
        except Exception as e:
            print(f"聊天消息处理错误: {e}")
            self.send_error(client_socket, ErrorCode.SERVER_ERROR, "消息发送失败")

    def handle_user_info_request(self, client_socket: socket.socket):
        """处理用户信息请求"""
        try:
            # 获取用户信息
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if not user_info:
                self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
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
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if not user_info:
                self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
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
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if not user_info:
                self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
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
            user_info = self.user_manager.get_user_by_socket(client_socket)
            if not user_info:
                self.send_error(client_socket, ErrorCode.INVALID_CREDENTIALS, "请先登录")
                return

            # 获取请求数据
            request_data = getattr(message, 'to_dict', lambda: {})()
            chat_name = request_data.get('chat_name', '')
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
            group_info = self.chat_manager.enter_chat_group(chat_name, user_info['user_id'])

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
        try:
            message_json = message.to_json() + '\n'
            client_socket.send(message_json.encode('utf-8'))
        except Exception as e:
            print(f"发送消息失败: {e}")

    def send_error(self, client_socket: socket.socket, error_code: int, error_message: str):
        """发送错误消息"""
        error_msg = ErrorMessage(error_code=error_code, error_message=error_message)
        self.send_message(client_socket, error_msg)

    def send_login_response(self, client_socket: socket.socket, success: bool,
                           user_id: int = None, username: str = None,
                           error_message: str = None):
        """发送登录响应"""
        response = LoginResponse(
            success=success,
            user_id=user_id,
            username=username,
            error_message=error_message
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
