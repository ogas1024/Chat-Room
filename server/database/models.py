"""
数据库模型定义
定义用户、聊天组、消息、文件等数据表结构和操作方法
"""

import sqlite3
import hashlib
import os
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from shared.constants import ChatType, DEFAULT_PUBLIC_CHAT
from shared.exceptions import DatabaseError, UserNotFoundError, ChatGroupNotFoundError
from shared.logger import get_logger, log_database_operation


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str):
        """初始化数据库管理器"""
        self.db_path = db_path
        self.logger = get_logger("database")
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
        self.logger.info("数据库管理器初始化完成", db_path=db_path)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
            yield conn
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"数据库操作失败: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_online INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建聊天组表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    is_private_chat INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建聊天组成员表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS group_members (
                    group_id INTEGER,
                    user_id INTEGER,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (group_id, user_id),
                    FOREIGN KEY (group_id) REFERENCES chat_groups(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            
            # 创建消息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER,
                    sender_id INTEGER,
                    content TEXT,
                    message_type TEXT DEFAULT 'text',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES chat_groups(id),
                    FOREIGN KEY (sender_id) REFERENCES users(id)
                )
            ''')
            
            # 创建文件元数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_filename TEXT NOT NULL,
                    server_filepath TEXT NOT NULL UNIQUE,
                    file_size INTEGER NOT NULL,
                    uploader_id INTEGER,
                    chat_group_id INTEGER,
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_id INTEGER,
                    FOREIGN KEY (uploader_id) REFERENCES users(id),
                    FOREIGN KEY (chat_group_id) REFERENCES chat_groups(id),
                    FOREIGN KEY (message_id) REFERENCES messages(id)
                )
            ''')
            
            conn.commit()

            # 创建默认公频聊天组
            self._create_default_public_chat(conn)

            # 创建AI用户
            self._create_ai_user(conn)

            # 创建管理员用户
            self._create_admin_user(conn)
    
    def _create_default_public_chat(self, conn: sqlite3.Connection):
        """创建默认的公频聊天组"""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM chat_groups WHERE name = ?",
            (DEFAULT_PUBLIC_CHAT,)
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO chat_groups (name, is_private_chat) VALUES (?, ?)",
                (DEFAULT_PUBLIC_CHAT, ChatType.GROUP_CHAT)
            )
            conn.commit()

    def _create_ai_user(self, conn: sqlite3.Connection):
        """创建AI用户"""
        from shared.constants import AI_USER_ID, AI_USERNAME

        cursor = conn.cursor()

        # 检查AI用户是否已存在
        cursor.execute("SELECT id FROM users WHERE id = ?", (AI_USER_ID,))
        if cursor.fetchone():
            return  # AI用户已存在

        # 创建AI用户，使用特殊的ID
        cursor.execute(
            "INSERT OR IGNORE INTO users (id, username, password_hash, is_online) VALUES (?, ?, ?, ?)",
            (AI_USER_ID, AI_USERNAME, "ai_user_no_password", 1)  # AI用户始终在线
        )

        # 将AI用户添加到所有聊天组
        cursor.execute("SELECT id FROM chat_groups")
        chat_groups = cursor.fetchall()

        for group in chat_groups:
            group_id = group[0]
            cursor.execute(
                "INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?, ?)",
                (group_id, AI_USER_ID)
            )

        conn.commit()
        print(f"✅ AI用户 '{AI_USERNAME}' 已创建并加入所有聊天组")

    def _create_admin_user(self, conn: sqlite3.Connection):
        """创建管理员用户"""
        from shared.constants import ADMIN_USER_ID, ADMIN_USERNAME

        cursor = conn.cursor()

        # 检查管理员用户是否已存在
        cursor.execute("SELECT id FROM users WHERE id = ?", (ADMIN_USER_ID,))
        if cursor.fetchone():
            return  # 管理员用户已存在

        # 创建管理员用户，使用特殊的ID=0
        cursor.execute(
            "INSERT OR IGNORE INTO users (id, username, password_hash, is_online) VALUES (?, ?, ?, ?)",
            (ADMIN_USER_ID, ADMIN_USERNAME, self.hash_password("admin123"), 0)  # 管理员默认离线
        )

        # 将管理员用户添加到所有聊天组
        cursor.execute("SELECT id FROM chat_groups")
        chat_groups = cursor.fetchall()

        for group in chat_groups:
            group_id = group[0]
            cursor.execute(
                "INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?, ?)",
                (group_id, ADMIN_USER_ID)
            )

        conn.commit()
        print(f"✅ 管理员用户 '{ADMIN_USERNAME}' 已创建并加入所有聊天组")
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str) -> int:
        """创建新用户"""
        password_hash = self.hash_password(password)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                user_id = cursor.lastrowid

                # 自动加入公频聊天组
                public_chat_id = self.get_chat_group_by_name(DEFAULT_PUBLIC_CHAT)['id']
                cursor.execute(
                    "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
                    (public_chat_id, user_id)
                )

                conn.commit()

                # 记录日志
                self.logger.info("创建新用户", user_id=user_id, username=username)
                log_database_operation("create", "users", user_id=user_id, username=username)

                return user_id
            except sqlite3.IntegrityError:
                self.logger.warning("用户创建失败：用户名已存在", username=username)
                raise DatabaseError(f"用户名 '{username}' 已存在")
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用户认证"""
        password_hash = self.hash_password(password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            row = cursor.fetchone()
            if row:
                return {"id": row["id"], "username": row["username"]}
            return None
    
    def update_user_status(self, user_id: int, is_online: bool):
        """更新用户在线状态"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET is_online = ? WHERE id = ?",
                (int(is_online), user_id)
            )
            conn.commit()
    
    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """根据ID获取用户信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, is_online FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            raise UserNotFoundError(user_id=user_id)
    
    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """根据用户名获取用户信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, is_online FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            raise UserNotFoundError(username=username)

    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, is_online FROM users ORDER BY username"
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_online_users_count(self) -> int:
        """获取在线用户数量"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_online = 1")
            return cursor.fetchone()["count"]

    def get_total_users_count(self) -> int:
        """获取总用户数量"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            return cursor.fetchone()["count"]

    def create_chat_group(self, name: str, is_private_chat: bool = False) -> int:
        """创建聊天组"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO chat_groups (name, is_private_chat) VALUES (?, ?)",
                    (name, int(is_private_chat))
                )
                group_id = cursor.lastrowid
                conn.commit()
                return group_id
            except sqlite3.IntegrityError:
                raise DatabaseError(f"聊天组名称 '{name}' 已存在")

    def get_chat_group_by_name(self, name: str) -> Dict[str, Any]:
        """根据名称获取聊天组信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, is_private_chat, created_at FROM chat_groups WHERE name = ?",
                (name,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            raise ChatGroupNotFoundError(chat_name=name)

    def get_chat_group_by_id(self, group_id: int) -> Dict[str, Any]:
        """根据ID获取聊天组信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, is_private_chat, created_at FROM chat_groups WHERE id = ?",
                (group_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            raise ChatGroupNotFoundError(chat_id=group_id)

    def add_user_to_chat_group(self, group_id: int, user_id: int):
        """将用户添加到聊天组"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
                    (group_id, user_id)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # 用户已在聊天组中，忽略
                pass

    def remove_user_from_chat_group(self, group_id: int, user_id: int):
        """从聊天组中移除用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM group_members WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            conn.commit()

    def is_user_in_chat_group(self, group_id: int, user_id: int) -> bool:
        """检查用户是否在聊天组中"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
                (group_id, user_id)
            )
            return cursor.fetchone() is not None

    def get_chat_group_members(self, group_id: int) -> List[Dict[str, Any]]:
        """获取聊天组成员列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT u.id, u.username, u.is_online, gm.joined_at
                FROM users u
                JOIN group_members gm ON u.id = gm.user_id
                WHERE gm.group_id = ?
                ORDER BY u.username
            ''', (group_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_user_chat_groups(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户加入的聊天组列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cg.id, cg.name, cg.is_private_chat, cg.created_at,
                       COUNT(gm2.user_id) as member_count
                FROM chat_groups cg
                JOIN group_members gm ON cg.id = gm.group_id
                LEFT JOIN group_members gm2 ON cg.id = gm2.group_id
                WHERE gm.user_id = ?
                GROUP BY cg.id, cg.name, cg.is_private_chat, cg.created_at
                ORDER BY cg.name
            ''', (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_group_chats(self) -> List[Dict[str, Any]]:
        """获取所有群聊（非私聊）列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cg.id, cg.name, cg.is_private_chat, cg.created_at,
                       COUNT(gm.user_id) as member_count
                FROM chat_groups cg
                LEFT JOIN group_members gm ON cg.id = gm.group_id
                WHERE cg.is_private_chat = 0
                GROUP BY cg.id, cg.name, cg.is_private_chat, cg.created_at
                ORDER BY cg.name
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def get_total_chat_groups_count(self) -> int:
        """获取聊天组总数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM chat_groups")
            return cursor.fetchone()["count"]

    def save_message(self, group_id: int, sender_id: int, content: str,
                    message_type: str = 'text') -> int:
        """保存消息到数据库"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (group_id, sender_id, content, message_type)
                VALUES (?, ?, ?, ?)
            ''', (group_id, sender_id, content, message_type))
            message_id = cursor.lastrowid
            conn.commit()
            return message_id

    def get_chat_history(self, group_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取聊天历史记录"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.id, m.content, m.message_type, m.timestamp,
                       u.id as sender_id, u.username as sender_username
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.group_id = ?
                ORDER BY m.timestamp DESC
                LIMIT ?
            ''', (group_id, limit))
            messages = [dict(row) for row in cursor.fetchall()]
            return list(reversed(messages))  # 按时间正序返回

    def save_file_metadata(self, original_filename: str, server_filepath: str,
                          file_size: int, uploader_id: int, chat_group_id: int,
                          message_id: int = None) -> int:
        """保存文件元数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO files_metadata
                (original_filename, server_filepath, file_size, uploader_id,
                 chat_group_id, message_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (original_filename, server_filepath, file_size, uploader_id,
                  chat_group_id, message_id))
            file_id = cursor.lastrowid
            conn.commit()
            return file_id

    def get_chat_group_files(self, group_id: int) -> List[Dict[str, Any]]:
        """获取聊天组的文件列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fm.id, fm.original_filename, fm.file_size,
                       fm.upload_timestamp, u.username as uploader_username
                FROM files_metadata fm
                JOIN users u ON fm.uploader_id = u.id
                WHERE fm.chat_group_id = ?
                ORDER BY fm.upload_timestamp DESC
            ''', (group_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_file_metadata_by_id(self, file_id: int) -> Dict[str, Any]:
        """根据ID获取文件元数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fm.*, u.username as uploader_username
                FROM files_metadata fm
                JOIN users u ON fm.uploader_id = u.id
                WHERE fm.id = ?
            ''', (file_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            raise DatabaseError(f"文件ID {file_id} 不存在")

    def update_file_message_id(self, file_id: int, message_id: int):
        """更新文件元数据中的消息ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE files_metadata
                SET message_id = ?
                WHERE id = ?
            ''', (message_id, file_id))
            conn.commit()

    # ==================== 管理员功能相关方法 ====================

    def is_admin_user(self, user_id: int) -> bool:
        """检查用户是否为管理员"""
        from shared.constants import ADMIN_USER_ID
        return user_id == ADMIN_USER_ID

    def ban_user(self, user_id: int):
        """禁言用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET is_banned = 1 WHERE id = ?",
                (user_id,)
            )
            conn.commit()

            # 记录日志
            self.logger.info("用户被禁言", user_id=user_id)
            log_database_operation("ban", "users", user_id=user_id)

    def unban_user(self, user_id: int):
        """解除用户禁言"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET is_banned = 0 WHERE id = ?",
                (user_id,)
            )
            conn.commit()

            # 记录日志
            self.logger.info("用户解除禁言", user_id=user_id)
            log_database_operation("unban", "users", user_id=user_id)

    def is_user_banned(self, user_id: int) -> bool:
        """检查用户是否被禁言"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_banned FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return bool(row["is_banned"]) if row else False

    def ban_chat_group(self, group_id: int):
        """禁言聊天组"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chat_groups SET is_banned = 1 WHERE id = ?",
                (group_id,)
            )
            conn.commit()

            # 记录日志
            self.logger.info("聊天组被禁言", group_id=group_id)
            log_database_operation("ban", "chat_groups", group_id=group_id)

    def unban_chat_group(self, group_id: int):
        """解除聊天组禁言"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chat_groups SET is_banned = 0 WHERE id = ?",
                (group_id,)
            )
            conn.commit()

            # 记录日志
            self.logger.info("聊天组解除禁言", group_id=group_id)
            log_database_operation("unban", "chat_groups", group_id=group_id)

    def is_chat_group_banned(self, group_id: int) -> bool:
        """检查聊天组是否被禁言"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT is_banned FROM chat_groups WHERE id = ?",
                (group_id,)
            )
            row = cursor.fetchone()
            return bool(row["is_banned"]) if row else False

    def delete_user(self, user_id: int):
        """删除用户（管理员操作）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 先删除相关的外键记录
            cursor.execute("DELETE FROM group_members WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM messages WHERE sender_id = ?", (user_id,))
            cursor.execute("DELETE FROM files_metadata WHERE uploader_id = ?", (user_id,))

            # 删除用户记录
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

            conn.commit()

            # 记录日志
            self.logger.info("用户被删除", user_id=user_id)
            log_database_operation("delete", "users", user_id=user_id)

    def delete_chat_group(self, group_id: int):
        """删除聊天组（管理员操作）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 先删除相关的外键记录
            cursor.execute("DELETE FROM group_members WHERE group_id = ?", (group_id,))
            cursor.execute("DELETE FROM messages WHERE group_id = ?", (group_id,))
            cursor.execute("DELETE FROM files_metadata WHERE chat_group_id = ?", (group_id,))

            # 删除聊天组记录
            cursor.execute("DELETE FROM chat_groups WHERE id = ?", (group_id,))

            conn.commit()

            # 记录日志
            self.logger.info("聊天组被删除", group_id=group_id)
            log_database_operation("delete", "chat_groups", group_id=group_id)

    def get_banned_users(self) -> List[Dict[str, Any]]:
        """获取被禁言的用户列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username FROM users WHERE is_banned = 1 ORDER BY username"
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_banned_chat_groups(self) -> List[Dict[str, Any]]:
        """获取被禁言的聊天组列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name FROM chat_groups WHERE is_banned = 1 ORDER BY name"
            )
            return [dict(row) for row in cursor.fetchall()]

    def update_user_info(self, user_id: int, username: str = None, password: str = None):
        """更新用户信息（管理员操作）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if username:
                cursor.execute(
                    "UPDATE users SET username = ? WHERE id = ?",
                    (username, user_id)
                )

            if password:
                password_hash = self.hash_password(password)
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (password_hash, user_id)
                )

            conn.commit()

            # 记录日志
            self.logger.info("用户信息被更新", user_id=user_id, username=username)
            log_database_operation("update", "users", user_id=user_id, username=username)

    def update_chat_group_info(self, group_id: int, name: str = None):
        """更新聊天组信息（管理员操作）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if name:
                cursor.execute(
                    "UPDATE chat_groups SET name = ? WHERE id = ?",
                    (name, group_id)
                )

            conn.commit()

            # 记录日志
            self.logger.info("聊天组信息被更新", group_id=group_id, name=name)
            log_database_operation("update", "chat_groups", group_id=group_id, name=name)
