#!/usr/bin/env python3
"""
Chat-Room 服务器状态检查工具
检查服务器是否正在运行，以及端口监听状态
"""

import socket
import subprocess
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_port_listening(host: str, port: int) -> tuple[bool, str]:
    """检查端口是否在监听"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, f"端口 {port} 正在监听"
        else:
            return False, f"端口 {port} 未监听 (错误代码: {result})"
    except Exception as e:
        return False, f"检查端口时出错: {e}"


def check_process_listening(port: int) -> tuple[bool, str]:
    """检查是否有进程在监听指定端口"""
    try:
        # 使用netstat检查端口
        result = subprocess.run(
            ["netstat", "-tlnp"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if f":{port} " in line and "LISTEN" in line:
                    return True, f"发现进程监听端口 {port}: {line.strip()}"
            
            return False, f"没有进程监听端口 {port}"
        else:
            return False, f"netstat命令失败: {result.stderr}"
            
    except FileNotFoundError:
        # 尝试使用ss命令
        try:
            result = subprocess.run(
                ["ss", "-tlnp"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if f":{port} " in line and "LISTEN" in line:
                        return True, f"发现进程监听端口 {port}: {line.strip()}"
                
                return False, f"没有进程监听端口 {port}"
            else:
                return False, f"ss命令失败: {result.stderr}"
                
        except FileNotFoundError:
            return False, "netstat和ss命令都不可用"
    except Exception as e:
        return False, f"检查进程时出错: {e}"


def start_server_suggestion():
    """提供启动服务器的建议"""
    print("\n💡 启动服务器的方法:")
    print("1. 在服务器上运行:")
    print("   conda activate chatroom")
    print("   python -m server.main")
    print()
    print("2. 或者使用后台运行:")
    print("   nohup python -m server.main > server.log 2>&1 &")
    print()
    print("3. 检查服务器配置文件:")
    print("   config/server_config.yaml")
    print("   确保 host: 0.0.0.0 (允许外部连接)")
    print("   确保 port: 8888")


def main():
    """主函数"""
    print("🔍 Chat-Room 服务器状态检查")
    print("=" * 50)
    
    # 从配置文件获取服务器信息
    try:
        from server.config.server_config import get_server_config
        server_config = get_server_config()
        host = server_config.get_server_host()
        port = server_config.get_server_port()
        
        print(f"📋 服务器配置:")
        print(f"   地址: {host}")
        print(f"   端口: {port}")
        
    except Exception as e:
        print(f"❌ 无法读取服务器配置: {e}")
        print("使用默认值进行检查...")
        host = "localhost"
        port = 8888
    
    print(f"\n🔍 检查服务器状态 ({host}:{port})")
    print("-" * 30)
    
    # 检查本地端口监听
    local_listening, local_msg = check_port_listening("localhost", port)
    if local_listening:
        print(f"✅ 本地连接: {local_msg}")
    else:
        print(f"❌ 本地连接: {local_msg}")
    
    # 检查外部端口监听（如果host不是localhost）
    if host != "localhost" and host != "127.0.0.1":
        external_listening, external_msg = check_port_listening(host, port)
        if external_listening:
            print(f"✅ 外部连接: {external_msg}")
        else:
            print(f"❌ 外部连接: {external_msg}")
    
    # 检查进程监听状态
    process_listening, process_msg = check_process_listening(port)
    if process_listening:
        print(f"✅ 进程状态: {process_msg}")
    else:
        print(f"❌ 进程状态: {process_msg}")
    
    # 总结和建议
    print("\n📊 检查结果:")
    if local_listening or process_listening:
        print("✅ 服务器似乎正在运行")
        if host == "localhost" or host == "127.0.0.1":
            print("⚠️ 注意: 服务器配置为只接受本地连接")
            print("💡 如需外部访问，请修改 config/server_config.yaml 中的 host 为 0.0.0.0")
    else:
        print("❌ 服务器未运行")
        start_server_suggestion()
    
    # 如果是远程服务器，提供额外的检查建议
    print("\n🔧 远程服务器部署检查清单:")
    print("□ 服务器程序是否正在运行")
    print("□ 服务器配置 host: 0.0.0.0")
    print("□ 防火墙是否开放端口 8888")
    print("□ 云服务器安全组是否开放端口 8888")
    print("□ 服务器是否有足够的资源运行程序")


if __name__ == "__main__":
    main()
