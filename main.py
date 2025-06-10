#!/usr/bin/env python3
"""
Chat-Room 聊天室项目统一入口
提供服务器、客户端、演示等功能的统一启动接口
"""

import sys
import argparse
from pathlib import Path

# 确保项目根目录在Python路径中
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def run_server(args):
    """启动服务器"""
    try:
        from src.server.main import main as server_main
        
        # 设置服务器参数
        sys.argv = ['server']
        if args.host:
            sys.argv.extend(['--host', args.host])
        if args.port:
            sys.argv.extend(['--port', str(args.port)])
        if args.debug:
            sys.argv.append('--debug')
        
        server_main()
    except ImportError as e:
        print(f"❌ 服务器模块导入失败: {e}")
        sys.exit(1)


def run_client(args):
    """启动客户端"""
    try:
        from src.client.main import main as client_main
        
        # 设置客户端参数
        sys.argv = ['client']
        if args.host:
            sys.argv.extend(['--host', args.host])
        if args.port:
            sys.argv.extend(['--port', str(args.port)])
        if args.mode:
            sys.argv.extend(['--mode', args.mode])
        
        client_main()
    except ImportError as e:
        print(f"❌ 客户端模块导入失败: {e}")
        sys.exit(1)


def run_demo(args):
    """运行演示"""
    try:
        if args.demo_type == 'basic':
            from demo.demo import run_demo
            run_demo()
        elif args.demo_type == 'ai':
            from demo.demo_ai_features import main as ai_demo_main
            ai_demo_main()
        elif args.demo_type == 'todo':
            from demo.demo_todo_features import main as todo_demo_main
            todo_demo_main()
        else:
            print("❌ 未知的演示类型")
            sys.exit(1)
    except ImportError as e:
        print(f"❌ 演示模块导入失败: {e}")
        sys.exit(1)


def run_test(args):
    """运行测试"""
    try:
        import pytest
        
        test_args = []
        if args.test_type == 'unit':
            test_args.append('test/unit')
        elif args.test_type == 'integration':
            test_args.append('test/integration')
        elif args.test_type == 'all':
            test_args.append('test')
        else:
            test_args.append('test')
        
        if args.verbose:
            test_args.append('-v')
        if args.coverage:
            test_args.extend(['--cov=src', '--cov-report=html'])
        
        pytest.main(test_args)
    except ImportError:
        print("❌ pytest未安装，请运行: pip install pytest")
        sys.exit(1)


def setup_config(_args):
    """配置设置"""
    try:
        from config.examples.config_setup import main as config_main
        config_main()
    except ImportError as e:
        print(f"❌ 配置工具导入失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Chat-Room 聊天室项目统一入口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s server                    # 启动服务器
  %(prog)s client --mode tui         # 启动TUI客户端
  %(prog)s demo --type basic         # 运行基础演示
  %(prog)s test --type unit          # 运行单元测试
  %(prog)s config                    # 配置设置
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 服务器命令
    server_parser = subparsers.add_parser('server', help='启动服务器')
    server_parser.add_argument('--host', default='localhost', help='服务器地址')
    server_parser.add_argument('--port', type=int, default=8888, help='服务器端口')
    server_parser.add_argument('--debug', action='store_true', help='调试模式')
    
    # 客户端命令
    client_parser = subparsers.add_parser('client', help='启动客户端')
    client_parser.add_argument('--host', default='localhost', help='服务器地址')
    client_parser.add_argument('--port', type=int, default=8888, help='服务器端口')
    client_parser.add_argument('--mode', choices=['tui', 'simple'], default='tui', help='客户端模式')
    
    # 演示命令
    demo_parser = subparsers.add_parser('demo', help='运行演示')
    demo_parser.add_argument('--type', dest='demo_type', choices=['basic', 'ai', 'todo'], 
                           default='basic', help='演示类型')
    
    # 测试命令
    test_parser = subparsers.add_parser('test', help='运行测试')
    test_parser.add_argument('--type', dest='test_type', choices=['unit', 'integration', 'all'], 
                           default='all', help='测试类型')
    test_parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    test_parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    
    # 配置命令
    subparsers.add_parser('config', help='配置设置')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 Chat-Room 聊天室项目")
    print("=" * 50)
    
    try:
        if args.command == 'server':
            run_server(args)
        elif args.command == 'client':
            run_client(args)
        elif args.command == 'demo':
            run_demo(args)
        elif args.command == 'test':
            run_test(args)
        elif args.command == 'config':
            setup_config(args)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
