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
from shared.constants import DISPLAY_TIME_FORMAT


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
    
    def __init__(self, host: str = None, port: int = None):
        """初始化应用"""
        super().__init__()

        # 如果没有传入参数，从配置文件读取默认值
        if host is None or port is None:
            from client.config.client_config import get_client_config
            client_config = get_client_config()
            if host is None:
                host = client_config.get_default_host()
            if port is None:
                port = client_config.get_default_port()

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

        # 历史消息收集器（类似Simple模式）
        self.history_messages = []
        self.current_chat_group_id = None

        # 状态更新定时器
        self.status_update_timer = None
    
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

            if self.chat_client.connect():
                self.is_connected = True
                self.connection_status = "已连接"

                # 连接成功后设置消息处理器（确保覆盖ChatClient的默认处理器）
                self.setup_message_handlers()

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

        # 设置各种消息的处理器，确保覆盖ChatClient的默认处理器
        self.chat_client.network_client.set_message_handler(
            MessageType.CHAT_MESSAGE, self.handle_chat_message
        )
        self.chat_client.network_client.set_message_handler(
            MessageType.CHAT_HISTORY, self.handle_chat_history
        )
        self.chat_client.network_client.set_message_handler(
            MessageType.CHAT_HISTORY_COMPLETE, self.handle_chat_history_complete
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
            MessageType.USER_INFO_RESPONSE, self.handle_user_info_response
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

                        # 不再使用定时器，完全依赖CHAT_HISTORY_COMPLETE通知来完成历史消息加载
                        # 历史消息加载完成将由handle_chat_history_complete方法处理
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

        # 检查禁言状态并提供友好提示
        if hasattr(self, 'status_list') and self.status_list:
            # 从状态面板获取禁言状态（如果有的话）
            # 这里我们先发送消息，让服务器返回具体的错误信息
            pass

        # 发送消息到当前聊天组
        group_id = self.chat_client.current_chat_group['id']
        success = self.chat_client.send_chat_message(message, group_id)

        if success:
            # 消息发送成功，等待服务器广播回来再显示
            # 不在这里立即显示，避免重复显示
            pass
        else:
            self.add_error_message("❌ 消息发送失败，请检查网络连接")
    
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

            # 启动状态更新定时器
            self.start_status_update_timer()

            # 立即请求一次用户信息以获取禁言状态
            self.request_user_info()
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

    def add_history_message(self, sender: str, content: str, is_self: bool = False, timestamp: str = None):
        """添加历史聊天消息（使用较淡的样式）"""
        if not self.chat_log:
            return

        # 按照设计文档格式，但使用较淡的样式表示历史消息
        # 如果提供了时间戳，使用原始时间戳；否则使用当前时间
        if timestamp:
            display_timestamp = timestamp
        else:
            display_timestamp = datetime.now().strftime(DISPLAY_TIME_FORMAT)

        # 第一行：用户名和时间戳（历史消息用较淡的颜色）
        header_line = Text()
        if is_self:
            header_line.append(f"{sender:<30}", style="dim green")
        else:
            header_line.append(f"{sender:<30}", style="dim blue")
        header_line.append(f"{display_timestamp}", style="dim")

        # 第二行：消息内容（带>前缀，历史消息用较淡的颜色）
        content_line = Text()
        content_line.append(">", style="dim")
        if is_self:
            content_line.append(content, style="dim green")
        else:
            content_line.append(content, style="dim")

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
        """处理历史聊天消息 - 收集消息而不是立即显示"""
        try:
            # 验证消息是否属于当前聊天组
            if not hasattr(message, 'chat_group_id'):
                return

            if not self.chat_client or not self.chat_client.current_chat_group:
                return

            current_group_id = self.chat_client.current_chat_group['id']
            if message.chat_group_id != current_group_id:
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
                    from shared.constants import TIMESTAMP_FORMAT, DISPLAY_TIME_FORMAT

                    if isinstance(message.timestamp, str):
                        try:
                            # 尝试解析完整格式并转换为显示格式
                            dt = datetime.strptime(message.timestamp, TIMESTAMP_FORMAT)
                            timestamp_str = dt.strftime(DISPLAY_TIME_FORMAT)
                        except:
                            # 如果解析失败，使用原始时间戳
                            timestamp_str = str(message.timestamp)
                    else:
                        timestamp_str = str(message.timestamp)
                except:
                    timestamp_str = "Unknown time"

            # 判断是否是自己的消息
            is_self = (self.current_user and
                      message.sender_username == self.current_user)

            # 收集历史消息到列表中
            formatted_message = {
                'username': message.sender_username,
                'timestamp': timestamp_str,
                'content': message.content,
                'is_self': is_self
            }
            self.history_messages.append(formatted_message)

            # 计数历史消息
            self.on_history_message_received()

        except Exception as e:
            # 如果处理失败，记录错误消息
            error_message = {
                'username': 'ERROR',
                'timestamp': 'Unknown time',
                'content': f'历史消息处理失败: {e}',
                'is_self': False
            }
            self.history_messages.append(error_message)

    def handle_chat_history_complete(self, message):
        """处理历史消息加载完成通知 - 批量显示所有历史消息"""
        try:
            # 验证消息是否属于当前聊天组
            if not hasattr(message, 'chat_group_id'):
                return

            if not self.chat_client or not self.chat_client.current_chat_group:
                return

            current_group_id = self.chat_client.current_chat_group['id']
            if message.chat_group_id != current_group_id:
                return

            # 批量显示历史消息
            if self.history_messages:
                # 显示加载成功消息
                self.add_system_message(f"✅ 已加载 {len(self.history_messages)} 条历史消息")

                # 逐条显示历史消息（使用较淡样式）
                for msg in self.history_messages:
                    self.add_history_message(
                        msg['username'],
                        msg['content'],
                        msg['is_self'],
                        msg['timestamp']
                    )

                # 添加分隔线
                self.add_system_message("-" * 50)
            else:
                # 检查服务器报告的消息数量
                if hasattr(message, 'message_count') and message.message_count > 0:
                    self.add_system_message(f"⚠️ 服务器报告有 {message.message_count} 条历史消息，但客户端未收到")
                else:
                    self.add_system_message("✅ 暂无历史消息")

                # 添加分隔线
                self.add_system_message("-" * 50)

            # 清空历史消息收集器，为下次使用做准备
            self.history_messages = []

            # 完成历史消息加载状态
            self.finish_history_loading()

        except Exception as e:
            # 如果批量显示失败，使用简单提示
            self.add_error_message(f"❌ 历史消息批量显示失败: {e}")
            if hasattr(message, 'message_count'):
                self.add_system_message(f"✅ 已加载 {message.message_count} 条历史消息")
            self.add_system_message("-" * 50)

            # 清空历史消息收集器
            self.history_messages = []

            # 完成历史消息加载状态
            self.finish_history_loading()

    def handle_system_message(self, message):
        """处理系统消息"""
        self.add_system_message(message.content)

    def handle_error_message(self, message):
        """处理错误消息"""
        error_msg = message.error_message

        # 检查是否是禁言相关的错误，提供更友好的提示
        if "禁言" in error_msg:
            if "您已被禁言" in error_msg:
                self.add_error_message("🚫 您已被管理员禁言，无法发送消息")
                self.add_system_message("💡 如需申诉，请联系管理员")
            elif "聊天组已被禁言" in error_msg or "该聊天组已被禁言" in error_msg:
                self.add_error_message("🚫 当前聊天组已被管理员禁言，无法发送消息")
                self.add_system_message("💡 请尝试切换到其他聊天组")
            else:
                self.add_error_message(f"🚫 {error_msg}")
        else:
            self.add_error_message(error_msg)

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

    def handle_user_info_response(self, message):
        """处理用户信息响应"""
        try:
            # 更新禁言状态显示
            is_user_banned = getattr(message, 'is_user_banned', False)
            is_current_chat_banned = getattr(message, 'is_current_chat_banned', False)

            # 更新状态面板的禁言状态
            if hasattr(self, 'status_list') and self.status_list:
                # 这里我们需要找到状态面板组件并更新它
                # 由于当前使用的是简单的ListView，我们需要重新构建状态显示
                self.update_status_area_with_ban_info(is_user_banned, is_current_chat_banned)

        except Exception as e:
            # 静默处理错误，不影响主要功能
            pass

    def request_user_info(self):
        """请求用户信息以更新状态"""
        if self.chat_client and self.is_logged_in:
            from shared.messages import UserInfoRequest
            request = UserInfoRequest()
            self.chat_client.network_client.send_message(request)

    def start_status_update_timer(self):
        """启动状态更新定时器"""
        if self.is_logged_in:
            # 每30秒更新一次状态
            self.status_update_timer = self.set_timer(30.0, self.request_user_info)

    def stop_status_update_timer(self):
        """停止状态更新定时器"""
        if self.status_update_timer:
            self.status_update_timer.stop()
            self.status_update_timer = None

    def update_status_area_with_ban_info(self, is_user_banned: bool = False, is_current_chat_banned: bool = False):
        """更新状态区域并显示禁言信息"""
        if not self.status_list:
            return

        # 清空现有内容
        self.status_list.clear()

        # 添加连接状态
        status_text = f"连接: {self.connection_status}"
        self.status_list.append(ListItem(Label(status_text)))

        # 添加用户信息（带禁言状态）
        if self.current_user:
            user_text = f"用户: {self.current_user}"
            if is_user_banned:
                user_text += " 🚫(禁言)"
            self.status_list.append(ListItem(Label(user_text)))

        # 添加当前聊天组（带禁言状态）
        chat_text = f"聊天组: {self.current_chat}"
        if is_current_chat_banned:
            chat_text += " 🚫(禁言)"
        self.status_list.append(ListItem(Label(chat_text)))

        # 如果有禁言状态，添加说明
        if is_user_banned or is_current_chat_banned:
            self.status_list.append(ListItem(Label("─" * 20)))
            if is_user_banned:
                self.status_list.append(ListItem(Label("⚠️ 您已被禁言")))
            if is_current_chat_banned:
                self.status_list.append(ListItem(Label("⚠️ 当前聊天组已被禁言")))
            self.status_list.append(ListItem(Label("💡 无法发送消息")))

        # 添加分隔线
        self.status_list.append(ListItem(Label("─" * 20)))

        # 添加在线用户列表
        if self.is_logged_in and self.chat_client:
            self.status_list.append(ListItem(Label("在线用户:")))
            # 这里可以添加在线用户列表，但为了简化，暂时省略

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
            # 设置一个标记，用于检测历史消息加载完成
            self.history_loading = True
            self.history_message_count = 0

            # 清空历史消息收集器
            self.history_messages = []

    def on_history_message_received(self):
        """历史消息接收计数"""
        if hasattr(self, 'history_loading') and self.history_loading:
            self.history_message_count += 1

    def finish_history_loading(self):
        """完成历史消息加载"""
        if hasattr(self, 'history_loading') and self.history_loading:
            self.history_loading = False
            if self.history_message_count > 0:
                self.add_system_message(f"✅ 已加载 {self.history_message_count} 条历史消息")
            else:
                self.add_system_message("✅ 暂无历史消息")
            self.history_message_count = 0

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


def run_chat_app(host: str = None, port: int = None):
    """运行聊天应用"""
    app = ChatRoomApp(host, port)
    app.run()
