#!/usr/bin/env python3
"""
文件下载功能测试脚本
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.core.client import ChatClient

def test_file_download():
    """测试文件下载功能"""
    print("=== 文件下载功能测试 ===")
    
    # 创建客户端
    client = ChatClient("localhost", 8888)

    try:
        # 连接服务器
        print("1. 连接服务器...")
        if not client.connect():
            print("❌ 连接服务器失败")
            return False
        print("✅ 连接服务器成功")
        
        # 登录
        print("2. 登录用户...")
        success, message = client.login("test", "123456qwer")
        if not success:
            print(f"❌ 登录失败: {message}")
            return False
        print(f"✅ 登录成功: {message}")
        
        # 列出聊天组
        print("3. 列出聊天组...")
        success, message, groups = client.list_chat_groups()
        if success and groups:
            print(f"✅ 找到 {len(groups)} 个聊天组")
            # 进入第一个聊天组
            group_id = groups[0]['id']
            print(f"4. 进入聊天组 {group_id}...")
            success, message = client.enter_chat_group(group_id)
            if not success:
                print(f"❌ 进入聊天组失败: {message}")
                return False
            print(f"✅ 进入聊天组成功: {message}")
        else:
            # 创建聊天组
            print("3.1 创建聊天组...")
            success, message = client.create_chat_group("测试聊天组")
            if not success:
                print(f"❌ 创建聊天组失败: {message}")
                return False
            print(f"✅ 创建聊天组成功: {message}")

            # 进入刚创建的聊天组
            print("4. 进入聊天组...")
            success, message, groups = client.list_chat_groups()
            if success and groups:
                group_id = groups[0]['id']
                success, message = client.enter_chat_group(group_id)
                if not success:
                    print(f"❌ 进入聊天组失败: {message}")
                    return False
                print(f"✅ 进入聊天组成功: {message}")
            else:
                print("❌ 无法找到创建的聊天组")
                return False
        
        # 列出可下载文件
        print("5. 列出可下载文件...")
        success, message, files = client.list_files()
        if not success:
            print(f"❌ 列出文件失败: {message}")
            return False

        if not files:
            print("❌ 没有可下载的文件，先上传一个测试文件...")
            # 上传一个测试文件
            test_file_path = "requirements.txt"
            if os.path.exists(test_file_path):
                success, message = client.upload_file(test_file_path)
                if success:
                    print(f"✅ 测试文件上传成功: {message}")
                    # 重新列出文件
                    success, message, files = client.list_files()
                    if not success or not files:
                        print("❌ 上传后仍然没有可下载的文件")
                        return False
                else:
                    print(f"❌ 测试文件上传失败: {message}")
                    return False
            else:
                print("❌ 没有可用的测试文件")
                return False
            
        print(f"✅ 找到 {len(files)} 个文件:")
        for file_info in files:
            print(f"  ID: {file_info['file_id']} - {file_info['original_filename']} ({file_info['file_size']}B)")
        
        # 下载第一个文件
        file_to_download = files[0]
        file_id = file_to_download['file_id']
        filename = file_to_download['original_filename']
        
        print(f"6. 下载文件 ID:{file_id} - {filename}...")
        success, message = client.download_file(file_id)
        
        if success:
            print(f"✅ 文件下载成功: {message}")
            
            # 检查下载的文件是否存在
            expected_path = f"client/Downloads/test/{filename}"
            if os.path.exists(expected_path):
                file_size = os.path.getsize(expected_path)
                print(f"✅ 下载文件验证成功: {expected_path} ({file_size}B)")
                return True
            else:
                print(f"❌ 下载文件不存在: {expected_path}")
                return False
        else:
            print(f"❌ 文件下载失败: {message}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False
    finally:
        # 断开连接
        client.disconnect()
        print("🔌 已断开连接")

if __name__ == "__main__":
    success = test_file_download()
    if success:
        print("\n🎉 文件下载功能测试通过！")
        sys.exit(0)
    else:
        print("\n💥 文件下载功能测试失败！")
        sys.exit(1)
