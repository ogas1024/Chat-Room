"""
聊天室客户端主程序
简单的命令行客户端，用于测试基本功能
"""

import sys

from client.core.client import ChatClient
from client.commands.parser import CommandHandler
from shared.constants import DEFAULT_HOST, DEFAULT_PORT


def get_user_input(prompt: str, required: bool = True) -> str:
    """获取用户输入并验证"""
    try:
        value = input(prompt).strip()
        if required and not value:
            print(f"❌ {prompt.replace(': ', '')}不能为空")
            return ""
        return value
    except (KeyboardInterrupt, EOFError):
        print(f"\n{prompt.replace(': ', '')}输入已取消")
        return ""


def validate_connection_state(current_state: str, required_state: str) -> bool:
    """验证连接状态"""
    if current_state != required_state:
        if required_state == "connected":
            print("❌ 请先连接到服务器")
        elif required_state == "logged_in":
            print("❌ 请先登录")
        return False
    return True


class SimpleChatClient:
    """简单的聊天客户端"""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化客户端"""
        self.chat_client = ChatClient(host, port)
        self.command_handler = CommandHandler(self.chat_client)
        # 设置Simple客户端的引用，以便命令处理器可以访问
        self.command_handler.simple_client = self
        self.running = False
        self.current_state = "disconnected"  # disconnected, connected, logged_in

        # 历史消息收集器
        self.history_messages = []
        self.current_chat_group_id = None

        # 设置Simple模式的消息处理器
        self._setup_simple_message_handlers()

    def _setup_simple_message_handlers(self):
        """设置Simple模式的消息处理器"""
        from shared.constants import MessageType

        # 历史消息处理器
        self.chat_client.network_client.set_message_handler(
            MessageType.CHAT_HISTORY, self._handle_simple_chat_history
        )

        # 历史消息加载完成处理器
        self.chat_client.network_client.set_message_handler(
            MessageType.CHAT_HISTORY_COMPLETE, self._handle_simple_chat_history_complete
        )

        # 实时聊天消息处理器
        self.chat_client.network_client.set_message_handler(
            MessageType.CHAT_MESSAGE, self._handle_simple_chat_message
        )

    def _force_override_message_handlers(self):
        """强制覆盖消息处理器，确保Simple模式的处理器不被覆盖"""
        from shared.constants import MessageType

        # 强制设置历史消息处理器
        self.chat_client.network_client.message_handlers[MessageType.CHAT_HISTORY] = self._handle_simple_chat_history
        self.chat_client.network_client.message_handlers[MessageType.CHAT_HISTORY_COMPLETE] = self._handle_simple_chat_history_complete
        self.chat_client.network_client.message_handlers[MessageType.CHAT_MESSAGE] = self._handle_simple_chat_message

        # 同时覆盖ChatClient中可能设置的处理器
        if hasattr(self.chat_client, '_handle_chat_history'):
            self.chat_client._handle_chat_history = self._handle_simple_chat_history
        if hasattr(self.chat_client, '_handle_chat_history_complete'):
            self.chat_client._handle_chat_history_complete = self._handle_simple_chat_history_complete
        if hasattr(self.chat_client, '_handle_chat_message'):
            self.chat_client._handle_chat_message = self._handle_simple_chat_message

    def _handle_simple_chat_history(self, message):
        """处理Simple模式的历史聊天消息 - 收集消息而不是立即输出"""
        try:
            # 验证消息是否属于当前聊天组
            if not hasattr(message, 'chat_group_id'):
                return

            if not self.chat_client.current_chat_group:
                return

            if message.chat_group_id != self.chat_client.current_chat_group['id']:
                return

            # 如果是新的聊天组，清空历史消息收集器
            if self.current_chat_group_id != message.chat_group_id:
                self.history_messages = []
                self.current_chat_group_id = message.chat_group_id

            # 格式化时间戳
            timestamp_str = ""
            if hasattr(message, 'timestamp') and message.timestamp:
                try:
                    # 尝试解析完整的时间戳格式
                    from datetime import datetime
                    from shared.constants import TIMESTAMP_FORMAT

                    if isinstance(message.timestamp, str):
                        try:
                            # 尝试解析完整格式
                            dt = datetime.strptime(message.timestamp, TIMESTAMP_FORMAT)
                            timestamp_str = dt.strftime("%a %b %d %I:%M:%S %p UTC %Y")
                        except:
                            # 如果解析失败，提取时间部分
                            if len(message.timestamp) > 10:
                                time_part = message.timestamp.split(' ')[-1][:8]
                                timestamp_str = f"Today {time_part}"
                            else:
                                timestamp_str = str(message.timestamp)
                    else:
                        timestamp_str = str(message.timestamp)
                except:
                    timestamp_str = "Unknown time"

            # 收集历史消息到列表中
            formatted_message = {
                'username': message.sender_username,
                'timestamp': timestamp_str,
                'content': message.content
            }
            self.history_messages.append(formatted_message)

        except Exception as e:
            # 如果处理失败，记录错误消息
            error_message = {
                'username': 'ERROR',
                'timestamp': 'Unknown time',
                'content': f'历史消息处理失败: {e}'
            }
            self.history_messages.append(error_message)

    def _handle_simple_chat_history_complete(self, message):
        """处理Simple模式的历史消息加载完成 - 批量输出所有历史消息"""
        import sys

        try:
            # 构建完整的输出字符串
            output_lines = []

            # 如果有历史消息，格式化并添加到输出中
            if self.history_messages:
                output_lines.append(f"✅ 已加载 {len(self.history_messages)} 条历史消息")
                output_lines.append("")  # 空行分隔

                # 按照指定格式添加每条历史消息
                for msg in self.history_messages:
                    output_lines.append(f"[{msg['username']}]    <{msg['timestamp']}>")
                    output_lines.append(f">{msg['content']}")
                    output_lines.append("")  # 消息间空行

                # 移除最后一个空行
                if output_lines and output_lines[-1] == "":
                    output_lines.pop()
            else:
                # 检查服务器报告的消息数量
                if hasattr(message, 'message_count') and message.message_count > 0:
                    output_lines.append(f"⚠️ 服务器报告有 {message.message_count} 条历史消息，但客户端未收到")
                else:
                    output_lines.append("✅ 暂无历史消息")

            # 添加分隔线
            output_lines.append("-" * 50)

            # 一次性输出所有内容
            complete_output = "\n".join(output_lines) + "\n"
            sys.stdout.write(complete_output)
            sys.stdout.flush()

            # 清空历史消息收集器，为下次使用做准备
            self.history_messages = []

        except Exception as e:
            # 如果批量输出失败，使用简单输出
            sys.stdout.write(f"❌ 历史消息批量输出失败: {e}\n")
            if hasattr(message, 'message_count'):
                sys.stdout.write(f"✅ 已加载 {message.message_count} 条历史消息\n")
            sys.stdout.write("-" * 50 + "\n")
            sys.stdout.flush()

            # 清空历史消息收集器
            self.history_messages = []

    def _handle_simple_chat_message(self, message):
        """处理Simple模式的实时聊天消息"""
        # 验证消息是否属于当前聊天组
        if not hasattr(message, 'chat_group_id'):
            return

        if not self.chat_client.current_chat_group:
            return

        if message.chat_group_id != self.chat_client.current_chat_group['id']:
            return

        # 显示实时消息
        from datetime import datetime
        timestamp_str = datetime.now().strftime("[%H:%M:%S]")
        print(f"💬 {timestamp_str} [{message.sender_username}]: {message.content}")

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

            # 重要：连接成功后重新设置Simple模式的消息处理器
            # 确保不被其他地方的处理器设置覆盖
            self._setup_simple_message_handlers()

            # 强制覆盖可能被其他地方设置的处理器
            self._force_override_message_handlers()

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
        if not validate_connection_state(self.current_state, "connected"):
            return

        username = get_user_input("用户名: ")
        if not username:
            return

        password = get_user_input("密码: ")
        if not password:
            return

        try:
            print("正在登录...")
            success, message = self.chat_client.login(username, password)

            if success:
                print(f"✅ {message}")
                self.current_state = "logged_in"
                print(f"欢迎, {username}! 您已进入公频聊天组")
            else:
                print(f"❌ {message}")

        except Exception as e:
            print(f"❌ 登录时出错: {e}")
    
    def handle_signin_command(self):
        """处理注册命令"""
        if not validate_connection_state(self.current_state, "connected"):
            return

        username = get_user_input("用户名: ")
        if not username:
            return

        password = get_user_input("密码: ")
        if not password:
            return

        confirm_password = get_user_input("确认密码: ")
        if not confirm_password:
            return

        if password != confirm_password:
            print("❌ 两次输入的密码不一致")
            return

        try:
            print("正在注册...")
            success, message = self.chat_client.register(username, password)

            if success:
                print(f"✅ {message}")
                print("请使用 /login 命令登录")
            else:
                print(f"❌ {message}")

        except Exception as e:
            print(f"❌ 注册时出错: {e}")
    
    def handle_message(self, message: str):
        """处理普通消息"""
        if not validate_connection_state(self.current_state, "logged_in"):
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
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )

    args = parser.parse_args()

    try:
        # 初始化客户端日志系统
        from client.config.client_config import get_client_config
        from shared.logger import init_logger

        client_config = get_client_config()
        logging_config = client_config.get_logging_config()

        # 如果启用调试模式，调整日志级别
        if args.debug:
            logging_config['level'] = 'DEBUG'
            logging_config['console_enabled'] = True

        # 根据模式调整日志配置
        if args.mode == 'tui':
            # TUI模式下禁用控制台日志，避免干扰界面
            logging_config['console_enabled'] = False
        else:
            # 简单模式下也禁用控制台日志，避免干扰print输出
            logging_config['console_enabled'] = False

        # 初始化日志系统
        init_logger(logging_config, "client")

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
