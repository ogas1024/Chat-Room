# /list命令使用指南

## 🎯 修复概述

Chat-Room项目的`/list`命令执行错误问题已经成功修复。现在所有列表查询命令都能正常工作，并且查询结果会在TUI界面右侧状态栏正确显示。

## 📋 可用的/list命令

### 1. 显示所有用户 (`/list -u`)

**功能：** 显示系统中所有注册用户及其在线状态

**使用方法：**
```
/list -u
```

**示例输出：**
```
✅ 所有用户列表:
  alice (ID: 1) - 在线
  bob (ID: 2) - 离线
  charlie (ID: 3) - 在线
  test_user (ID: 123) - 在线
```

### 2. 显示当前聊天组用户 (`/list -s`)

**功能：** 显示当前聊天组的所有成员及其在线状态

**使用方法：**
```
/list -s
```

**前提条件：** 必须先进入一个聊天组

**示例输出：**
```
✅ 聊天组 'public' 成员列表:
  alice - 在线
  test_user - 在线
  bob - 离线
```

### 3. 显示已加入的聊天组 (`/list -c`)

**功能：** 显示用户已加入的所有聊天组

**使用方法：**
```
/list -c
```

**示例输出：**
```
✅ 已加入的聊天组:
  public (ID: 1) - 群聊 - 4人
  dev-team (ID: 2) - 群聊 - 3人
  alice-test_user (ID: 3) - 私聊 - 2人
```

### 4. 显示所有群聊 (`/list -g`)

**功能：** 显示系统中所有公开的群聊

**使用方法：**
```
/list -g
```

**示例输出：**
```
✅ 所有群聊列表:
  public (ID: 1) - 4人
  dev-team (ID: 2) - 3人
  general (ID: 4) - 8人
```

### 5. 显示当前聊天组文件 (`/list -f`)

**功能：** 显示当前聊天组中的所有文件

**使用方法：**
```
/list -f
```

**前提条件：** 必须先进入一个聊天组

**示例输出：**
```
✅ 聊天组 'public' 文件列表:
  document.pdf (1000.0KB) - 上传者: alice
  image.jpg (500.0KB) - 上传者: bob
```

## 🔧 使用步骤

### 1. 启动系统

```bash
# 启动服务器
cd /home/ogas/Code/CN/Chat-Room
python server/main.py

# 启动客户端（新终端窗口）
python client/main.py
```

### 2. 登录用户

```
/login
# 然后按提示输入用户名和密码
```

### 3. 使用列表命令

登录成功后，就可以使用所有的`/list`命令了：

```
/list -u    # 查看所有用户
/list -s    # 查看当前聊天组成员
/list -c    # 查看已加入的聊天组
/list -g    # 查看所有群聊
/list -f    # 查看当前聊天组文件
```

## 📊 界面显示

### 主聊天区域

命令执行结果会在主聊天区域显示：

```
[12:34:56] 系统: ✅ 所有用户列表:
  alice (ID: 1) - 在线
  bob (ID: 2) - 离线
  charlie (ID: 3) - 在线
```

### 右侧状态栏

查询结果也会同时在右侧状态栏显示，便于快速查看：

```
┌─ 状态信息 ─────────┐
│ 连接: 已连接       │
│ 用户: test_user    │
│ 聊天组: public     │
│ ──────────────── │
│ 所有用户列表:      │
│ alice (ID: 1) -... │
│ bob (ID: 2) - 离... │
│ charlie (ID: 3)... │
│ ... 还有 1 项      │
└─────────────────┘
```

## ❌ 错误处理

### 常见错误及解决方法

#### 1. 未指定选项

**错误信息：**
```
❌ 请指定列表类型: -u(用户) -s(当前聊天组用户) -c(已加入聊天组) -g(所有群聊) -f(文件)
```

**解决方法：** 在`/list`后面添加正确的选项，如`/list -u`

#### 2. 无效选项

**错误信息：**
```
❌ 未知选项: -x。支持的选项: -u, -s, -c, -g, -f
```

**解决方法：** 使用支持的选项之一

#### 3. 未登录

**错误信息：**
```
❌ 请先登录
```

**解决方法：** 使用`/login`命令先登录

#### 4. 未进入聊天组

**错误信息：**
```
❌ 请先进入聊天组
```

**解决方法：** 使用`/enter_chat <聊天组名>`进入聊天组

## 📝 日志记录

所有`/list`命令的执行都会被记录到日志系统中：

### 查看日志

```bash
# 查看客户端命令日志
python tools/log_viewer.py search "command_list" --file-pattern 'client/*.log'

# 查看用户操作日志
python tools/log_viewer.py search "list" --file-pattern 'server/*.log'
```

### 日志内容示例

```json
{
  "timestamp": "2024-01-01T12:34:56.789Z",
  "level": "INFO",
  "module": "client.commands",
  "message": "执行命令",
  "command": "list",
  "args": [],
  "options": {"-u": true},
  "user_id": 123,
  "username": "test_user",
  "action": "command_list"
}
```

## 🔍 故障排除

### 如果命令仍然不工作

1. **检查服务器状态**
   ```bash
   # 确保服务器正在运行
   ps aux | grep "python.*server"
   ```

2. **检查网络连接**
   ```
   # 在客户端中检查连接状态
   右侧状态栏应显示 "连接: 已连接"
   ```

3. **重启客户端**
   ```bash
   # 完全关闭客户端后重新启动
   python client/main.py
   ```

4. **查看错误日志**
   ```bash
   # 查看最近的错误日志
   python tools/log_viewer.py view client/client_error.log --lines 20
   ```

### 性能问题

如果命令执行缓慢：

1. **检查网络延迟**
2. **查看服务器负载**
3. **检查数据库性能**

## 📚 相关文档

- [命令系统文档](command_system.md)
- [日志系统文档](logging_system.md)
- [TUI界面使用指南](tui_usage_guide.md)
- [故障排除指南](troubleshooting.md)

## 🆘 获取帮助

如果遇到问题：

1. **查看内置帮助**
   ```
   /help
   /help list
   ```

2. **查看日志文件**
   ```bash
   python tools/log_viewer.py analyze --hours 1
   ```

3. **检查系统状态**
   ```
   /info  # 显示用户和系统信息
   ```

---

**最后更新：** 2025-06-11  
**适用版本：** v1.0+  
**修复状态：** 已完成
