#!/usr/bin/env python3
"""
文件上传和下载测试脚本
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.core.client import ChatClient

def test_upload_download():
    """测试文件上传和下载功能"""
    print("=== 文件上传和下载功能测试 ===")
    
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
        
        # 创建聊天组
        print("3. 创建聊天组...")
        group_name = "测试聊天组"
        success, message = client.create_chat_group(group_name)
        if not success:
            print(f"❌ 创建聊天组失败: {message}")
            # 尝试进入已存在的聊天组
            print("3.1 尝试进入已存在的聊天组...")
            success, message = client.enter_chat_group(group_name)
            if not success:
                print(f"❌ 进入聊天组失败: {message}")
                return False
        else:
            print(f"✅ 创建聊天组成功: {message}")
            # 进入刚创建的聊天组
            print("4. 进入聊天组...")
            success, message = client.enter_chat_group(group_name)
            if not success:
                print(f"❌ 进入聊天组失败: {message}")
                return False

        print(f"✅ 进入聊天组成功: {message}")
        
        # 上传测试文件
        test_file_path = "requirements.txt"
        if not os.path.exists(test_file_path):
            print(f"❌ 测试文件不存在: {test_file_path}")
            return False
            
        print(f"5. 上传文件 {test_file_path}...")
        success, message = client.send_file(test_file_path)
        if not success:
            print(f"❌ 文件上传失败: {message}")
            return False
        print(f"✅ 文件上传成功: {message}")
        
        # 等待一下确保文件上传完成
        time.sleep(1)
        
        # 列出可下载文件
        print("5. 列出可下载文件...")
        success, message, files = client.list_files()
        if not success:
            print(f"❌ 列出文件失败: {message}")
            return False
        
        if not files:
            print("❌ 没有可下载的文件")
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
                original_size = os.path.getsize(test_file_path)
                print(f"✅ 下载文件验证成功: {expected_path} ({file_size}B)")
                
                if file_size == original_size:
                    print("✅ 文件大小匹配，下载完整")
                    return True
                else:
                    print(f"❌ 文件大小不匹配: 原始{original_size}B vs 下载{file_size}B")
                    return False
            else:
                print(f"❌ 下载文件不存在: {expected_path}")
                return False
        else:
            print(f"❌ 文件下载失败: {message}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 断开连接
        try:
            client.disconnect()
            print("🔌 已断开连接")
        except:
            pass

if __name__ == "__main__":
    success = test_upload_download()
    if success:
        print("\n🎉 文件上传和下载功能测试通过！")
        sys.exit(0)
    else:
        print("\n💥 文件上传和下载功能测试失败！")
        sys.exit(1)
