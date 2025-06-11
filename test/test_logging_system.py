#!/usr/bin/env python3
"""
日志系统测试脚本
验证日志系统的各项功能
"""

import os
import sys
import time
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.logger import (
    init_logger, get_logger, log_user_action, log_database_operation,
    log_ai_operation, log_security_event, log_network_event, 
    log_performance, log_function_call, log_performance_decorator
)


def test_basic_logging():
    """测试基础日志功能"""
    print("🧪 测试基础日志功能...")
    
    # 初始化日志系统
    logging_config = {
        'level': 'DEBUG',
        'file_enabled': True,
        'console_enabled': True,
        'file_max_size': 1048576,  # 1MB
        'file_backup_count': 3
    }
    
    init_logger(logging_config, "test")
    logger = get_logger("test.basic")
    
    # 测试不同级别的日志
    logger.debug("这是一条调试信息")
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    print("✅ 基础日志功能测试完成")


def test_structured_logging():
    """测试结构化日志"""
    print("🧪 测试结构化日志...")
    
    logger = get_logger("test.structured")
    
    # 测试带额外字段的日志
    logger.info("用户操作", 
               user_id=123, 
               username="test_user", 
               action="login",
               client_ip="127.0.0.1")
    
    logger.error("数据库错误",
                database="chatroom.db",
                table="users",
                operation="select",
                error_code=1001)
    
    print("✅ 结构化日志测试完成")


def test_specialized_logging():
    """测试专用日志函数"""
    print("🧪 测试专用日志函数...")
    
    # 测试用户操作日志
    log_user_action(123, "alice", "send_message", 
                   chat_group_id=1, message_length=50)
    
    # 测试数据库操作日志
    log_database_operation("insert", "messages", 
                         message_id=456, user_id=123)
    
    # 测试AI操作日志
    log_ai_operation("generate_reply", "glm-4-flash",
                    user_id=123, response_time=1.5, tokens=100)
    
    # 测试安全事件日志
    log_security_event("login_attempt", 
                      username="alice", client_ip="127.0.0.1", success=True)
    
    # 测试网络事件日志
    log_network_event("client_connected", 
                     client_ip="127.0.0.1", client_port=12345)
    
    # 测试性能日志
    log_performance("database_query", 0.05, 
                   query="SELECT * FROM users", rows=10)
    
    print("✅ 专用日志函数测试完成")


@log_function_call(event_type="test_function", log_args=True, log_result=True)
def test_function_with_logging(param1, param2="default"):
    """测试带日志装饰器的函数"""
    time.sleep(0.1)  # 模拟处理时间
    return f"处理结果: {param1} + {param2}"


@log_performance_decorator("test_performance")
def test_performance_function():
    """测试性能监控装饰器的函数"""
    time.sleep(0.2)  # 模拟处理时间
    return "性能测试完成"


def test_decorators():
    """测试日志装饰器"""
    print("🧪 测试日志装饰器...")
    
    # 测试函数调用日志装饰器
    result = test_function_with_logging("test_value", param2="custom")
    print(f"函数返回结果: {result}")
    
    # 测试性能监控装饰器
    result = test_performance_function()
    print(f"性能测试结果: {result}")
    
    print("✅ 日志装饰器测试完成")


def test_sensitive_data_sanitization():
    """测试敏感信息脱敏"""
    print("🧪 测试敏感信息脱敏...")
    
    logger = get_logger("test.security")
    
    # 测试包含敏感信息的日志
    logger.info("用户注册", 
               username="test_user",
               password="secret123",  # 应该被脱敏
               api_key="sk-1234567890abcdef",  # 应该被脱敏
               email="test@example.com")
    
    logger.warning("配置更新",
                  config={
                      "database_url": "sqlite:///test.db",
                      "secret_key": "super_secret_key",  # 应该被脱敏
                      "api_token": "token_12345"  # 应该被脱敏
                  })
    
    print("✅ 敏感信息脱敏测试完成")


def test_exception_logging():
    """测试异常日志记录"""
    print("🧪 测试异常日志记录...")
    
    logger = get_logger("test.exception")
    
    try:
        # 故意触发异常
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error("除零错误", 
                    operation="division",
                    dividend=1,
                    divisor=0,
                    exc_info=True)
    
    try:
        # 另一个异常示例
        data = {"key": "value"}
        value = data["nonexistent_key"]
    except KeyError as e:
        logger.error("键不存在错误",
                    data_keys=list(data.keys()),
                    requested_key="nonexistent_key",
                    exc_info=True)
    
    print("✅ 异常日志记录测试完成")


def test_log_file_creation():
    """测试日志文件创建"""
    print("🧪 测试日志文件创建...")
    
    log_dir = Path("logs/test")
    
    # 检查日志文件是否创建
    expected_files = [
        "test.log",
        "test_error.log",
        "test_database.log",
        "test_ai.log",
        "test_security.log"
    ]
    
    created_files = []
    for file_name in expected_files:
        file_path = log_dir / file_name
        if file_path.exists():
            created_files.append(file_name)
            print(f"  ✅ {file_name} 已创建")
        else:
            print(f"  ❌ {file_name} 未创建")
    
    print(f"✅ 日志文件创建测试完成 ({len(created_files)}/{len(expected_files)} 文件已创建)")


def test_log_content_validation():
    """测试日志内容验证"""
    print("🧪 测试日志内容验证...")
    
    log_file = Path("logs/test/test.log")
    
    if not log_file.exists():
        print("❌ 主日志文件不存在，跳过内容验证")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        json_lines = 0
        valid_json_lines = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            json_lines += 1
            try:
                data = json.loads(line)
                # 验证必需字段
                required_fields = ['timestamp', 'level', 'message']
                if all(field in data for field in required_fields):
                    valid_json_lines += 1
            except json.JSONDecodeError:
                pass
        
        print(f"  总日志行数: {json_lines}")
        print(f"  有效JSON行数: {valid_json_lines}")
        print(f"  有效率: {valid_json_lines/json_lines*100:.1f}%" if json_lines > 0 else "  有效率: 0%")
        
        if valid_json_lines > 0:
            print("✅ 日志内容验证通过")
        else:
            print("❌ 日志内容验证失败")
            
    except Exception as e:
        print(f"❌ 日志内容验证出错: {e}")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始日志系统测试")
    print("=" * 50)
    
    try:
        test_basic_logging()
        print()
        
        test_structured_logging()
        print()
        
        test_specialized_logging()
        print()
        
        test_decorators()
        print()
        
        test_sensitive_data_sanitization()
        print()
        
        test_exception_logging()
        print()
        
        # 等待一下让日志写入完成
        time.sleep(1)
        
        test_log_file_creation()
        print()
        
        test_log_content_validation()
        print()
        
        print("=" * 50)
        print("🎉 所有测试完成！")
        print()
        print("📁 日志文件位置: logs/test/")
        print("🔍 使用以下命令查看日志:")
        print("   python tools/log_viewer.py list")
        print("   python tools/log_viewer.py view test/test.log")
        print("   python tools/log_viewer.py analyze --file-pattern 'test/*.log'")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
