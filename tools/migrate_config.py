#!/usr/bin/env python3
"""
配置迁移工具
帮助用户从环境变量配置迁移到配置文件
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def detect_environment_config() -> Dict[str, Any]:
    """检测环境变量中的配置"""
    env_config = {}
    
    # 检测智谱AI API密钥
    zhipu_key = os.getenv('ZHIPU_API_KEY')
    if zhipu_key:
        env_config['ZHIPU_API_KEY'] = zhipu_key
    
    # 检测其他可能的环境变量
    env_vars = [
        'CHAT_ROOM_HOST',
        'CHAT_ROOM_PORT', 
        'CHAT_ROOM_DB_PATH',
        'CHAT_ROOM_FILES_PATH',
        'CHAT_ROOM_LOG_LEVEL',
        'CHAT_ROOM_MAX_CONNECTIONS'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            env_config[var] = value
    
    return env_config


def migrate_to_server_config(env_config: Dict[str, Any]) -> bool:
    """迁移环境变量到服务器配置文件"""
    try:
        from server.config.server_config import get_server_config
        
        config = get_server_config()
        updated = False
        
        # 迁移智谱AI API密钥
        if 'ZHIPU_API_KEY' in env_config:
            api_key = env_config['ZHIPU_API_KEY']
            if config.set_ai_api_key(api_key):
                print(f"✅ 已迁移 ZHIPU_API_KEY: {api_key[:8]}...")
                updated = True
            else:
                print("❌ 迁移 ZHIPU_API_KEY 失败")
        
        # 迁移服务器主机
        if 'CHAT_ROOM_HOST' in env_config:
            host = env_config['CHAT_ROOM_HOST']
            if config.config_manager.set("server.host", host):
                print(f"✅ 已迁移 CHAT_ROOM_HOST: {host}")
                updated = True
            else:
                print("❌ 迁移 CHAT_ROOM_HOST 失败")
        
        # 迁移服务器端口
        if 'CHAT_ROOM_PORT' in env_config:
            try:
                port = int(env_config['CHAT_ROOM_PORT'])
                if config.config_manager.set("server.port", port):
                    print(f"✅ 已迁移 CHAT_ROOM_PORT: {port}")
                    updated = True
                else:
                    print("❌ 迁移 CHAT_ROOM_PORT 失败")
            except ValueError:
                print(f"❌ CHAT_ROOM_PORT 值无效: {env_config['CHAT_ROOM_PORT']}")
        
        # 迁移数据库路径
        if 'CHAT_ROOM_DB_PATH' in env_config:
            db_path = env_config['CHAT_ROOM_DB_PATH']
            if config.config_manager.set("database.path", db_path):
                print(f"✅ 已迁移 CHAT_ROOM_DB_PATH: {db_path}")
                updated = True
            else:
                print("❌ 迁移 CHAT_ROOM_DB_PATH 失败")
        
        # 迁移文件存储路径
        if 'CHAT_ROOM_FILES_PATH' in env_config:
            files_path = env_config['CHAT_ROOM_FILES_PATH']
            if config.config_manager.set("file_storage.path", files_path):
                print(f"✅ 已迁移 CHAT_ROOM_FILES_PATH: {files_path}")
                updated = True
            else:
                print("❌ 迁移 CHAT_ROOM_FILES_PATH 失败")
        
        # 迁移日志级别
        if 'CHAT_ROOM_LOG_LEVEL' in env_config:
            log_level = env_config['CHAT_ROOM_LOG_LEVEL'].upper()
            if log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
                if config.config_manager.set("logging.level", log_level):
                    print(f"✅ 已迁移 CHAT_ROOM_LOG_LEVEL: {log_level}")
                    updated = True
                else:
                    print("❌ 迁移 CHAT_ROOM_LOG_LEVEL 失败")
            else:
                print(f"❌ CHAT_ROOM_LOG_LEVEL 值无效: {log_level}")
        
        # 迁移最大连接数
        if 'CHAT_ROOM_MAX_CONNECTIONS' in env_config:
            try:
                max_conn = int(env_config['CHAT_ROOM_MAX_CONNECTIONS'])
                if config.config_manager.set("server.max_connections", max_conn):
                    print(f"✅ 已迁移 CHAT_ROOM_MAX_CONNECTIONS: {max_conn}")
                    updated = True
                else:
                    print("❌ 迁移 CHAT_ROOM_MAX_CONNECTIONS 失败")
            except ValueError:
                print(f"❌ CHAT_ROOM_MAX_CONNECTIONS 值无效: {env_config['CHAT_ROOM_MAX_CONNECTIONS']}")
        
        # 保存配置
        if updated:
            if config.save_config():
                print("✅ 服务器配置已保存")
                return True
            else:
                print("❌ 服务器配置保存失败")
                return False
        else:
            print("ℹ️ 没有需要迁移的服务器配置")
            return True
            
    except Exception as e:
        print(f"❌ 迁移服务器配置失败: {e}")
        return False


def create_migration_backup() -> Optional[str]:
    """创建迁移备份"""
    try:
        import shutil
        from datetime import datetime
        
        backup_dir = project_root / "backup" / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份现有配置文件
        config_files = [
            "config/server_config.yaml",
            "config/client_config.yaml"
        ]
        
        for config_file in config_files:
            config_path = project_root / config_file
            if config_path.exists():
                backup_path = backup_dir / config_file
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(config_path, backup_path)
                print(f"✅ 已备份: {config_file}")
        
        # 保存环境变量信息
        env_file = backup_dir / "environment_variables.txt"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# 迁移前的环境变量\n")
            f.write(f"# 备份时间: {datetime.now()}\n\n")
            
            for key, value in os.environ.items():
                if key.startswith('ZHIPU_') or key.startswith('CHAT_ROOM_'):
                    f.write(f"{key}={value}\n")
        
        print(f"✅ 迁移备份已创建: {backup_dir}")
        return str(backup_dir)
        
    except Exception as e:
        print(f"❌ 创建迁移备份失败: {e}")
        return None


def generate_migration_report(env_config: Dict[str, Any], backup_dir: Optional[str]) -> bool:
    """生成迁移报告"""
    try:
        from datetime import datetime
        
        report_file = project_root / "migration_report.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Chat-Room 配置迁移报告\n")
            f.write(f"# 迁移时间: {datetime.now()}\n")
            f.write(f"# 备份位置: {backup_dir or '无'}\n\n")
            
            f.write("## 检测到的环境变量:\n")
            if env_config:
                for key, value in env_config.items():
                    if key == 'ZHIPU_API_KEY':
                        f.write(f"- {key}: {value[:8]}...\n")
                    else:
                        f.write(f"- {key}: {value}\n")
            else:
                f.write("- 无\n")
            
            f.write("\n## 迁移后的配置文件:\n")
            f.write("- 服务器配置: config/server_config.yaml\n")
            f.write("- 客户端配置: config/client_config.yaml\n")
            
            f.write("\n## 后续步骤:\n")
            f.write("1. 验证配置文件内容是否正确\n")
            f.write("2. 测试服务器和客户端功能\n")
            f.write("3. 如果一切正常，可以删除相关环境变量\n")
            f.write("4. 更新启动脚本，移除环境变量设置\n")
            
            if env_config.get('ZHIPU_API_KEY'):
                f.write("\n## 环境变量清理命令:\n")
                f.write("# Linux/Mac:\n")
                f.write("unset ZHIPU_API_KEY\n")
                f.write("# 同时从 ~/.bashrc 或 ~/.zshrc 中删除相关export语句\n\n")
                f.write("# Windows:\n")
                f.write("set ZHIPU_API_KEY=\n")
                f.write("# 或通过系统设置删除环境变量\n")
        
        print(f"✅ 迁移报告已生成: {report_file}")
        return True
        
    except Exception as e:
        print(f"❌ 生成迁移报告失败: {e}")
        return False


def main():
    """主函数"""
    print("🔄 Chat-Room 配置迁移工具")
    print("=" * 60)
    print("此工具将帮助您从环境变量配置迁移到配置文件")
    print()
    
    # 检测环境变量配置
    print("🔍 检测环境变量配置...")
    env_config = detect_environment_config()
    
    if not env_config:
        print("ℹ️ 未检测到相关环境变量，无需迁移")
        print("💡 如果您是首次使用，请运行: python tools/config_setup.py")
        return
    
    print(f"✅ 检测到 {len(env_config)} 个环境变量:")
    for key, value in env_config.items():
        if key == 'ZHIPU_API_KEY':
            print(f"  - {key}: {value[:8]}...")
        else:
            print(f"  - {key}: {value}")
    
    print()
    confirm = input("是否继续迁移？(y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("⏭️ 迁移已取消")
        return
    
    # 创建备份
    print("\n📦 创建迁移备份...")
    backup_dir = create_migration_backup()
    
    # 执行迁移
    print("\n🔄 开始迁移配置...")
    
    # 迁移服务器配置
    print("\n📊 迁移服务器配置...")
    server_success = migrate_to_server_config(env_config)
    
    # 生成迁移报告
    print("\n📝 生成迁移报告...")
    generate_migration_report(env_config, backup_dir)
    
    # 总结
    print("\n" + "=" * 60)
    if server_success:
        print("🎉 配置迁移完成！")
        print("\n✅ 迁移成功:")
        print("  - 环境变量已迁移到配置文件")
        print("  - 配置文件已保存")
        print("  - 迁移报告已生成")
        
        print("\n📋 后续步骤:")
        print("  1. 验证配置: python tools/config_setup.py")
        print("  2. 测试服务器: python -m server.main")
        print("  3. 测试客户端: python -m client.main")
        print("  4. 如果一切正常，可以删除环境变量")
        
        if env_config.get('ZHIPU_API_KEY'):
            print("\n🗑️ 清理环境变量 (可选):")
            print("  Linux/Mac: unset ZHIPU_API_KEY")
            print("  Windows: set ZHIPU_API_KEY=")
            print("  记得从启动脚本中删除相关设置")
    else:
        print("❌ 配置迁移失败")
        print("💡 请检查错误信息并手动配置")
        if backup_dir:
            print(f"🔄 如需恢复，请查看备份: {backup_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 迁移被用户中断")
    except Exception as e:
        print(f"\n❌ 迁移出现错误: {e}")
