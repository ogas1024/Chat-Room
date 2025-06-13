#!/usr/bin/env python3
"""
最小化测试
"""

print("开始测试...")

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("路径设置完成")

try:
    print("开始导入...")
    from shared.constants import DEFAULT_HOST, DEFAULT_PORT
    print("常量导入成功")
    
    from client.core.client import ChatClient
    print("客户端导入成功")
    
    print("测试完成")
    
except Exception as e:
    print(f"导入异常: {e}")
    import traceback
    traceback.print_exc()

print("脚本结束")
