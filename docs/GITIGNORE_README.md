# .gitignore 文件说明

本项目的 `.gitignore` 文件已经配置完善，包含了Python项目开发中常见的需要忽略的文件和目录。

## 🎯 主要忽略的文件类型

### Python相关
- `*.pyc` - Python字节码文件
- `__pycache__/` - Python缓存目录
- `*.pyo`, `*.pyd` - Python优化文件
- `build/`, `dist/` - 构建和分发目录
- `*.egg-info/` - 包信息目录
- `.pytest_cache/` - pytest缓存
- `.coverage` - 代码覆盖率文件

### 虚拟环境
- `venv/`, `env/` - 虚拟环境目录
- `.venv/` - 虚拟环境目录（隐藏）
- `ENV/` - 环境目录

### IDE和编辑器
- `.idea/` - PyCharm配置
- `.vscode/` - VS Code配置
- `*.sublime-*` - Sublime Text配置
- `*.swp`, `*.swo` - Vim临时文件

### 操作系统
- `.DS_Store` - macOS系统文件
- `Thumbs.db` - Windows缩略图
- `*.tmp`, `*.temp` - 临时文件

### 项目特定
- `*.db`, `*.sqlite*` - 数据库文件
- `*.log` - 日志文件
- `.env*` - 环境变量文件
- `config.ini` - 配置文件
- `uploads/` - 用户上传文件
- `cache/` - 缓存目录

## 🔧 使用说明

### 清理已跟踪的文件
如果某些文件已经被git跟踪，但现在想要忽略它们：

```bash
# 从git中移除但保留本地文件
git rm --cached filename

# 移除整个目录
git rm -r --cached directory/

# 提交更改
git commit -m "移除不需要跟踪的文件"
```

### 验证.gitignore是否生效
```bash
# 检查git状态
git status

# 查看被忽略的文件
git status --ignored
```

### 强制添加被忽略的文件（如果需要）
```bash
git add -f filename
```

## 📝 注意事项

1. **敏感信息**：确保不要提交包含密码、API密钥等敏感信息的文件
2. **数据库文件**：本地数据库文件不应包含在版本控制中
3. **日志文件**：日志文件通常很大且包含运行时信息，不适合版本控制
4. **缓存文件**：Python缓存文件会自动生成，不需要版本控制

## 🚀 最佳实践

1. **及早配置**：在项目开始时就配置好`.gitignore`
2. **定期检查**：定期检查是否有新的文件类型需要忽略
3. **团队协作**：确保团队成员都了解`.gitignore`的配置
4. **环境隔离**：使用虚拟环境，避免全局包污染

## 📚 相关命令

```bash
# 查看当前忽略的文件
git ls-files --others --ignored --exclude-standard

# 检查特定文件是否被忽略
git check-ignore filename

# 查看忽略规则的来源
git check-ignore -v filename
```
