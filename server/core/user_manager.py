"""
用户管理模块
处理用户注册、登录、状态管理等功能
"""

import socket
from typing import Dict, List, Optional, Set
from datetime import datetime

from server.database.connection import get_db
from shared.constants import UserStatus, AI_USER_ID, AI_USERNAME
from shared.exceptions import (
    AuthenticationError, UserAlreadyExistsError, 
    UserNotFoundError, DatabaseError
)
from shared.messages import UserInfo


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        """初始化用户管理器"""
        self.db = get_db()
        # 在线用户连接映射 {user_id: socket}
        self.online_users: Dict[int, socket.socket] = {}
        # 用户会话信息 {user_id: user_info}
        self.user_sessions: Dict[int, Dict] = {}
    
    def register_user(self, username: str, password: str) -> int:
        """注册新用户"""
        try:
            # 检查用户名是否已存在
            try:
                self.db.get_user_by_username(username)
                raise UserAlreadyExistsError(username)
            except UserNotFoundError:
                # 用户不存在，可以注册
                pass
            
            # 创建新用户
            user_id = self.db.create_user(username, password)
            return user_id
            
        except DatabaseError as e:
            if "已存在" in str(e):
                raise UserAlreadyExistsError(username)
            raise e
    
    def authenticate_user(self, username: str, password: str) -> Dict:
        """用户认证"""
        user_info = self.db.authenticate_user(username, password)
        if not user_info:
            raise AuthenticationError("用户名或密码错误")
        return user_info
    
    def login_user(self, user_id: int, client_socket: socket.socket) -> Dict:
        """用户登录"""
        # 获取用户信息
        user_info = self.db.get_user_by_id(user_id)
        
        # 如果用户已在线，断开之前的连接
        if user_id in self.online_users:
            old_socket = self.online_users[user_id]
            try:
                old_socket.close()
            except:
                pass
        
        # 更新在线状态
        self.db.update_user_status(user_id, True)
        self.online_users[user_id] = client_socket
        self.user_sessions[user_id] = {
            'user_id': user_id,
            'username': user_info['username'],
            'login_time': datetime.now(),
            'current_chat_group': None
        }
        
        return user_info
    
    def logout_user(self, user_id: int):
        """用户登出"""
        if user_id in self.online_users:
            # 更新数据库状态
            self.db.update_user_status(user_id, False)
            
            # 移除在线记录
            del self.online_users[user_id]
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
    
    def disconnect_user(self, client_socket: socket.socket):
        """断开用户连接（通过socket查找用户）"""
        user_id = None
        for uid, sock in self.online_users.items():
            if sock == client_socket:
                user_id = uid
                break
        
        if user_id:
            self.logout_user(user_id)
    
    def get_user_by_socket(self, client_socket: socket.socket) -> Optional[Dict]:
        """通过socket获取用户信息"""
        for user_id, sock in self.online_users.items():
            if sock == client_socket:
                return self.user_sessions.get(user_id)
        return None
    
    def get_online_users(self) -> List[UserInfo]:
        """获取在线用户列表"""
        online_user_ids = list(self.online_users.keys())
        users = []
        
        for user_id in online_user_ids:
            try:
                user_info = self.db.get_user_by_id(user_id)
                users.append(UserInfo(
                    user_id=user_info['id'],
                    username=user_info['username'],
                    is_online=True
                ))
            except UserNotFoundError:
                # 用户可能已被删除，从在线列表中移除
                if user_id in self.online_users:
                    del self.online_users[user_id]
                if user_id in self.user_sessions:
                    del self.user_sessions[user_id]
        
        return users
    
    def get_all_users(self) -> List[UserInfo]:
        """获取所有用户列表"""
        users_data = self.db.get_all_users()
        return [
            UserInfo(
                user_id=user['id'],
                username=user['username'],
                is_online=bool(user['is_online'])
            )
            for user in users_data
        ]
    
    def get_user_info(self, user_id: int) -> Dict:
        """获取用户详细信息"""
        user_info = self.db.get_user_by_id(user_id)
        
        # 获取统计信息
        user_chats = self.db.get_user_chat_groups(user_id)
        private_chats = [chat for chat in user_chats if chat['is_private_chat']]
        group_chats = [chat for chat in user_chats if not chat['is_private_chat']]
        
        return {
            'user_info': UserInfo(
                user_id=user_info['id'],
                username=user_info['username'],
                is_online=bool(user_info['is_online'])
            ),
            'joined_chats_count': len(user_chats),
            'private_chats_count': len(private_chats),
            'group_chats_count': len(group_chats),
            'total_users_count': self.db.get_total_users_count(),
            'online_users_count': self.db.get_online_users_count(),
            'total_chats_count': self.db.get_total_chat_groups_count()
        }
    
    def is_user_online(self, user_id: int) -> bool:
        """检查用户是否在线"""
        return user_id in self.online_users
    
    def get_user_socket(self, user_id: int) -> Optional[socket.socket]:
        """获取用户的socket连接"""
        return self.online_users.get(user_id)
    
    def set_user_current_chat(self, user_id: int, chat_group_id: int):
        """设置用户当前聊天组"""
        if user_id in self.user_sessions:
            self.user_sessions[user_id]['current_chat_group'] = chat_group_id
    
    def get_user_current_chat(self, user_id: int) -> Optional[int]:
        """获取用户当前聊天组"""
        session = self.user_sessions.get(user_id)
        return session['current_chat_group'] if session else None
