"""
命令处理器
统一处理客户端命令
"""

from typing import Dict, Callable
from client.core.client import ChatClient


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
        if not args:
            return "用法: /send_files <文件路径1> [文件路径2] ..."

        if not self.client.is_logged_in():
            return "请先登录"

        if not self.client.current_chat_group:
            return "请先进入聊天组"

        results = []
        for file_path in args:
            success, message = self.client.send_file(file_path)
            if success:
                results.append(f"✓ {message}")
            else:
                results.append(f"✗ {file_path}: {message}")

        return "\n".join(results)

    def handle_recv_files(self, args: list) -> str:
        """处理接收文件命令"""
        if not args:
            return "用法: /recv_files -l 或 /recv_files -n <文件ID1> [文件ID2] ..."

        if not self.client.is_logged_in():
            return "请先登录"

        if not self.client.current_chat_group:
            return "请先进入聊天组"

        if args[0] == '-l':
            # 列出可下载文件
            success, message, files = self.client.list_files()
            if success and files:
                result = "可下载文件列表:\n"
                for file_info in files:
                    size_mb = file_info['file_size'] / (1024 * 1024)
                    result += f"ID: {file_info['file_id']} | {file_info['original_filename']} | {size_mb:.2f}MB | 上传者: {file_info['uploader_username']} | 时间: {file_info['upload_time']}\n"
                return result.rstrip()
            else:
                return message or "没有可下载的文件"

        elif args[0] == '-n' and len(args) > 1:
            # 下载指定文件
            results = []
            for file_id_str in args[1:]:
                try:
                    file_id = int(file_id_str)
                    success, message = self.client.download_file(file_id)
                    if success:
                        results.append(f"✓ {message}")
                    else:
                        results.append(f"✗ 文件ID {file_id}: {message}")
                except ValueError:
                    results.append(f"✗ 无效的文件ID: {file_id_str}")

            return "\n".join(results)

        else:
            return "用法: /recv_files -l 或 /recv_files -n <文件ID1> [文件ID2] ..."
    
    def handle_exit(self, args: list) -> str:
        """处理退出命令"""
        return "退出功能"
