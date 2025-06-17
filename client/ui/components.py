"""
自定义UI组件
提供增强的聊天室界面组件
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from textual.widgets import Static, Input, RichLog
from textual.reactive import reactive
from textual.message import Message
from textual import events
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align

from client.ui.themes import get_current_theme, get_message_style, get_status_style


class EnhancedChatLog(RichLog):
    """增强的聊天日志组件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_count = 0
        self.max_messages = 1000  # 最大消息数量
        
    def add_message(self, sender: str, content: str, message_type: str = "chat", 
                   is_self: bool = False, timestamp: datetime = None):
        """添加消息到聊天日志"""
        if timestamp is None:
            timestamp = datetime.now()
        
        theme = get_current_theme()
        
        # 创建消息显示
        if message_type == "chat":
            self._add_chat_message(sender, content, is_self, timestamp, theme)
        elif message_type == "system":
            self._add_system_message(content, timestamp, theme)
        elif message_type == "error":
            self._add_error_message(content, timestamp, theme)
        elif message_type == "ai":
            self._add_ai_message(content, timestamp, theme)
        elif message_type == "file":
            self._add_file_message(sender, content, timestamp, theme)
        
        # 管理消息数量
        self.message_count += 1
        if self.message_count > self.max_messages:
            self.clear()
            self.write(Text("--- 消息历史已清理 ---", style="dim"))
            self.message_count = 1
    
    def _add_chat_message(self, sender: str, content: str, is_self: bool, 
                         timestamp: datetime, theme):
        """添加聊天消息"""
        # 按设计文档格式显示
        time_str = timestamp.strftime("<%a %b %d %H:%M:%S CST %Y>")
        
        # 第一行：用户名和时间戳
        header = Text()
        style = theme.styles["chat.self"] if is_self else theme.styles["chat.other"]
        header.append(f"{sender:<30}", style=style)
        header.append(time_str, style=theme.styles["chat.timestamp"])
        
        # 第二行：消息内容
        content_line = Text()
        content_line.append(">", style=theme.styles["chat.timestamp"])
        content_line.append(content, style=style if is_self else None)
        
        self.write(header)
        self.write(content_line)
        self.write("")  # 空行分隔
    
    def _add_system_message(self, content: str, timestamp: datetime, theme):
        """添加系统消息"""
        time_str = timestamp.strftime("%H:%M:%S")
        message = Text()
        message.append(f"[{time_str}] ", style=theme.styles["chat.timestamp"])
        message.append("🔔 系统: ", style=theme.styles["chat.system"])
        message.append(content, style=theme.styles["chat.system"])
        self.write(message)
    
    def _add_error_message(self, content: str, timestamp: datetime, theme):
        """添加错误消息"""
        time_str = timestamp.strftime("%H:%M:%S")
        message = Text()
        message.append(f"[{time_str}] ", style=theme.styles["chat.timestamp"])
        message.append("❌ 错误: ", style=theme.styles["chat.error"])
        message.append(content, style=theme.styles["chat.error"])
        self.write(message)
    
    def _add_ai_message(self, content: str, timestamp: datetime, theme):
        """添加AI消息"""
        time_str = timestamp.strftime("%H:%M:%S")
        message = Text()
        message.append(f"[{time_str}] ", style=theme.styles["chat.timestamp"])
        message.append("🤖 AI助手: ", style=theme.styles["chat.ai"])
        message.append(content, style=theme.styles["chat.ai"])
        self.write(message)
    
    def _add_file_message(self, sender: str, content: str, timestamp: datetime, theme):
        """添加文件消息"""
        time_str = timestamp.strftime("%H:%M:%S")
        message = Text()
        message.append(f"[{time_str}] ", style=theme.styles["chat.timestamp"])
        message.append(f"📎 {sender}: ", style=theme.styles["chat.system"])
        message.append(content, style=theme.styles["chat.system"])
        self.write(message)


class StatusPanel(Static):
    """状态面板组件"""

    connection_status = reactive("未连接")
    current_user = reactive("")
    current_chat = reactive("未进入聊天组")
    online_users = reactive([])
    # 禁言状态
    is_user_banned = reactive(False)
    is_current_chat_banned = reactive(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme = get_current_theme()
    
    def render(self) -> Panel:
        """渲染状态面板"""
        # 创建状态表格
        table = Table.grid(padding=(0, 1))
        table.add_column(style="bold")
        table.add_column()

        # 连接状态
        status_style = self.theme.styles["status.online"] if "已连接" in self.connection_status else self.theme.styles["status.offline"]
        table.add_row("连接:", Text(self.connection_status, style=status_style))

        # 用户信息
        if self.current_user:
            user_text = Text()
            user_text.append(self.current_user, style=self.theme.styles["chat.self"])

            # 添加用户禁言状态指示器
            if self.is_user_banned:
                user_text.append(" 🚫", style="red")
                user_text.append("(禁言)", style="red")

            table.add_row("用户:", user_text)

        # 当前聊天组
        chat_text = Text()
        chat_text.append(self.current_chat, style=self.theme.styles["chat.other"])

        # 添加聊天组禁言状态指示器
        if self.is_current_chat_banned:
            chat_text.append(" 🚫", style="red")
            chat_text.append("(禁言)", style="red")

        table.add_row("聊天组:", chat_text)

        # 禁言状态说明
        if self.is_user_banned or self.is_current_chat_banned:
            table.add_row("", "")
            if self.is_user_banned:
                table.add_row("", Text("⚠️ 您已被禁言", style="red bold"))
            if self.is_current_chat_banned:
                table.add_row("", Text("⚠️ 当前聊天组已被禁言", style="red bold"))
            table.add_row("", Text("无法发送消息", style="red"))

        # 分隔线
        table.add_row("", "")
        table.add_row("在线用户:", "")

        # 在线用户列表
        for user in self.online_users[:8]:  # 最多显示8个用户
            status_icon = "🟢" if user.get('is_online', False) else "🔴"
            username = user.get('username', 'Unknown')
            table.add_row("", f"{status_icon} {username}")

        if len(self.online_users) > 8:
            table.add_row("", f"... 还有 {len(self.online_users) - 8} 个用户")

        return Panel(
            table,
            title="[bold]状态信息[/bold]",
            border_style=self.theme.styles["border.active"]
        )
    
    def update_connection_status(self, status: str):
        """更新连接状态"""
        self.connection_status = status
    
    def update_user_info(self, username: str):
        """更新用户信息"""
        self.current_user = username

    def update_ban_status(self, is_user_banned: bool = False, is_current_chat_banned: bool = False):
        """更新禁言状态"""
        self.is_user_banned = is_user_banned
        self.is_current_chat_banned = is_current_chat_banned
    
    def update_chat_info(self, chat_name: str):
        """更新聊天组信息"""
        self.current_chat = chat_name
    
    def update_online_users(self, users: List[Dict[str, Any]]):
        """更新在线用户列表"""
        self.online_users = users


class EnhancedInput(Input):
    """增强的输入组件"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command_history = []
        self.history_index = -1
        self.max_history = 50
    
    def add_to_history(self, command: str):
        """添加命令到历史记录"""
        if command and command != self.command_history[-1:]:
            self.command_history.append(command)
            if len(self.command_history) > self.max_history:
                self.command_history.pop(0)
        self.history_index = len(self.command_history)
    
    def on_key(self, event: events.Key) -> None:
        """处理按键事件"""
        if event.key == "up":
            # 上箭头：历史记录向上
            if self.command_history and self.history_index > 0:
                self.history_index -= 1
                self.value = self.command_history[self.history_index]
                self.cursor_position = len(self.value)
                event.prevent_default()
        elif event.key == "down":
            # 下箭头：历史记录向下
            if self.command_history and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.value = self.command_history[self.history_index]
                self.cursor_position = len(self.value)
                event.prevent_default()
            elif self.history_index >= len(self.command_history) - 1:
                self.value = ""
                self.history_index = len(self.command_history)
                event.prevent_default()
        elif event.key == "tab":
            # Tab键：命令自动补全（可以扩展）
            self._handle_tab_completion()
            event.prevent_default()
        else:
            super().on_key(event)
    
    def _handle_tab_completion(self):
        """处理Tab自动补全"""
        current_text = self.value
        if current_text.startswith("/"):
            # 命令补全
            commands = [
                "/help", "/login", "/signin", "/info", "/list", 
                "/create_chat", "/join_chat", "/enter_chat",
                "/send_files", "/recv_files", "/ai", "/exit"
            ]
            
            matches = [cmd for cmd in commands if cmd.startswith(current_text)]
            if len(matches) == 1:
                self.value = matches[0] + " "
                self.cursor_position = len(self.value)
            elif len(matches) > 1:
                # 显示可能的补全选项（这里简化处理）
                pass


class LoadingIndicator(Static):
    """加载指示器组件"""
    
    def __init__(self, message: str = "加载中...", **kwargs):
        super().__init__(**kwargs)
        self.loading_message = message
        self.is_loading = False
    
    def render(self) -> Panel:
        """渲染加载指示器"""
        if not self.is_loading:
            return Panel("")
        
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.add_task(description=self.loading_message, total=None)
        
        return Panel(
            Align.center(progress),
            title="[bold]请稍候[/bold]",
            border_style="blue"
        )
    
    def start_loading(self, message: str = None):
        """开始加载"""
        if message:
            self.loading_message = message
        self.is_loading = True
        self.refresh()
    
    def stop_loading(self):
        """停止加载"""
        self.is_loading = False
        self.refresh()
