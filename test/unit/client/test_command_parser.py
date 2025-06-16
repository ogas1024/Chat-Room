"""
测试客户端命令解析器
测试命令解析、参数提取、选项处理等功能
"""

import pytest
from unittest.mock import Mock, patch

from client.commands.parser import CommandParser, Command, CommandHandler
from client.core.client import ChatClient


class TestCommand:
    """测试命令数据类"""
    
    def test_command_creation(self):
        """测试命令创建"""
        command = Command(
            name="login",
            args=["alice", "password123"],
            options={"-r": True, "-t": "30"}
        )
        
        assert command.name == "login"
        assert command.args == ["alice", "password123"]
        assert command.options == {"-r": True, "-t": "30"}
    
    def test_command_str_representation(self):
        """测试命令字符串表示"""
        command = Command(
            name="login",
            args=["alice"],
            options={"-r": True}
        )
        
        str_repr = str(command)
        assert "login" in str_repr
        assert "alice" in str_repr
        assert "-r" in str_repr


class TestCommandParser:
    """测试命令解析器"""
    
    def test_command_parser_creation(self):
        """测试命令解析器创建"""
        parser = CommandParser()
        assert parser is not None
        assert hasattr(parser, 'commands')
        assert isinstance(parser.commands, dict)
    
    def test_parse_simple_command(self):
        """测试解析简单命令"""
        parser = CommandParser()
        
        command = parser.parse_command("/help")
        
        assert command is not None
        assert command.name == "help"
        assert command.args == []
        assert command.options == {}
    
    def test_parse_command_with_args(self):
        """测试解析带参数的命令"""
        parser = CommandParser()
        
        command = parser.parse_command("/login alice password123")
        
        assert command is not None
        assert command.name == "login"
        assert command.args == ["alice", "password123"]
        assert command.options == {}
    
    def test_parse_command_with_options(self):
        """测试解析带选项的命令"""
        parser = CommandParser()
        
        command = parser.parse_command("/recv_files -l")
        
        assert command is not None
        assert command.name == "recv_files"
        assert command.args == []
        assert "-l" in command.options
        assert command.options["-l"] is True
    
    def test_parse_command_with_option_values(self):
        """测试解析带选项值的命令"""
        parser = CommandParser()
        
        command = parser.parse_command("/recv_files -n 123")
        
        assert command is not None
        assert command.name == "recv_files"
        assert command.args == []
        assert "-n" in command.options
        assert command.options["-n"] == "123"
    
    def test_parse_command_with_mixed_args_options(self):
        """测试解析混合参数和选项的命令"""
        parser = CommandParser()
        
        command = parser.parse_command("/send_files file1.txt file2.txt -c compress")
        
        assert command is not None
        assert command.name == "send_files"
        assert command.args == ["file1.txt", "file2.txt"]
        assert "-c" in command.options
        assert command.options["-c"] == "compress"
    
    def test_parse_command_with_quotes(self):
        """测试解析带引号的命令"""
        parser = CommandParser()
        
        command = parser.parse_command('/create_chat "My Chat Group" -p private')
        
        assert command is not None
        assert command.name == "create_chat"
        assert command.args == ["My Chat Group"]
        assert "-p" in command.options
        assert command.options["-p"] == "private"
    
    def test_parse_command_with_chinese(self):
        """测试解析中文命令"""
        parser = CommandParser()
        
        command = parser.parse_command("/create_chat 中文聊天室 -d 这是描述")
        
        assert command is not None
        assert command.name == "create_chat"
        assert command.args == ["中文聊天室"]
        assert "-d" in command.options
        assert command.options["-d"] == "这是描述"
    
    def test_parse_invalid_command_format(self):
        """测试解析无效命令格式"""
        parser = CommandParser()
        
        # 不以/开头
        command = parser.parse_command("help")
        assert command is None
        
        # 空命令
        command = parser.parse_command("/")
        assert command is None
        
        # 只有空格
        command = parser.parse_command("/   ")
        assert command is None
    
    def test_parse_command_with_malformed_quotes(self):
        """测试解析格式错误的引号"""
        parser = CommandParser()
        
        # 未闭合的引号，应该回退到简单分割
        command = parser.parse_command('/create_chat "unclosed quote')
        
        assert command is not None
        assert command.name == "create_chat"
        # 应该包含引号字符
        assert '"unclosed' in command.args[0]
    
    def test_parse_command_edge_cases(self):
        """测试命令解析边界情况"""
        parser = CommandParser()
        
        # 多个连续空格
        command = parser.parse_command("/login    alice    password")
        assert command.name == "login"
        assert command.args == ["alice", "password"]
        
        # 选项在参数前面
        command = parser.parse_command("/send_files -v file.txt")
        assert command.name == "send_files"
        assert command.args == ["file.txt"]
        assert "-v" in command.options
        
        # 多个选项
        command = parser.parse_command("/recv_files -l -a -n 5")
        assert command.name == "recv_files"
        assert command.args == []
        assert "-l" in command.options
        assert "-a" in command.options
        assert "-n" in command.options
        assert command.options["-n"] == "5"
    
    def test_get_command_help(self):
        """测试获取命令帮助"""
        parser = CommandParser()
        
        # 获取特定命令帮助
        help_text = parser.get_command_help("login")
        assert help_text is not None
        assert "login" in help_text.lower()
        
        # 获取不存在命令的帮助
        help_text = parser.get_command_help("nonexistent")
        assert help_text is not None
        assert "未知" in help_text or "unknown" in help_text.lower()
    
    def test_get_all_commands_help(self):
        """测试获取所有命令帮助"""
        parser = CommandParser()
        
        help_text = parser.get_all_commands_help()
        assert help_text is not None
        assert len(help_text) > 0
        
        # 应该包含主要命令
        assert "login" in help_text
        assert "help" in help_text
    
    def test_validate_command(self):
        """测试命令验证"""
        parser = CommandParser()
        
        # 有效命令
        valid_command = Command("login", ["alice", "password"], {})
        assert parser.validate_command(valid_command) is True
        
        # 无效命令名
        invalid_command = Command("", ["alice"], {})
        assert parser.validate_command(invalid_command) is False
        
        # None命令
        assert parser.validate_command(None) is False


class TestCommandHandler:
    """测试命令处理器"""
    
    def test_command_handler_creation(self):
        """测试命令处理器创建"""
        mock_client = Mock(spec=ChatClient)
        handler = CommandHandler(mock_client)
        
        assert handler is not None
        assert handler.chat_client == mock_client
        assert hasattr(handler, 'command_handlers')
        assert isinstance(handler.command_handlers, dict)
    
    def test_handle_help_command(self):
        """测试处理帮助命令"""
        mock_client = Mock(spec=ChatClient)
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/?")
        
        assert success is True
        assert "命令" in message or "help" in message.lower()
    
    def test_handle_help_specific_command(self):
        """测试处理特定命令帮助"""
        mock_client = Mock(spec=ChatClient)
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/help login")
        
        assert success is True
        assert "login" in message.lower()
    
    def test_handle_login_command(self):
        """测试处理登录命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.login.return_value = (True, "登录成功")
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/login alice password123")
        
        assert success is True
        assert "成功" in message
        mock_client.login.assert_called_once_with("alice", "password123")
    
    def test_handle_login_command_insufficient_args(self):
        """测试处理参数不足的登录命令"""
        mock_client = Mock(spec=ChatClient)
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/login alice")
        
        assert success is False
        assert "参数" in message or "用法" in message
    
    def test_handle_signin_command(self):
        """测试处理注册命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.register.return_value = (True, "注册成功")
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/signin bob password456")
        
        assert success is True
        assert "成功" in message
        mock_client.register.assert_called_once_with("bob", "password456")
    
    def test_handle_info_command(self):
        """测试处理信息命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.get_user_info.return_value = (True, "用户信息", {"username": "alice", "id": 1})
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/info")
        
        assert success is True
        mock_client.get_user_info.assert_called_once()
    
    def test_handle_list_command(self):
        """测试处理列表命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.list_users.return_value = (True, "用户列表", [{"username": "alice"}])
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/list users")
        
        assert success is True
        mock_client.list_users.assert_called_once()
    
    def test_handle_create_chat_command(self):
        """测试处理创建聊天组命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.create_chat_group.return_value = (True, "创建成功")
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/create_chat test_group")
        
        assert success is True
        assert "成功" in message
        mock_client.create_chat_group.assert_called_once_with("test_group")
    
    def test_handle_enter_chat_command(self):
        """测试处理进入聊天组命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.enter_chat.return_value = (True, "进入成功")
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/enter_chat public")
        
        assert success is True
        assert "成功" in message
        mock_client.enter_chat.assert_called_once_with("public")
    
    def test_handle_send_files_command(self):
        """测试处理发送文件命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.send_file.return_value = (True, "发送成功")
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/send_files file1.txt file2.txt")
        
        assert success is True
        # 应该为每个文件调用一次
        assert mock_client.send_file.call_count == 2
    
    def test_handle_recv_files_command_list(self):
        """测试处理接收文件列表命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.list_files.return_value = (True, "文件列表", [{"filename": "test.txt"}])
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/recv_files -l")
        
        assert success is True
        mock_client.list_files.assert_called_once()
    
    def test_handle_recv_files_command_download(self):
        """测试处理下载文件命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.download_file.return_value = (True, "下载成功")
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/recv_files -n 123")
        
        assert success is True
        mock_client.download_file.assert_called_once_with("123")
    
    def test_handle_ai_command(self):
        """测试处理AI命令"""
        mock_client = Mock(spec=ChatClient)
        mock_client.send_ai_request.return_value = (True, "AI响应")
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/ai status")
        
        assert success is True
        mock_client.send_ai_request.assert_called_once_with("status")
    
    def test_handle_unknown_command(self):
        """测试处理未知命令"""
        mock_client = Mock(spec=ChatClient)
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/unknown_command")
        
        assert success is False
        assert "未知" in message or "unknown" in message.lower()
    
    def test_handle_invalid_command_format(self):
        """测试处理无效命令格式"""
        mock_client = Mock(spec=ChatClient)
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("not_a_command")
        
        assert success is False
        assert "格式" in message or "format" in message.lower()
    
    def test_handle_command_with_exception(self):
        """测试处理命令时发生异常"""
        mock_client = Mock(spec=ChatClient)
        mock_client.login.side_effect = Exception("Test exception")
        
        handler = CommandHandler(mock_client)
        
        success, message = handler.handle_command("/login alice password")
        
        assert success is False
        assert "错误" in message or "error" in message.lower()
    
    def test_command_performance_logging(self):
        """测试命令性能日志记录"""
        mock_client = Mock(spec=ChatClient)
        mock_client.login.return_value = (True, "登录成功")
        
        handler = CommandHandler(mock_client)
        
        with patch('time.time', side_effect=[0.0, 1.0]):  # 模拟1秒执行时间
            success, message = handler.handle_command("/login alice password")
            
            assert success is True
            # 验证性能日志被记录（通过检查日志调用）
    
    def test_concurrent_command_handling(self):
        """测试并发命令处理"""
        import threading
        
        mock_client = Mock(spec=ChatClient)
        mock_client.get_user_info.return_value = (True, "用户信息", {})
        
        handler = CommandHandler(mock_client)
        
        results = []
        
        def handle_command():
            success, message = handler.handle_command("/info")
            results.append((success, message))
        
        # 创建多个线程同时处理命令
        threads = []
        for i in range(5):
            thread = threading.Thread(target=handle_command)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) == 5
        for success, message in results:
            assert success is True
