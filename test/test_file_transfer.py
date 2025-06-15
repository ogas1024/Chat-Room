#!/usr/bin/env python3
"""
文件传输功能测试脚本
测试文件上传和下载功能
"""

import os
import sys
import time
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from client.core.client import ChatClient
from server.main import main as start_server
import threading


def create_test_file(content: str = "这是一个测试文件\nTest file content\n测试中文内容") -> str:
    """创建测试文件"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        return f.name


def test_file_transfer():
    """测试文件传输功能"""
    print("开始文件传输功能测试...")
    
    # 创建测试文件
    test_file_path = create_test_file()
    print(f"创建测试文件: {test_file_path}")
    
    try:
        # 创建客户端
        client = ChatClient()
        
        # 连接到服务器
        print("连接到服务器...")
        if not client.connect():
            print("连接服务器失败")
            return False
        
        # 登录
        print("登录用户...")
        success, message = client.login("test", "123456qwer")
        if not success:
            print(f"登录失败: {message}")
            return False
        print(f"登录成功: {message}")
        
        # 进入默认聊天组
        print("进入聊天组...")
        success, message = client.enter_chat("public")
        if not success:
            print(f"进入聊天组失败: {message}")
            return False
        print(f"进入聊天组成功: {message}")
        
        # 测试文件上传
        print("测试文件上传...")
        success, message = client.send_file(test_file_path)
        if success:
            print(f"文件上传成功: {message}")
        else:
            print(f"文件上传失败: {message}")
            return False
        
        # 等待一下让服务器处理完成
        time.sleep(2)
        
        # 测试文件列表
        print("获取文件列表...")
        success, message, files = client.list_files()
        if success and files:
            print(f"文件列表获取成功，共 {len(files)} 个文件:")
            for file_info in files:
                print(f"  ID: {file_info['file_id']}, 文件名: {file_info['original_filename']}, 大小: {file_info['file_size']} bytes")
            
            # 测试文件下载
            if files:
                file_id = files[0]['file_id']
                print(f"测试下载文件 ID: {file_id}")
                success, message = client.download_file(file_id)
                if success:
                    print(f"文件下载成功: {message}")
                else:
                    print(f"文件下载失败: {message}")
        else:
            print(f"获取文件列表失败: {message}")
        
        # 断开连接
        client.disconnect()
        print("测试完成")
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        return False
    finally:
        # 清理测试文件
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            print(f"清理测试文件: {test_file_path}")


if __name__ == "__main__":
    print("请先手动启动服务器，然后运行此测试脚本")
    print("启动服务器命令: python server/main.py")
    print("等待5秒后开始测试...")
    time.sleep(5)

    # 运行测试
    success = test_file_transfer()

    if success:
        print("✓ 文件传输功能测试通过")
        sys.exit(0)
    else:
        print("✗ 文件传输功能测试失败")
        sys.exit(1)
