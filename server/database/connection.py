"""
数据库连接管理
提供数据库连接的单例管理和初始化功能
"""

import os
from typing import Optional

from server.database.models import DatabaseManager
from shared.constants import DATABASE_PATH


class DatabaseConnection:
    """数据库连接单例管理器"""
    
    _instance: Optional[DatabaseManager] = None
    _db_path: str = DATABASE_PATH
    
    @classmethod
    def get_instance(cls) -> DatabaseManager:
        """获取数据库管理器实例"""
        if cls._instance is None:
            cls._instance = DatabaseManager(cls._db_path)
        return cls._instance
    
    @classmethod
    def set_database_path(cls, db_path: str):
        """设置数据库路径（用于测试）"""
        cls._db_path = db_path
        cls._instance = None  # 重置实例，下次获取时会使用新路径
    
    @classmethod
    def close(cls):
        """关闭数据库连接"""
        if cls._instance:
            cls._instance = None


def get_db() -> DatabaseManager:
    """获取数据库管理器实例的便捷函数"""
    return DatabaseConnection.get_instance()


def get_connection():
    """获取数据库连接的便捷函数（兼容性函数）"""
    import sqlite3
    db_manager = DatabaseConnection.get_instance()
    # 创建一个新的连接对象用于测试
    conn = sqlite3.connect(db_manager.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: str = None):
    """初始化数据库"""
    if db_path:
        DatabaseConnection.set_database_path(db_path)
    
    # 确保数据库目录存在
    db_path = DatabaseConnection._db_path
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 获取实例会自动初始化数据库
    DatabaseConnection.get_instance()
    print(f"数据库初始化完成: {db_path}")


if __name__ == "__main__":
    # 直接运行此文件可以初始化数据库
    init_database()
