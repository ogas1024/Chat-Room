"""
Textual TUI应用主类
实现聊天室的图形化命令行界面
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header, Footer, Input, RichLog, Static,
    Button, Label, ListView, ListItem
)
from textual.reactive import reactive
from textual.message import Message
from textual import events
from rich.text import Text
from rich.console import Console
from datetime import datetime
from typing import Optional

from client.core.client import ChatClient
from client.commands.parser import CommandHandler
from client.ui.themes import get_theme_manager, apply_theme_to_console
from client.ui.components import EnhancedChatLog, StatusPanel, EnhancedInput, LoadingIndicator
from shared.constants import DEFAULT_HOST, DEFAULT_PORT, DISPLAY_TIME_FORMAT


class ChatRoomApp(App):
    """聊天室TUI应用"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 3;
        grid-gutter: 1;
    }
    
    #chat_area {
        column-span: 2;
        row-span: 2;
        border: solid $primary;
        padding: 1;
    }
    
    #status_area {
        row-span: 3;
        border: solid $secondary;
        padding: 1;
    }
    
    #input_area {
        column-span: 2;
        border: solid $accent;
        padding: 1;
    }
    
    #chat_log {
        height: 100%;
        scrollbar-gutter: stable;
    }
    
    #status_list {
        height: 100%;
    }
    
    #message_input {
        width: 100%;
    }
    
    .user_message {
        color: $success;
    }
    
    .other_message {
        color: $text;
    }
    
    .system_message {
        color: $warning;
        text-style: italic;
    }

    .error_message {
        color: $error;
        text-style: bold;
    }
    
    .timestamp {
        color: $text-muted;
    }
    """
    
    TITLE = "Chat-Room 聊天室"
    SUB_TITLE = "基于Python的实时聊天应用"
    
    # 响应式属性
    current_user = reactive(None)
    current_chat = reactive("未连接")
    connection_status = reactive("断开连接")
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """初始化应用"""
        super().__init__()
        self.host = host
        self.port = port
        self.chat_client: Optional[ChatClient] = None
        self.command_handler: Optional[CommandHandler] = None
        
        # UI组件引用
        self.chat_log: Optional[RichLog] = None
        self.message_input: Optional[Input] = None
        self.status_list: Optional[ListView] = None
        
        # 应用状态
        self.is_connected = False
        self.is_logged_in = False
        self.login_mode = False  # 是否处于登录模式
        self.register_mode = False  # 是否处于注册模式
        self.login_step = 0  # 登录步骤：0=用户名，1=密码
        self.temp_username = ""  # 临时存储用户名
    
    def compose(self) -> ComposeResult:
        """构建UI布局"""
        yield Header()
        
        # 聊天区域
        with Container(id="chat_area"):
            yield Label("聊天记录", classes="area_title")
            yield RichLog(id="chat_log", highlight=True, markup=True)
        
        # 状态区域
        with Container(id="status_area"):
            yield Label("状态信息", classes="area_title")
            yield ListView(id="status_list")
        
        # 输入区域
        with Container(id="input_area"):
            yield Label("消息输入 (输入 /help 查看命令)", classes="area_title")
            yield Input(
                placeholder="输入消息或命令...",
                id="message_input"
            )
        
        yield Footer()
    
    def on_mount(self) -> None:
        """应用挂载时的初始化"""
        # 获取组件引用
        self.chat_log = self.query_one("#chat_log", RichLog)
        self.message_input = self.query_one("#message_input", Input)
        self.status_list = self.query_one("#status_list", ListView)
        
        # 设置焦点到输入框
        self.message_input.focus()
        
        # 显示欢迎信息
        self.add_system_message("欢迎使用Chat-Room聊天室！")
        self.add_system_message("请使用 /login 登录或 /signin 注册")
        
        # 尝试连接服务器
        self.connect_to_server()
    
    def connect_to_server(self):
        """连接到服务器"""
        try:
            self.chat_client = ChatClient(self.host, self.port)
            self.command_handler = CommandHandler(self.chat_client)
            
            # 设置消息处理器
            self.setup_message_handlers()
            
            if self.chat_client.connect():
                self.is_connected = True
                self.connection_status = "已连接"
                self.add_system_message(f"✅ 已连接到服务器 {self.host}:{self.port}")
                self.update_status_area()
            else:
                self.add_error_message(f"❌ 无法连接到服务器 {self.host}:{self.port}")
                
        except Exception as e:
            self.add_error_message(f"❌ 连接错误: {str(e)}")
    
    def setup_message_handlers(self):
        """设置消息处理器"""
        if not self.chat_client:
            return

        from shared.constants import MessageType

        # 设置各种消息的处理器
        self.chat_client.network_client.set_message_handler(
            MessageType.CHAT_MESSAGE, self.handle_chat_message
        )
        self.chat_client.network_client.set_message_handler(
            MessageType.CHAT_HISTORY, self.handle_chat_history
        )
        self.chat_client.network_client.set_message_handler(
            MessageType.SYSTEM_MESSAGE, self.handle_system_message
        )
        self.chat_client.network_client.set_message_handler(
            MessageType.ERROR_MESSAGE, self.handle_error_message
        )
        self.chat_client.network_client.set_message_handler(
            MessageType.USER_STATUS_UPDATE, self.handle_user_status_update
        )
        self.chat_client.network_client.set_message_handler(
            MessageType.FILE_NOTIFICATION, self.handle_file_notification
        )
        self.chat_client.network_client.set_message_handler(
            MessageType.AI_CHAT_RESPONSE, self.handle_ai_response
        )
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入提交"""
        if event.input.id != "message_input":
            return
        
        user_input = event.value.strip()
        if not user_input:
            return
        
        # 清空输入框
        self.message_input.value = ""
        
        # 处理特殊模式
        if self.login_mode:
            self.handle_login_input(user_input)
            return
        elif self.register_mode:
            self.handle_register_input(user_input)
            return
        
        # 处理普通输入
        if user_input.startswith('/'):
            self.handle_command(user_input)
        else:
            self.handle_message(user_input)
    
    def handle_command(self, command: str):
        """处理命令"""
        if command == "/login":
            self.start_login_process()
        elif command == "/signin":
            self.start_register_process()
        elif command == "/exit":
            self.exit()
        elif command in ["/help", "/?"]:
            self.show_help()
        else:
            # 使用命令处理器
            if self.command_handler:
                success, message = self.command_handler.handle_command(command)
                if success:
                    self.add_system_message(f"✅ {message}")
                    # 如果是进入聊天组命令，清空聊天记录并更新当前聊天组显示
                    if command.startswith('/enter_chat'):
                        self.clear_chat_log()
                        # 更新当前聊天组显示
                        if self.chat_client and self.chat_client.current_chat_group:
                            self.current_chat = self.chat_client.current_chat_group['name']
                        self.update_status_area()
                    # 如果是列表命令，更新状态区域
                    elif command.startswith('/list'):
                        self.update_status_area_with_list_result(command, message)
                else:
                    self.add_error_message(f"❌ {message}")
            else:
                self.add_error_message("❌ 未连接到服务器")
    
    def handle_message(self, message: str):
        """处理普通消息"""
        if not self.is_logged_in:
            self.add_error_message("❌ 请先登录")
            return

        if not self.chat_client:
            self.add_error_message("❌ 未连接到服务器")
            return

        # 检查是否在聊天组中
        if not self.chat_client.current_chat_group:
            self.add_error_message("❌ 请先进入聊天组")
            return

        # 发送消息到当前聊天组
        group_id = self.chat_client.current_chat_group['id']
        success = self.chat_client.send_chat_message(message, group_id)

        if success:
            # 消息发送成功，等待服务器广播回来再显示
            # 不在这里立即显示，避免重复显示
            pass
        else:
            self.add_error_message("❌ 消息发送失败")
    
    def start_login_process(self):
        """开始登录流程"""
        if not self.is_connected:
            self.add_error_message("❌ 请先连接到服务器")
            return
        
        self.login_mode = True
        self.login_step = 0
        self.add_system_message("请输入用户名:")
        self.message_input.placeholder = "用户名"
    
    def start_register_process(self):
        """开始注册流程"""
        if not self.is_connected:
            self.add_error_message("❌ 请先连接到服务器")
            return
        
        self.register_mode = True
        self.login_step = 0
        self.add_system_message("请输入用户名:")
        self.message_input.placeholder = "用户名"
    
    def handle_login_input(self, user_input: str):
        """处理登录输入"""
        if self.login_step == 0:
            # 输入用户名
            self.temp_username = user_input
            self.login_step = 1
            self.add_system_message("请输入密码:")
            self.message_input.placeholder = "密码"
            # 设置密码掩码
            self.message_input.password = True
        elif self.login_step == 1:
            # 输入密码
            password = user_input
            self.perform_login(self.temp_username, password)
            self.reset_input_mode()
    
    def handle_register_input(self, user_input: str):
        """处理注册输入"""
        if self.login_step == 0:
            # 输入用户名
            self.temp_username = user_input
            self.login_step = 1
            self.add_system_message("请输入密码:")
            self.message_input.placeholder = "密码"
        elif self.login_step == 1:
            # 输入密码
            password = user_input
            self.perform_register(self.temp_username, password)
            self.reset_input_mode()
    
    def perform_login(self, username: str, password: str):
        """执行登录"""
        if not self.chat_client:
            self.add_error_message("❌ 未连接到服务器")
            return
        
        self.add_system_message("正在登录...")
        success, message = self.chat_client.login(username, password)
        
        if success:
            self.is_logged_in = True
            self.current_user = username
            self.current_chat = "public"
            self.add_system_message(f"✅ {message}")
            self.add_system_message(f"欢迎, {username}! 您已进入公频聊天组")
            self.update_status_area()
        else:
            self.add_error_message(f"❌ {message}")
    
    def perform_register(self, username: str, password: str):
        """执行注册"""
        if not self.chat_client:
            self.add_error_message("❌ 未连接到服务器")
            return
        
        self.add_system_message("正在注册...")
        success, message = self.chat_client.register(username, password)
        
        if success:
            self.add_system_message(f"✅ {message}")
            self.add_system_message("请使用 /login 命令登录")
        else:
            self.add_error_message(f"❌ {message}")
    
    def reset_input_mode(self):
        """重置输入模式"""
        self.login_mode = False
        self.register_mode = False
        self.login_step = 0
        self.temp_username = ""
        self.message_input.placeholder = "输入消息或命令..."
        # 清除密码掩码
        self.message_input.password = False

    def show_help(self):
        """显示帮助信息"""
        help_text = """
可用命令:
• /help 或 /? - 显示此帮助信息
• /login - 用户登录
• /signin - 用户注册
• /info - 显示用户信息
• /list -u - 显示所有用户
• /list -s - 显示当前聊天组用户
• /list -c - 显示已加入的聊天组
• /create_chat <名称> [用户...] - 创建聊天组
• /enter_chat <名称> - 进入聊天组
• /join_chat <名称> - 加入聊天组
• /exit - 退出程序

直接输入文字即可发送消息到当前聊天组
        """
        self.add_system_message(help_text.strip())

    # 消息处理方法
    def add_chat_message(self, sender: str, content: str, is_self: bool = False):
        """添加聊天消息"""
        if not self.chat_log:
            return

        # 按照设计文档格式：Alice                    <Sat May 24 23:12:36 CST 2025>
        #                        >hello Bob!🥰
        timestamp = datetime.now().strftime(DISPLAY_TIME_FORMAT)

        # 第一行：用户名和时间戳
        header_line = Text()
        if is_self:
            header_line.append(f"{sender:<30}", style="bold green")
        else:
            header_line.append(f"{sender:<30}", style="bold blue")
        header_line.append(f"{timestamp}", style="dim")

        # 第二行：消息内容（带>前缀）
        content_line = Text()
        content_line.append(">", style="dim")
        if is_self:
            content_line.append(content, style="green")
        else:
            content_line.append(content)

        # 写入两行
        self.chat_log.write(header_line)
        self.chat_log.write(content_line)

        # 添加空行分隔
        self.chat_log.write("")

    def add_system_message(self, content: str):
        """添加系统消息"""
        if not self.chat_log:
            return

        # 系统消息使用简化格式
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = Text()
        message.append(f"[{timestamp}] ", style="dim")
        message.append("系统: ", style="bold yellow")
        message.append(content, style="italic")

        self.chat_log.write(message)

    def add_error_message(self, content: str):
        """添加错误消息"""
        if not self.chat_log:
            return

        # 错误消息使用简化格式
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = Text()
        message.append(f"[{timestamp}] ", style="dim")
        message.append("错误: ", style="bold red")
        message.append(content, style="red")

        self.chat_log.write(message)

    def update_status_area(self):
        """更新状态区域"""
        if not self.status_list:
            return

        # 清空现有内容
        self.status_list.clear()

        # 添加连接状态
        status_text = f"连接: {self.connection_status}"
        self.status_list.append(ListItem(Label(status_text)))

        # 添加用户信息
        if self.current_user:
            user_text = f"用户: {self.current_user}"
            self.status_list.append(ListItem(Label(user_text)))

        # 添加当前聊天组
        chat_text = f"聊天组: {self.current_chat}"
        self.status_list.append(ListItem(Label(chat_text)))

        # 添加分隔线
        self.status_list.append(ListItem(Label("─" * 20)))

        # 添加在线用户列表
        if self.is_logged_in and self.chat_client:
            self.status_list.append(ListItem(Label("在线用户:")))

            # 获取当前聊天组用户列表
            if self.chat_client.current_chat_group:
                success, _, users = self.chat_client.list_users("current_chat")
                if success and users:
                    for user in users[:5]:  # 最多显示5个用户
                        status_icon = "🟢" if user['is_online'] else "🔴"
                        user_text = f"{status_icon} {user['username']}"
                        self.status_list.append(ListItem(Label(user_text)))

                    if len(users) > 5:
                        self.status_list.append(ListItem(Label(f"... 还有 {len(users) - 5} 个用户")))
                else:
                    self.status_list.append(ListItem(Label("  暂无其他用户")))
            else:
                self.status_list.append(ListItem(Label("  请先进入聊天组")))

    def update_status_area_with_list_result(self, command: str, result: str):
        """根据列表命令结果更新状态区域"""
        if not self.status_list:
            return

        # 清空现有内容
        self.status_list.clear()

        # 添加基本状态信息
        status_text = f"连接: {self.connection_status}"
        self.status_list.append(ListItem(Label(status_text)))

        if self.current_user:
            user_text = f"用户: {self.current_user}"
            self.status_list.append(ListItem(Label(user_text)))

        chat_text = f"聊天组: {self.current_chat}"
        self.status_list.append(ListItem(Label(chat_text)))

        # 添加分隔线
        self.status_list.append(ListItem(Label("─" * 20)))

        # 添加命令结果标题
        if "/list -u" in command:
            title = "所有用户列表:"
        elif "/list -s" in command:
            title = "当前聊天组成员:"
        elif "/list -c" in command:
            title = "已加入的聊天组:"
        elif "/list -g" in command:
            title = "所有群聊列表:"
        elif "/list -f" in command:
            title = "聊天组文件列表:"
        else:
            title = "查询结果:"

        self.status_list.append(ListItem(Label(title)))

        # 解析并显示结果
        lines = result.split('\n')
        for line in lines[1:]:  # 跳过第一行标题
            if line.strip():
                # 限制显示长度，避免界面过于拥挤
                display_line = line[:50] + "..." if len(line) > 50 else line
                self.status_list.append(ListItem(Label(display_line)))

        # 如果结果太多，显示提示
        if len(lines) > 10:
            self.status_list.append(ListItem(Label(f"... 还有 {len(lines) - 10} 项")))

    # 网络消息处理器
    def handle_chat_message(self, message):
        """处理实时聊天消息"""
        # 验证消息是否属于当前聊天组
        if not hasattr(message, 'chat_group_id'):
            # 消息没有聊天组ID，忽略显示
            return

        if not self.chat_client or not self.chat_client.current_chat_group:
            # 没有聊天客户端或用户没有当前聊天组，忽略显示
            return

        current_group_id = self.chat_client.current_chat_group['id']
        if message.chat_group_id != current_group_id:
            # 消息不属于当前聊天组，忽略显示
            return

        is_self = (self.current_user and
                  message.sender_username == self.current_user)
        self.add_chat_message(
            message.sender_username,
            message.content,
            is_self
        )

    def handle_chat_history(self, message):
        """处理历史聊天消息"""
        # 验证消息是否属于当前聊天组
        if not hasattr(message, 'chat_group_id'):
            return

        if not self.chat_client or not self.chat_client.current_chat_group:
            return

        current_group_id = self.chat_client.current_chat_group['id']
        if message.chat_group_id != current_group_id:
            return

        # 历史消息以不同样式显示，不区分是否为自己发送
        is_self = (self.current_user and
                  message.sender_username == self.current_user)
        self.add_chat_message(
            message.sender_username,
            message.content,
            is_self
        )

    def handle_system_message(self, message):
        """处理系统消息"""
        self.add_system_message(message.content)

    def handle_error_message(self, message):
        """处理错误消息"""
        self.add_error_message(message.error_message)

    def handle_user_status_update(self, message):
        """处理用户状态更新"""
        # 显示用户状态变化消息
        if hasattr(message, 'username') and hasattr(message, 'is_online'):
            status = "上线" if message.is_online else "下线"
            self.add_system_message(f"用户 {message.username} 已{status}")

        # 更新用户在线状态显示
        self.update_status_area()

    def handle_file_notification(self, message):
        """处理文件通知消息"""
        # 文件通知作为系统消息显示
        self.add_system_message(message.content)

    def handle_ai_response(self, message):
        """处理AI响应消息"""
        if hasattr(message, 'message') and message.message:
            # AI响应作为系统消息显示，带特殊标识
            self.add_ai_message(message.message)

    def add_ai_message(self, content: str):
        """添加AI消息"""
        if not self.chat_log:
            return

        # AI消息使用特殊格式
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = Text()
        message.append(f"[{timestamp}] ", style="dim")
        message.append("🤖 AI助手: ", style="bold cyan")
        message.append(content, style="cyan")

        self.chat_log.write(message)

    def clear_chat_log(self):
        """清空聊天记录"""
        if self.chat_log:
            self.chat_log.clear()
            self.add_system_message("已清空聊天记录，正在加载历史消息...")

    # 应用生命周期
    def on_unmount(self) -> None:
        """应用卸载时清理资源"""
        if self.chat_client:
            self.chat_client.disconnect()

    def action_quit(self) -> None:
        """退出应用"""
        if self.chat_client:
            self.chat_client.disconnect()
        self.exit()


def run_chat_app(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    """运行聊天应用"""
    app = ChatRoomApp(host, port)
    app.run()
