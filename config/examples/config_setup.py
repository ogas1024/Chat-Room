#!/usr/bin/env python3
"""
配置设置工具
帮助用户快速配置Chat-Room项目
"""

import os
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def setup_server_config():
    """设置服务器配置"""
    print("🔧 服务器配置设置")
    print("=" * 50)
    
    try:
        from server.config.server_config import get_server_config
        
        config = get_server_config()
        
        # 显示当前配置信息
        info = config.get_config_info()
        print(f"📁 配置文件: {info['config_file']}")
        print(f"📊 文件状态: {'存在' if info['file_exists'] else '不存在'}")
        print(f"🤖 AI功能: {'启用' if info['ai_enabled'] else '禁用'}")
        print(f"🔑 API密钥: {'已设置' if info['ai_api_key_set'] else '未设置'}")
        print(f"🧠 AI模型: {info['ai_model']}")
        print(f"🌐 服务器地址: {info['server_address']}")
        
        print("\n" + "-" * 50)
        
        # 交互式配置
        while True:
            print("\n可用操作:")
            print("1. 设置AI API密钥")
            print("2. 更改AI模型")
            print("3. 更改服务器地址")
            print("4. 导出配置模板")
            print("5. 重置为默认配置")
            print("6. 显示配置信息")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-6): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                setup_ai_api_key(config)
            elif choice == "2":
                setup_ai_model(config)
            elif choice == "3":
                setup_server_address(config)
            elif choice == "4":
                export_config_template(config)
            elif choice == "5":
                reset_config(config)
            elif choice == "6":
                show_config_info(config)
            else:
                print("❌ 无效选择，请重试")
        
        print("\n✅ 配置设置完成")
        
    except Exception as e:
        print(f"❌ 配置设置失败: {e}")


def setup_client_config():
    """设置客户端配置"""
    print("🔧 客户端配置设置")
    print("=" * 50)
    
    try:
        from client.config.client_config import get_client_config
        
        config = get_client_config()
        
        # 显示当前配置信息
        info = config.get_config_info()
        print(f"📁 配置文件: {info['config_file']}")
        print(f"📊 文件状态: {'存在' if info['file_exists'] else '不存在'}")
        print(f"🎨 UI模式: {info['ui_mode']}")
        print(f"🎭 主题: {info['theme']}")
        print(f"🌐 默认服务器: {info['default_server']}")
        print(f"🔐 自动登录: {'启用' if info['auto_login'] else '禁用'}")
        
        print("\n" + "-" * 50)
        
        # 交互式配置
        while True:
            print("\n可用操作:")
            print("1. 设置默认服务器地址")
            print("2. 更改UI模式")
            print("3. 更改主题")
            print("4. 设置下载路径")
            print("5. 导出配置模板")
            print("6. 重置为默认配置")
            print("7. 显示配置信息")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                setup_default_server(config)
            elif choice == "2":
                setup_ui_mode(config)
            elif choice == "3":
                setup_theme(config)
            elif choice == "4":
                setup_download_path(config)
            elif choice == "5":
                export_client_template(config)
            elif choice == "6":
                reset_client_config(config)
            elif choice == "7":
                show_client_info(config)
            else:
                print("❌ 无效选择，请重试")
        
        print("\n✅ 配置设置完成")
        
    except Exception as e:
        print(f"❌ 配置设置失败: {e}")


def setup_ai_api_key(config):
    """设置AI API密钥"""
    print("\n🔑 设置AI API密钥")
    print("💡 获取API密钥: https://open.bigmodel.cn/")
    
    current_key = config.get_ai_api_key()
    if current_key:
        print(f"当前API密钥: {current_key[:8]}...")
    
    api_key = input("请输入新的API密钥 (留空取消): ").strip()
    if api_key:
        if config.set_ai_api_key(api_key):
            print("✅ API密钥设置成功")
        else:
            print("❌ API密钥设置失败")
    else:
        print("⏭️ 跳过API密钥设置")


def setup_ai_model(config):
    """设置AI模型"""
    print("\n🧠 设置AI模型")
    
    ai_config = config.get_ai_config()
    available_models = ai_config.get("available_models", [])
    current_model = config.get_ai_model()
    
    print(f"当前模型: {current_model}")
    print("可用模型:")
    for i, model in enumerate(available_models, 1):
        print(f"  {i}. {model}")
    
    try:
        choice = input(f"请选择模型 (1-{len(available_models)}, 留空取消): ").strip()
        if choice:
            index = int(choice) - 1
            if 0 <= index < len(available_models):
                model = available_models[index]
                if config.set_ai_model(model):
                    print(f"✅ AI模型已设置为: {model}")
                else:
                    print("❌ AI模型设置失败")
            else:
                print("❌ 无效选择")
        else:
            print("⏭️ 跳过模型设置")
    except ValueError:
        print("❌ 请输入有效数字")


def setup_server_address(config):
    """设置服务器地址"""
    print("\n🌐 设置服务器地址")
    
    current_host = config.get_server_host()
    current_port = config.get_server_port()
    print(f"当前地址: {current_host}:{current_port}")
    
    host = input(f"请输入主机地址 (当前: {current_host}, 留空保持不变): ").strip()
    if not host:
        host = current_host
    
    port_input = input(f"请输入端口 (当前: {current_port}, 留空保持不变): ").strip()
    if port_input:
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                success = True
                success &= config.config_manager.set("server.host", host)
                success &= config.config_manager.set("server.port", port)
                if success:
                    config.save_config()
                    print(f"✅ 服务器地址已设置为: {host}:{port}")
                else:
                    print("❌ 服务器地址设置失败")
            else:
                print("❌ 端口必须在1-65535范围内")
        except ValueError:
            print("❌ 请输入有效端口号")
    else:
        if host != current_host:
            if config.config_manager.set("server.host", host):
                config.save_config()
                print(f"✅ 服务器主机已设置为: {host}")
            else:
                print("❌ 服务器主机设置失败")


def setup_default_server(config):
    """设置默认服务器"""
    print("\n🌐 设置默认服务器")
    
    current_host = config.get_default_host()
    current_port = config.get_default_port()
    print(f"当前默认服务器: {current_host}:{current_port}")
    
    host = input(f"请输入服务器地址 (当前: {current_host}, 留空保持不变): ").strip()
    if not host:
        host = current_host
    
    port_input = input(f"请输入端口 (当前: {current_port}, 留空保持不变): ").strip()
    if port_input:
        try:
            port = int(port_input)
            if 1 <= port <= 65535:
                success = True
                success &= config.config_manager.set("connection.default_host", host)
                success &= config.config_manager.set("connection.default_port", port)
                if success:
                    config.save_config()
                    print(f"✅ 默认服务器已设置为: {host}:{port}")
                else:
                    print("❌ 默认服务器设置失败")
            else:
                print("❌ 端口必须在1-65535范围内")
        except ValueError:
            print("❌ 请输入有效端口号")
    else:
        if host != current_host:
            if config.config_manager.set("connection.default_host", host):
                config.save_config()
                print(f"✅ 默认服务器主机已设置为: {host}")
            else:
                print("❌ 默认服务器主机设置失败")


def setup_ui_mode(config):
    """设置UI模式"""
    print("\n🎨 设置UI模式")
    
    current_mode = config.get_ui_mode()
    print(f"当前模式: {current_mode}")
    print("可用模式:")
    print("  1. tui - 图形化终端界面")
    print("  2. cli - 命令行界面")
    
    choice = input("请选择模式 (1-2, 留空取消): ").strip()
    if choice == "1":
        if config.set_ui_mode("tui"):
            print("✅ UI模式已设置为: tui")
        else:
            print("❌ UI模式设置失败")
    elif choice == "2":
        if config.set_ui_mode("cli"):
            print("✅ UI模式已设置为: cli")
        else:
            print("❌ UI模式设置失败")
    elif choice:
        print("❌ 无效选择")
    else:
        print("⏭️ 跳过UI模式设置")


def setup_theme(config):
    """设置主题"""
    print("\n🎭 设置主题")
    
    current_theme = config.get_theme()
    print(f"当前主题: {current_theme}")
    
    theme = input("请输入主题名称 (留空取消): ").strip()
    if theme:
        if config.set_theme(theme):
            print(f"✅ 主题已设置为: {theme}")
        else:
            print("❌ 主题设置失败")
    else:
        print("⏭️ 跳过主题设置")


def setup_download_path(config):
    """设置下载路径"""
    print("\n📁 设置下载路径")
    
    current_path = config.get_download_path()
    print(f"当前下载路径: {current_path}")
    
    path = input("请输入新的下载路径 (留空取消): ").strip()
    if path:
        if config.set_download_path(path):
            print(f"✅ 下载路径已设置为: {path}")
        else:
            print("❌ 下载路径设置失败")
    else:
        print("⏭️ 跳过下载路径设置")


def export_config_template(config):
    """导出服务器配置模板"""
    print("\n📝 导出配置模板")
    
    template_file = input("请输入模板文件路径 (留空使用默认): ").strip()
    if not template_file:
        template_file = "config/server_config.template.yaml"
    
    if config.export_template(template_file):
        print(f"✅ 配置模板已导出到: {template_file}")
    else:
        print("❌ 配置模板导出失败")


def export_client_template(config):
    """导出客户端配置模板"""
    print("\n📝 导出配置模板")
    
    template_file = input("请输入模板文件路径 (留空使用默认): ").strip()
    if not template_file:
        template_file = "config/client_config.template.yaml"
    
    if config.export_template(template_file):
        print(f"✅ 配置模板已导出到: {template_file}")
    else:
        print("❌ 配置模板导出失败")


def reset_config(config):
    """重置服务器配置"""
    print("\n🔄 重置配置")
    
    confirm = input("确定要重置为默认配置吗？这将丢失所有自定义设置 (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        if config.config_manager.reset_to_default():
            print("✅ 配置已重置为默认值")
        else:
            print("❌ 配置重置失败")
    else:
        print("⏭️ 取消重置操作")


def reset_client_config(config):
    """重置客户端配置"""
    print("\n🔄 重置配置")
    
    confirm = input("确定要重置为默认配置吗？这将丢失所有自定义设置 (y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        if config.config_manager.reset_to_default():
            print("✅ 配置已重置为默认值")
        else:
            print("❌ 配置重置失败")
    else:
        print("⏭️ 取消重置操作")


def show_config_info(config):
    """显示服务器配置信息"""
    print("\n📊 配置信息")
    
    info = config.get_config_info()
    for key, value in info.items():
        print(f"  {key}: {value}")


def show_client_info(config):
    """显示客户端配置信息"""
    print("\n📊 配置信息")
    
    info = config.get_config_info()
    for key, value in info.items():
        print(f"  {key}: {value}")


def main():
    """主函数"""
    print("🔧 Chat-Room 配置设置工具")
    print("=" * 60)
    
    while True:
        print("\n请选择要配置的组件:")
        print("1. 服务器配置")
        print("2. 客户端配置")
        print("3. 创建配置目录")
        print("0. 退出")
        
        choice = input("\n请选择 (0-3): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            setup_server_config()
        elif choice == "2":
            setup_client_config()
        elif choice == "3":
            create_config_directories()
        else:
            print("❌ 无效选择，请重试")
    
    print("\n👋 配置设置工具已退出")


def create_config_directories():
    """创建配置目录"""
    print("\n📁 创建配置目录")
    
    directories = [
        "config",
        "logs",
        "data",
        "downloads"
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 目录已创建: {directory}")
        except Exception as e:
            print(f"❌ 创建目录失败 {directory}: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 配置设置被用户中断")
    except Exception as e:
        print(f"\n❌ 配置设置出现错误: {e}")
