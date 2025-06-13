"""
聊天管理模块
处理聊天组创建、消息发送、聊天历史等功能
"""

import json
from typing import List, Dict, Optional
from datetime import datetime

from server.database.connection import get_db
from shared.constants import ChatType, DEFAULT_PUBLIC_CHAT, MessageType
from shared.exceptions import ChatGroupNotFoundError, PermissionDeniedError
from shared.messages import ChatMessage, ChatGroupInfo, UserInfo


class ChatManager:
    """聊天管理器"""
    
    def __init__(self, user_manager):
        """初始化聊天管理器"""
        self.db = get_db()
        self.user_manager = user_manager
    
    def create_chat_group(self, name: str, creator_id: int,
                         initial_members: List[int] = None,
                         is_private_chat: bool = False) -> int:
        """创建聊天组"""
        from shared.constants import AI_USER_ID

        # 创建聊天组
        group_id = self.db.create_chat_group(name, is_private_chat)

        # 添加创建者到聊天组
        self.db.add_user_to_chat_group(group_id, creator_id)

        # 自动添加AI用户到所有聊天组（除了私聊）
        if not is_private_chat:
            try:
                self.db.add_user_to_chat_group(group_id, AI_USER_ID)
            except Exception as e:
                print(f"警告：无法将AI用户添加到聊天组 {name}: {e}")

        # 添加初始成员
        # 对于私聊：自动添加所有初始成员
        # 对于普通群聊：不自动添加其他用户，他们需要主动加入
        if initial_members:
            for user_id in initial_members:
                if user_id != creator_id:  # 避免重复添加创建者
                    try:
                        # 验证用户是否存在
                        self.db.get_user_by_id(user_id)
                        # 只对私聊自动添加成员
                        if is_private_chat:
                            self.db.add_user_to_chat_group(group_id, user_id)
                    except:
                        # 忽略不存在的用户
                        pass

        return group_id
    
    def join_chat_group(self, group_name: str, user_id: int) -> Dict:
        """加入聊天组"""
        # 获取聊天组信息
        group_info = self.db.get_chat_group_by_name(group_name)
        group_id = group_info['id']
        
        # 检查是否已在聊天组中
        if self.db.is_user_in_chat_group(group_id, user_id):
            return group_info
        
        # 添加用户到聊天组
        self.db.add_user_to_chat_group(group_id, user_id)
        
        return group_info
    
    def enter_chat_group(self, group_name: str, user_id: int) -> Dict:
        """进入聊天组（需要已是成员）"""
        # 获取聊天组信息
        group_info = self.db.get_chat_group_by_name(group_name)
        group_id = group_info['id']

        # 检查用户是否在聊天组中
        if not self.db.is_user_in_chat_group(group_id, user_id):
            raise PermissionDeniedError(f"您不是聊天组 '{group_name}' 的成员")

        # 设置用户当前聊天组
        self.user_manager.set_user_current_chat(user_id, group_id)

        return group_info

    def load_chat_history_for_user(self, group_id: int, user_id: int, limit: int = 50) -> List[ChatMessage]:
        """为用户加载聊天组历史消息"""
        # 验证用户是否在聊天组中
        if not self.db.is_user_in_chat_group(group_id, user_id):
            raise PermissionDeniedError("您不在此聊天组中")

        # 获取历史消息
        history_data = self.db.get_chat_history(group_id, limit)

        # 转换为ChatMessage对象列表
        history_messages = []
        for msg_data in history_data:
            message = ChatMessage(
                message_type=MessageType.CHAT_HISTORY,  # 设置为历史消息类型
                message_id=msg_data['id'],
                sender_id=msg_data['sender_id'],
                sender_username=msg_data['sender_username'],
                chat_group_id=group_id,
                chat_group_name="",  # 可以后续填充
                content=msg_data['content'],
                timestamp=msg_data['timestamp']
            )
            history_messages.append(message)

        return history_messages
    
    def send_message(self, sender_id: int, group_id: int, content: str) -> ChatMessage:
        """发送消息"""
        from shared.constants import AI_USER_ID

        # AI用户特殊处理：确保AI用户在所有聊天组中
        if sender_id == AI_USER_ID:
            # 确保AI用户在该聊天组中
            if not self.db.is_user_in_chat_group(group_id, sender_id):
                self.db.add_user_to_chat_group(group_id, sender_id)
        else:
            # 普通用户需要验证权限
            if not self.db.is_user_in_chat_group(group_id, sender_id):
                raise PermissionDeniedError("您不在此聊天组中")

        # 获取发送者和聊天组信息
        sender_info = self.db.get_user_by_id(sender_id)
        group_info = self.db.get_chat_group_by_id(group_id)

        # 保存消息到数据库
        message_id = self.db.save_message(group_id, sender_id, content)

        # 创建消息对象
        message = ChatMessage(
            message_id=message_id,
            sender_id=sender_id,
            sender_username=sender_info['username'],
            chat_group_id=group_id,
            chat_group_name=group_info['name'],
            content=content
        )

        return message
    
    def broadcast_message_to_group(self, message: ChatMessage):
        """向聊天组广播消息"""
        # 获取聊天组成员
        members = self.db.get_chat_group_members(message.chat_group_id)

        # 向在线成员发送消息，但只发送给当前在该聊天组中的用户
        for member in members:
            user_id = member['id']
            if self.user_manager.is_user_online(user_id):
                # 检查用户当前是否在这个聊天组中
                current_chat_group = self.user_manager.get_user_current_chat(user_id)
                if current_chat_group == message.chat_group_id:
                    user_socket = self.user_manager.get_user_socket(user_id)
                    if user_socket:
                        try:
                            message_json = message.to_json() + '\n'
                            user_socket.send(message_json.encode('utf-8'))
                        except:
                            # 发送失败，可能连接已断开
                            self.user_manager.disconnect_user(user_socket)
    
    def get_chat_history(self, group_id: int, user_id: int, limit: int = 50) -> List[Dict]:
        """获取聊天历史"""
        # 验证用户是否在聊天组中
        if not self.db.is_user_in_chat_group(group_id, user_id):
            raise PermissionDeniedError("您不在此聊天组中")
        
        return self.db.get_chat_history(group_id, limit)
    
    def get_chat_group_members(self, group_id: int, user_id: int) -> List[UserInfo]:
        """获取聊天组成员列表"""
        # 验证用户是否在聊天组中
        if not self.db.is_user_in_chat_group(group_id, user_id):
            raise PermissionDeniedError("您不在此聊天组中")
        
        members_data = self.db.get_chat_group_members(group_id)
        return [
            UserInfo(
                user_id=member['id'],
                username=member['username'],
                is_online=bool(member['is_online'])
            )
            for member in members_data
        ]
    
    def get_user_chat_groups(self, user_id: int) -> List[ChatGroupInfo]:
        """获取用户加入的聊天组列表"""
        chats_data = self.db.get_user_chat_groups(user_id)
        return [
            ChatGroupInfo(
                group_id=chat['id'],
                group_name=chat['name'],
                is_private_chat=bool(chat['is_private_chat']),
                member_count=chat['member_count'],
                created_at=chat['created_at']
            )
            for chat in chats_data
        ]
    
    def get_all_group_chats(self) -> List[ChatGroupInfo]:
        """获取所有群聊列表"""
        chats_data = self.db.get_all_group_chats()
        return [
            ChatGroupInfo(
                group_id=chat['id'],
                group_name=chat['name'],
                is_private_chat=bool(chat['is_private_chat']),
                member_count=chat['member_count'],
                created_at=chat['created_at']
            )
            for chat in chats_data
        ]
    
    def create_private_chat(self, user1_id: int, user2_id: int) -> int:
        """创建私聊"""
        # 检查是否已存在私聊
        user1_chats = self.db.get_user_chat_groups(user1_id)
        user2_chats = self.db.get_user_chat_groups(user2_id)
        
        # 查找共同的私聊
        for chat1 in user1_chats:
            if chat1['is_private_chat']:
                for chat2 in user2_chats:
                    if chat2['id'] == chat1['id'] and chat2['is_private_chat']:
                        return chat1['id']
        
        # 创建新的私聊
        user1_info = self.db.get_user_by_id(user1_id)
        user2_info = self.db.get_user_by_id(user2_id)
        
        # 私聊名称格式：user1_user2
        chat_name = f"{user1_info['username']}_{user2_info['username']}"
        
        return self.create_chat_group(
            name=chat_name,
            creator_id=user1_id,
            initial_members=[user2_id],
            is_private_chat=True
        )
    
    def get_public_chat_id(self) -> int:
        """获取公频聊天组ID"""
        public_chat = self.db.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)
        return public_chat['id']
