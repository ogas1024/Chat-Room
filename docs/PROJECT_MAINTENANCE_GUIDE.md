# Chat-Room 项目维护指南

## 项目文件管理原则

### 极简主义原则
遵循"如无必要，勿增实体"的原则，确保项目根目录只保留必要文件，所有临时文件、调试脚本、过时文档都应及时归档。

### 文件分类标准

#### 应该保留在主目录的文件：
1. **核心源代码**
   - `client/`, `server/`, `shared/` 目录下的所有源代码
   - 主入口文件 `main.py`

2. **配置文件**
   - `config/` 目录下的配置文件和模板
   - `package.json`, `requirements.txt`

3. **正式文档**
   - `docs/` 目录下的核心文档
   - `README.md`, `LICENSE`

4. **标准测试**
   - `test/` 目录下的正式测试代码

5. **工具和演示**
   - `tools/` 目录下的开发工具
   - `demo/` 目录下的演示代码

#### 应该归档到archive/的文件：
1. **调试脚本**
   - 以 `debug_` 开头的文件
   - 临时调试工具和分析脚本

2. **临时测试文件**
   - 非标准测试框架的测试文件
   - 一次性验证脚本
   - 问题重现工具

3. **过时文档**
   - 重复的修复总结
   - 临时使用指南
   - 过时的分析文档

4. **验证工具**
   - 修复效果验证脚本
   - 系统状态检查工具

5. **一次性工具**
   - 数据迁移脚本
   - 临时处理工具

## Archive 目录结构

```
archive/
├── README.md                    # 归档说明文档
├── debug_scripts/              # 调试脚本
│   └── debug_*.py
├── test_scripts/               # 临时测试文件
│   ├── test_*.py
│   └── *.db (测试数据库)
├── temp_docs/                  # 临时文档
│   ├── bug_fixes/             # Bug修复文档
│   ├── test_guides/           # 测试指南
│   ├── usage_guides/          # 使用指南
│   └── migration_docs/        # 迁移文档
├── verification_tools/         # 验证工具
│   └── verify_*.py
└── one_time_tools/            # 一次性工具
    └── 临时处理脚本
```

## 日常维护流程

### 开发过程中
1. **创建临时文件时**
   - 使用明确的命名前缀（如 `debug_`, `test_`, `verify_`）
   - 在文件头部添加注释说明用途和创建时间

2. **完成功能开发后**
   - 立即将临时文件移动到 `archive/` 对应目录
   - 更新 `archive/README.md` 记录重要归档

3. **Git提交前**
   - 检查项目根目录是否有需要归档的文件
   - 确保只提交必要的文件

### 定期维护
1. **每周检查**
   - 检查项目根目录是否有临时文件
   - 清理不再需要的日志文件

2. **每月整理**
   - 检查 `archive/` 目录，删除确实不再需要的文件
   - 更新项目文档，确保与代码同步

3. **版本发布前**
   - 全面检查项目结构
   - 确保所有文档都是最新的
   - 清理所有临时文件

## 文件归档操作

### 手动归档
```bash
# 移动调试脚本
mv debug_*.py archive/debug_scripts/

# 移动临时测试
mv test_*.py archive/test_scripts/

# 移动验证工具
mv verify_*.py archive/verification_tools/
```

### 批量归档脚本
可以创建一个归档脚本 `tools/archive_temp_files.py`：

```python
#!/usr/bin/env python3
"""
临时文件归档工具
自动将临时文件移动到archive目录
"""

import os
import shutil
import glob

def archive_files():
    """归档临时文件"""
    # 归档调试脚本
    for file in glob.glob("debug_*.py"):
        shutil.move(file, f"archive/debug_scripts/{file}")
    
    # 归档临时测试
    for file in glob.glob("test_*.py"):
        if not file.startswith("test/"):  # 排除正式测试
            shutil.move(file, f"archive/test_scripts/{file}")
    
    # 归档验证工具
    for file in glob.glob("verify_*.py"):
        shutil.move(file, f"archive/verification_tools/{file}")

if __name__ == "__main__":
    archive_files()
    print("✅ 临时文件归档完成")
```

## Git 管理

### .gitignore 配置
确保 `archive/` 目录已添加到 `.gitignore`：

```gitignore
# 归档目录（临时文件和调试文件）
archive/
```

### 提交规范
归档操作的提交信息格式：

```
[整理]: 文件归档和结构优化

- 归档调试脚本到archive/debug_scripts/
- 归档临时测试到archive/test_scripts/
- 归档过时文档到archive/temp_docs/
- 更新项目结构文档
```

## 最佳实践

### 文件命名规范
1. **调试脚本**: `debug_功能描述.py`
2. **临时测试**: `test_功能描述_临时标识.py`
3. **验证工具**: `verify_功能描述.py`
4. **临时文档**: `功能描述_临时标识.md`

### 代码注释
临时文件应包含清晰的注释：

```python
#!/usr/bin/env python3
"""
调试脚本：用户权限问题调试
创建时间：2025-01-XX
用途：调查用户无法发送消息的权限问题
状态：已完成，可归档
"""
```

### 文档管理
1. **保留最终版本**：只保留最终的、完整的文档
2. **归档草稿版本**：将草稿和临时版本移到archive
3. **定期更新**：确保保留的文档都是最新的

## 注意事项

1. **不要删除重要文件**
   - 归档前确认文件确实不再需要
   - 重要的调试脚本可能在未来有参考价值

2. **保持分类清晰**
   - 按照功能和类型分类存放
   - 使用清晰的目录结构

3. **定期清理**
   - archive目录也需要定期清理
   - 删除确实过时的文件

4. **文档同步**
   - 归档操作后及时更新相关文档
   - 确保README等文档反映最新结构

## 工具推荐

### 文件管理工具
- `find` - 查找特定类型的文件
- `tree` - 显示目录结构
- `du` - 检查目录大小

### 示例命令
```bash
# 查找所有调试脚本
find . -name "debug_*.py" -not -path "./archive/*"

# 显示项目结构
tree -I "__pycache__|*.pyc|archive"

# 检查archive目录大小
du -sh archive/
```

## 总结

通过遵循这些维护原则和流程，可以确保Chat-Room项目始终保持整洁的结构，便于开发、维护和新人理解。定期的文件整理不仅提高了项目的可读性，也体现了专业的开发习惯。
