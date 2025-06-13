#!/usr/bin/env python3
"""
简单的文件传输功能测试
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试导入是否正常"""
    try:
        from server.database.models import DatabaseManager
        from client.core.client import ChatClient
        from shared.constants import FILE_CHUNK_SIZE, MessageType
        print("✅ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_database_file_methods():
    """测试数据库文件相关方法"""
    try:
        from server.database.models import DatabaseManager
        
        # 创建临时数据库
        import tempfile
        temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        temp_db.close()
        db = DatabaseManager(temp_db.name)
        
        # 测试保存文件元数据
        file_id = db.save_file_metadata(
            "test.txt", "/tmp/test.txt", 1024, 1, 1
        )
        print(f"✅ 保存文件元数据成功，文件ID: {file_id}")
        
        # 测试更新文件路径
        db.update_file_server_path(file_id, "/new/path/test.txt")
        print("✅ 更新文件路径成功")
        
        # 测试获取文件元数据
        file_info = db.get_file_metadata_by_id(file_id)
        print(f"✅ 获取文件元数据成功: {file_info['original_filename']}")

        # 清理临时数据库
        os.unlink(temp_db.name)

        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_file_storage_paths():
    """测试文件存储路径"""
    try:
        # 检查服务器存储路径
        server_path = "server/data/files"
        if not os.path.exists(server_path):
            os.makedirs(server_path, exist_ok=True)
        print(f"✅ 服务器存储路径: {server_path}")
        
        # 检查客户端下载路径
        client_path = "client/Downloads"
        if not os.path.exists(client_path):
            os.makedirs(client_path, exist_ok=True)
        print(f"✅ 客户端下载路径: {client_path}")
        
        return True
    except Exception as e:
        print(f"❌ 路径测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 简单文件传输功能测试")
    print("=" * 40)
    
    tests = [
        ("模块导入测试", test_imports),
        ("数据库方法测试", test_database_file_methods),
        ("文件路径测试", test_file_storage_paths),
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
    else:
        print("⚠️ 部分测试失败，请检查相关功能")

if __name__ == "__main__":
    main()
