#!/usr/bin/env python3
"""
文件传输功能测试
测试文件上传和下载功能
"""

import os
import sys
import time
import tempfile
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.main import main as server_main
from client.main import main as client_main
from shared.logger import get_logger

logger = get_logger("test.file_transfer")

def create_test_file(filename: str, content: str) -> str:
    """创建测试文件"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f"_{filename}") as f:
        f.write(content)
        return f.name

def test_file_upload_download():
    """测试文件上传和下载功能"""
    print("🧪 开始文件传输功能测试...")
    
    # 创建测试文件
    test_content = "这是一个测试文件内容\n包含中文字符\n用于测试文件传输功能"
    test_file_path = create_test_file("test.txt", test_content)
    
    try:
        print(f"📁 创建测试文件: {test_file_path}")
        
        # 启动服务器（在后台线程中）
        print("🚀 启动服务器...")
        server_thread = threading.Thread(target=server_main, daemon=True)
        server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        
        print("✅ 服务器启动完成")
        print("📝 请手动测试以下功能:")
        print("1. 启动客户端: python client/main.py")
        print("2. 登录用户")
        print("3. 进入聊天组")
        print(f"4. 上传文件: /send_files {test_file_path}")
        print("5. 列出文件: /recv_files -l")
        print("6. 下载文件: /recv_files -n test.txt")
        print("7. 检查下载目录: client/Downloads/[用户名]/")
        
        # 保持服务器运行
        input("按回车键停止测试...")
        
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        logger.error("文件传输测试失败", error=str(e))
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"🗑️ 清理测试文件: {test_file_path}")

def test_file_storage_structure():
    """测试文件存储结构"""
    print("🧪 测试文件存储结构...")
    
    # 检查服务器文件存储目录
    server_storage_path = "server/data/files"
    if not os.path.exists(server_storage_path):
        os.makedirs(server_storage_path, exist_ok=True)
        print(f"📁 创建服务器存储目录: {server_storage_path}")
    
    # 检查客户端下载目录
    client_download_path = "client/Downloads"
    if not os.path.exists(client_download_path):
        os.makedirs(client_download_path, exist_ok=True)
        print(f"📁 创建客户端下载目录: {client_download_path}")
    
    print("✅ 文件存储结构检查完成")

if __name__ == "__main__":
    print("🔧 文件传输功能测试工具")
    print("=" * 50)
    
    # 测试文件存储结构
    test_file_storage_structure()
    
    print()
    
    # 测试文件传输功能
    test_file_upload_download()
