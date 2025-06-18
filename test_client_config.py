#!/usr/bin/env python3
"""
测试客户端配置是否正确读取
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_client_config():
    """测试客户端配置"""
    print("🔍 测试客户端配置读取")
    print("=" * 40)
    
    try:
        from client.config.client_config import get_client_config
        
        # 获取配置
        config = get_client_config()
        
        # 显示配置信息
        print(f"✅ 配置文件路径: {config.config_file}")
        print(f"✅ 配置文件存在: {config.config_file.exists()}")
        
        # 测试关键配置项
        host = config.get_default_host()
        port = config.get_default_port()
        timeout = config.get_connection_timeout()
        
        print(f"✅ 默认主机: {host}")
        print(f"✅ 默认端口: {port}")
        print(f"✅ 连接超时: {timeout}秒")
        
        # 验证是否使用了配置文件中的值
        if host == "47.116.210.212":
            print("✅ 配置文件中的服务器地址已正确读取")
        else:
            print(f"❌ 配置文件中的服务器地址未正确读取，当前值: {host}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置读取失败: {e}")
        return False


def test_command_line_args():
    """测试命令行参数默认值"""
    print("\n🔍 测试命令行参数默认值")
    print("=" * 40)
    
    try:
        # 模拟命令行参数解析
        import argparse
        from client.config.client_config import get_client_config
        
        # 获取配置文件中的默认值
        client_config = get_client_config()
        config_host = client_config.get_default_host()
        config_port = client_config.get_default_port()
        
        # 创建参数解析器（模拟main.py中的逻辑）
        parser = argparse.ArgumentParser(description='聊天室客户端')
        parser.add_argument(
            '--host',
            default=config_host,
            help=f'服务器地址 (默认: {config_host})'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=config_port,
            help=f'服务器端口 (默认: {config_port})'
        )
        
        # 解析空参数（使用默认值）
        args = parser.parse_args([])
        
        print(f"✅ 命令行默认主机: {args.host}")
        print(f"✅ 命令行默认端口: {args.port}")
        
        if args.host == "47.116.210.212":
            print("✅ 命令行参数正确使用了配置文件中的默认值")
            return True
        else:
            print(f"❌ 命令行参数未使用配置文件默认值，当前值: {args.host}")
            return False
            
    except Exception as e:
        print(f"❌ 命令行参数测试失败: {e}")
        return False


def test_client_creation():
    """测试客户端创建"""
    print("\n🔍 测试客户端创建")
    print("=" * 40)
    
    try:
        from client.core.client import ChatClient
        
        # 创建客户端（不传入参数，使用配置文件默认值）
        client = ChatClient()
        
        print(f"✅ 客户端主机: {client.network_client.host}")
        print(f"✅ 客户端端口: {client.network_client.port}")
        
        if client.network_client.host == "47.116.210.212":
            print("✅ 客户端正确使用了配置文件中的服务器地址")
            return True
        else:
            print(f"❌ 客户端未使用配置文件中的服务器地址，当前值: {client.network_client.host}")
            return False
            
    except Exception as e:
        print(f"❌ 客户端创建测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 Chat-Room 客户端配置测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        ("配置文件读取", test_client_config),
        ("命令行参数", test_command_line_args),
        ("客户端创建", test_client_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n📊 测试结果汇总")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！客户端配置正确。")
        print("💡 现在只需要确保服务器在 47.116.210.212:8888 上运行即可。")
    else:
        print("❌ 部分测试失败，请检查配置。")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
