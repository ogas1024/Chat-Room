#!/usr/bin/env python3
"""
Chat-Room 客户端连接诊断工具
用于诊断客户端连接到服务器的问题
"""

import socket
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from client.config.client_config import get_client_config
from shared.logger import get_logger


def test_network_connectivity(host: str, port: int, timeout: int = 10) -> tuple[bool, str]:
    """测试网络连通性"""
    try:
        print(f"🔍 测试连接到 {host}:{port} (超时: {timeout}秒)")
        
        # 创建socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        start_time = time.time()
        result = sock.connect_ex((host, port))
        end_time = time.time()
        
        sock.close()
        
        if result == 0:
            return True, f"连接成功 (耗时: {end_time - start_time:.2f}秒)"
        else:
            return False, f"连接失败 (错误代码: {result})"
            
    except socket.gaierror as e:
        return False, f"DNS解析失败: {e}"
    except socket.timeout:
        return False, f"连接超时 ({timeout}秒)"
    except Exception as e:
        return False, f"连接异常: {e}"


def test_ping(host: str) -> tuple[bool, str]:
    """测试ping连通性"""
    import subprocess
    import platform
    
    try:
        # 根据操作系统选择ping命令
        if platform.system().lower() == "windows":
            cmd = ["ping", "-n", "3", host]
        else:
            cmd = ["ping", "-c", "3", host]
        
        print(f"🔍 测试ping到 {host}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return True, "ping成功"
        else:
            return False, f"ping失败: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "ping超时"
    except FileNotFoundError:
        return False, "ping命令不可用"
    except Exception as e:
        return False, f"ping异常: {e}"


def diagnose_config():
    """诊断配置文件"""
    print("=" * 60)
    print("📋 配置文件诊断")
    print("=" * 60)
    
    try:
        # 获取客户端配置
        client_config = get_client_config()
        
        # 显示配置信息
        config_info = client_config.get_config_info()
        print(f"✅ 配置文件路径: {client_config.config_file}")
        print(f"✅ 配置文件存在: {client_config.config_file.exists()}")
        print(f"✅ 默认服务器: {config_info['default_server']}")
        print(f"✅ UI模式: {config_info['ui_mode']}")
        print(f"✅ 主题: {config_info['theme']}")
        
        # 显示连接配置详情
        host = client_config.get_default_host()
        port = client_config.get_default_port()
        timeout = client_config.get_connection_timeout()
        
        print(f"✅ 服务器地址: {host}")
        print(f"✅ 服务器端口: {port}")
        print(f"✅ 连接超时: {timeout}秒")
        
        return host, port, timeout
        
    except Exception as e:
        print(f"❌ 配置文件读取失败: {e}")
        return None, None, None


def diagnose_network(host: str, port: int, timeout: int):
    """诊断网络连接"""
    print("\n" + "=" * 60)
    print("🌐 网络连接诊断")
    print("=" * 60)
    
    # 测试ping
    ping_success, ping_msg = test_ping(host)
    if ping_success:
        print(f"✅ Ping测试: {ping_msg}")
    else:
        print(f"❌ Ping测试: {ping_msg}")
    
    # 测试TCP连接
    tcp_success, tcp_msg = test_network_connectivity(host, port, timeout)
    if tcp_success:
        print(f"✅ TCP连接: {tcp_msg}")
    else:
        print(f"❌ TCP连接: {tcp_msg}")
    
    return tcp_success


def test_client_connection(host: str, port: int):
    """测试客户端连接"""
    print("\n" + "=" * 60)
    print("🔌 客户端连接测试")
    print("=" * 60)
    
    try:
        from client.core.client import NetworkClient
        
        print(f"🔍 使用NetworkClient连接到 {host}:{port}")
        
        # 创建网络客户端
        client = NetworkClient(host, port)
        
        # 尝试连接
        success = client.connect()
        
        if success:
            print("✅ 客户端连接成功")
            print(f"✅ 连接状态: {client.is_connected()}")
            
            # 断开连接
            client.disconnect()
            print("✅ 连接已断开")
            return True
        else:
            print("❌ 客户端连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 客户端连接异常: {e}")
        return False


def main():
    """主函数"""
    print("🚀 Chat-Room 客户端连接诊断工具")
    print("=" * 60)
    
    # 诊断配置文件
    host, port, timeout = diagnose_config()
    
    if not host or not port:
        print("❌ 无法获取服务器配置，诊断终止")
        return
    
    # 诊断网络连接
    network_ok = diagnose_network(host, port, timeout)
    
    # 测试客户端连接
    client_ok = test_client_connection(host, port)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 诊断总结")
    print("=" * 60)
    
    if network_ok and client_ok:
        print("✅ 所有测试通过，客户端应该能够正常连接")
    elif network_ok and not client_ok:
        print("⚠️ 网络连通正常，但客户端连接失败")
        print("💡 建议检查服务器是否正在运行Chat-Room服务")
    elif not network_ok:
        print("❌ 网络连接失败")
        print("💡 建议检查:")
        print("   - 服务器地址是否正确")
        print("   - 服务器端口是否正确")
        print("   - 防火墙设置")
        print("   - 网络连接")
    
    print("\n🔧 如需修改服务器配置，请编辑: config/client_config.yaml")


if __name__ == "__main__":
    main()
