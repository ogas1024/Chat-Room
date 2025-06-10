"""
聊天室服务器主程序
启动聊天室服务器的入口文件
"""

import sys
import signal
import argparse
from typing import Optional

from server.core.server import ChatRoomServer
from shared.constants import DEFAULT_HOST, DEFAULT_PORT


def signal_handler(signum, frame):
    """信号处理器，用于优雅关闭服务器"""
    print("\n收到关闭信号，正在关闭服务器...")
    if hasattr(signal_handler, 'server'):
        signal_handler.server.stop()
    sys.exit(0)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='聊天室服务器')
    parser.add_argument(
        '--host', 
        default=DEFAULT_HOST,
        help=f'服务器监听地址 (默认: {DEFAULT_HOST})'
    )
    parser.add_argument(
        '--port', 
        type=int,
        default=DEFAULT_PORT,
        help=f'服务器监听端口 (默认: {DEFAULT_PORT})'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    args = parser.parse_args()
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 创建并启动服务器
        server = ChatRoomServer(args.host, args.port)
        signal_handler.server = server  # 保存服务器实例用于信号处理
        
        print("=" * 50)
        print("🚀 聊天室服务器")
        print("=" * 50)
        print(f"监听地址: {args.host}")
        print(f"监听端口: {args.port}")
        print(f"调试模式: {'开启' if args.debug else '关闭'}")
        print("=" * 50)
        print("按 Ctrl+C 停止服务器")
        print("=" * 50)
        
        # 启动服务器
        server.start()
        
    except KeyboardInterrupt:
        print("\n用户中断，正在关闭服务器...")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
