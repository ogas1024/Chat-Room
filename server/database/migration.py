"""
数据库迁移脚本
处理数据库表结构的升级和数据迁移
"""

import sqlite3
import os
from typing import List, Tuple
from contextlib import contextmanager

from shared.logger import get_logger
from shared.constants import ADMIN_USER_ID, ADMIN_USERNAME


class DatabaseMigration:
    """数据库迁移管理器"""
    
    def __init__(self, db_path: str):
        """
        初始化数据库迁移管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.logger = get_logger(__name__)
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def check_column_exists(self, table_name: str, column_name: str) -> bool:
        """检查表中是否存在指定列"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            return column_name in columns
    
    def add_column_if_not_exists(self, table_name: str, column_name: str, column_type: str, default_value: str = ""):
        """如果列不存在则添加列"""
        if not self.check_column_exists(table_name, column_name):
            with self.get_connection() as conn:
                cursor = conn.cursor()
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                if default_value:
                    sql += f" DEFAULT {default_value}"
                cursor.execute(sql)
                conn.commit()
                self.logger.info(f"添加列 {table_name}.{column_name}")
                return True
        return False
    
    def migrate_to_admin_support(self):
        """迁移数据库以支持管理员功能"""
        self.logger.info("开始数据库迁移：添加管理员功能支持")
        
        try:
            # 为users表添加is_banned字段
            if self.add_column_if_not_exists("users", "is_banned", "INTEGER", "0"):
                self.logger.info("为users表添加is_banned字段")
            
            # 为chat_groups表添加is_banned字段
            if self.add_column_if_not_exists("chat_groups", "is_banned", "INTEGER", "0"):
                self.logger.info("为chat_groups表添加is_banned字段")
            
            # 创建管理员用户
            self._create_admin_user_if_not_exists()
            
            self.logger.info("数据库迁移完成：管理员功能支持已添加")
            
        except Exception as e:
            self.logger.error(f"数据库迁移失败: {e}")
            raise
    
    def _create_admin_user_if_not_exists(self):
        """如果管理员用户不存在则创建"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查管理员用户是否已存在
            cursor.execute("SELECT id FROM users WHERE id = ?", (ADMIN_USER_ID,))
            if cursor.fetchone():
                self.logger.info("管理员用户已存在，跳过创建")
                return
            
            # 创建管理员用户
            import hashlib
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            cursor.execute(
                "INSERT INTO users (id, username, password_hash, is_online, is_banned) VALUES (?, ?, ?, ?, ?)",
                (ADMIN_USER_ID, ADMIN_USERNAME, password_hash, 0, 0)
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
            self.logger.info(f"管理员用户 '{ADMIN_USERNAME}' 已创建并加入所有聊天组")
    
    def get_migration_status(self) -> dict:
        """获取迁移状态"""
        status = {
            "users_has_is_banned": self.check_column_exists("users", "is_banned"),
            "chat_groups_has_is_banned": self.check_column_exists("chat_groups", "is_banned"),
            "admin_user_exists": False
        }
        
        # 检查管理员用户是否存在
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE id = ?", (ADMIN_USER_ID,))
                status["admin_user_exists"] = cursor.fetchone() is not None
        except Exception:
            pass
        
        return status
    
    def run_all_migrations(self):
        """运行所有迁移"""
        self.logger.info("开始运行所有数据库迁移")
        
        # 检查当前状态
        status = self.get_migration_status()
        self.logger.info(f"当前迁移状态: {status}")
        
        # 运行管理员功能迁移
        if not all([status["users_has_is_banned"], status["chat_groups_has_is_banned"], status["admin_user_exists"]]):
            self.migrate_to_admin_support()
        else:
            self.logger.info("所有迁移已完成，无需重复执行")


def run_migration(db_path: str):
    """运行数据库迁移的便捷函数"""
    migration = DatabaseMigration(db_path)
    migration.run_all_migrations()


if __name__ == "__main__":
    # 用于测试迁移脚本
    import sys
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "server/database/chat_room.db"
    
    run_migration(db_path)
