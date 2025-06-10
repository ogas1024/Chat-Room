"""
聊天室客户端主程序
简单的命令行客户端，用于测试基本功能
"""

import sys
import threading
import time
from typing import Optional

from client.network.client import ChatClient
from client.commands.parser import CommandHandler
from shared.constants import DEFAULT_HOST, DEFAULT_PORT


class SimpleChatClient:
    """简单的聊天客户端"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化客户端"""
        self.chat_client = ChatClient(host, port)
        self.command_handler = CommandHandler(self.chat_client)
        self.running = False
        self.current_state = "disconnected"  # disconnected, connected, logged_in
    
    def start(self):
        """启动客户端"""
        print("=" * 50)
        print("🚀 聊天室客户端")
        print("=" * 50)
        print("输入 /help 查看可用命令")
        print("输入 /exit 退出程序")
        print("=" * 50)
        
        # 尝试连接服务器
        if self.connect_to_server():
            self.running = True
            self.main_loop()
        else:
            print("无法连接到服务器，程序退出")
    
    def connect_to_server(self) -> bool:
        """连接到服务器"""
        print(f"正在连接服务器 {self.chat_client.network_client.host}:{self.chat_client.network_client.port}...")
        
        if self.chat_client.connect():
            print("✅ 连接服务器成功")
            self.current_state = "connected"
            return True
        else:
            print("❌ 连接服务器失败")
            return False
    
    def main_loop(self):
        """主循环"""
        try:
            while self.running:
                # 显示提示符
                if self.current_state == "connected":
                    prompt = "未登录> "
                elif self.current_state == "logged_in":
                    username = self.chat_client.current_user.get('username', 'Unknown')
                    prompt = f"{username}> "
                else:
                    prompt = "断开连接> "
                
                try:
                    user_input = input(prompt).strip()
                    if not user_input:
                        continue
                    
                    # 处理输入
                    self.handle_input(user_input)
                    
                except KeyboardInterrupt:
                    print("\n用户中断，正在退出...")
                    break
                except EOFError:
                    print("\n输入结束，正在退出...")
                    break
                    
        finally:
            self.cleanup()
    
    def handle_input(self, user_input: str):
        """处理用户输入"""
        if user_input.startswith('/'):
            # 处理命令
            self.handle_command(user_input)
        else:
            # 处理普通消息
            self.handle_message(user_input)
    
    def handle_command(self, command_input: str):
        """处理命令"""
        if command_input == "/login":
            self.handle_login_command()
        elif command_input == "/signin":
            self.handle_signin_command()
        elif command_input == "/exit":
            self.running = False
        else:
            # 使用命令处理器
            success, message = self.command_handler.handle_command(command_input)
            if success:
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
    
    def handle_login_command(self):
        """处理登录命令"""
        if self.current_state != "connected":
            print("❌ 请先连接到服务器")
            return
        
        try:
            username = input("用户名: ").strip()
            if not username:
                print("❌ 用户名不能为空")
                return
            
            password = input("密码: ").strip()
            if not password:
                print("❌ 密码不能为空")
                return
            
            print("正在登录...")
            success, message = self.chat_client.login(username, password)
            
            if success:
                print(f"✅ {message}")
                self.current_state = "logged_in"
                print(f"欢迎, {username}! 您已进入公频聊天组")
            else:
                print(f"❌ {message}")
                
        except KeyboardInterrupt:
            print("\n登录已取消")
        except Exception as e:
            print(f"❌ 登录时出错: {e}")
    
    def handle_signin_command(self):
        """处理注册命令"""
        if self.current_state != "connected":
            print("❌ 请先连接到服务器")
            return
        
        try:
            username = input("用户名: ").strip()
            if not username:
                print("❌ 用户名不能为空")
                return
            
            password = input("密码: ").strip()
            if not password:
                print("❌ 密码不能为空")
                return
            
            confirm_password = input("确认密码: ").strip()
            if password != confirm_password:
                print("❌ 两次输入的密码不一致")
                return
            
            print("正在注册...")
            success, message = self.chat_client.register(username, password)
            
            if success:
                print(f"✅ {message}")
                print("请使用 /login 命令登录")
            else:
                print(f"❌ {message}")
                
        except KeyboardInterrupt:
            print("\n注册已取消")
        except Exception as e:
            print(f"❌ 注册时出错: {e}")
    
    def handle_message(self, message: str):
        """处理普通消息"""
        if self.current_state != "logged_in":
            print("❌ 请先登录")
            return
        
        # 检查是否在聊天组中
        if not self.chat_client.current_chat_group:
            print("❌ 请先进入聊天组")
            return

        # 发送消息到当前聊天组
        group_id = self.chat_client.current_chat_group['id']
        success = self.chat_client.send_chat_message(message, group_id)

        if success:
            print(f"✅ 消息已发送: {message}")
        else:
            print("❌ 消息发送失败")
    
    def cleanup(self):
        """清理资源"""
        print("正在断开连接...")
        self.chat_client.disconnect()
        print("客户端已退出")


def main():
    """主函数"""
    import argparse

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='聊天室客户端')
    parser.add_argument(
        '--host',
        default=DEFAULT_HOST,
        help=f'服务器地址 (默认: {DEFAULT_HOST})'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=DEFAULT_PORT,
        help=f'服务器端口 (默认: {DEFAULT_PORT})'
    )
    parser.add_argument(
        '--mode',
        choices=['tui', 'simple'],
        default='tui',
        help='客户端模式: tui(图形界面) 或 simple(简单命令行)'
    )

    args = parser.parse_args()

    try:
        if args.mode == 'tui':
            # 使用TUI界面
            try:
                from client.ui.app import run_chat_app
                run_chat_app(args.host, args.port)
            except ImportError as e:
                print(f"TUI模式需要textual库: {e}")
                print("请运行: pip install textual")
                print("或使用简单模式: python -m client.main --mode simple")
                sys.exit(1)
        else:
            # 使用简单命令行界面
            client = SimpleChatClient(args.host, args.port)
            client.start()

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
