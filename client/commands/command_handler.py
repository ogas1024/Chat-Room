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
            # 新的管理员命令架构
            'add': self.handle_admin_add,
            'del': self.handle_admin_del,
            'modify': self.handle_admin_modify,
            'ban': self.handle_admin_ban,
            'free': self.handle_admin_free,
            # 保持向后兼容的旧命令
            'user': self.handle_admin_user_legacy,
            'group': self.handle_admin_group_legacy,
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

    def handle_admin_user(self, args: list) -> str:
        """处理用户管理命令"""
        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要Admin权限"

        if len(args) < 2:
            return "用法: /user -d <用户ID> 或 /user -m <用户ID> <字段> <新值>"

        action = args[0]
        if action == "-d":
            # 删除用户
            if len(args) < 2:
                return "用法: /user -d <用户ID>"

            try:
                user_id = int(args[1])
                return self._confirm_and_execute_admin_command("user", action, user_id, "", "")
            except ValueError:
                return "用户ID必须是数字"

        elif action == "-m":
            # 修改用户信息
            if len(args) < 4:
                return "用法: /user -m <用户ID> <字段> <新值>"

            try:
                user_id = int(args[1])
                field = args[2]
                new_value = args[3]
                return self._confirm_and_execute_admin_command("user", action, user_id, "", new_value)
            except ValueError:
                return "用户ID必须是数字"

        else:
            return "不支持的操作。用法: /user -d <用户ID> 或 /user -m <用户ID> <字段> <新值>"

    def handle_admin_group(self, args: list) -> str:
        """处理群组管理命令"""
        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要Admin权限"

        if len(args) < 2:
            return "用法: /group -d <群组ID> 或 /group -m <群组ID> <字段> <新值>"

        action = args[0]
        if action == "-d":
            # 删除群组
            if len(args) < 2:
                return "用法: /group -d <群组ID>"

            try:
                group_id = int(args[1])
                return self._confirm_and_execute_admin_command("group", action, group_id, "", "")
            except ValueError:
                return "群组ID必须是数字"

        elif action == "-m":
            # 修改群组信息
            if len(args) < 4:
                return "用法: /group -m <群组ID> <字段> <新值>"

            try:
                group_id = int(args[1])
                field = args[2]
                new_value = args[3]
                return self._confirm_and_execute_admin_command("group", action, group_id, "", new_value)
            except ValueError:
                return "群组ID必须是数字"

        else:
            return "不支持的操作。用法: /group -d <群组ID> 或 /group -m <群组ID> <字段> <新值>"

    def handle_admin_ban(self, args: list) -> str:
        """处理禁言命令（新架构）"""
        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要Admin权限"

        if len(args) < 2:
            return "用法: /ban -u <用户ID/用户名> 或 /ban -g <群组ID/群组名>"

        object_type = args[0]
        target = args[1]

        if object_type == "-u":
            # 禁言用户
            return self._confirm_and_execute_admin_command("ban", object_type, None, target, "")
        elif object_type == "-g":
            # 禁言群组
            return self._confirm_and_execute_admin_command("ban", object_type, None, target, "")
        else:
            return "禁言操作支持: -u(用户) -g(群组)"

    def handle_admin_free(self, args: list) -> str:
        """处理解禁命令（新架构）"""
        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要Admin权限"

        if len(args) < 1:
            return "用法: /free -u <用户ID/用户名> 或 /free -g <群组ID/群组名> 或 /free -l"

        object_type = args[0]

        if object_type == "-l":
            # 列出被禁言对象
            return self._execute_admin_command("free", object_type, None, "", "")
        elif object_type == "-u" and len(args) > 1:
            # 解除用户禁言
            target = args[1]
            return self._execute_admin_command("free", object_type, None, target, "")
        elif object_type == "-g" and len(args) > 1:
            # 解除群组禁言
            target = args[1]
            return self._execute_admin_command("free", object_type, None, target, "")
        else:
            return "用法: /free -u <用户ID/用户名> 或 /free -g <群组ID/群组名> 或 /free -l"

    # ==================== 向后兼容的旧命令 ====================

    def handle_admin_user_legacy(self, args: list) -> str:
        """处理用户管理命令（旧版本兼容）"""
        print("⚠️  警告: /user 命令已废弃，请使用新的命令格式:")
        print("   删除用户: /del -u <用户ID>")
        print("   修改用户: /modify -u <用户ID> <字段> <新值>")
        print("   新增用户: /add -u <用户名> <密码>")

        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要Admin权限"

        if len(args) < 2:
            return "用法: /user -d <用户ID> 或 /user -m <用户ID> <字段> <新值>"

        action = args[0]
        if action == "-d":
            # 转换为新命令格式
            if len(args) < 2:
                return "用法: /user -d <用户ID>"

            try:
                user_id = int(args[1])
                return self._confirm_and_execute_admin_command("del", "-u", user_id, "", "")
            except ValueError:
                return "用户ID必须是数字"

        elif action == "-m":
            # 转换为新命令格式
            if len(args) < 4:
                return "用法: /user -m <用户ID> <字段> <新值>"

            try:
                user_id = int(args[1])
                field = args[2]
                new_value = args[3]
                return self._execute_admin_command("modify", "-u", user_id, "", f"{field} {new_value}")
            except ValueError:
                return "用户ID必须是数字"

        else:
            return "不支持的操作。用法: /user -d <用户ID> 或 /user -m <用户ID> <字段> <新值>"

    def handle_admin_group_legacy(self, args: list) -> str:
        """处理群组管理命令（旧版本兼容）"""
        print("⚠️  警告: /group 命令已废弃，请使用新的命令格式:")
        print("   删除群组: /del -g <群组ID>")
        print("   修改群组: /modify -g <群组ID> <字段> <新值>")

        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要Admin权限"

        if len(args) < 2:
            return "用法: /group -d <群组ID> 或 /group -m <群组ID> <字段> <新值>"

        action = args[0]
        if action == "-d":
            # 转换为新命令格式
            if len(args) < 2:
                return "用法: /group -d <群组ID>"

            try:
                group_id = int(args[1])
                return self._confirm_and_execute_admin_command("del", "-g", group_id, "", "")
            except ValueError:
                return "群组ID必须是数字"

        elif action == "-m":
            # 转换为新命令格式
            if len(args) < 4:
                return "用法: /group -m <群组ID> <字段> <新值>"

            try:
                group_id = int(args[1])
                field = args[2]
                new_value = args[3]
                return self._execute_admin_command("modify", "-g", group_id, "", f"{field} {new_value}")
            except ValueError:
                return "群组ID必须是数字"

        else:
            return "不支持的操作。用法: /group -d <群组ID> 或 /group -m <群组ID> <字段> <新值>"

    def _is_admin(self) -> bool:
        """检查当前用户是否为Admin"""
        from shared.constants import ADMIN_USER_ID
        return hasattr(self.client, 'user_id') and self.client.user_id == ADMIN_USER_ID

    def _confirm_and_execute_admin_command(self, operation: str, object_type: str,
                                         target_id: int = None, target_name: str = "",
                                         new_value: str = "") -> str:
        """确认并执行管理员命令（新架构）"""
        # 构建确认消息
        if operation == "del" and object_type == "-u":
            confirm_msg = f"确认删除用户 {target_id}？这将删除用户的所有数据！(y/N): "
        elif operation == "del" and object_type == "-g":
            confirm_msg = f"确认删除群组 {target_id}？这将删除群组的所有数据！(y/N): "
        elif operation == "del" and object_type == "-f":
            confirm_msg = f"确认删除文件 {target_id}？此操作不可恢复！(y/N): "
        elif operation == "ban" and object_type == "-u":
            confirm_msg = f"确认禁言用户 {target_name}？(y/N): "
        elif operation == "ban" and object_type == "-g":
            confirm_msg = f"确认禁言群组 {target_name}？(y/N): "
        else:
            # 对于修改操作和解禁操作，直接执行
            return self._execute_admin_command(operation, object_type, target_id, target_name, new_value)

        # 获取用户确认
        try:
            response = input(confirm_msg).strip().lower()
            if response in ['y', 'yes']:
                return self._execute_admin_command(operation, object_type, target_id, target_name, new_value)
            else:
                return "操作已取消"
        except (EOFError, KeyboardInterrupt):
            return "操作已取消"

    def _execute_admin_command(self, operation: str, object_type: str,
                             target_id: int = None, target_name: str = "",
                             new_value: str = "") -> str:
        """执行管理员命令（新架构）"""
        try:
            # 发送管理员命令请求
            success, message = self.client.send_admin_command(
                operation, object_type, target_id, target_name, new_value
            )

            if success:
                return f"✓ {message}"
            else:
                return f"✗ {message}"

        except Exception as e:
            return f"✗ 命令执行失败: {e}"

    # ==================== 新的管理员命令架构 ====================

    def handle_admin_add(self, args: list) -> str:
        """处理新增命令"""
        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要管理员权限"

        if len(args) < 1:
            return "用法: /add -u <用户名> <密码>"

        object_type = args[0]
        if object_type == "-u":
            # 新增用户
            if len(args) < 3:
                # 交互式输入
                try:
                    username = input("请输入用户名: ").strip()
                    if not username:
                        return "用户名不能为空"

                    password = input("请输入密码: ").strip()
                    if not password:
                        return "密码不能为空"

                    confirm_password = input("请确认密码: ").strip()
                    if password != confirm_password:
                        return "两次输入的密码不一致"

                    return self._execute_admin_command("add", "-u", None, "", f"{username} {password}")

                except (EOFError, KeyboardInterrupt):
                    return "操作已取消"
            else:
                # 直接使用参数
                username = args[1]
                password = args[2]
                return self._execute_admin_command("add", "-u", None, "", f"{username} {password}")
        else:
            return "新增操作只支持用户(-u)"

    def handle_admin_del(self, args: list) -> str:
        """处理删除命令"""
        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要管理员权限"

        if len(args) < 2:
            return "用法: /del -u <用户ID> 或 /del -g <群组ID> 或 /del -f <文件ID>"

        object_type = args[0]
        target = args[1]

        if object_type == "-u":
            # 删除用户
            try:
                user_id = int(target)
                return self._confirm_and_execute_admin_command("del", object_type, user_id, "", "")
            except ValueError:
                return "用户ID必须是数字"
        elif object_type == "-g":
            # 删除群组
            try:
                group_id = int(target)
                return self._confirm_and_execute_admin_command("del", object_type, group_id, "", "")
            except ValueError:
                return "群组ID必须是数字"
        elif object_type == "-f":
            # 删除文件
            try:
                file_id = int(target)
                return self._confirm_and_execute_admin_command("del", object_type, file_id, "", "")
            except ValueError:
                return "文件ID必须是数字"
        else:
            return "删除操作支持: -u(用户) -g(群组) -f(文件)"

    def handle_admin_modify(self, args: list) -> str:
        """处理修改命令"""
        if not self.client.is_logged_in():
            return "请先登录"

        if not self._is_admin():
            return "权限不足：需要管理员权限"

        if len(args) < 4:
            return "用法: /modify -u <用户ID> <字段> <新值> 或 /modify -g <群组ID> <字段> <新值>"

        object_type = args[0]
        target_id = args[1]
        field = args[2]
        new_value = args[3]

        if object_type == "-u":
            # 修改用户信息
            try:
                user_id = int(target_id)
                return self._execute_admin_command("modify", object_type, user_id, "", f"{field} {new_value}")
            except ValueError:
                return "用户ID必须是数字"
        elif object_type == "-g":
            # 修改群组信息
            try:
                group_id = int(target_id)
                return self._execute_admin_command("modify", object_type, group_id, "", f"{field} {new_value}")
            except ValueError:
                return "群组ID必须是数字"
        else:
            return "修改操作支持: -u(用户) -g(群组)"
