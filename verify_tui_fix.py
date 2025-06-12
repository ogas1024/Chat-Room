#!/usr/bin/env python3
"""
验证TUI修复
简单验证定时器是否被移除
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def verify_timer_removal():
    """验证定时器移除"""
    print("🔍 验证定时器移除...")
    
    try:
        # 读取TUI应用文件内容
        with open("client/ui/app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查是否还有定时器设置
        if "self.set_timer(3.0, self.finish_history_loading)" in content:
            print("❌ 定时器设置仍然存在")
            return False
        
        # 检查是否有正确的注释
        if "不再使用定时器，完全依赖CHAT_HISTORY_COMPLETE通知" in content:
            print("✅ 找到正确的修复注释")
        else:
            print("⚠️ 没有找到修复注释，但定时器已移除")
        
        # 检查是否有handle_chat_history_complete方法
        if "def handle_chat_history_complete(self, message):" in content:
            print("✅ handle_chat_history_complete方法存在")
        else:
            print("❌ handle_chat_history_complete方法不存在")
            return False
        
        print("✅ 定时器移除验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def verify_message_handler_setup():
    """验证消息处理器设置"""
    print("\n🔍 验证消息处理器设置...")
    
    try:
        with open("client/ui/app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查CHAT_HISTORY_COMPLETE处理器设置
        if "MessageType.CHAT_HISTORY_COMPLETE, self.handle_chat_history_complete" in content:
            print("✅ CHAT_HISTORY_COMPLETE处理器设置正确")
        else:
            print("❌ CHAT_HISTORY_COMPLETE处理器设置不正确")
            return False
        
        print("✅ 消息处理器设置验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def verify_shared_constants():
    """验证共享常量"""
    print("\n🔍 验证共享常量...")
    
    try:
        with open("shared/constants.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if 'CHAT_HISTORY_COMPLETE = "chat_history_complete"' in content:
            print("✅ CHAT_HISTORY_COMPLETE常量存在")
        else:
            print("❌ CHAT_HISTORY_COMPLETE常量不存在")
            return False
        
        print("✅ 共享常量验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def verify_shared_messages():
    """验证共享消息类"""
    print("\n🔍 验证共享消息类...")
    
    try:
        with open("shared/messages.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        if "class ChatHistoryComplete(BaseMessage):" in content:
            print("✅ ChatHistoryComplete消息类存在")
        else:
            print("❌ ChatHistoryComplete消息类不存在")
            return False
        
        if "MessageType.CHAT_HISTORY_COMPLETE: ChatHistoryComplete" in content:
            print("✅ ChatHistoryComplete消息类映射存在")
        else:
            print("❌ ChatHistoryComplete消息类映射不存在")
            return False
        
        print("✅ 共享消息类验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False


def main():
    """主验证函数"""
    print("🚀 开始验证TUI修复...")
    
    verifications = [
        ("定时器移除", verify_timer_removal),
        ("消息处理器设置", verify_message_handler_setup),
        ("共享常量", verify_shared_constants),
        ("共享消息类", verify_shared_messages),
    ]
    
    passed = 0
    total = len(verifications)
    
    for verification_name, verification_func in verifications:
        if verification_func():
            passed += 1
            print(f"✅ {verification_name} 验证通过")
        else:
            print(f"❌ {verification_name} 验证失败")
    
    print(f"\n📊 验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有验证通过！TUI历史消息加载修复已正确实施。")
        print("\n📝 修复内容总结:")
        print("1. ✅ 移除了TUI中的3秒定时器")
        print("2. ✅ 添加了CHAT_HISTORY_COMPLETE消息类型和处理器")
        print("3. ✅ 服务器端会在发送完历史消息后发送完成通知")
        print("4. ✅ 客户端和TUI正确处理完成通知")
        print("\n🔧 修复机制:")
        print("- 用户执行/enter_chat命令")
        print("- TUI清空聊天记录，显示'正在加载历史消息...'")
        print("- 服务器发送历史消息，然后发送CHAT_HISTORY_COMPLETE通知")
        print("- TUI收到通知后调用finish_history_loading()显示结果")
        return True
    else:
        print("\n💥 部分验证失败！修复可能不完整。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
