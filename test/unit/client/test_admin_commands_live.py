#!/usr/bin/env python3
"""
管理员命令实际测试脚本
用于测试管理员命令的实际功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.core.client import ChatClient
from client.commands.parser import CommandHandler
from shared.constants import ADMIN_USER_ID, ADMIN_USERNAME


def test_admin_commands_with_server():
    """测试管理员命令与服务器的交互"""
    print("🚀 开始管理员命令实际测试")
    print("=" * 60)
    
    # 创建客户端
    client = ChatClient()
    command_handler = CommandHandler(client)
    
    try:
        # 1. 连接服务器
        print("📡 连接服务器...")
        if not client.connect():
            print("❌ 无法连接到服务器，请确保服务器正在运行")
            return False
        
        print("✅ 服务器连接成功")
        
        # 2. 管理员登录
        print("\n🔐 管理员登录...")
        success, message = client.login(ADMIN_USERNAME, "admin123")
        
        if not success:
            print(f"❌ 管理员登录失败: {message}")
            return False
        
        print(f"✅ 管理员登录成功: {message}")
        print(f"   用户ID: {client.user_id}")
        print(f"   用户名: {client.current_user['username']}")
        
        # 验证管理员权限
        is_admin = command_handler._is_admin()
        print(f"   管理员权限: {'✅ 是' if is_admin else '❌ 否'}")
        
        if not is_admin:
            print("❌ 权限验证失败，无法继续测试")
            return False
        
        # 3. 测试管理员命令
        print("\n🛠️ 测试管理员命令...")
        
        # 测试命令列表
        test_commands = [
            ("/help", "帮助命令"),
            ("/free -l", "查看禁言列表"),
            ("/list -u", "查看用户列表"),
            ("/list -g", "查看群组列表"),
        ]
        
        for cmd, description in test_commands:
            print(f"\n🔹 测试 {description}: {cmd}")
            try:
                success, result = command_handler.handle_command(cmd)
                if success:
                    print(f"   ✅ 成功: {result[:100]}{'...' if len(result) > 100 else ''}")
                else:
                    print(f"   ❌ 失败: {result}")
            except Exception as e:
                print(f"   ⚠️  异常: {e}")
        
        # 4. 测试新增用户命令（如果用户确认）
        print(f"\n🆕 测试新增用户命令...")
        try:
            response = input("是否测试新增用户功能？这将创建一个测试用户 (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                test_username = f"testuser_{int(time.time())}"
                cmd = f"/add -u {test_username} testpass123"
                print(f"   执行命令: {cmd}")
                
                success, result = command_handler.handle_command(cmd)
                if success:
                    print(f"   ✅ 新增用户成功: {result}")
                else:
                    print(f"   ❌ 新增用户失败: {result}")
            else:
                print("   ⏭️  跳过新增用户测试")
        except (EOFError, KeyboardInterrupt):
            print("   ⏭️  跳过新增用户测试")
        
        print("\n✅ 管理员命令测试完成")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理
        print("\n🧹 清理连接...")
        client.disconnect()
        print("✅ 连接已断开")


def test_command_help():
    """测试命令帮助功能"""
    print("\n📚 测试命令帮助功能...")
    
    client = ChatClient()
    command_handler = CommandHandler(client)
    
    # 测试帮助命令
    help_commands = [
        "/help",
        "/help add",
        "/help del",
        "/help ban",
        "/help free",
        "/help user",
        "/help group"
    ]
    
    for cmd in help_commands:
        print(f"\n🔹 {cmd}")
        try:
            success, result = command_handler.handle_command(cmd)
            if success:
                print(f"   ✅ {result[:200]}{'...' if len(result) > 200 else ''}")
            else:
                print(f"   ❌ {result}")
        except Exception as e:
            print(f"   ⚠️  异常: {e}")


def main():
    """主函数"""
    print("🎯 Chat-Room 管理员命令实际测试")
    print("=" * 60)
    
    try:
        # 1. 测试命令帮助
        test_command_help()
        
        # 2. 询问是否进行服务器测试
        print("\n" + "=" * 60)
        try:
            response = input("是否进行服务器连接测试？需要服务器正在运行 (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                test_admin_commands_with_server()
            else:
                print("⏭️  跳过服务器连接测试")
        except (EOFError, KeyboardInterrupt):
            print("\n⏭️  跳过服务器连接测试")
        
        print("\n" + "=" * 60)
        print("🎉 测试完成！")
        
        print("\n💡 使用说明:")
        print("1. 确保使用管理员账户登录（用户名: Admin, 密码: admin123）")
        print("2. 新的管理员命令格式:")
        print("   - /add -u <用户名> <密码>")
        print("   - /del -u <用户ID> | /del -g <群组ID> | /del -f <文件ID>")
        print("   - /modify -u <用户ID> <字段> <新值>")
        print("   - /ban -u <用户ID/用户名> | /ban -g <群组ID/群组名>")
        print("   - /free -u <用户ID/用户名> | /free -g <群组ID/群组名> | /free -l")
        print("3. 旧命令仍然可用但会显示废弃警告")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
