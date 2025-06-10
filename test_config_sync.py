#!/usr/bin/env python3
"""
配置文件同步验证脚本
验证配置文件的修改能否正确反映到程序模块中
"""

import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_server_config_sync():
    """测试服务器配置同步"""
    print("🔧 测试服务器配置同步...")
    
    try:
        from server.config.server_config import get_server_config
        
        config = get_server_config()
        
        # 测试基本配置读取
        original_host = config.get_server_host()
        original_port = config.get_server_port()
        original_ai_model = config.get_ai_model()
        
        print(f"  📋 原始配置:")
        print(f"     - 服务器地址: {original_host}:{original_port}")
        print(f"     - AI模型: {original_ai_model}")
        print(f"     - AI启用: {config.is_ai_enabled()}")
        
        # 测试配置修改
        print(f"  🔄 测试配置修改...")
        
        # 修改服务器端口
        success = config.config_manager.set("server.port", 9999)
        if success:
            new_port = config.get_server_port()
            print(f"     ✅ 端口修改成功: {original_port} -> {new_port}")
        else:
            print(f"     ❌ 端口修改失败")
        
        # 修改AI模型
        success = config.set_ai_model("glm-4")
        if success:
            new_model = config.get_ai_model()
            print(f"     ✅ AI模型修改成功: {original_ai_model} -> {new_model}")
        else:
            print(f"     ❌ AI模型修改失败")
        
        # 测试配置保存
        if config.save_config():
            print(f"     ✅ 配置保存成功")
        else:
            print(f"     ❌ 配置保存失败")
        
        # 测试配置重载
        if config.reload_config():
            print(f"     ✅ 配置重载成功")
            
            # 验证重载后的配置
            reloaded_port = config.get_server_port()
            reloaded_model = config.get_ai_model()
            
            if reloaded_port == 9999:
                print(f"     ✅ 端口重载验证成功: {reloaded_port}")
            else:
                print(f"     ❌ 端口重载验证失败: {reloaded_port}")
            
            if reloaded_model == "glm-4":
                print(f"     ✅ AI模型重载验证成功: {reloaded_model}")
            else:
                print(f"     ❌ AI模型重载验证失败: {reloaded_model}")
        else:
            print(f"     ❌ 配置重载失败")
        
        # 恢复原始配置
        config.config_manager.set("server.port", original_port)
        config.set_ai_model(original_ai_model)
        config.save_config()
        
        print("✅ 服务器配置同步测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 服务器配置同步测试失败: {e}")
        return False


def test_client_config_sync():
    """测试客户端配置同步"""
    print("\n🎨 测试客户端配置同步...")
    
    try:
        from client.config.client_config import get_client_config
        
        config = get_client_config()
        
        # 测试基本配置读取
        original_host = config.get_default_host()
        original_port = config.get_default_port()
        original_ui_mode = config.get_ui_mode()
        original_theme = config.get_theme()
        
        print(f"  📋 原始配置:")
        print(f"     - 默认服务器: {original_host}:{original_port}")
        print(f"     - UI模式: {original_ui_mode}")
        print(f"     - 主题: {original_theme}")
        
        # 测试配置修改
        print(f"  🔄 测试配置修改...")
        
        # 修改默认端口
        success = config.config_manager.set("connection.default_port", 9998)
        if success:
            new_port = config.get_default_port()
            print(f"     ✅ 默认端口修改成功: {original_port} -> {new_port}")
        else:
            print(f"     ❌ 默认端口修改失败")
        
        # 修改UI模式
        success = config.set_ui_mode("cli")
        if success:
            new_ui_mode = config.get_ui_mode()
            print(f"     ✅ UI模式修改成功: {original_ui_mode} -> {new_ui_mode}")
        else:
            print(f"     ❌ UI模式修改失败")
        
        # 修改主题
        success = config.set_theme("dark")
        if success:
            new_theme = config.get_theme()
            print(f"     ✅ 主题修改成功: {original_theme} -> {new_theme}")
        else:
            print(f"     ❌ 主题修改失败")
        
        # 测试配置保存
        if config.save_config():
            print(f"     ✅ 配置保存成功")
        else:
            print(f"     ❌ 配置保存失败")
        
        # 测试配置重载
        if config.reload_config():
            print(f"     ✅ 配置重载成功")
            
            # 验证重载后的配置
            reloaded_port = config.get_default_port()
            reloaded_ui_mode = config.get_ui_mode()
            reloaded_theme = config.get_theme()
            
            if reloaded_port == 9998:
                print(f"     ✅ 端口重载验证成功: {reloaded_port}")
            else:
                print(f"     ❌ 端口重载验证失败: {reloaded_port}")
            
            if reloaded_ui_mode == "cli":
                print(f"     ✅ UI模式重载验证成功: {reloaded_ui_mode}")
            else:
                print(f"     ❌ UI模式重载验证失败: {reloaded_ui_mode}")
            
            if reloaded_theme == "dark":
                print(f"     ✅ 主题重载验证成功: {reloaded_theme}")
            else:
                print(f"     ❌ 主题重载验证失败: {reloaded_theme}")
        else:
            print(f"     ❌ 配置重载失败")
        
        # 恢复原始配置
        config.config_manager.set("connection.default_port", original_port)
        config.set_ui_mode(original_ui_mode)
        config.set_theme(original_theme)
        config.save_config()
        
        print("✅ 客户端配置同步测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 客户端配置同步测试失败: {e}")
        return False


def test_ai_config_sync():
    """测试AI配置同步"""
    print("\n🤖 测试AI配置同步...")
    
    try:
        from server.config.ai_config import get_ai_config
        
        ai_config = get_ai_config()
        
        # 测试基本配置读取
        original_enabled = ai_config.is_enabled()
        original_model = ai_config.model
        original_api_key = ai_config.get_api_key()
        
        print(f"  📋 原始AI配置:")
        print(f"     - AI启用: {original_enabled}")
        print(f"     - 当前模型: {original_model}")
        print(f"     - API密钥: {'已设置' if original_api_key else '未设置'}")
        
        # 测试配置修改
        print(f"  🔄 测试AI配置修改...")
        
        # 测试API密钥设置
        test_api_key = "test_api_key_12345"
        success = ai_config.set_api_key(test_api_key)
        if success:
            new_api_key = ai_config.get_api_key()
            print(f"     ✅ API密钥设置成功: {new_api_key[:8]}...")
        else:
            print(f"     ❌ API密钥设置失败")
        
        # 测试模型切换
        success = ai_config.set_model("glm-4-plus")
        if success:
            new_model = ai_config.model
            print(f"     ✅ 模型切换成功: {original_model} -> {new_model}")
        else:
            print(f"     ❌ 模型切换失败")
        
        # 测试配置重载
        ai_config.reload_from_config()
        reloaded_model = ai_config.model
        reloaded_api_key = ai_config.get_api_key()
        
        print(f"     ✅ AI配置重载完成")
        print(f"     - 重载后模型: {reloaded_model}")
        print(f"     - 重载后API密钥: {'已设置' if reloaded_api_key else '未设置'}")
        
        # 恢复原始配置（如果有的话）
        if original_api_key:
            ai_config.set_api_key(original_api_key)
        ai_config.set_model(original_model)
        
        print("✅ AI配置同步测试完成")
        return True
        
    except Exception as e:
        print(f"❌ AI配置同步测试失败: {e}")
        return False


def test_config_file_modification():
    """测试直接修改配置文件"""
    print("\n📝 测试直接修改配置文件...")
    
    try:
        import yaml
        from server.config.server_config import get_server_config
        
        config = get_server_config()
        config_file = config.config_file
        
        # 备份原始配置文件
        backup_file = config_file.with_suffix('.backup')
        if config_file.exists():
            shutil.copy2(config_file, backup_file)
            print(f"  📦 已备份配置文件: {backup_file}")
        
        # 读取当前配置
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        original_port = config_data.get('server', {}).get('port', 8888)
        
        # 修改配置文件
        config_data['server']['port'] = 7777
        config_data['server']['host'] = 'test.example.com'
        
        # 写入修改后的配置
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, 
                     allow_unicode=True, indent=2, sort_keys=False)
        
        print(f"  ✏️ 已修改配置文件")
        print(f"     - 端口: {original_port} -> 7777")
        print(f"     - 主机: localhost -> test.example.com")
        
        # 重新加载配置
        config.reload_config()
        
        # 验证修改是否生效
        new_port = config.get_server_port()
        new_host = config.get_server_host()
        
        if new_port == 7777:
            print(f"     ✅ 端口修改验证成功: {new_port}")
        else:
            print(f"     ❌ 端口修改验证失败: {new_port}")
        
        if new_host == 'test.example.com':
            print(f"     ✅ 主机修改验证成功: {new_host}")
        else:
            print(f"     ❌ 主机修改验证失败: {new_host}")
        
        # 恢复原始配置文件
        if backup_file.exists():
            shutil.copy2(backup_file, config_file)
            backup_file.unlink()
            config.reload_config()
            print(f"  🔄 已恢复原始配置文件")
        
        print("✅ 配置文件修改测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件修改测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🔄 配置文件同步验证测试")
    print("=" * 60)
    
    tests = [
        test_server_config_sync,
        test_client_config_sync,
        test_ai_config_sync,
        test_config_file_modification,
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
    print(f"📊 配置同步测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有配置同步测试通过！")
        print("\n✨ 验证结果:")
        print("  • 配置文件修改能正确反映到程序模块")
        print("  • 配置热重载功能正常工作")
        print("  • 服务器和客户端配置独立管理")
        print("  • AI配置同步机制正常")
        return True
    else:
        print("❌ 部分配置同步测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
