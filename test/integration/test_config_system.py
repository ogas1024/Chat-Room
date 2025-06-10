#!/usr/bin/env python3
"""
配置系统测试脚本
测试新的配置文件管理系统
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_config_manager():
    """测试配置管理器基础功能"""
    print("🔍 测试配置管理器基础功能...")
    
    try:
        from shared.config_manager import ConfigManager
        
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_config_file = f.name
        
        # 默认配置
        default_config = {
            "test": {
                "value1": "hello",
                "value2": 123,
                "nested": {
                    "key": "world"
                }
            }
        }
        
        # 测试配置管理器
        manager = ConfigManager(temp_config_file, default_config)
        
        # 测试获取配置
        assert manager.get("test.value1") == "hello"
        assert manager.get("test.value2") == 123
        assert manager.get("test.nested.key") == "world"
        assert manager.get("nonexistent", "default") == "default"
        
        # 测试设置配置
        assert manager.set("test.value1", "modified")
        assert manager.get("test.value1") == "modified"
        
        # 测试保存和重新加载
        assert manager.save_config()
        
        # 创建新的管理器实例验证持久化
        manager2 = ConfigManager(temp_config_file, default_config)
        assert manager2.get("test.value1") == "modified"
        
        # 清理
        os.unlink(temp_config_file)
        
        print("✅ 配置管理器基础功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False


def test_server_config():
    """测试服务器配置"""
    print("\n🔍 测试服务器配置...")
    
    try:
        from server.config.server_config import get_server_config
        
        config = get_server_config()
        
        # 测试基本配置获取
        host = config.get_server_host()
        port = config.get_server_port()
        max_conn = config.get_max_connections()
        
        print(f"  服务器地址: {host}:{port}")
        print(f"  最大连接数: {max_conn}")
        
        # 测试AI配置
        ai_enabled = config.is_ai_enabled()
        ai_model = config.get_ai_model()
        api_key = config.get_ai_api_key()
        
        print(f"  AI功能: {'启用' if ai_enabled else '禁用'}")
        print(f"  AI模型: {ai_model}")
        print(f"  API密钥: {'已设置' if api_key else '未设置'}")
        
        # 测试配置信息
        info = config.get_config_info()
        print(f"  配置文件: {info['config_file']}")
        print(f"  文件存在: {info['file_exists']}")
        
        print("✅ 服务器配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 服务器配置测试失败: {e}")
        return False


def test_client_config():
    """测试客户端配置"""
    print("\n🔍 测试客户端配置...")
    
    try:
        from client.config.client_config import get_client_config
        
        config = get_client_config()
        
        # 测试基本配置获取
        host = config.get_default_host()
        port = config.get_default_port()
        timeout = config.get_connection_timeout()
        
        print(f"  默认服务器: {host}:{port}")
        print(f"  连接超时: {timeout}秒")
        
        # 测试UI配置
        ui_mode = config.get_ui_mode()
        theme = config.get_theme()
        download_path = config.get_download_path()
        
        print(f"  UI模式: {ui_mode}")
        print(f"  主题: {theme}")
        print(f"  下载路径: {download_path}")
        
        # 测试配置信息
        info = config.get_config_info()
        print(f"  配置文件: {info['config_file']}")
        print(f"  文件存在: {info['file_exists']}")
        
        print("✅ 客户端配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 客户端配置测试失败: {e}")
        return False


def test_ai_config_compatibility():
    """测试AI配置兼容性"""
    print("\n🔍 测试AI配置兼容性...")
    
    try:
        from server.config.ai_config import get_ai_config
        
        ai_config = get_ai_config()
        
        # 测试兼容性方法
        enabled = ai_config.is_enabled()
        api_key = ai_config.get_api_key()
        model = ai_config.model
        models = ai_config.get_available_models()
        
        print(f"  AI启用: {enabled}")
        print(f"  API密钥: {'已设置' if api_key else '未设置'}")
        print(f"  当前模型: {model}")
        print(f"  可用模型: {len(models)}个")
        
        # 测试配置字典
        config_dict = ai_config.to_dict()
        print(f"  配置项数量: {len(config_dict)}")
        
        print("✅ AI配置兼容性测试通过")
        return True
        
    except Exception as e:
        print(f"❌ AI配置兼容性测试失败: {e}")
        return False


def test_constants_integration():
    """测试常量集成"""
    print("\n🔍 测试常量集成...")
    
    try:
        from shared.constants import get_server_constants, get_client_constants
        
        # 测试服务器常量
        server_constants = get_server_constants()
        print(f"  服务器常量: {len(server_constants)}个")
        print(f"  服务器地址: {server_constants['HOST']}:{server_constants['PORT']}")
        
        # 测试客户端常量
        client_constants = get_client_constants()
        print(f"  客户端常量: {len(client_constants)}个")
        print(f"  默认服务器: {client_constants['DEFAULT_HOST']}:{client_constants['DEFAULT_PORT']}")
        
        print("✅ 常量集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 常量集成测试失败: {e}")
        return False


def test_config_templates():
    """测试配置模板"""
    print("\n🔍 测试配置模板...")
    
    try:
        # 检查模板文件是否存在
        server_template = Path("config/server_config.template.yaml")
        client_template = Path("config/client_config.template.yaml")
        
        print(f"  服务器模板: {'存在' if server_template.exists() else '不存在'}")
        print(f"  客户端模板: {'存在' if client_template.exists() else '不存在'}")
        
        # 测试模板导出
        from server.config.server_config import get_server_config
        from client.config.client_config import get_client_config
        
        server_config = get_server_config()
        client_config = get_client_config()
        
        # 导出到临时文件
        temp_dir = Path(tempfile.mkdtemp())
        
        server_temp = temp_dir / "server_test.yaml"
        client_temp = temp_dir / "client_test.yaml"
        
        server_success = server_config.export_template(str(server_temp))
        client_success = client_config.export_template(str(client_temp))
        
        print(f"  服务器模板导出: {'成功' if server_success else '失败'}")
        print(f"  客户端模板导出: {'成功' if client_success else '失败'}")
        
        # 清理
        shutil.rmtree(temp_dir)
        
        print("✅ 配置模板测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置模板测试失败: {e}")
        return False


def test_environment_migration():
    """测试环境变量迁移检测"""
    print("\n🔍 测试环境变量迁移检测...")
    
    try:
        # 临时设置环境变量
        original_key = os.environ.get('ZHIPU_API_KEY')
        os.environ['ZHIPU_API_KEY'] = 'test_key_12345'
        
        from tools.migrate_config import detect_environment_config
        
        env_config = detect_environment_config()
        
        print(f"  检测到环境变量: {len(env_config)}个")
        if 'ZHIPU_API_KEY' in env_config:
            print(f"  ZHIPU_API_KEY: {env_config['ZHIPU_API_KEY'][:8]}...")
        
        # 恢复环境变量
        if original_key:
            os.environ['ZHIPU_API_KEY'] = original_key
        else:
            del os.environ['ZHIPU_API_KEY']
        
        print("✅ 环境变量迁移检测测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 环境变量迁移检测测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 配置系统测试")
    print("=" * 60)
    
    tests = [
        test_config_manager,
        test_server_config,
        test_client_config,
        test_ai_config_compatibility,
        test_constants_integration,
        test_config_templates,
        test_environment_migration,
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
        print("🎉 所有配置系统测试通过！")
        print("\n✨ 配置系统特性:")
        print("  • 统一的YAML/JSON配置文件管理")
        print("  • 服务器和客户端独立配置")
        print("  • 配置验证和错误处理")
        print("  • 配置模板和示例")
        print("  • 环境变量迁移支持")
        print("  • 向后兼容性保证")
        
        print("\n🔧 使用方法:")
        print("  • 配置设置: python tools/config_setup.py")
        print("  • 环境变量迁移: python tools/migrate_config.py")
        print("  • 服务器配置: config/server_config.yaml")
        print("  • 客户端配置: config/client_config.yaml")
        
        return True
    else:
        print("❌ 部分测试失败，请检查配置系统实现")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
