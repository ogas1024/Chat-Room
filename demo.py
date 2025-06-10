#!/usr/bin/env python3
"""
Chat-Room 演示脚本
展示基本的注册、登录、聊天功能
"""

import threading
import time
import sys
from server.core.server import ChatRoomServer
from client.network.client import ChatClient


def demo_server():
    """演示服务器"""
    print("🚀 启动演示服务器...")
    server = ChatRoomServer("localhost", 8890)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n服务器被用户中断")
    except Exception as e:
        print(f"服务器错误: {e}")
    finally:
        server.stop()


def demo_client(username: str, password: str):
    """演示客户端"""
    print(f"👤 启动客户端 {username}...")
    
    # 等待服务器启动
    time.sleep(2)
    
    client = ChatClient("localhost", 8890)
    
    try:
        # 连接服务器
        if not client.connect():
            print(f"❌ {username}: 无法连接到服务器")
            return
        
        print(f"✅ {username}: 已连接到服务器")
        
        # 注册用户
        success, message = client.register(username, password)
        if success:
            print(f"✅ {username}: 注册成功 - {message}")
        else:
            print(f"ℹ️ {username}: 注册信息 - {message}")
        
        # 登录用户
        success, message = client.login(username, password)
        if success:
            print(f"✅ {username}: 登录成功 - {message}")
        else:
            print(f"❌ {username}: 登录失败 - {message}")
            return
        
        # 模拟聊天
        print(f"💬 {username}: 开始聊天...")
        time.sleep(1)
        
        # TODO: 发送消息功能
        print(f"📝 {username}: 发送消息功能待实现")
        
        # 保持连接一段时间
        time.sleep(5)
        
    except Exception as e:
        print(f"❌ {username}: 客户端错误 - {e}")
    finally:
        client.disconnect()
        print(f"👋 {username}: 已断开连接")


def run_demo():
    """运行演示"""
    print("=" * 60)
    print("🎉 Chat-Room 聊天室演示")
    print("=" * 60)
    print("这个演示将展示:")
    print("• 服务器启动")
    print("• 多个客户端连接")
    print("• 用户注册和登录")
    print("• 基本的聊天功能")
    print("=" * 60)
    
    # 启动服务器线程
    server_thread = threading.Thread(target=demo_server, daemon=True)
    server_thread.start()
    
    # 等待服务器启动
    time.sleep(3)
    
    # 启动多个客户端线程
    clients = [
        ("Alice", "password123"),
        ("Bob", "password456"),
        ("Charlie", "password789")
    ]
    
    client_threads = []
    for username, password in clients:
        thread = threading.Thread(
            target=demo_client, 
            args=(username, password),
            daemon=True
        )
        client_threads.append(thread)
        thread.start()
        time.sleep(1)  # 错开启动时间
    
    # 等待所有客户端完成
    for thread in client_threads:
        thread.join()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("\n要启动完整的聊天室，请运行:")
    print("• 服务器: python -m server.main")
    print("• 客户端: python -m client.main")
    print("• TUI客户端: python -m client.main --mode tui")


def test_basic_connection():
    """测试基本连接功能"""
    print("🔧 测试基本连接功能...")

    # 启动测试服务器
    server = ChatRoomServer("localhost", 8891)
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    # 等待服务器启动
    time.sleep(2)

    try:
        # 测试客户端连接
        client = ChatClient("localhost", 8891)

        if client.connect():
            print("✅ 客户端连接成功")

            # 使用简短的唯一用户名
            import random
            username = f"test{random.randint(1000, 9999)}"

            # 测试注册
            success, message = client.register(username, "testpass123")
            if success:
                print("✅ 用户注册成功")

                # 测试登录
                success, message = client.login(username, "testpass123")
                if success:
                    print("✅ 用户登录成功")
                    print("🎉 基本功能测试通过！")
                else:
                    print(f"❌ 登录失败: {message}")
            else:
                print(f"ℹ️ 注册信息: {message}")

                # 如果用户已存在，尝试登录
                if "已存在" in message:
                    success, message = client.login(username, "testpass123")
                    if success:
                        print("✅ 用户登录成功（已存在用户）")
                        print("🎉 基本功能测试通过！")
                    else:
                        print(f"❌ 登录失败: {message}")

            client.disconnect()
        else:
            print("❌ 客户端连接失败")

    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
    finally:
        server.stop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_basic_connection()
    else:
        run_demo()
