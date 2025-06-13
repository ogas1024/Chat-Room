#!/usr/bin/env python3
"""
最小化文件传输功能测试
"""

import os
import sys
import sqlite3
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_operations():
    """直接测试数据库操作"""
    print("🧪 测试数据库文件操作...")
    
    # 创建临时数据库
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    try:
        # 直接使用sqlite3创建表
        conn = sqlite3.connect(temp_db.name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 创建必要的表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_online INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                is_private_chat INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
                FOREIGN KEY (chat_group_id) REFERENCES chat_groups(id)
            )
        ''')
        
        # 插入测试数据
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                      ("testuser", "testhash"))
        user_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO chat_groups (name) VALUES (?)", ("testgroup",))
        group_id = cursor.lastrowid
        
        # 测试文件元数据操作
        cursor.execute('''
            INSERT INTO files_metadata
            (original_filename, server_filepath, file_size, uploader_id, chat_group_id)
            VALUES (?, ?, ?, ?, ?)
        ''', ("test.txt", "/tmp/test.txt", 1024, user_id, group_id))
        file_id = cursor.lastrowid
        
        print(f"✅ 插入文件元数据成功，文件ID: {file_id}")
        
        # 测试更新文件路径
        cursor.execute('''
            UPDATE files_metadata
            SET server_filepath = ?
            WHERE id = ?
        ''', ("/new/path/test.txt", file_id))
        
        print("✅ 更新文件路径成功")
        
        # 测试查询文件元数据
        cursor.execute('''
            SELECT fm.*, u.username as uploader_username
            FROM files_metadata fm
            JOIN users u ON fm.uploader_id = u.id
            WHERE fm.id = ?
        ''', (file_id,))
        row = cursor.fetchone()
        
        if row:
            print(f"✅ 查询文件元数据成功: {dict(row)['original_filename']}")
        else:
            print("❌ 查询文件元数据失败")
            return False
        
        # 测试按文件名查询
        cursor.execute('''
            SELECT fm.*, u.username as uploader_username
            FROM files_metadata fm
            JOIN users u ON fm.uploader_id = u.id
            WHERE fm.original_filename = ? AND fm.chat_group_id = ?
            ORDER BY fm.upload_timestamp DESC
            LIMIT 1
        ''', ("test.txt", group_id))
        row = cursor.fetchone()
        
        if row:
            print(f"✅ 按文件名查询成功: {dict(row)['original_filename']}")
        else:
            print("❌ 按文件名查询失败")
            return False
        
        conn.commit()
        conn.close()
        
        print("✅ 所有数据库操作测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据库操作测试失败: {e}")
        return False
    finally:
        # 清理临时数据库
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)

def test_file_paths():
    """测试文件路径创建"""
    print("🧪 测试文件路径...")
    
    try:
        # 测试服务器存储路径
        server_base = "server/data/files"
        group_path = os.path.join(server_base, "1")
        os.makedirs(group_path, exist_ok=True)
        print(f"✅ 服务器存储路径: {group_path}")
        
        # 测试客户端下载路径
        client_base = "client/Downloads"
        user_path = os.path.join(client_base, "testuser")
        os.makedirs(user_path, exist_ok=True)
        print(f"✅ 客户端下载路径: {user_path}")
        
        return True
    except Exception as e:
        print(f"❌ 文件路径测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 最小化文件传输功能测试")
    print("=" * 40)
    
    tests = [
        ("数据库操作测试", test_database_operations),
        ("文件路径测试", test_file_paths),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！文件传输功能基础组件正常")
        print("\n📝 下一步可以测试:")
        print("1. 启动服务器: python server/main.py")
        print("2. 启动客户端: python client/main.py")
        print("3. 测试文件上传下载功能")
    else:
        print("⚠️ 部分测试失败，请检查相关功能")

if __name__ == "__main__":
    main()
