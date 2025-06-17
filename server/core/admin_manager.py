"""
管理员功能管理器
处理管理员命令和操作
"""

from typing import Dict, Any, List, Optional, Tuple
from server.database.connection import get_db
from server.utils.admin_auth import (
    validate_admin_command, parse_admin_command, log_admin_operation,
    AdminPermissionChecker
)
from shared.logger import get_logger
from shared.exceptions import UserNotFoundError, ChatGroupNotFoundError, DatabaseError


class AdminManager:
    """管理员功能管理器"""
    
    def __init__(self):
        """初始化管理员管理器"""
        self.db = get_db()
        self.permission_checker = AdminPermissionChecker(self.db)
        self.logger = get_logger(__name__)
    
    def handle_admin_command(self, command_str: str, operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        处理管理员命令（新架构）

        Args:
            command_str: 命令字符串，如 "/del -u 123" 或 "/add -u"
            operator_id: 操作者ID
            operator_name: 操作者用户名

        Returns:
            (是否成功, 消息, 数据)
        """
        try:
            # 解析命令
            operation, object_type, args = parse_admin_command(command_str)

            # 验证命令格式
            valid, error_msg = validate_admin_command(operation, object_type)
            if not valid:
                return False, error_msg, None

            # 检查权限
            can_perform, perm_error = self.permission_checker.can_perform_admin_operation(operator_id, f"{operation}_{object_type}")
            if not can_perform:
                return False, perm_error, None

            # 执行命令
            if operation == "add":
                return self._handle_add_command(object_type, args, operator_id, operator_name)
            elif operation == "del":
                return self._handle_del_command(object_type, args, operator_id, operator_name)
            elif operation == "modify":
                return self._handle_modify_command(object_type, args, operator_id, operator_name)
            elif operation == "ban":
                return self._handle_ban_command(object_type, args, operator_id, operator_name)
            elif operation == "free":
                return self._handle_free_command(object_type, args, operator_id, operator_name)
            else:
                return False, f"未知操作类型: {operation}", None

        except Exception as e:
            self.logger.error(f"处理管理员命令失败: {e}", exc_info=True)
            return False, f"命令执行失败: {str(e)}", None
    
    def _handle_add_command(self, object_type: str, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理新增命令"""
        if object_type == "-u":  # 新增用户
            return self._add_user_interactive(args, operator_id, operator_name)
        else:
            return False, f"新增操作不支持对象类型: {object_type}", None

    def _handle_del_command(self, object_type: str, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理删除命令"""
        if object_type == "-u":  # 删除用户
            return self._delete_user(args, operator_id, operator_name)
        elif object_type == "-g":  # 删除群组
            return self._delete_group(args, operator_id, operator_name)
        elif object_type == "-f":  # 删除文件
            return self._delete_file(args, operator_id, operator_name)
        else:
            return False, f"删除操作不支持对象类型: {object_type}", None

    def _handle_modify_command(self, object_type: str, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理修改命令"""
        if object_type == "-u":  # 修改用户信息
            return self._modify_user(args, operator_id, operator_name)
        elif object_type == "-g":  # 修改群组信息
            return self._modify_group(args, operator_id, operator_name)
        else:
            return False, f"修改操作不支持对象类型: {object_type}", None

    def _handle_ban_command(self, object_type: str, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理禁言命令"""
        if object_type == "-u":  # 禁言用户
            return self._ban_user(args, operator_id, operator_name)
        elif object_type == "-g":  # 禁言群组
            return self._ban_group(args, operator_id, operator_name)
        else:
            return False, f"禁言操作不支持对象类型: {object_type}", None

    def _handle_free_command(self, object_type: str, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理解禁命令"""
        if object_type == "-u":  # 解除用户禁言
            return self._unban_user(args, operator_id, operator_name)
        elif object_type == "-g":  # 解除群组禁言
            return self._unban_group(args, operator_id, operator_name)
        elif object_type == "-l":  # 列出被禁言对象
            return self._list_banned_objects(operator_id, operator_name)
        else:
            return False, f"解禁操作不支持对象类型: {object_type}", None

    def _add_user_interactive(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """新增用户（需要用户名和密码参数）"""
        if len(args) < 2:
            return False, "用法: /add -u <用户名> <密码>", None

        username = args[0]
        password = args[1]

        try:
            # 创建用户
            user_id = self.db.create_user_interactive(username, password)

            # 记录日志
            log_admin_operation("add_user", operator_id, operator_name, "user", user_id, username, True)

            return True, f"用户 {username} (ID: {user_id}) 已创建成功", None

        except Exception as e:
            from shared.exceptions import UserAlreadyExistsError
            if isinstance(e, UserAlreadyExistsError) or "已存在" in str(e):
                return False, f"用户名 {username} 已存在", None
            log_admin_operation("add_user", operator_id, operator_name, "user", 0, username, False, str(e))
            return False, f"创建用户失败: {str(e)}", None

    def _delete_file(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """删除文件"""
        if not args:
            return False, "用法: /del -f <文件ID>", None

        try:
            file_id = int(args[0])

            # 获取文件信息用于日志
            file_info = self.db.get_file_by_id(file_id)
            filename = file_info['original_filename']
            uploader_name = file_info.get('uploader_username', '未知用户')
            group_name = file_info.get('group_name', '未知群组')

            # 执行删除
            self.db.delete_file(file_id)

            # 记录日志
            log_admin_operation("delete_file", operator_id, operator_name, "file", file_id, filename, True)

            return True, f"文件 {filename} (ID: {file_id}) 已被删除\n上传者: {uploader_name}\n所属群组: {group_name}", None

        except ValueError:
            return False, "文件ID必须是数字", None
        except Exception as e:
            if "不存在" in str(e):
                return False, f"文件ID {args[0]} 不存在", None
            log_admin_operation("delete_file", operator_id, operator_name, "file", int(args[0]) if args[0].isdigit() else 0, args[0], False, str(e))
            return False, f"删除文件失败: {str(e)}", None
    
    def _delete_user(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """删除用户"""
        if not args:
            return False, "用法: /del -u <用户ID>", None
        
        try:
            user_id = int(args[0])
            
            # 获取用户信息用于日志
            user_info = self.db.get_user_by_id(user_id)
            username = user_info['username']
            
            # 不能删除管理员自己
            if user_id == operator_id:
                return False, "不能删除自己", None
            
            # 执行删除
            self.db.delete_user(user_id)
            
            # 记录日志
            log_admin_operation("delete_user", operator_id, operator_name, "user", user_id, username, True)
            
            return True, f"用户 {username} (ID: {user_id}) 已被删除", None
            
        except ValueError:
            return False, "用户ID必须是数字", None
        except UserNotFoundError:
            return False, f"用户ID {args[0]} 不存在", None
        except Exception as e:
            log_admin_operation("delete_user", operator_id, operator_name, "user", int(args[0]) if args[0].isdigit() else 0, args[0], False, str(e))
            return False, f"删除用户失败: {str(e)}", None
    
    def _modify_user(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """修改用户信息"""
        if len(args) < 3:
            return False, "用法: /modify -u <用户ID> <字段> <新值>", None
        
        try:
            user_id = int(args[0])
            field = args[1]
            new_value = args[2]
            
            # 获取用户信息
            user_info = self.db.get_user_by_id(user_id)
            username = user_info['username']
            
            # 支持的字段
            if field == "username":
                self.db.update_user_info(user_id, username=new_value)
                message = f"用户 {username} 的用户名已修改为 {new_value}"
            elif field == "password":
                self.db.update_user_info(user_id, password=new_value)
                message = f"用户 {username} 的密码已重置"
            else:
                return False, f"不支持修改字段: {field}", None
            
            # 记录日志
            log_admin_operation("modify_user", operator_id, operator_name, "user", user_id, username, True)
            
            return True, message, None
            
        except ValueError:
            return False, "用户ID必须是数字", None
        except UserNotFoundError:
            return False, f"用户ID {args[0]} 不存在", None
        except Exception as e:
            log_admin_operation("modify_user", operator_id, operator_name, "user", int(args[0]) if args[0].isdigit() else 0, args[0], False, str(e))
            return False, f"修改用户信息失败: {str(e)}", None
    
    def _delete_group(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """删除群组"""
        if not args:
            return False, "用法: /del -g <群组ID>", None
        
        try:
            group_id = int(args[0])
            
            # 获取群组信息用于日志
            group_info = self.db.get_chat_group_by_id(group_id)
            group_name = group_info['name']
            
            # 不能删除public群组
            if group_name == "public":
                return False, "不能删除public群组", None
            
            # 执行删除
            self.db.delete_chat_group(group_id)
            
            # 记录日志
            log_admin_operation("delete_group", operator_id, operator_name, "group", group_id, group_name, True)
            
            return True, f"群组 {group_name} (ID: {group_id}) 已被删除", None
            
        except ValueError:
            return False, "群组ID必须是数字", None
        except ChatGroupNotFoundError:
            return False, f"群组ID {args[0]} 不存在", None
        except Exception as e:
            log_admin_operation("delete_group", operator_id, operator_name, "group", int(args[0]) if args[0].isdigit() else 0, args[0], False, str(e))
            return False, f"删除群组失败: {str(e)}", None
    
    def _modify_group(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """修改群组信息"""
        if len(args) < 3:
            return False, "用法: /modify -g <群组ID> <字段> <新值>", None
        
        try:
            group_id = int(args[0])
            field = args[1]
            new_value = args[2]
            
            # 获取群组信息
            group_info = self.db.get_chat_group_by_id(group_id)
            group_name = group_info['name']
            
            # 支持的字段
            if field == "name":
                self.db.update_chat_group_info(group_id, name=new_value)
                message = f"群组 {group_name} 的名称已修改为 {new_value}"
            else:
                return False, f"不支持修改字段: {field}", None
            
            # 记录日志
            log_admin_operation("modify_group", operator_id, operator_name, "group", group_id, group_name, True)
            
            return True, message, None
            
        except ValueError:
            return False, "群组ID必须是数字", None
        except ChatGroupNotFoundError:
            return False, f"群组ID {args[0]} 不存在", None
        except Exception as e:
            log_admin_operation("modify_group", operator_id, operator_name, "group", int(args[0]) if args[0].isdigit() else 0, args[0], False, str(e))
            return False, f"修改群组信息失败: {str(e)}", None

    def _ban_user(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """禁言用户"""
        if not args:
            return False, "用法: /ban -u <用户ID或用户名>", None

        try:
            target = args[0]

            # 尝试按ID查找，如果失败则按用户名查找
            try:
                user_id = int(target)
                user_info = self.db.get_user_by_id(user_id)
            except ValueError:
                user_info = self.db.get_user_by_username(target)
                user_id = user_info['id']

            username = user_info['username']

            # 不能禁言管理员
            if user_id == operator_id:
                return False, "不能禁言自己", None

            # 检查是否已被禁言
            if self.db.is_user_banned(user_id):
                return False, f"用户 {username} 已被禁言", None

            # 执行禁言
            self.db.ban_user(user_id)

            # 记录日志
            log_admin_operation("ban_user", operator_id, operator_name, "user", user_id, username, True)

            return True, f"用户 {username} (ID: {user_id}) 已被禁言", None

        except (UserNotFoundError, ValueError):
            return False, f"用户 {target} 不存在", None
        except Exception as e:
            log_admin_operation("ban_user", operator_id, operator_name, "user", 0, target, False, str(e))
            return False, f"禁言用户失败: {str(e)}", None

    def _ban_group(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """禁言群组"""
        if not args:
            return False, "用法: /ban -g <群组ID或群组名>", None

        try:
            target = args[0]

            # 尝试按ID查找，如果失败则按名称查找
            try:
                group_id = int(target)
                group_info = self.db.get_chat_group_by_id(group_id)
            except ValueError:
                group_info = self.db.get_chat_group_by_name(target)
                group_id = group_info['id']

            group_name = group_info['name']

            # 不能禁言public群组
            if group_name == "public":
                return False, "不能禁言public群组", None

            # 检查是否已被禁言
            if self.db.is_chat_group_banned(group_id):
                return False, f"群组 {group_name} 已被禁言", None

            # 执行禁言
            self.db.ban_chat_group(group_id)

            # 记录日志
            log_admin_operation("ban_group", operator_id, operator_name, "group", group_id, group_name, True)

            return True, f"群组 {group_name} (ID: {group_id}) 已被禁言", None

        except (ChatGroupNotFoundError, ValueError):
            return False, f"群组 {target} 不存在", None
        except Exception as e:
            log_admin_operation("ban_group", operator_id, operator_name, "group", 0, target, False, str(e))
            return False, f"禁言群组失败: {str(e)}", None

    def _unban_user(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """解除用户禁言"""
        if not args:
            return False, "用法: /free -u <用户ID或用户名>", None

        try:
            target = args[0]

            # 尝试按ID查找，如果失败则按用户名查找
            try:
                user_id = int(target)
                user_info = self.db.get_user_by_id(user_id)
            except ValueError:
                user_info = self.db.get_user_by_username(target)
                user_id = user_info['id']

            username = user_info['username']

            # 检查是否被禁言
            if not self.db.is_user_banned(user_id):
                return False, f"用户 {username} 未被禁言", None

            # 执行解禁
            self.db.unban_user(user_id)

            # 记录日志
            log_admin_operation("unban_user", operator_id, operator_name, "user", user_id, username, True)

            return True, f"用户 {username} (ID: {user_id}) 已解除禁言", None

        except (UserNotFoundError, ValueError):
            return False, f"用户 {target} 不存在", None
        except Exception as e:
            log_admin_operation("unban_user", operator_id, operator_name, "user", 0, target, False, str(e))
            return False, f"解除用户禁言失败: {str(e)}", None

    def _unban_group(self, args: List[str], operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """解除群组禁言"""
        if not args:
            return False, "用法: /free -g <群组ID或群组名>", None

        try:
            target = args[0]

            # 尝试按ID查找，如果失败则按名称查找
            try:
                group_id = int(target)
                group_info = self.db.get_chat_group_by_id(group_id)
            except ValueError:
                group_info = self.db.get_chat_group_by_name(target)
                group_id = group_info['id']

            group_name = group_info['name']

            # 检查是否被禁言
            if not self.db.is_chat_group_banned(group_id):
                return False, f"群组 {group_name} 未被禁言", None

            # 执行解禁
            self.db.unban_chat_group(group_id)

            # 记录日志
            log_admin_operation("unban_group", operator_id, operator_name, "group", group_id, group_name, True)

            return True, f"群组 {group_name} (ID: {group_id}) 已解除禁言", None

        except (ChatGroupNotFoundError, ValueError):
            return False, f"群组 {target} 不存在", None
        except Exception as e:
            log_admin_operation("unban_group", operator_id, operator_name, "group", 0, target, False, str(e))
            return False, f"解除群组禁言失败: {str(e)}", None

    def _list_banned_objects(self, operator_id: int, operator_name: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """列出被禁言对象"""
        try:
            banned_users = self.db.get_banned_users()
            banned_groups = self.db.get_banned_chat_groups()

            data = {
                "banned_users": banned_users,
                "banned_groups": banned_groups
            }

            # 构建消息
            message_parts = []

            if banned_users:
                user_list = [f"{user['username']} (ID: {user['id']})" for user in banned_users]
                message_parts.append(f"被禁言用户 ({len(banned_users)}个):\n" + "\n".join(user_list))
            else:
                message_parts.append("被禁言用户: 无")

            if banned_groups:
                group_list = [f"{group['name']} (ID: {group['id']})" for group in banned_groups]
                message_parts.append(f"被禁言群组 ({len(banned_groups)}个):\n" + "\n".join(group_list))
            else:
                message_parts.append("被禁言群组: 无")

            message = "\n\n".join(message_parts)

            # 记录日志
            log_admin_operation("list_banned", operator_id, operator_name, "system", 0, "banned_objects", True)

            return True, message, data

        except Exception as e:
            log_admin_operation("list_banned", operator_id, operator_name, "system", 0, "banned_objects", False, str(e))
            return False, f"获取禁言列表失败: {str(e)}", None
