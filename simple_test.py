#!/usr/bin/env python3
"""
简单的连接测试
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.core.client import ChatClient

def simple_test():
    """简单测试"""
    print("=== 简单连接测试 ===")
    
    # 创建客户端
    client = ChatClient("localhost", 8888)
    
    try:
        # 连接服务器
        print("1. 连接服务器...")
        if not client.connect():
            print("❌ 连接服务器失败")
            return False
        print("✅ 连接服务器成功")
        
        # 等待一下
        time.sleep(1)
        
        # 登录
        print("2. 登录用户...")
        success, message = client.login("test", "123456qwer")
        if not success:
            print(f"❌ 登录失败: {message}")
            return False
        print(f"✅ 登录成功: {message}")
        
        # 等待一下
        time.sleep(1)
        
        print("✅ 基本功能正常")
        return True
            
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
    success = simple_test()
    if success:
        print("\n🎉 简单测试通过！")
        sys.exit(0)
    else:
        print("\n💥 简单测试失败！")
        sys.exit(1)
