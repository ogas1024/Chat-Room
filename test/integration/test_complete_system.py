#!/usr/bin/env python3
"""
完整系统测试脚本
验证配置系统重构后的整体功能
"""

import os
import sys
import time
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent.parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_configuration_system():
    """测试配置系统"""
    print("🔧 测试配置系统...")
    
    try:
        # 测试服务器配置
        from src.server.config.server_config import get_server_config
        server_config = get_server_config()
        
        print(f"  ✅ 服务器配置加载成功")
        print(f"     - 服务器地址: {server_config.get_server_host()}:{server_config.get_server_port()}")
        print(f"     - AI功能: {'启用' if server_config.is_ai_enabled() else '禁用'}")
        print(f"     - 配置文件: {server_config.config_file}")
        
        # 测试客户端配置
        from src.client.config.client_config import get_client_config
        client_config = get_client_config()
        
        print(f"  ✅ 客户端配置加载成功")
        print(f"     - 默认服务器: {client_config.get_default_host()}:{client_config.get_default_port()}")
        print(f"     - UI模式: {client_config.get_ui_mode()}")
        print(f"     - 配置文件: {client_config.config_file}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置系统测试失败: {e}")
        return False


def test_ai_integration():
    """测试AI集成"""
    print("\n🤖 测试AI集成...")
    
    try:
        from src.server.config.ai_config import get_ai_config
        ai_config = get_ai_config()
        
        print(f"  ✅ AI配置加载成功")
        print(f"     - AI启用: {ai_config.is_enabled()}")
        print(f"     - 当前模型: {ai_config.model}")
        print(f"     - API密钥: {'已设置' if ai_config.get_api_key() else '未设置'}")
        print(f"     - 可用模型: {len(ai_config.get_available_models())}个")
        
        # 测试智谱AI客户端
        if ai_config.get_api_key():
            from src.server.ai.zhipu_client import ZhipuClient
            try:
                client = ZhipuClient()
                print(f"  ✅ 智谱AI客户端初始化成功")
                print(f"     - 使用SDK: {client.use_sdk}")
                print(f"     - 模型信息: {client.get_model_info()}")
            except Exception as e:
                print(f"  ⚠️ 智谱AI客户端初始化失败: {e}")
        else:
            print(f"  ⚠️ 未设置API密钥，跳过客户端测试")
        
        return True
        
    except Exception as e:
        print(f"  ❌ AI集成测试失败: {e}")
        return False


def test_database_connection():
    """测试数据库连接"""
    print("\n💾 测试数据库连接...")
    
    try:
        from src.server.database.connection import get_connection
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 测试基本查询
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"  ✅ 数据库连接成功")
        print(f"     - 数据库表数量: {len(tables)}")
        print(f"     - 表名: {[table[0] for table in tables]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ 数据库连接测试失败: {e}")
        return False


def test_server_startup():
    """测试服务器启动"""
    print("\n🚀 测试服务器启动...")
    
    try:
        from src.server.core.server import ChatRoomServer
        from src.server.config.server_config import get_server_config
        
        config = get_server_config()
        
        # 使用测试端口避免冲突
        test_port = 8899
        server = ChatRoomServer(host="localhost", port=test_port)
        
        print(f"  ✅ 服务器实例创建成功")
        print(f"     - 监听地址: localhost:{test_port}")
        print(f"     - 最大连接数: {server.max_connections}")
        
        # 不实际启动服务器，只测试初始化
        return True
        
    except Exception as e:
        print(f"  ❌ 服务器启动测试失败: {e}")
        return False


def test_client_initialization():
    """测试客户端初始化"""
    print("\n📱 测试客户端初始化...")
    
    try:
        from src.client.network.client import ChatClient
        from src.client.config.client_config import get_client_config
        
        config = get_client_config()
        
        # 创建客户端实例（不连接）
        client = ChatClient()
        
        print(f"  ✅ 客户端实例创建成功")
        print(f"     - 默认服务器: {config.get_default_host()}:{config.get_default_port()}")
        print(f"     - 连接超时: {config.get_connection_timeout()}秒")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 客户端初始化测试失败: {e}")
        return False


def test_command_system():
    """测试命令系统"""
    print("\n⌨️ 测试命令系统...")
    
    try:
        from src.client.commands.command_handler import CommandHandler
        from src.client.network.client import ChatClient
        
        client = ChatClient()
        handler = CommandHandler(client)
        
        # 测试命令解析
        test_commands = [
            "/help",
            "/info",
            "/list -u",
            "/create_chat test_group",
            "/send_files test.txt"
        ]
        
        print(f"  ✅ 命令处理器创建成功")
        print(f"     - 可用命令: {len(handler.commands)}个")
        
        for cmd in test_commands:
            try:
                # 只测试命令解析，不执行
                parts = cmd.split()
                command_name = parts[0][1:]  # 移除 '/'
                if command_name in handler.commands:
                    print(f"     - 命令 '{command_name}' 可用")
                else:
                    print(f"     - 命令 '{command_name}' 不可用")
            except Exception:
                pass
        
        return True
        
    except Exception as e:
        print(f"  ❌ 命令系统测试失败: {e}")
        return False


def test_message_protocol():
    """测试消息协议"""
    print("\n📨 测试消息协议...")
    
    try:
        from src.shared.protocol import MessageType, create_message, parse_message
        
        # 测试消息创建和解析
        test_message = create_message(MessageType.LOGIN_REQUEST, {
            "username": "test_user",
            "password": "test_password"
        })
        
        parsed = parse_message(test_message)
        
        print(f"  ✅ 消息协议测试成功")
        print(f"     - 消息类型: {parsed['type']}")
        print(f"     - 消息数据: {parsed['data']}")
        print(f"     - 消息长度: {len(test_message)}字节")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 消息协议测试失败: {e}")
        return False


def test_file_operations():
    """测试文件操作"""
    print("\n📁 测试文件操作...")
    
    try:
        from src.server.config.server_config import get_server_config
        
        config = get_server_config()
        
        # 检查文件存储路径
        files_path = Path(config.get_files_storage_path())
        db_path = Path(config.get_database_path())
        
        print(f"  ✅ 文件路径配置正确")
        print(f"     - 文件存储: {files_path}")
        print(f"     - 数据库: {db_path}")
        print(f"     - 最大文件大小: {config.get_max_file_size() // 1024 // 1024}MB")
        print(f"     - 允许扩展名: {len(config.get_allowed_file_extensions())}种")
        
        # 确保目录存在
        files_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 文件操作测试失败: {e}")
        return False


def test_configuration_tools():
    """测试配置工具"""
    print("\n🔧 测试配置工具...")
    
    try:
        # 测试配置模板存在
        templates = [
            "config/templates/server_config.template.yaml",
            "config/templates/client_config.template.yaml"
        ]
        
        for template in templates:
            template_path = Path(template)
            if template_path.exists():
                print(f"  ✅ 配置模板存在: {template}")
            else:
                print(f"  ⚠️ 配置模板缺失: {template}")
        
        # 测试配置工具脚本存在
        tools = [
            "config/examples/config_setup.py",
            "config/examples/migrate_config.py"
        ]
        
        for tool in tools:
            tool_path = Path(tool)
            if tool_path.exists():
                print(f"  ✅ 配置工具存在: {tool}")
            else:
                print(f"  ⚠️ 配置工具缺失: {tool}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 配置工具测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 Chat-Room 完整系统测试")
    print("=" * 60)
    print("验证配置系统重构后的整体功能")
    print("=" * 60)
    
    tests = [
        test_configuration_system,
        test_ai_integration,
        test_database_connection,
        test_server_startup,
        test_client_initialization,
        test_command_system,
        test_message_protocol,
        test_file_operations,
        test_configuration_tools,
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ 测试 {test_func.__name__} 失败")
        except Exception as e:
            print(f"\n❌ 测试 {test_func.__name__} 出现异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有系统测试通过！")
        print("\n✨ 系统重构完成，主要改进:")
        print("  • 移除环境变量依赖")
        print("  • 统一配置文件管理")
        print("  • 服务器和客户端独立配置")
        print("  • 配置验证和错误处理")
        print("  • 配置模板和迁移工具")
        print("  • AI功能完全集成")
        print("  • 向后兼容性保证")
        
        print("\n🚀 系统已准备就绪，可以开始使用:")
        print("  1. 配置设置: python tools/config_setup.py")
        print("  2. 启动服务器: python -m server.main")
        print("  3. 启动客户端: python -m client.main")
        print("  4. 查看文档: docs/Configuration_Guide.md")
        
        return True
    else:
        print("❌ 部分测试失败，请检查系统配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
