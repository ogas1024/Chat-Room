#!/usr/bin/env python3
"""
Chat-Room 学习文档系统演示脚本

这个脚本演示如何使用学习文档系统进行渐进式学习。
它会引导用户完成学习路径，跟踪进度，并提供交互式学习体验。

使用方法：
    python docs/learning-v02/demo/learning-demo.py

功能：
1. 显示学习路径和进度
2. 提供章节导航
3. 检查学习前置条件
4. 记录学习进度
5. 生成学习报告
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class LearningProgress:
    """学习进度管理器"""
    
    def __init__(self, progress_file: str = "learning_progress.json"):
        """
        初始化学习进度管理器
        
        Args:
            progress_file: 进度文件路径
        """
        self.progress_file = Path(__file__).parent / progress_file
        self.progress_data = self.load_progress()
    
    def load_progress(self) -> Dict:
        """加载学习进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载进度文件失败: {e}")
        
        # 返回默认进度结构
        return {
            "start_date": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "completed_chapters": [],
            "current_chapter": "00-preparation",
            "total_study_time": 0,  # 分钟
            "notes": {},
            "milestones": []
        }
    
    def save_progress(self):
        """保存学习进度"""
        self.progress_data["last_update"] = datetime.now().isoformat()
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
            print("✅ 学习进度已保存")
        except Exception as e:
            print(f"❌ 保存进度失败: {e}")
    
    def mark_chapter_complete(self, chapter: str):
        """标记章节完成"""
        if chapter not in self.progress_data["completed_chapters"]:
            self.progress_data["completed_chapters"].append(chapter)
            self.progress_data["milestones"].append({
                "chapter": chapter,
                "completed_at": datetime.now().isoformat(),
                "type": "chapter_complete"
            })
            print(f"🎉 恭喜完成章节: {chapter}")
    
    def add_study_time(self, minutes: int):
        """添加学习时间"""
        self.progress_data["total_study_time"] += minutes
    
    def add_note(self, chapter: str, note: str):
        """添加学习笔记"""
        if chapter not in self.progress_data["notes"]:
            self.progress_data["notes"][chapter] = []
        self.progress_data["notes"][chapter].append({
            "content": note,
            "timestamp": datetime.now().isoformat()
        })

class LearningGuide:
    """学习指导系统"""
    
    def __init__(self):
        """初始化学习指导系统"""
        self.docs_root = Path(__file__).parent.parent
        self.progress = LearningProgress()
        self.chapters = self.load_chapter_structure()
    
    def load_chapter_structure(self) -> Dict:
        """加载章节结构"""
        return {
            "00-preparation": {
                "name": "准备工作",
                "files": [
                    "environment-setup.md",
                    "project-overview.md", 
                    "learning-guide.md"
                ],
                "estimated_days": 3,
                "difficulty": "⭐",
                "prerequisites": []
            },
            "01-python-basics": {
                "name": "Python基础",
                "files": [
                    "syntax-fundamentals.md",
                    "data-structures.md",
                    "functions-modules.md",
                    "oop-basics.md"
                ],
                "estimated_days": 10,
                "difficulty": "⭐⭐",
                "prerequisites": ["00-preparation"]
            },
            "02-socket-programming": {
                "name": "Socket网络编程",
                "files": [
                    "network-concepts.md",
                    "tcp-basics.md",
                    "socket-api.md",
                    "simple-client-server.md"
                ],
                "estimated_days": 10,
                "difficulty": "⭐⭐⭐",
                "prerequisites": ["01-python-basics"]
            },
            "03-simple-chat": {
                "name": "简单聊天室",
                "files": [
                    "protocol-design.md",
                    "message-handling.md",
                    "threading-basics.md",
                    "error-handling.md"
                ],
                "estimated_days": 7,
                "difficulty": "⭐⭐⭐",
                "prerequisites": ["02-socket-programming"]
            }
            # 可以继续添加更多章节...
        }
    
    def show_welcome(self):
        """显示欢迎信息"""
        print("=" * 60)
        print("🎓 欢迎使用 Chat-Room 学习文档系统！")
        print("=" * 60)
        print()
        print("这是一个渐进式学习系统，将引导您从零基础到高级开发。")
        print("通过Chat-Room项目，您将学习：")
        print("• Python编程基础和高级特性")
        print("• Socket网络编程")
        print("• 数据库设计和操作")
        print("• 用户界面开发")
        print("• AI集成和系统优化")
        print()
    
    def show_progress_overview(self):
        """显示学习进度概览"""
        print("📊 学习进度概览")
        print("-" * 40)
        
        total_chapters = len(self.chapters)
        completed_chapters = len(self.progress.progress_data["completed_chapters"])
        completion_rate = (completed_chapters / total_chapters) * 100
        
        print(f"总章节数: {total_chapters}")
        print(f"已完成: {completed_chapters}")
        print(f"完成率: {completion_rate:.1f}%")
        print(f"总学习时间: {self.progress.progress_data['total_study_time']} 分钟")
        
        # 显示进度条
        bar_length = 30
        filled_length = int(bar_length * completion_rate / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"进度: [{bar}] {completion_rate:.1f}%")
        print()
    
    def show_chapter_list(self):
        """显示章节列表"""
        print("📚 学习章节")
        print("-" * 40)
        
        for chapter_id, chapter_info in self.chapters.items():
            status = "✅" if chapter_id in self.progress.progress_data["completed_chapters"] else "📝"
            current = "👉" if chapter_id == self.progress.progress_data["current_chapter"] else "  "
            
            print(f"{current} {status} {chapter_info['name']} ({chapter_info['difficulty']})")
            print(f"     预计时间: {chapter_info['estimated_days']} 天")
            
            # 检查前置条件
            if chapter_info["prerequisites"]:
                missing_prereqs = [
                    prereq for prereq in chapter_info["prerequisites"]
                    if prereq not in self.progress.progress_data["completed_chapters"]
                ]
                if missing_prereqs:
                    print(f"     ⚠️  需要先完成: {', '.join(missing_prereqs)}")
            print()
    
    def check_prerequisites(self, chapter_id: str) -> bool:
        """检查章节前置条件"""
        chapter_info = self.chapters.get(chapter_id)
        if not chapter_info:
            return False
        
        for prereq in chapter_info["prerequisites"]:
            if prereq not in self.progress.progress_data["completed_chapters"]:
                print(f"❌ 需要先完成章节: {prereq}")
                return False
        
        return True
    
    def start_chapter(self, chapter_id: str):
        """开始学习章节"""
        if chapter_id not in self.chapters:
            print(f"❌ 章节不存在: {chapter_id}")
            return
        
        if not self.check_prerequisites(chapter_id):
            return
        
        chapter_info = self.chapters[chapter_id]
        print(f"🚀 开始学习: {chapter_info['name']}")
        print(f"难度: {chapter_info['difficulty']}")
        print(f"预计时间: {chapter_info['estimated_days']} 天")
        print()
        
        # 显示章节文件
        print("📄 章节文件:")
        chapter_dir = self.docs_root / chapter_id
        
        for i, filename in enumerate(chapter_info["files"], 1):
            file_path = chapter_dir / filename
            status = "✅" if file_path.exists() else "📝"
            print(f"  {i}. {status} {filename}")
            
            if file_path.exists():
                print(f"     路径: {file_path}")
            else:
                print(f"     状态: 待创建")
        
        print()
        self.progress.progress_data["current_chapter"] = chapter_id
    
    def complete_chapter(self, chapter_id: str):
        """完成章节学习"""
        if chapter_id not in self.chapters:
            print(f"❌ 章节不存在: {chapter_id}")
            return
        
        # 简单的完成确认
        chapter_info = self.chapters[chapter_id]
        print(f"完成章节: {chapter_info['name']}")
        
        # 学习检查
        print("\n📋 学习检查清单:")
        checklist = [
            "理解了核心概念",
            "能够解释实现原理", 
            "成功运行了代码示例",
            "完成了练习题目",
            "能够独立实现类似功能"
        ]
        
        for item in checklist:
            confirm = input(f"✓ {item} (y/n): ").lower().strip()
            if confirm != 'y':
                print("建议继续复习相关内容")
                return
        
        # 标记完成
        self.progress.mark_chapter_complete(chapter_id)
        
        # 添加学习时间（估算）
        estimated_hours = chapter_info["estimated_days"] * 2.5  # 每天2.5小时
        self.progress.add_study_time(int(estimated_hours * 60))
        
        # 建议下一步
        self.suggest_next_chapter(chapter_id)
    
    def suggest_next_chapter(self, current_chapter: str):
        """建议下一个学习章节"""
        chapter_list = list(self.chapters.keys())
        try:
            current_index = chapter_list.index(current_chapter)
            if current_index + 1 < len(chapter_list):
                next_chapter = chapter_list[current_index + 1]
                next_info = self.chapters[next_chapter]
                print(f"\n💡 建议下一步学习: {next_info['name']}")
                print(f"   章节ID: {next_chapter}")
                print(f"   难度: {next_info['difficulty']}")
        except ValueError:
            pass
    
    def add_learning_note(self):
        """添加学习笔记"""
        current_chapter = self.progress.progress_data["current_chapter"]
        print(f"📝 为章节 {current_chapter} 添加学习笔记:")
        note = input("请输入笔记内容: ").strip()
        
        if note:
            self.progress.add_note(current_chapter, note)
            print("✅ 笔记已添加")
    
    def show_learning_notes(self):
        """显示学习笔记"""
        notes = self.progress.progress_data["notes"]
        if not notes:
            print("📝 暂无学习笔记")
            return
        
        print("📝 学习笔记")
        print("-" * 40)
        
        for chapter, chapter_notes in notes.items():
            chapter_name = self.chapters.get(chapter, {}).get("name", chapter)
            print(f"\n📚 {chapter_name}:")
            
            for note in chapter_notes:
                timestamp = note["timestamp"][:19]  # 只显示日期时间
                print(f"  • {note['content']}")
                print(f"    时间: {timestamp}")
    
    def generate_learning_report(self):
        """生成学习报告"""
        print("📊 学习报告")
        print("=" * 50)
        
        # 基本统计
        start_date = self.progress.progress_data["start_date"][:10]
        total_time_hours = self.progress.progress_data["total_study_time"] / 60
        completed_count = len(self.progress.progress_data["completed_chapters"])
        total_count = len(self.chapters)
        
        print(f"开始学习时间: {start_date}")
        print(f"总学习时间: {total_time_hours:.1f} 小时")
        print(f"完成章节: {completed_count}/{total_count}")
        print(f"完成率: {(completed_count/total_count)*100:.1f}%")
        
        # 里程碑
        milestones = self.progress.progress_data["milestones"]
        if milestones:
            print(f"\n🏆 学习里程碑 ({len(milestones)} 个):")
            for milestone in milestones[-5:]:  # 显示最近5个
                date = milestone["completed_at"][:10]
                chapter_name = self.chapters.get(milestone["chapter"], {}).get("name", milestone["chapter"])
                print(f"  • {date}: 完成 {chapter_name}")
        
        # 学习建议
        print(f"\n💡 学习建议:")
        if completed_count == 0:
            print("  • 建议从准备工作开始，搭建开发环境")
        elif completed_count < total_count * 0.3:
            print("  • 继续保持学习节奏，重点掌握基础知识")
        elif completed_count < total_count * 0.7:
            print("  • 已完成基础学习，可以开始实践项目")
        else:
            print("  • 接近完成，建议总结和实践应用")
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n" + "=" * 50)
            print("🎓 Chat-Room 学习系统")
            print("=" * 50)
            print("1. 查看学习进度")
            print("2. 显示章节列表")
            print("3. 开始学习章节")
            print("4. 完成章节")
            print("5. 添加学习笔记")
            print("6. 查看学习笔记")
            print("7. 生成学习报告")
            print("8. 保存并退出")
            print("-" * 50)
            
            choice = input("请选择操作 (1-8): ").strip()
            
            if choice == "1":
                self.show_progress_overview()
            elif choice == "2":
                self.show_chapter_list()
            elif choice == "3":
                chapter_id = input("请输入章节ID (如 01-python-basics): ").strip()
                self.start_chapter(chapter_id)
            elif choice == "4":
                chapter_id = input("请输入要完成的章节ID: ").strip()
                self.complete_chapter(chapter_id)
            elif choice == "5":
                self.add_learning_note()
            elif choice == "6":
                self.show_learning_notes()
            elif choice == "7":
                self.generate_learning_report()
            elif choice == "8":
                self.progress.save_progress()
                print("👋 感谢使用学习系统，继续加油！")
                break
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")

def main():
    """主函数"""
    try:
        guide = LearningGuide()
        guide.show_welcome()
        guide.interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
