#!/usr/bin/env python3
"""
修复现有数据库中的AI用户配置
为现有数据库添加AI用户并确保其在所有聊天组中
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.database.connection import get_db
from shared.constants import AI_USER_ID, AI_USERNAME


def fix_ai_user_in_database():
    """修复数据库中的AI用户配置"""
    print("🔧 修复数据库中的AI用户配置...")
    
    try:
        db = get_db()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查AI用户是否已存在
            cursor.execute("SELECT id FROM users WHERE id = ?", (AI_USER_ID,))
            ai_user_exists = cursor.fetchone() is not None
            
            if not ai_user_exists:
                print(f"📝 创建AI用户: {AI_USERNAME}")
                # 创建AI用户
                cursor.execute(
                    "INSERT INTO users (id, username, password_hash, is_online) VALUES (?, ?, ?, ?)",
                    (AI_USER_ID, AI_USERNAME, "ai_user_no_password", 1)
                )
            else:
                print(f"✅ AI用户已存在: {AI_USERNAME}")
            
            # 获取所有聊天组
            cursor.execute("SELECT id, name FROM chat_groups")
            chat_groups = cursor.fetchall()
            
            print(f"📋 检查 {len(chat_groups)} 个聊天组...")
            
            added_count = 0
            for group in chat_groups:
                group_id, group_name = group[0], group[1]
                
                # 检查AI用户是否在该聊天组中
                cursor.execute(
                    "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
                    (group_id, AI_USER_ID)
                )
                
                if not cursor.fetchone():
                    # AI用户不在该聊天组中，添加它
                    cursor.execute(
                        "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
                        (group_id, AI_USER_ID)
                    )
                    print(f"  ➕ 将AI用户添加到聊天组: {group_name}")
                    added_count += 1
                else:
                    print(f"  ✅ AI用户已在聊天组中: {group_name}")
            
            conn.commit()
            
            print(f"🎉 修复完成！AI用户已添加到 {added_count} 个聊天组")
            
            # 验证修复结果
            cursor.execute(
                "SELECT COUNT(*) FROM group_members WHERE user_id = ?",
                (AI_USER_ID,)
            )
            total_groups = cursor.fetchone()[0]
            print(f"📊 AI用户现在是 {total_groups} 个聊天组的成员")
            
            return True
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 Chat-Room AI用户数据库修复工具")
    print("=" * 60)
    
    if fix_ai_user_in_database():
        print("\n✅ 数据库修复成功！")
        print("💡 现在可以重启服务器测试AI功能")
    else:
        print("\n❌ 数据库修复失败！")
        print("💡 请检查错误信息并重试")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
