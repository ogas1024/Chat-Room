#!/usr/bin/env python3
"""
配置修改演示脚本
演示如何修改配置文件并验证程序能立即读取新配置
"""

import sys
import time
import yaml
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from client.config.client_config import get_client_config, reload_client_config
from server.config.server_config import get_server_config, reload_server_config


def demo_client_config_modification():
    """演示客户端配置修改"""
    print("=" * 60)
    print("🔧 客户端配置修改演示")
    print("=" * 60)
    
    # 获取客户端配置
    client_config = get_client_config()
    
    print("📋 当前客户端配置:")
    print(f"  默认服务器: {client_config.get_default_host()}:{client_config.get_default_port()}")
    print(f"  UI模式: {client_config.get_ui_mode()}")
    print(f"  主题: {client_config.get_theme()}")
    print(f"  下载路径: {client_config.get_download_path()}")
    
    # 保存原始配置
    original_host = client_config.get_default_host()
    original_port = client_config.get_default_port()
    original_theme = client_config.get_theme()
    
    print("\n🔄 修改配置...")
    
    # 通过代码修改配置
    print("1. 通过代码API修改配置:")
    client_config.config_manager.set("connection.default_host", "192.168.1.100")
    client_config.config_manager.set("connection.default_port", 9999)
    client_config.set_theme("dark")
    client_config.save_config()
    
    print(f"  ✅ 修改后 - 服务器: {client_config.get_default_host()}:{client_config.get_default_port()}")
    print(f"  ✅ 修改后 - 主题: {client_config.get_theme()}")
    
    # 直接修改配置文件
    print("\n2. 直接修改配置文件:")
    config_file = project_root / "config" / "client_config.yaml"
    
    # 读取当前配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    # 修改配置
    config_data['ui']['theme'] = 'light'
    config_data['connection']['default_host'] = '127.0.0.1'
    config_data['connection']['default_port'] = 7777
    
    # 保存配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print("  ✅ 配置文件已直接修改")
    
    # 重新加载配置
    print("\n3. 重新加载配置验证修改生效:")
    reload_client_config()
    client_config = get_client_config()
    
    print(f"  ✅ 重新加载后 - 服务器: {client_config.get_default_host()}:{client_config.get_default_port()}")
    print(f"  ✅ 重新加载后 - 主题: {client_config.get_theme()}")
    
    # 恢复原始配置
    print("\n🔄 恢复原始配置...")
    client_config.config_manager.set("connection.default_host", original_host)
    client_config.config_manager.set("connection.default_port", original_port)
    client_config.set_theme(original_theme)
    client_config.save_config()
    
    print(f"  ✅ 已恢复 - 服务器: {client_config.get_default_host()}:{client_config.get_default_port()}")
    print(f"  ✅ 已恢复 - 主题: {client_config.get_theme()}")


def demo_server_config_modification():
    """演示服务器配置修改"""
    print("\n" + "=" * 60)
    print("🔧 服务器配置修改演示")
    print("=" * 60)
    
    # 获取服务器配置
    server_config = get_server_config()
    
    print("📋 当前服务器配置:")
    print(f"  监听地址: {server_config.get_server_host()}:{server_config.get_server_port()}")
    print(f"  最大连接数: {server_config.get_max_connections()}")
    print(f"  AI功能: {'启用' if server_config.is_ai_enabled() else '禁用'}")
    print(f"  AI模型: {server_config.get_ai_model()}")
    
    # 保存原始配置
    original_host = server_config.get_server_host()
    original_port = server_config.get_server_port()
    original_max_conn = server_config.get_max_connections()
    original_model = server_config.get_ai_model()
    
    print("\n🔄 修改配置...")
    
    # 通过代码修改配置
    print("1. 通过代码API修改配置:")
    server_config.config_manager.set("server.host", "0.0.0.0")
    server_config.config_manager.set("server.port", 8889)
    server_config.config_manager.set("server.max_connections", 200)
    server_config.set_ai_model("glm-4")
    server_config.save_config()
    
    print(f"  ✅ 修改后 - 监听地址: {server_config.get_server_host()}:{server_config.get_server_port()}")
    print(f"  ✅ 修改后 - 最大连接数: {server_config.get_max_connections()}")
    print(f"  ✅ 修改后 - AI模型: {server_config.get_ai_model()}")
    
    # 直接修改配置文件
    print("\n2. 直接修改配置文件:")
    config_file = project_root / "config" / "server_config.yaml"
    
    # 读取当前配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)
    
    # 修改配置
    config_data['server']['host'] = 'localhost'
    config_data['server']['port'] = 8890
    config_data['server']['max_connections'] = 150
    config_data['ai']['model'] = 'glm-4-plus'
    
    # 保存配置文件
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, indent=2)
    
    print("  ✅ 配置文件已直接修改")
    
    # 重新加载配置
    print("\n3. 重新加载配置验证修改生效:")
    reload_server_config()
    server_config = get_server_config()
    
    print(f"  ✅ 重新加载后 - 监听地址: {server_config.get_server_host()}:{server_config.get_server_port()}")
    print(f"  ✅ 重新加载后 - 最大连接数: {server_config.get_max_connections()}")
    print(f"  ✅ 重新加载后 - AI模型: {server_config.get_ai_model()}")
    
    # 恢复原始配置
    print("\n🔄 恢复原始配置...")
    server_config.config_manager.set("server.host", original_host)
    server_config.config_manager.set("server.port", original_port)
    server_config.config_manager.set("server.max_connections", original_max_conn)
    server_config.set_ai_model(original_model)
    server_config.save_config()
    
    print(f"  ✅ 已恢复 - 监听地址: {server_config.get_server_host()}:{server_config.get_server_port()}")
    print(f"  ✅ 已恢复 - 最大连接数: {server_config.get_max_connections()}")
    print(f"  ✅ 已恢复 - AI模型: {server_config.get_ai_model()}")


def demo_config_validation():
    """演示配置验证功能"""
    print("\n" + "=" * 60)
    print("🔧 配置验证演示")
    print("=" * 60)
    
    # 获取配置信息
    client_config = get_client_config()
    server_config = get_server_config()
    
    print("📋 客户端配置信息:")
    client_info = client_config.get_config_info()
    for key, value in client_info.items():
        print(f"  {key}: {value}")
    
    print("\n📋 服务器配置信息:")
    server_info = server_config.get_config_info()
    for key, value in server_info.items():
        print(f"  {key}: {value}")
    
    # 测试配置模板导出
    print("\n🔄 测试配置模板导出...")
    
    client_template = project_root / "config" / "templates" / "client_config_demo.template.yaml"
    server_template = project_root / "config" / "templates" / "server_config_demo.template.yaml"
    
    if client_config.export_template(str(client_template)):
        print(f"  ✅ 客户端配置模板已导出: {client_template}")
    
    if server_config.export_template(str(server_template)):
        print(f"  ✅ 服务器配置模板已导出: {server_template}")
    
    # 清理演示文件
    if client_template.exists():
        client_template.unlink()
        print(f"  🗑️ 已清理演示文件: {client_template}")
    
    if server_template.exists():
        server_template.unlink()
        print(f"  🗑️ 已清理演示文件: {server_template}")


def main():
    """主函数"""
    print("🚀 Chat-Room 配置管理系统演示")
    print("演示配置文件的修改、重新加载和验证功能")
    
    try:
        # 演示客户端配置修改
        demo_client_config_modification()
        
        # 演示服务器配置修改
        demo_server_config_modification()
        
        # 演示配置验证
        demo_config_validation()
        
        print("\n" + "=" * 60)
        print("🎉 配置管理系统演示完成！")
        print("=" * 60)
        print("\n📝 总结:")
        print("  ✅ 配置文件可以通过代码API修改")
        print("  ✅ 配置文件可以直接编辑")
        print("  ✅ 修改后可以重新加载生效")
        print("  ✅ 配置验证和模板导出功能正常")
        print("  ✅ 配置管理系统运行良好")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
