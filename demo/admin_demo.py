#!/usr/bin/env python3
"""
管理员功能演示脚本
展示Chat-Room项目的管理员功能使用方法
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.core.client import ChatClient
from client.commands.command_handler import CommandHandler
from shared.constants import ADMIN_USERNAME


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🛡️  Chat-Room 管理员功能演示")
    print("=" * 60)
    print()


def print_section(title):
    """打印章节标题"""
    print(f"\n📋 {title}")
    print("-" * 40)


def demo_admin_commands():
    """演示管理员命令"""
    print_banner()
    
    print("本演示将展示Chat-Room项目的管理员功能，包括：")
    print("• 用户管理（删除、修改）")
    print("• 群组管理（删除、修改）") 
    print("• 禁言功能（用户禁言、群组禁言）")
    print("• 解禁功能（解除禁言、查看禁言列表）")
    print()
    
    # 创建模拟的客户端和命令处理器
    client = ChatClient()
    client.user_id = 0  # 模拟管理员用户
    command_handler = CommandHandler(client)
    
    print_section("1. 用户管理命令")
    
    print("🔹 删除用户命令格式:")
    print("   /user -d <用户ID>")
    print("   示例: /user -d 123")
    print()
    
    print("🔹 修改用户信息命令格式:")
    print("   /user -m <用户ID> <字段> <新值>")
    print("   示例: /user -m 123 username 新用户名")
    print("   示例: /user -m 123 password 新密码123")
    print()
    
    print_section("2. 群组管理命令")
    
    print("🔹 删除群组命令格式:")
    print("   /group -d <群组ID>")
    print("   示例: /group -d 5")
    print()
    
    print("🔹 修改群组信息命令格式:")
    print("   /group -m <群组ID> <字段> <新值>")
    print("   示例: /group -m 5 name 新群组名")
    print()
    
    print_section("3. 禁言功能")
    
    print("🔹 禁言用户命令格式:")
    print("   /ban -u <用户ID或用户名>")
    print("   示例: /ban -u 123")
    print("   示例: /ban -u 张三")
    print()
    
    print("🔹 禁言群组命令格式:")
    print("   /ban -g <群组ID或群组名>")
    print("   示例: /ban -g 5")
    print("   示例: /ban -g 测试群")
    print()
    
    print_section("4. 解禁功能")
    
    print("🔹 解除用户禁言命令格式:")
    print("   /free -u <用户ID或用户名>")
    print("   示例: /free -u 123")
    print("   示例: /free -u 张三")
    print()
    
    print("🔹 解除群组禁言命令格式:")
    print("   /free -g <群组ID或群组名>")
    print("   示例: /free -g 5")
    print("   示例: /free -g 测试群")
    print()
    
    print("🔹 查看禁言列表命令格式:")
    print("   /free -l")
    print()
    
    print_section("5. 权限和安全")
    
    print("🔒 权限控制:")
    print("   • 只有管理员用户（ID=0）可以执行管理员命令")
    print("   • 普通用户尝试执行会收到权限不足错误")
    print()
    
    print("🛡️ 安全机制:")
    print("   • 删除和禁言操作需要用户确认")
    print("   • 管理员不能删除或禁言自己")
    print("   • 不能删除或禁言public群组")
    print("   • 所有操作都有详细日志记录")
    print()
    
    print("📢 操作通知:")
    print("   • 管理员操作会广播给所有在线用户")
    print("   • 被操作用户会收到特殊提示")
    print("   • 被删除用户的连接会自动断开")
    print()
    
    print_section("6. 使用场景示例")
    
    print("📝 场景1: 处理违规用户")
    print("   1. /ban -u 违规用户名     # 先禁言")
    print("   2. /free -l              # 查看禁言列表")
    print("   3. /user -d 123          # 如需要可删除用户")
    print()
    
    print("📝 场景2: 管理群组")
    print("   1. /ban -g 问题群组      # 禁言整个群组")
    print("   2. /group -m 5 name 新名 # 修改群组名称")
    print("   3. /free -g 5            # 解除群组禁言")
    print()
    
    print("📝 场景3: 用户信息管理")
    print("   1. /user -m 123 password 新密码  # 重置密码")
    print("   2. /user -m 123 username 新名字  # 修改用户名")
    print()
    
    print_section("7. 默认管理员账户")
    
    print(f"👤 管理员账户信息:")
    print(f"   用户名: {ADMIN_USERNAME}")
    print(f"   用户ID: 0")
    print(f"   默认密码: admin123")
    print()
    print("⚠️  安全提醒: 首次使用时请立即修改管理员密码！")
    print()
    
    print("=" * 60)
    print("✅ 管理员功能演示完成")
    print("📚 更多详细信息请参考: docs/admin-guide.md")
    print("🧪 运行测试脚本: python test/test_admin_functions.py")
    print("=" * 60)


def interactive_demo():
    """交互式演示"""
    print_banner()
    print("🎮 交互式管理员功能演示")
    print()
    print("注意: 这是一个模拟演示，不会连接到真实服务器")
    print()
    
    # 创建模拟的客户端和命令处理器
    client = ChatClient()
    client.user_id = 0  # 模拟管理员用户
    command_handler = CommandHandler(client)
    
    print("可用的管理员命令:")
    print("• /user -d <用户ID>           - 删除用户")
    print("• /user -m <用户ID> <字段> <值> - 修改用户信息")
    print("• /group -d <群组ID>          - 删除群组")
    print("• /group -m <群组ID> <字段> <值> - 修改群组信息")
    print("• /ban -u <用户ID/用户名>      - 禁言用户")
    print("• /ban -g <群组ID/群组名>      - 禁言群组")
    print("• /free -u <用户ID/用户名>     - 解除用户禁言")
    print("• /free -g <群组ID/群组名>     - 解除群组禁言")
    print("• /free -l                   - 查看禁言列表")
    print("• help                       - 显示帮助")
    print("• exit                       - 退出演示")
    print()
    
    while True:
        try:
            user_input = input("管理员> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("👋 退出演示")
                break
            
            if user_input.lower() == 'help':
                print("\n📖 管理员命令帮助:")
                print("详细使用方法请参考 docs/admin-guide.md")
                continue
            
            # 解析命令
            parts = user_input.split()
            if not parts:
                continue
            
            command = parts[0].lstrip('/')
            args = parts[1:] if len(parts) > 1 else []
            
            # 模拟命令处理
            if command in ['user', 'group', 'ban', 'free']:
                print(f"📝 模拟执行管理员命令: /{command} {' '.join(args)}")
                
                if command == 'user':
                    if len(args) >= 2 and args[0] == '-d':
                        print(f"⚠️  这将删除用户ID {args[1]} 及其所有数据")
                        print("💡 在真实环境中，这里会要求确认操作")
                    elif len(args) >= 4 and args[0] == '-m':
                        print(f"📝 修改用户ID {args[1]} 的 {args[2]} 为 {args[3]}")
                    else:
                        print("❌ 用法: /user -d <用户ID> 或 /user -m <用户ID> <字段> <新值>")
                
                elif command == 'group':
                    if len(args) >= 2 and args[0] == '-d':
                        print(f"⚠️  这将删除群组ID {args[1]} 及其所有数据")
                        print("💡 在真实环境中，这里会要求确认操作")
                    elif len(args) >= 4 and args[0] == '-m':
                        print(f"📝 修改群组ID {args[1]} 的 {args[2]} 为 {args[3]}")
                    else:
                        print("❌ 用法: /group -d <群组ID> 或 /group -m <群组ID> <字段> <新值>")
                
                elif command == 'ban':
                    if len(args) >= 2 and args[0] == '-u':
                        print(f"🔇 禁言用户: {args[1]}")
                        print("💡 在真实环境中，这里会要求确认操作")
                    elif len(args) >= 2 and args[0] == '-g':
                        print(f"🔇 禁言群组: {args[1]}")
                        print("💡 在真实环境中，这里会要求确认操作")
                    else:
                        print("❌ 用法: /ban -u <用户ID/用户名> 或 /ban -g <群组ID/群组名>")
                
                elif command == 'free':
                    if len(args) >= 1 and args[0] == '-l':
                        print("📋 被禁言对象列表:")
                        print("   被禁言用户: 无")
                        print("   被禁言群组: 无")
                    elif len(args) >= 2 and args[0] == '-u':
                        print(f"🔊 解除用户禁言: {args[1]}")
                    elif len(args) >= 2 and args[0] == '-g':
                        print(f"🔊 解除群组禁言: {args[1]}")
                    else:
                        print("❌ 用法: /free -u <用户ID/用户名> 或 /free -g <群组ID/群组名> 或 /free -l")
                
                print("✅ 命令模拟完成")
            else:
                print(f"❌ 未知命令: {command}")
                print("💡 输入 'help' 查看可用命令")
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 退出演示")
            break
        except EOFError:
            print("\n👋 退出演示")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        demo_admin_commands()
        print()
        print("💡 运行交互式演示: python demo/admin_demo.py --interactive")
