"""
命令解析器
解析用户输入的斜杠命令并执行相应操作
"""

import re
import shlex
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from shared.constants import COMMAND_PREFIX


@dataclass
class Command:
    """命令数据结构"""
    name: str
    args: List[str]
    options: Dict[str, Any]
    raw_input: str


class CommandParser:
    """命令解析器"""
    
    def __init__(self):
        """初始化命令解析器"""
        self.commands: Dict[str, Dict[str, Any]] = {}
        self._register_builtin_commands()
    
    def _register_builtin_commands(self):
        """注册内置命令"""
        # 帮助命令
        self.register_command("?", {
            "description": "显示所有可用命令",
            "usage": "/?",
            "handler": None
        })
        
        self.register_command("help", {
            "description": "显示命令帮助信息",
            "usage": "/help [命令名]",
            "handler": None
        })
        
        # 认证命令
        self.register_command("login", {
            "description": "用户登录",
            "usage": "/login",
            "handler": None
        })
        
        self.register_command("signin", {
            "description": "用户注册",
            "usage": "/signin",
            "handler": None
        })
        
        # 信息查询命令
        self.register_command("info", {
            "description": "显示当前用户信息",
            "usage": "/info",
            "handler": None
        })
        
        self.register_command("list", {
            "description": "显示各种列表信息",
            "usage": "/list [-u|-s|-c|-g|-f]",
            "options": {
                "-u": "显示所有用户",
                "-s": "显示当前聊天组用户",
                "-c": "显示已加入的聊天组",
                "-g": "显示所有群聊",
                "-f": "显示当前聊天组文件"
            },
            "handler": None
        })
        
        # 聊天组命令
        self.register_command("create_chat", {
            "description": "创建聊天组",
            "usage": "/create_chat <聊天组名> [用户名1] [用户名2] ...",
            "handler": None
        })
        
        self.register_command("enter_chat", {
            "description": "进入聊天组",
            "usage": "/enter_chat <聊天组名>",
            "handler": None
        })
        
        self.register_command("join_chat", {
            "description": "加入聊天组",
            "usage": "/join_chat <聊天组名>",
            "handler": None
        })
        
        # 文件命令
        self.register_command("send_files", {
            "description": "发送文件",
            "usage": "/send_files <文件路径1> [文件路径2] ...",
            "handler": None
        })
        
        self.register_command("recv_files", {
            "description": "接收文件",
            "usage": "/recv_files [-n <文件标识>|-l|-a]",
            "options": {
                "-n": "接收指定文件",
                "-l": "列出可下载文件",
                "-a": "接收所有文件"
            },
            "handler": None
        })
        
        # 系统命令
        self.register_command("exit", {
            "description": "退出系统",
            "usage": "/exit",
            "handler": None
        })
    
    def register_command(self, name: str, command_info: Dict[str, Any]):
        """注册命令"""
        self.commands[name] = command_info
    
    def parse_command(self, input_text: str) -> Optional[Command]:
        """解析命令"""
        if not input_text.startswith(COMMAND_PREFIX):
            return None
        
        # 移除命令前缀
        command_text = input_text[len(COMMAND_PREFIX):].strip()
        if not command_text:
            return None
        
        try:
            # 使用shlex分割命令，支持引号
            parts = shlex.split(command_text)
        except ValueError:
            # 如果shlex失败，使用简单分割
            parts = command_text.split()
        
        if not parts:
            return None
        
        command_name = parts[0]
        args = []
        options = {}
        
        # 解析参数和选项
        i = 1
        while i < len(parts):
            part = parts[i]
            if part.startswith('-'):
                # 这是一个选项
                option_name = part
                option_value = True
                
                # 检查是否有选项值
                if i + 1 < len(parts) and not parts[i + 1].startswith('-'):
                    option_value = parts[i + 1]
                    i += 1
                
                options[option_name] = option_value
            else:
                # 这是一个参数
                args.append(part)
            i += 1
        
        return Command(
            name=command_name,
            args=args,
            options=options,
            raw_input=input_text
        )
    
    def get_command_help(self, command_name: str = None) -> str:
        """获取命令帮助信息"""
        if command_name:
            # 获取特定命令的帮助
            if command_name in self.commands:
                cmd_info = self.commands[command_name]
                help_text = f"命令: /{command_name}\n"
                help_text += f"描述: {cmd_info.get('description', '无描述')}\n"
                help_text += f"用法: {cmd_info.get('usage', f'/{command_name}')}\n"
                
                if 'options' in cmd_info:
                    help_text += "选项:\n"
                    for option, desc in cmd_info['options'].items():
                        help_text += f"  {option}: {desc}\n"
                
                return help_text
            else:
                return f"未知命令: {command_name}"
        else:
            # 获取所有命令的列表
            help_text = "可用命令:\n"
            for cmd_name, cmd_info in self.commands.items():
                help_text += f"  /{cmd_name}: {cmd_info.get('description', '无描述')}\n"
            help_text += "\n使用 /help <命令名> 获取详细帮助"
            return help_text
    
    def is_valid_command(self, command_name: str) -> bool:
        """检查是否为有效命令"""
        return command_name in self.commands
    
    def get_command_suggestions(self, partial_command: str) -> List[str]:
        """获取命令建议（用于自动补全）"""
        suggestions = []
        for cmd_name in self.commands.keys():
            if cmd_name.startswith(partial_command):
                suggestions.append(cmd_name)
        return sorted(suggestions)


class CommandHandler:
    """命令处理器"""
    
    def __init__(self, chat_client):
        """初始化命令处理器"""
        self.chat_client = chat_client
        self.parser = CommandParser()
        self.command_handlers: Dict[str, Callable] = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """注册命令处理器"""
        self.command_handlers = {
            "?": self.handle_help,
            "help": self.handle_help,
            "login": self.handle_login,
            "signin": self.handle_signin,
            "info": self.handle_info,
            "list": self.handle_list,
            "create_chat": self.handle_create_chat,
            "enter_chat": self.handle_enter_chat,
            "join_chat": self.handle_join_chat,
            "send_files": self.handle_send_files,
            "recv_files": self.handle_recv_files,
            "exit": self.handle_exit,
        }
    
    def handle_command(self, input_text: str) -> tuple[bool, str]:
        """处理命令"""
        command = self.parser.parse_command(input_text)
        if not command:
            return False, "无效的命令格式"
        
        if command.name not in self.command_handlers:
            return False, f"未知命令: {command.name}"
        
        try:
            handler = self.command_handlers[command.name]
            return handler(command)
        except Exception as e:
            return False, f"命令执行错误: {str(e)}"
    
    def handle_help(self, command: Command) -> tuple[bool, str]:
        """处理帮助命令"""
        if command.args:
            help_text = self.parser.get_command_help(command.args[0])
        else:
            help_text = self.parser.get_command_help()
        return True, help_text
    
    def handle_login(self, command: Command) -> tuple[bool, str]:
        """处理登录命令"""
        # 这里应该触发登录界面
        return True, "请输入用户名和密码进行登录"
    
    def handle_signin(self, command: Command) -> tuple[bool, str]:
        """处理注册命令"""
        # 这里应该触发注册界面
        return True, "请输入用户名和密码进行注册"
    
    def handle_info(self, command: Command) -> tuple[bool, str]:
        """处理信息查询命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"
        # TODO: 实现用户信息查询
        return True, "用户信息查询功能待实现"
    
    def handle_list(self, command: Command) -> tuple[bool, str]:
        """处理列表命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"
        # TODO: 实现各种列表查询
        return True, "列表查询功能待实现"
    
    def handle_create_chat(self, command: Command) -> tuple[bool, str]:
        """处理创建聊天组命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"
        
        if not command.args:
            return False, "请指定聊天组名称"
        
        # TODO: 实现创建聊天组
        return True, f"创建聊天组 '{command.args[0]}' 功能待实现"
    
    def handle_enter_chat(self, command: Command) -> tuple[bool, str]:
        """处理进入聊天组命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"
        
        if not command.args:
            return False, "请指定聊天组名称"
        
        # TODO: 实现进入聊天组
        return True, f"进入聊天组 '{command.args[0]}' 功能待实现"
    
    def handle_join_chat(self, command: Command) -> tuple[bool, str]:
        """处理加入聊天组命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"
        
        if not command.args:
            return False, "请指定聊天组名称"
        
        # TODO: 实现加入聊天组
        return True, f"加入聊天组 '{command.args[0]}' 功能待实现"
    
    def handle_send_files(self, command: Command) -> tuple[bool, str]:
        """处理发送文件命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"
        
        if not command.args:
            return False, "请指定文件路径"
        
        # TODO: 实现文件发送
        return True, f"发送文件功能待实现"
    
    def handle_recv_files(self, command: Command) -> tuple[bool, str]:
        """处理接收文件命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"
        
        # TODO: 实现文件接收
        return True, "接收文件功能待实现"
    
    def handle_exit(self, command: Command) -> tuple[bool, str]:
        """处理退出命令"""
        # TODO: 实现退出逻辑
        return True, "正在退出..."
