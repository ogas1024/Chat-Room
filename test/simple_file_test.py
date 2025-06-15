#!/usr/bin/env python3
"""
简单的文件传输测试
"""

import os
import sys
import tempfile

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print(f"项目根目录: {project_root}")
print("开始导入模块...")

try:
    from client.core.client import ChatClient
    print("✓ 成功导入 ChatClient")
except Exception as e:
    print(f"✗ 导入 ChatClient 失败: {e}")
    sys.exit(1)

def main():
    print("创建测试文件...")
    # 创建一个简单的测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("这是一个测试文件\nHello World\n测试中文")
        test_file = f.name
    
    print(f"测试文件路径: {test_file}")
    
    try:
        # 创建客户端
        print("创建客户端...")
        client = ChatClient()
        
        # 连接服务器
        print("连接服务器...")
        if client.connect():
            print("✓ 连接成功")
        else:
            print("✗ 连接失败")
            return
        
        # 登录
        print("登录...")
        success, message = client.login("test", "123456qwer")
        if success:
            print(f"✓ 登录成功: {message}")
        else:
            print(f"✗ 登录失败: {message}")
            return
        
        # 进入聊天组
        print("进入聊天组...")
        success, message = client.enter_chat("public")
        if success:
            print(f"✓ 进入聊天组成功: {message}")
        else:
            print(f"✗ 进入聊天组失败: {message}")
            return
        
        # 测试文件上传
        print("测试文件上传...")
        success, message = client.send_file(test_file)
        if success:
            print(f"✓ 文件上传成功: {message}")
        else:
            print(f"✗ 文件上传失败: {message}")
        
        # 断开连接
        client.disconnect()
        print("✓ 测试完成")
        
    except Exception as e:
        print(f"✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"清理测试文件: {test_file}")

if __name__ == "__main__":
    main()
