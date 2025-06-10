#!/usr/bin/env python3
"""
Chat-Room UI启动脚本
解决模块导入路径问题
"""

import sys
import os

# 确保项目根目录在Python路径中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """启动聊天室UI应用"""
    try:
        from client.ui.app import run_chat_app
        from shared.constants import DEFAULT_HOST, DEFAULT_PORT
        
        print("正在启动Chat-Room聊天室...")
        print(f"连接服务器: {DEFAULT_HOST}:{DEFAULT_PORT}")
        print("按 Ctrl+C 退出应用")
        print("-" * 50)
        
        # 启动应用
        run_chat_app()
        
    except KeyboardInterrupt:
        print("\n应用已退出")
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有依赖已正确安装: pip install -r requirements.txt")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()
