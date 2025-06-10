"""
命令处理器
统一处理客户端命令
"""

from typing import Dict, Callable, Any
from .network.client import ChatClient


class CommandHandler:
    """命令处理器类"""
    
    def __init__(self, client: ChatClient):
        """
        初始化命令处理器
        
        Args:
            client: 聊天客户端实例
        """
        self.client = client
        self.commands = self._init_commands()
    
    def _init_commands(self) -> Dict[str, Callable]:
        """初始化命令映射"""
        return {
            'help': self.handle_help,
            'login': self.handle_login,
            'signin': self.handle_signin,
            'logout': self.handle_logout,
            'info': self.handle_info,
            'list': self.handle_list,
            'create_chat': self.handle_create_chat,
            'join_chat': self.handle_join_chat,
            'enter_chat': self.handle_enter_chat,
            'send_files': self.handle_send_files,
            'recv_files': self.handle_recv_files,
            'exit': self.handle_exit,
        }
    
    def handle_command(self, command: str, args: list) -> str:
        """
        处理命令
        
        Args:
            command: 命令名称
            args: 命令参数
            
        Returns:
            处理结果消息
        """
        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                return f"命令执行错误: {e}"
        else:
            return f"未知命令: {command}"
    
    def handle_help(self, args: list) -> str:
        """处理帮助命令"""
        if args:
            command = args[0]
            if command in self.commands:
                return f"命令 '{command}' 的帮助信息"
            else:
                return f"未知命令: {command}"
        else:
            return "可用命令: " + ", ".join(self.commands.keys())
    
    def handle_login(self, args: list) -> str:
        """处理登录命令"""
        return "登录功能"
    
    def handle_signin(self, args: list) -> str:
        """处理注册命令"""
        return "注册功能"
    
    def handle_logout(self, args: list) -> str:
        """处理登出命令"""
        return "登出功能"
    
    def handle_info(self, args: list) -> str:
        """处理用户信息命令"""
        return "用户信息功能"
    
    def handle_list(self, args: list) -> str:
        """处理列表命令"""
        return "列表功能"
    
    def handle_create_chat(self, args: list) -> str:
        """处理创建聊天组命令"""
        return "创建聊天组功能"
    
    def handle_join_chat(self, args: list) -> str:
        """处理加入聊天组命令"""
        return "加入聊天组功能"
    
    def handle_enter_chat(self, args: list) -> str:
        """处理进入聊天组命令"""
        return "进入聊天组功能"
    
    def handle_send_files(self, args: list) -> str:
        """处理发送文件命令"""
        return "发送文件功能"
    
    def handle_recv_files(self, args: list) -> str:
        """处理接收文件命令"""
        return "接收文件功能"
    
    def handle_exit(self, args: list) -> str:
        """处理退出命令"""
        return "退出功能"
