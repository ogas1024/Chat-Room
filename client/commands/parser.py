"""
命令解析器
解析用户输入的斜杠命令并执行相应操作
"""

import shlex
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from functools import wraps

from shared.constants import COMMAND_PREFIX
from shared.logger import get_logger, log_user_action


def require_login(func: Callable) -> Callable:
    """装饰器：要求用户登录"""
    @wraps(func)
    def wrapper(self, command):
        if not self.chat_client.is_logged_in():
            return False, "请先登录"
        return func(self, command)
    return wrapper


def require_chat_group(func: Callable) -> Callable:
    """装饰器：要求用户在聊天组中"""
    @wraps(func)
    def wrapper(self, command):
        if not self.chat_client.current_chat_group:
            return False, "请先进入聊天组"
        return func(self, command)
    return wrapper


def require_args(min_args: int = 1, error_msg: str = "请提供必要的参数"):
    """装饰器：要求最少参数数量"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, command):
            if len(command.args) < min_args:
                return False, error_msg
            return func(self, command)
        return wrapper
    return decorator


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f}MB"


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
        
        # AI相关命令
        self.register_command("ai", {
            "description": "AI助手相关命令",
            "usage": "/ai <status|clear|help> [消息]",
            "options": {
                "status": "查看AI状态",
                "clear": "清除对话上下文",
                "help": "显示AI帮助"
            },
            "handler": None
        })

        # 管理员命令（新架构）
        self.register_command("add", {
            "description": "新增用户",
            "usage": "/add -u <用户名> <密码>",
            "options": {
                "-u": "新增用户"
            },
            "handler": None
        })

        self.register_command("del", {
            "description": "删除对象",
            "usage": "/del -u <用户ID> | /del -g <群组ID> | /del -f <文件ID>",
            "options": {
                "-u": "删除用户",
                "-g": "删除群组",
                "-f": "删除文件"
            },
            "handler": None
        })

        self.register_command("modify", {
            "description": "修改对象信息",
            "usage": "/modify -u <用户ID> <字段> <新值> | /modify -g <群组ID> <字段> <新值>",
            "options": {
                "-u": "修改用户信息",
                "-g": "修改群组信息"
            },
            "handler": None
        })

        self.register_command("ban", {
            "description": "禁言用户或群组",
            "usage": "/ban -u <用户ID/用户名> | /ban -g <群组ID/群组名>",
            "options": {
                "-u": "禁言用户",
                "-g": "禁言群组"
            },
            "handler": None
        })

        self.register_command("free", {
            "description": "解禁用户或群组",
            "usage": "/free -u <用户ID/用户名> | /free -g <群组ID/群组名> | /free -l",
            "options": {
                "-u": "解除用户禁言",
                "-g": "解除群组禁言",
                "-l": "列出被禁言对象"
            },
            "handler": None
        })

        # 管理员命令（向后兼容）
        self.register_command("user", {
            "description": "用户管理（已废弃，建议使用新格式）",
            "usage": "/user -d <用户ID> | /user -m <用户ID> <字段> <新值>",
            "options": {
                "-d": "删除用户",
                "-m": "修改用户信息"
            },
            "handler": None
        })

        self.register_command("group", {
            "description": "群组管理（已废弃，建议使用新格式）",
            "usage": "/group -d <群组ID> | /group -m <群组ID> <字段> <新值>",
            "options": {
                "-d": "删除群组",
                "-m": "修改群组信息"
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
        self.logger = get_logger("client.commands")
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
            "ai": self.handle_ai,
            # 新的管理员命令架构
            "add": self.handle_admin_add,
            "del": self.handle_admin_del,
            "modify": self.handle_admin_modify,
            "ban": self.handle_admin_ban,
            "free": self.handle_admin_free,
            # 保持向后兼容的旧命令
            "user": self.handle_admin_user_legacy,
            "group": self.handle_admin_group_legacy,
            "exit": self.handle_exit,
        }
    
    def handle_command(self, input_text: str) -> tuple[bool, str]:
        """处理命令"""
        start_time = time.time()

        command = self.parser.parse_command(input_text)
        if not command:
            self.logger.warning("无效的命令格式", command=input_text)
            return False, "无效的命令格式"

        if command.name not in self.command_handlers:
            self.logger.warning("未知命令", command=command.name, input=input_text)
            return False, f"未知命令: {command.name}"

        try:
            # 记录命令开始执行
            self.logger.info("执行命令", command=command.name, args=command.args, options=command.options)

            # 记录recv_files命令的详细解析信息到日志
            if command.name == "recv_files":
                self.logger.debug("recv_files命令解析详情",
                                args=command.args,
                                options=command.options,
                                raw_input=command.raw_input)

            # 如果用户已登录，记录用户操作
            if self.chat_client.is_logged_in() and self.chat_client.current_user:
                user_id = self.chat_client.current_user.get('id')
                username = self.chat_client.current_user.get('username')
                if user_id and username:
                    log_user_action(user_id, username, f"command_{command.name}",
                                  command_args=command.args, command_options=command.options)

            handler = self.command_handlers[command.name]
            success, message = handler(command)

            # 记录命令执行结果
            duration = time.time() - start_time
            if success:
                self.logger.info("命令执行成功", command=command.name, duration=duration, result_length=len(message))
            else:
                self.logger.warning("命令执行失败", command=command.name, duration=duration, error=message)

            return success, message

        except Exception as e:
            duration = time.time() - start_time
            self.logger.error("命令执行异常", command=command.name, duration=duration, error=str(e), exc_info=True)
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
    
    @require_login
    def handle_info(self, command: Command) -> tuple[bool, str]:
        """处理信息查询命令"""
        # 获取用户信息
        success, message, user_info = self.chat_client.get_user_info()
        if not success:
            return False, message

        # 格式化用户信息
        info_text = f"""
用户信息:
  用户ID: {user_info['user_id']}
  用户名: {user_info['username']}
  在线状态: {'在线' if user_info['is_online'] else '离线'}

聊天组统计:
  已加入聊天组: {user_info['joined_chats_count']}
  私聊数量: {user_info['private_chats_count']}
  群聊数量: {user_info['group_chats_count']}

系统统计:
  总用户数: {user_info['total_users_count']}
  在线用户数: {user_info['online_users_count']}
  总聊天组数: {user_info['total_chats_count']}
        """.strip()

        return True, info_text
    
    @require_login
    def handle_list(self, command: Command) -> tuple[bool, str]:
        """处理列表命令"""
        # 检查参数
        if not command.options:
            return False, "请指定列表类型: -u(用户) -s(当前聊天组用户) -c(已加入聊天组) -g(所有群聊) -f(文件)"

        # 获取第一个选项（字典的第一个键）
        option = list(command.options.keys())[0]

        if option == "-u":
            # 显示所有用户
            success, message, users = self.chat_client.list_users("all")
            if not success:
                return False, message

            if not users:
                return True, "暂无用户"

            user_list = "所有用户列表:\n"
            for user in users:
                status = "在线" if user['is_online'] else "离线"
                user_list += f"  {user['username']} (ID: {user['user_id']}) - {status}\n"

            return True, user_list.strip()

        elif option == "-s":
            # 显示当前聊天组用户
            if not self.chat_client.current_chat_group:
                return False, "请先进入聊天组"

            success, message, users = self.chat_client.list_users("current_chat")
            if not success:
                return False, message

            if not users:
                return True, "当前聊天组暂无其他用户"

            chat_name = self.chat_client.current_chat_group['name']
            user_list = f"聊天组 '{chat_name}' 成员列表:\n"
            for user in users:
                status = "在线" if user['is_online'] else "离线"
                user_list += f"  {user['username']} - {status}\n"

            return True, user_list.strip()

        elif option == "-c":
            # 显示已加入的聊天组
            success, message, chats = self.chat_client.list_chats("joined")
            if not success:
                return False, message

            if not chats:
                return True, "您还没有加入任何聊天组"

            chat_list = "已加入的聊天组:\n"
            for chat in chats:
                chat_type = "私聊" if chat['is_private_chat'] else "群聊"
                chat_list += f"  {chat['group_name']} (ID: {chat['group_id']}) - {chat_type} - {chat['member_count']}人\n"

            return True, chat_list.strip()

        elif option == "-g":
            # 显示所有群聊
            success, message, chats = self.chat_client.list_chats("all")
            if not success:
                return False, message

            if not chats:
                return True, "暂无公开群聊"

            # 过滤出群聊（非私聊）
            group_chats = [chat for chat in chats if not chat['is_private_chat']]
            if not group_chats:
                return True, "暂无公开群聊"

            chat_list = "所有群聊列表:\n"
            for chat in group_chats:
                chat_list += f"  {chat['group_name']} (ID: {chat['group_id']}) - {chat['member_count']}人\n"

            return True, chat_list.strip()

        elif option == "-f":
            # 显示当前聊天组文件
            if not self.chat_client.current_chat_group:
                return False, "请先进入聊天组"

            success, message, files = self.chat_client.list_files()
            if not success:
                return False, message

            if not files:
                return True, "当前聊天组暂无文件"

            chat_name = self.chat_client.current_chat_group['name']
            file_list = f"聊天组 '{chat_name}' 文件列表:\n"
            for file_info in files:
                size_str = format_file_size(file_info['file_size'])
                file_list += f"  {file_info['original_filename']} ({size_str}) - 上传者: {file_info['uploader_username']}\n"

            return True, file_list.strip()

        else:
            return False, f"未知选项: {option}。支持的选项: -u, -s, -c, -g, -f"
    
    @require_login
    @require_args(1, "请指定聊天组名称")
    def handle_create_chat(self, command: Command) -> tuple[bool, str]:
        """处理创建聊天组命令"""

        group_name = command.args[0]
        member_usernames = command.args[1:] if len(command.args) > 1 else []

        # 创建聊天组
        success, message = self.chat_client.create_chat_group(group_name, member_usernames)
        if success:
            if member_usernames:
                return True, f"{message}，已邀请用户: {', '.join(member_usernames)}"
            else:
                return True, message
        else:
            return False, message
    
    @require_login
    @require_args(1, "请指定聊天组名称")
    def handle_enter_chat(self, command: Command) -> tuple[bool, str]:
        """处理进入聊天组命令"""
        group_name = command.args[0]

        # 如果是Simple模式，在进入聊天组前重新设置消息处理器
        if hasattr(self, 'simple_client') and self.simple_client:
            # 清空历史消息收集器，准备接收新的历史消息
            self.simple_client.history_messages = []
            self.simple_client.current_chat_group_id = None

            # 强制重新设置消息处理器
            self.simple_client._force_override_message_handlers()

        # 进入聊天组
        success, message = self.chat_client.enter_chat_group(group_name)

        # 如果成功进入聊天组，确保Simple客户端的状态同步
        if success and hasattr(self, 'simple_client') and self.simple_client:
            # 同步聊天组信息到Simple客户端
            if self.chat_client.current_chat_group:
                self.simple_client.current_chat_group_id = self.chat_client.current_chat_group['id']

        return success, message
    
    @require_login
    @require_args(1, "请指定聊天组名称")
    def handle_join_chat(self, command: Command) -> tuple[bool, str]:
        """处理加入聊天组命令"""
        group_name = command.args[0]

        # 加入聊天组
        success, message = self.chat_client.join_chat_group(group_name)
        return success, message
    
    @require_login
    @require_args(1, "请指定文件路径")
    def handle_send_files(self, command: Command) -> tuple[bool, str]:
        """处理发送文件命令"""
        # 发送多个文件
        results = []
        for file_path in command.args:
            success, message = self.chat_client.send_file(file_path)
            if success:
                results.append(f"✅ {message}")
            else:
                results.append(f"❌ {file_path}: {message}")

        return True, "\n".join(results)
    
    def handle_recv_files(self, command: Command) -> tuple[bool, str]:
        """处理接收文件命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        # 调试信息已记录到日志系统

        if not command.options:
            return False, "请指定操作: -l(列出文件) -n <文件ID>(下载文件) -a(下载所有)"

        # 获取第一个选项（字典的第一个键）
        option = list(command.options.keys())[0]

        if option == "-l":
            # 列出可下载的文件
            if not self.chat_client.current_chat_group:
                return False, "请先进入聊天组"

            success, message, files = self.chat_client.list_files()
            if not success:
                return False, message

            if not files:
                return True, "当前聊天组暂无文件"

            file_list = "可下载文件列表:\n"
            for file_info in files:
                size_str = format_file_size(file_info['file_size'])
                file_list += f"  ID: {file_info['file_id']} - {file_info['original_filename']} ({size_str})\n"
                file_list += f"    上传者: {file_info['uploader_username']} - 时间: {file_info['upload_time']}\n"

            return True, file_list.strip()

        elif option == "-n":
            # 下载指定文件
            # 文件ID应该从选项值中获取，而不是从args中
            option_value = command.options[option]

            # 检查选项值是否为True（表示没有提供文件ID）
            if option_value is True:
                return False, "请指定文件ID"

            try:
                file_id = int(option_value)
            except ValueError:
                return False, "文件ID必须是数字"

            # 保存路径可以从args中获取（如果有的话）
            save_path = command.args[0] if len(command.args) > 0 else None
            success, message = self.chat_client.download_file(file_id, save_path)
            return success, message

        elif option == "-a":
            # 下载所有文件
            if not self.chat_client.current_chat_group:
                return False, "请先进入聊天组"

            success, message, files = self.chat_client.list_files()
            if not success:
                return False, message

            if not files:
                return True, "当前聊天组暂无文件"

            results = []
            for file_info in files:
                success, msg = self.chat_client.download_file(file_info['file_id'])
                if success:
                    results.append(f"✅ {file_info['original_filename']}: {msg}")
                else:
                    results.append(f"❌ {file_info['original_filename']}: {msg}")

            return True, "\n".join(results)

        else:
            return False, f"未知选项: {option}。支持的选项: -l, -n, -a"

    def handle_ai(self, command: Command) -> tuple[bool, str]:
        """处理AI命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        if not command.args:
            return False, "请指定AI命令: status, clear, help 或直接输入消息"

        ai_command = command.args[0].lower()

        # 发送AI命令请求
        success, response = self.chat_client.send_ai_request(ai_command)
        return success, response

    def handle_exit(self, command: Command) -> tuple[bool, str]:
        """处理退出命令"""
        # 如果已登录，先发送logout请求
        if self.chat_client.is_logged_in():
            try:
                success = self.chat_client.logout()
                if not success:
                    # 即使logout失败也继续断开连接
                    pass
            except Exception:
                # 忽略logout过程中的异常，继续断开连接
                pass

        # 断开连接
        if self.chat_client.is_connected():
            self.chat_client.disconnect()

        # 这里可以添加其他清理逻辑
        return True, "已断开连接，正在退出..."

    # ==================== 管理员命令处理器 ====================

    def _is_admin(self) -> bool:
        """检查当前用户是否为管理员"""
        from shared.constants import ADMIN_USER_ID
        return (hasattr(self.chat_client, 'user_id') and
                self.chat_client.user_id == ADMIN_USER_ID)

    def handle_admin_add(self, command: Command) -> tuple[bool, str]:
        """处理新增命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        if not self._is_admin():
            return False, "权限不足：需要管理员权限"

        # 检查选项中是否有 -u
        if "-u" not in command.options:
            return False, "用法: /add -u <用户名> <密码>"

        username = command.options["-u"]
        if username is True:  # 如果选项没有值
            return False, "用法: /add -u <用户名> <密码>"

        if len(command.args) < 1:
            return False, "用法: /add -u <用户名> <密码>"

        password = command.args[0]

        # 发送管理员命令
        success, message = self.chat_client.send_admin_command(
            "add", "-u", None, "", f"{username} {password}"
        )

        return success, message

    def handle_admin_del(self, command: Command) -> tuple[bool, str]:
        """处理删除命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        if not self._is_admin():
            return False, "权限不足：需要管理员权限"

        # 检查选项中是否有 -u, -g 或 -f
        object_type = None
        target = None

        if "-u" in command.options:
            object_type = "-u"
            target = command.options["-u"]
            if target is True:  # 如果选项没有值
                return False, "用法: /del -u <用户ID>"
        elif "-g" in command.options:
            object_type = "-g"
            target = command.options["-g"]
            if target is True:  # 如果选项没有值
                return False, "用法: /del -g <群组ID>"
        elif "-f" in command.options:
            object_type = "-f"
            target = command.options["-f"]
            if target is True:  # 如果选项没有值
                return False, "用法: /del -f <文件ID>"
        else:
            return False, "用法: /del -u <用户ID> 或 /del -g <群组ID> 或 /del -f <文件ID>"

        if object_type == "-u":
            try:
                user_id = int(target)
                # 需要确认的操作
                confirm = input(f"确认删除用户 {user_id}？这将删除用户的所有数据！(y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    return True, "操作已取消"

                success, message = self.chat_client.send_admin_command(
                    "del", object_type, user_id, "", ""
                )
                return success, message
            except ValueError:
                return False, "用户ID必须是数字"
        elif object_type == "-g":
            try:
                group_id = int(target)
                confirm = input(f"确认删除群组 {group_id}？这将删除群组的所有数据！(y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    return True, "操作已取消"

                success, message = self.chat_client.send_admin_command(
                    "del", object_type, group_id, "", ""
                )
                return success, message
            except ValueError:
                return False, "群组ID必须是数字"
        elif object_type == "-f":
            try:
                file_id = int(target)
                confirm = input(f"确认删除文件 {file_id}？此操作不可恢复！(y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    return True, "操作已取消"

                success, message = self.chat_client.send_admin_command(
                    "del", object_type, file_id, "", ""
                )
                return success, message
            except ValueError:
                return False, "文件ID必须是数字"
        else:
            return False, "删除操作支持: -u(用户) -g(群组) -f(文件)"

    def handle_admin_modify(self, command: Command) -> tuple[bool, str]:
        """处理修改命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        if not self._is_admin():
            return False, "权限不足：需要管理员权限"

        # 检查选项中是否有 -u 或 -g
        if "-u" in command.options:
            target_id = command.options["-u"]
            if target_id is True:  # 如果选项没有值
                return False, "用法: /modify -u <用户ID> <字段> <新值>"

            if len(command.args) < 2:
                return False, "用法: /modify -u <用户ID> <字段> <新值>"

            field = command.args[0]
            new_value = command.args[1]

            try:
                user_id = int(target_id)
                success, message = self.chat_client.send_admin_command(
                    "modify", "-u", user_id, "", f"{field} {new_value}"
                )
                return success, message
            except ValueError:
                return False, "用户ID必须是数字"

        elif "-g" in command.options:
            target_id = command.options["-g"]
            if target_id is True:  # 如果选项没有值
                return False, "用法: /modify -g <群组ID> <字段> <新值>"

            if len(command.args) < 2:
                return False, "用法: /modify -g <群组ID> <字段> <新值>"

            field = command.args[0]
            new_value = command.args[1]

            try:
                group_id = int(target_id)
                success, message = self.chat_client.send_admin_command(
                    "modify", "-g", group_id, "", f"{field} {new_value}"
                )
                return success, message
            except ValueError:
                return False, "群组ID必须是数字"
        else:
            return False, "用法: /modify -u <用户ID> <字段> <新值> 或 /modify -g <群组ID> <字段> <新值>"

    def handle_admin_ban(self, command: Command) -> tuple[bool, str]:
        """处理禁言命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        if not self._is_admin():
            return False, "权限不足：需要管理员权限"

        # 检查选项中是否有 -u 或 -g，并获取目标
        object_type = None
        target = None

        if "-u" in command.options:
            object_type = "-u"
            target = command.options["-u"]
            if target is True:  # 如果选项没有值
                return False, "用法: /ban -u <用户ID/用户名>"
        elif "-g" in command.options:
            object_type = "-g"
            target = command.options["-g"]
            if target is True:  # 如果选项没有值
                return False, "用法: /ban -g <群组ID/群组名>"
        else:
            return False, "用法: /ban -u <用户ID/用户名> 或 /ban -g <群组ID/群组名>"

        if object_type == "-u":
            confirm = input(f"确认禁言用户 {target}？(y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                return True, "操作已取消"

            success, message = self.chat_client.send_admin_command(
                "ban", object_type, None, target, ""
            )
            return success, message
        elif object_type == "-g":
            confirm = input(f"确认禁言群组 {target}？(y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                return True, "操作已取消"

            success, message = self.chat_client.send_admin_command(
                "ban", object_type, None, target, ""
            )
            return success, message
        else:
            return False, "禁言操作支持: -u(用户) -g(群组)"

    def handle_admin_free(self, command: Command) -> tuple[bool, str]:
        """处理解禁命令"""
        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        if not self._is_admin():
            return False, "权限不足：需要管理员权限"

        # 检查选项中是否有 -u, -g 或 -l
        if "-l" in command.options:
            # 列出被禁言对象
            success, message = self.chat_client.send_admin_command(
                "free", "-l", None, "", ""
            )
            return success, message
        elif "-u" in command.options:
            target = command.options["-u"]
            if target is True:  # 如果选项没有值
                return False, "用法: /free -u <用户ID/用户名>"
            success, message = self.chat_client.send_admin_command(
                "free", "-u", None, target, ""
            )
            return success, message
        elif "-g" in command.options:
            target = command.options["-g"]
            if target is True:  # 如果选项没有值
                return False, "用法: /free -g <群组ID/群组名>"
            success, message = self.chat_client.send_admin_command(
                "free", "-g", None, target, ""
            )
            return success, message
        else:
            return False, "用法: /free -u <用户ID/用户名> 或 /free -g <群组ID/群组名> 或 /free -l"

    def handle_admin_user_legacy(self, command: Command) -> tuple[bool, str]:
        """处理用户管理命令（旧版本兼容）"""
        print("⚠️  警告: /user 命令已废弃，请使用新的命令格式:")
        print("   删除用户: /del -u <用户ID>")
        print("   修改用户: /modify -u <用户ID> <字段> <新值>")
        print("   新增用户: /add -u <用户名> <密码>")

        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        if not self._is_admin():
            return False, "权限不足：需要管理员权限"

        if len(command.args) < 2:
            return False, "用法: /user -d <用户ID> 或 /user -m <用户ID> <字段> <新值>"

        action = command.args[0]
        if action == "-d":
            if len(command.args) < 2:
                return False, "用法: /user -d <用户ID>"

            try:
                user_id = int(command.args[1])
                confirm = input(f"确认删除用户 {user_id}？这将删除用户的所有数据！(y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    return True, "操作已取消"

                success, message = self.chat_client.send_admin_command(
                    "del", "-u", user_id, "", ""
                )
                return success, message
            except ValueError:
                return False, "用户ID必须是数字"

        elif action == "-m":
            if len(command.args) < 4:
                return False, "用法: /user -m <用户ID> <字段> <新值>"

            try:
                user_id = int(command.args[1])
                field = command.args[2]
                new_value = command.args[3]
                success, message = self.chat_client.send_admin_command(
                    "modify", "-u", user_id, "", f"{field} {new_value}"
                )
                return success, message
            except ValueError:
                return False, "用户ID必须是数字"

        else:
            return False, "不支持的操作。用法: /user -d <用户ID> 或 /user -m <用户ID> <字段> <新值>"

    def handle_admin_group_legacy(self, command: Command) -> tuple[bool, str]:
        """处理群组管理命令（旧版本兼容）"""
        print("⚠️  警告: /group 命令已废弃，请使用新的命令格式:")
        print("   删除群组: /del -g <群组ID>")
        print("   修改群组: /modify -g <群组ID> <字段> <新值>")

        if not self.chat_client.is_logged_in():
            return False, "请先登录"

        if not self._is_admin():
            return False, "权限不足：需要管理员权限"

        if len(command.args) < 2:
            return False, "用法: /group -d <群组ID> 或 /group -m <群组ID> <字段> <新值>"

        action = command.args[0]
        if action == "-d":
            if len(command.args) < 2:
                return False, "用法: /group -d <群组ID>"

            try:
                group_id = int(command.args[1])
                confirm = input(f"确认删除群组 {group_id}？这将删除群组的所有数据！(y/N): ").strip().lower()
                if confirm not in ['y', 'yes']:
                    return True, "操作已取消"

                success, message = self.chat_client.send_admin_command(
                    "del", "-g", group_id, "", ""
                )
                return success, message
            except ValueError:
                return False, "群组ID必须是数字"

        elif action == "-m":
            if len(command.args) < 4:
                return False, "用法: /group -m <群组ID> <字段> <新值>"

            try:
                group_id = int(command.args[1])
                field = command.args[2]
                new_value = command.args[3]
                success, message = self.chat_client.send_admin_command(
                    "modify", "-g", group_id, "", f"{field} {new_value}"
                )
                return success, message
            except ValueError:
                return False, "群组ID必须是数字"

        else:
            return False, "不支持的操作。用法: /group -d <群组ID> 或 /group -m <群组ID> <字段> <新值>"
