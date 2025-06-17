#!/usr/bin/env python3
"""
管理员命令诊断脚本
用于检查管理员命令注册和权限问题
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client.commands.command_handler import CommandHandler
from client.core.client import ChatClient
from shared.constants import ADMIN_USER_ID, ADMIN_USERNAME


def test_command_registration():
    """测试命令注册情况"""
    print("🔍 检查命令注册情况...")
    
    # 创建模拟客户端
    client = ChatClient()
    command_handler = CommandHandler(client)
    
    # 检查新管理员命令是否注册
    new_admin_commands = ['add', 'del', 'modify', 'ban', 'free']
    
    print("\n📋 新管理员命令注册状态:")
    for cmd in new_admin_commands:
        if cmd in command_handler.commands:
            handler_func = command_handler.commands[cmd]
            print(f"  ✅ {cmd} -> {handler_func.__name__}")
        else:
            print(f"  ❌ {cmd} -> 未注册")
    
    print("\n📋 所有已注册命令:")
    for cmd, handler in command_handler.commands.items():
        print(f"  {cmd} -> {handler.__name__}")
    
    return command_handler


def test_admin_permission_check():
    """测试管理员权限检查"""
    print("\n🔐 检查管理员权限逻辑...")
    
    # 创建模拟客户端
    client = ChatClient()
    command_handler = CommandHandler(client)
    
    print(f"📊 管理员常量配置:")
    print(f"  ADMIN_USER_ID: {ADMIN_USER_ID}")
    print(f"  ADMIN_USERNAME: {ADMIN_USERNAME}")
    
    # 测试不同的用户ID设置
    test_cases = [
        (None, "未设置user_id"),
        (0, "管理员用户ID"),
        (1, "普通用户ID"),
        (-1, "AI用户ID")
    ]
    
    print(f"\n🧪 权限检查测试:")
    for user_id, description in test_cases:
        client.user_id = user_id
        is_admin = command_handler._is_admin()
        print(f"  user_id={user_id} ({description}): {'✅ 管理员' if is_admin else '❌ 非管理员'}")
    
    return client, command_handler


def test_admin_command_execution():
    """测试管理员命令执行"""
    print("\n⚡ 测试管理员命令执行...")
    
    client = ChatClient()
    command_handler = CommandHandler(client)
    
    # 模拟管理员登录
    client.user_id = ADMIN_USER_ID
    client.current_user = {'id': ADMIN_USER_ID, 'username': ADMIN_USERNAME}
    
    # 模拟登录状态
    def mock_is_logged_in():
        return True
    client.is_logged_in = mock_is_logged_in
    
    # 测试命令
    test_commands = [
        ('ban', ['-u', 'testuser']),
        ('free', ['-l']),
        ('add', ['-u', 'newuser', 'password123']),
        ('del', ['-u', '123']),
        ('modify', ['-u', '123', 'username', 'newname'])
    ]
    
    print(f"\n🎯 命令执行测试:")
    for cmd, args in test_commands:
        try:
            if cmd in command_handler.commands:
                # 这里只测试命令是否能被调用，不执行实际网络操作
                print(f"  ✅ /{cmd} {' '.join(args)} -> 命令处理器存在")
            else:
                print(f"  ❌ /{cmd} {' '.join(args)} -> 命令处理器不存在")
        except Exception as e:
            print(f"  ⚠️  /{cmd} {' '.join(args)} -> 执行异常: {e}")


def test_command_parsing():
    """测试命令解析"""
    print("\n📝 测试命令解析...")
    
    client = ChatClient()
    command_handler = CommandHandler(client)
    
    # 模拟管理员登录
    client.user_id = ADMIN_USER_ID
    client.current_user = {'id': ADMIN_USER_ID, 'username': ADMIN_USERNAME}
    
    def mock_is_logged_in():
        return True
    client.is_logged_in = mock_is_logged_in
    
    # 测试命令解析
    test_inputs = [
        "ban -u testuser",
        "free -l",
        "add -u newuser password123",
        "del -u 123",
        "modify -u 123 username newname",
        "unknown_command"
    ]
    
    print(f"\n🔍 命令解析测试:")
    for input_str in test_inputs:
        parts = input_str.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        result = command_handler.handle_command(command, args)
        print(f"  /{input_str} -> {result[:100]}{'...' if len(result) > 100 else ''}")


def main():
    """主函数"""
    print("🚀 管理员命令诊断开始")
    print("=" * 60)
    
    try:
        # 1. 检查命令注册
        command_handler = test_command_registration()
        
        # 2. 检查权限逻辑
        client, command_handler = test_admin_permission_check()
        
        # 3. 测试命令执行
        test_admin_command_execution()
        
        # 4. 测试命令解析
        test_command_parsing()
        
        print("\n" + "=" * 60)
        print("✅ 诊断完成")
        
        # 提供修复建议
        print("\n💡 修复建议:")
        print("1. 确认使用正确的管理员用户名登录")
        print(f"   - 配置的管理员用户名: {ADMIN_USERNAME}")
        print(f"   - 配置的管理员用户ID: {ADMIN_USER_ID}")
        print("2. 确认客户端登录后正确设置了user_id")
        print("3. 检查服务器端是否正确创建了管理员用户")
        print("4. 验证数据库中管理员用户的ID是否为0")
        
    except Exception as e:
        print(f"\n❌ 诊断过程中出现异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
