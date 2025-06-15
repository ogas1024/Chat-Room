#!/usr/bin/env python3
"""
测试命令解析功能
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from client.commands.parser import CommandParser

def test_command_parsing():
    """测试命令解析功能"""
    parser = CommandParser()
    
    # 测试用例
    test_cases = [
        "/recv_files -l",
        "/recv_files -n 7",
        "/recv_files -n 123",
        "/recv_files -a",
        "/send_files test.txt",
        "/send_files file1.txt file2.txt",
    ]
    
    print("命令解析测试:")
    print("=" * 50)
    
    for test_input in test_cases:
        print(f"\n输入: {test_input}")
        command = parser.parse_command(test_input)
        
        if command:
            print(f"  命令名: {command.name}")
            print(f"  参数: {command.args}")
            print(f"  选项: {command.options}")
        else:
            print("  解析失败")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_command_parsing()
