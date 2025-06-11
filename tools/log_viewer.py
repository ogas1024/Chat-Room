#!/usr/bin/env python3
"""
Chat-Room 日志查看工具
提供简单的日志查看、搜索和分析功能
"""

import os
import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter


class LogViewer:
    """日志查看器"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        
    def list_log_files(self) -> List[Path]:
        """列出所有日志文件"""
        log_files = []
        if self.log_dir.exists():
            for file_path in self.log_dir.rglob("*.log"):
                log_files.append(file_path)
        return sorted(log_files)
    
    def read_log_file(self, file_path: Path, lines: int = None) -> List[Dict[str, Any]]:
        """读取日志文件"""
        entries = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        # 尝试解析loguru的JSON格式日志
                        entry = json.loads(line)

                        # 处理loguru的JSON格式
                        if 'record' in entry:
                            record = entry['record']
                            processed_entry = {
                                "timestamp": record.get('time', {}).get('repr', ''),
                                "level": record.get('level', {}).get('name', 'INFO'),
                                "module": record.get('name', ''),
                                "function": record.get('function', ''),
                                "line": record.get('line', 0),
                                "message": record.get('message', ''),
                            }

                            # 添加额外信息
                            if record.get('extra'):
                                processed_entry.update(record['extra'])

                            # 添加异常信息
                            if record.get('exception'):
                                processed_entry['exception'] = record['exception']

                            entries.append(processed_entry)
                        else:
                            # 标准JSON格式
                            entries.append(entry)

                    except json.JSONDecodeError:
                        # 如果不是JSON格式，作为普通文本处理
                        entries.append({
                            "timestamp": datetime.now().isoformat(),
                            "level": "INFO",
                            "message": line,
                            "raw": True
                        })

            # 如果指定了行数限制，返回最后N行
            if lines:
                entries = entries[-lines:]

        except Exception as e:
            print(f"读取日志文件失败: {e}")

        return entries
    
    def search_logs(self, pattern: str, file_pattern: str = "*.log", 
                   start_time: str = None, end_time: str = None,
                   level: str = None) -> List[Dict[str, Any]]:
        """搜索日志"""
        results = []
        
        # 编译搜索模式
        regex = re.compile(pattern, re.IGNORECASE)
        
        # 解析时间范围
        start_dt = None
        end_dt = None
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
            except ValueError:
                print(f"无效的开始时间格式: {start_time}")
                return results
                
        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time)
            except ValueError:
                print(f"无效的结束时间格式: {end_time}")
                return results
        
        # 搜索匹配的日志文件
        for file_path in self.log_dir.rglob(file_pattern):
            if not file_path.is_file():
                continue
                
            entries = self.read_log_file(file_path)
            for entry in entries:
                # 检查时间范围
                if start_dt or end_dt:
                    try:
                        timestamp_str = entry.get('timestamp', '')
                        # 处理不同的时间格式
                        if '+' in timestamp_str:
                            # 移除时区信息进行简单解析
                            timestamp_str = timestamp_str.split('+')[0]
                        entry_time = datetime.fromisoformat(timestamp_str)
                        if start_dt and entry_time < start_dt:
                            continue
                        if end_dt and entry_time > end_dt:
                            continue
                    except (ValueError, TypeError):
                        continue
                
                # 检查日志级别
                if level and entry.get('level', '').upper() != level.upper():
                    continue
                
                # 检查搜索模式
                message = entry.get('message', '')
                if regex.search(message) or regex.search(str(entry)):
                    entry['file'] = str(file_path)
                    results.append(entry)
        
        return results
    
    def analyze_logs(self, file_pattern: str = "*.log", 
                    hours: int = 24) -> Dict[str, Any]:
        """分析日志统计信息"""
        stats = {
            'total_entries': 0,
            'level_counts': Counter(),
            'module_counts': Counter(),
            'error_counts': Counter(),
            'user_actions': Counter(),
            'ai_operations': Counter(),
            'database_operations': Counter(),
            'network_events': Counter(),
            'time_range': {'start': None, 'end': None}
        }
        
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        for file_path in self.log_dir.rglob(file_pattern):
            if not file_path.is_file():
                continue
                
            entries = self.read_log_file(file_path)
            for entry in entries:
                # 检查时间范围
                try:
                    timestamp_str = entry.get('timestamp', '')
                    # 处理不同的时间格式
                    if '+' in timestamp_str:
                        # 移除时区信息进行简单解析
                        timestamp_str = timestamp_str.split('+')[0]
                    entry_time = datetime.fromisoformat(timestamp_str)
                    if entry_time < start_time:
                        continue
                except (ValueError, TypeError):
                    continue
                
                stats['total_entries'] += 1
                
                # 更新时间范围
                timestamp = entry.get('timestamp', '')
                if not stats['time_range']['start']:
                    stats['time_range']['start'] = timestamp
                if not stats['time_range']['end']:
                    stats['time_range']['end'] = timestamp

                try:
                    if stats['time_range']['start']:
                        start_time_obj = datetime.fromisoformat(stats['time_range']['start'].split('+')[0])
                        if entry_time < start_time_obj:
                            stats['time_range']['start'] = timestamp

                    if stats['time_range']['end']:
                        end_time_obj = datetime.fromisoformat(stats['time_range']['end'].split('+')[0])
                        if entry_time > end_time_obj:
                            stats['time_range']['end'] = timestamp
                except (ValueError, TypeError):
                    pass
                
                # 统计日志级别
                level = entry.get('level', 'UNKNOWN')
                stats['level_counts'][level] += 1
                
                # 统计模块
                module = entry.get('module', 'unknown')
                stats['module_counts'][module] += 1
                
                # 统计错误
                if level == 'ERROR':
                    error_msg = entry.get('message', '')
                    stats['error_counts'][error_msg] += 1
                
                # 统计用户操作
                if 'action' in entry:
                    action = entry.get('action')
                    stats['user_actions'][action] += 1
                
                # 统计AI操作
                if entry.get('ai'):
                    operation = entry.get('operation', 'unknown')
                    stats['ai_operations'][operation] += 1
                
                # 统计数据库操作
                if entry.get('database'):
                    operation = entry.get('operation', 'unknown')
                    table = entry.get('table', 'unknown')
                    stats['database_operations'][f"{operation}:{table}"] += 1
                
                # 统计网络事件
                if entry.get('network'):
                    event = entry.get('event', 'unknown')
                    stats['network_events'][event] += 1
        
        return stats
    
    def format_entry(self, entry: Dict[str, Any]) -> str:
        """格式化日志条目"""
        if entry.get('raw'):
            return entry.get('message', '')
        
        timestamp = entry.get('timestamp', '')
        level = entry.get('level', 'INFO')
        module = entry.get('module', '')
        message = entry.get('message', '')
        
        # 格式化时间戳
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            formatted_time = timestamp
        
        # 构建基础信息
        parts = [f"[{formatted_time}]", f"[{level}]"]
        if module:
            parts.append(f"[{module}]")
        parts.append(message)
        
        result = " ".join(parts)
        
        # 添加额外信息
        extra_info = []
        for key, value in entry.items():
            if key not in ['timestamp', 'level', 'module', 'message', 'raw', 'file']:
                extra_info.append(f"{key}={value}")
        
        if extra_info:
            result += f" | {', '.join(extra_info)}"
        
        return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Chat-Room 日志查看工具')
    parser.add_argument('--log-dir', default='logs', help='日志目录路径')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出日志文件
    list_parser = subparsers.add_parser('list', help='列出所有日志文件')
    
    # 查看日志
    view_parser = subparsers.add_parser('view', help='查看日志文件')
    view_parser.add_argument('file', help='日志文件路径')
    view_parser.add_argument('--lines', '-n', type=int, help='显示最后N行')
    
    # 搜索日志
    search_parser = subparsers.add_parser('search', help='搜索日志')
    search_parser.add_argument('pattern', help='搜索模式（正则表达式）')
    search_parser.add_argument('--file-pattern', default='*.log', help='文件模式')
    search_parser.add_argument('--start-time', help='开始时间 (ISO格式)')
    search_parser.add_argument('--end-time', help='结束时间 (ISO格式)')
    search_parser.add_argument('--level', help='日志级别过滤')
    
    # 分析日志
    analyze_parser = subparsers.add_parser('analyze', help='分析日志统计')
    analyze_parser.add_argument('--file-pattern', default='*.log', help='文件模式')
    analyze_parser.add_argument('--hours', type=int, default=24, help='分析最近N小时的日志')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    viewer = LogViewer(args.log_dir)
    
    if args.command == 'list':
        files = viewer.list_log_files()
        if files:
            print("可用的日志文件:")
            for file_path in files:
                print(f"  {file_path}")
        else:
            print("未找到日志文件")
    
    elif args.command == 'view':
        file_path = Path(args.file)
        if not file_path.exists():
            file_path = viewer.log_dir / args.file
        
        if not file_path.exists():
            print(f"日志文件不存在: {args.file}")
            return
        
        entries = viewer.read_log_file(file_path, args.lines)
        for entry in entries:
            print(viewer.format_entry(entry))
    
    elif args.command == 'search':
        results = viewer.search_logs(
            args.pattern, args.file_pattern,
            args.start_time, args.end_time, args.level
        )
        
        if results:
            print(f"找到 {len(results)} 条匹配的日志:")
            for entry in results:
                print(viewer.format_entry(entry))
        else:
            print("未找到匹配的日志")
    
    elif args.command == 'analyze':
        stats = viewer.analyze_logs(args.file_pattern, args.hours)
        
        print(f"日志分析报告 (最近 {args.hours} 小时)")
        print("=" * 50)
        print(f"总日志条数: {stats['total_entries']}")
        print(f"时间范围: {stats['time_range']['start']} ~ {stats['time_range']['end']}")
        
        print("\n日志级别分布:")
        for level, count in stats['level_counts'].most_common():
            print(f"  {level}: {count}")
        
        print("\n模块分布:")
        for module, count in stats['module_counts'].most_common(10):
            print(f"  {module}: {count}")
        
        if stats['error_counts']:
            print("\n错误统计:")
            for error, count in stats['error_counts'].most_common(5):
                print(f"  {error[:50]}...: {count}")
        
        if stats['user_actions']:
            print("\n用户操作统计:")
            for action, count in stats['user_actions'].most_common(10):
                print(f"  {action}: {count}")
        
        if stats['ai_operations']:
            print("\nAI操作统计:")
            for operation, count in stats['ai_operations'].most_common():
                print(f"  {operation}: {count}")


if __name__ == '__main__':
    main()
