# Chat-Room 快速上手指南

## 🚀 5分钟快速体验

这个指南将帮你在5分钟内运行Chat-Room项目，体验所有核心功能。

### 第一步：环境准备

**系统要求**：
- Python 3.8+
- 支持UTF-8的终端
- 至少100MB可用磁盘空间

**安装依赖**：
```bash
# 1. 克隆项目（如果还没有）
git clone <repository-url>
cd Chat-Room

# 2. 激活conda环境（重要！）
conda activate chatroom

# 3. 安装依赖
pip install -r requirements.txt
```

**验证安装**：
```bash
# 检查Python版本
python --version

# 检查依赖是否安装成功
python -c "import textual, zhipuai, sqlite3; print('✅ 依赖安装成功')"
```

### 第二步：运行演示

**启动演示模式**：
```bash
# 运行完整演示
python main.py demo

# 或者运行AI功能演示
python main.py demo ai
```

**演示内容**：
- 自动创建测试用户
- 模拟聊天对话
- 展示文件传输
- 演示AI对话功能

### 第三步：手动体验

#### 启动服务器
```bash
# 在第一个终端窗口启动服务器
python main.py server

# 看到以下信息表示启动成功：
# ✅ 服务器启动成功，监听 localhost:8888
# ✅ 数据库初始化完成
# ✅ AI功能已启用
```

#### 启动客户端
```bash
# 在第二个终端窗口启动客户端
python main.py client

# 或者使用TUI界面（推荐）
python main.py client --ui tui
```

## 📱 基础操作指南

### 用户注册和登录

**注册新用户**：
```
# 在客户端输入
/signin

# 按提示输入用户名和密码
用户名: alice
密码: ******

# 看到成功提示
✅ 注册成功！用户ID: 1
```

**登录已有用户**：
```
# 在客户端输入
/login

# 输入用户名和密码
用户名: alice
密码: ******

# 看到登录成功提示
✅ 登录成功！欢迎回来，alice
```

### 基础聊天操作

**查看帮助**：
```
/?
# 或者
/help
```

**查看用户信息**：
```
/info
# 显示：用户ID、用户名、当前聊天组等信息
```

**列出在线用户**：
```
/list -u
# 显示所有在线用户列表
```

**发送消息**：
```
# 直接输入消息内容（不以/开头）
大家好，我是新用户！

# 消息会发送到当前聊天组
```

### 聊天组操作

**列出所有聊天组**：
```
/list -c
# 显示所有可用的聊天组
```

**创建新聊天组**：
```
/create_chat 项目讨论
# 创建名为"项目讨论"的聊天组
```

**加入聊天组**：
```
/join_chat 项目讨论
# 加入"项目讨论"聊天组
```

**进入聊天组**：
```
/enter_chat 项目讨论
# 进入"项目讨论"聊天组开始聊天
```

### 文件传输操作

**发送文件**：
```
/send_files ./test.txt ./image.jpg
# 发送多个文件到当前聊天组
```

**查看可下载文件**：
```
/recv_files -l
# 列出当前聊天组的所有文件
```

**下载文件**：
```
/recv_files -n test.txt
# 下载指定文件
```

### AI对话体验

**群聊中@AI**：
```
# 进入任意聊天组后
@AI 你好，请介绍一下自己

# 或者使用关键词
AI能帮我解释一下Python的装饰器吗？
```

**私聊AI**：
```
# 创建与AI的私聊
/create_chat private_with_ai
/enter_chat private_with_ai

# 在私聊中，所有消息都会得到AI回复
你好，这是私聊消息
```

## 🔧 常见问题解决

### 连接问题

**问题**：客户端无法连接服务器
```
❌ 连接服务器失败: [Errno 61] Connection refused
```

**解决方案**：
1. 确保服务器已启动
2. 检查端口是否被占用
3. 确认防火墙设置

```bash
# 检查端口占用
netstat -an | grep 8888

# 如果端口被占用，修改配置文件
vim config/server_config.yaml
# 修改 port: 8889
```

### 编码问题

**问题**：中文显示乱码

**解决方案**：
```bash
# 设置环境变量
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 或者在Windows上
set PYTHONIOENCODING=utf-8
```

### AI功能问题

**问题**：AI功能无法使用

**解决方案**：
1. 检查API密钥配置
```yaml
# config/server_config.yaml
ai:
  enabled: true
  api_key: "your-zhipu-ai-api-key"  # 确保API密钥正确
```

2. 测试网络连接
```bash
# 测试API连接
python -c "
from server.ai.zhipu_client import ZhipuClient
client = ZhipuClient('your-api-key')
print(client.test_connection())
"
```

### 数据库问题

**问题**：数据库文件损坏

**解决方案**：
```bash
# 删除数据库文件，重新初始化
rm server/data/chatroom.db

# 重启服务器，会自动创建新数据库
python main.py server
```

## 🎯 学习路径建议

### 第一周：基础理解
1. **运行演示**：熟悉所有功能
2. **阅读架构文档**：理解整体设计
3. **查看代码结构**：了解文件组织

### 第二周：深入学习
1. **学习共享模块**：理解基础组件
2. **分析消息协议**：掌握通信机制
3. **研究数据库设计**：理解数据模型

### 第三周：实践修改
1. **修改界面主题**：学习UI定制
2. **添加新命令**：理解命令系统
3. **扩展AI功能**：学习AI集成

### 第四周：项目实践
1. **实现新功能**：如表情包、语音消息
2. **性能优化**：改进系统性能
3. **部署测试**：学习项目部署

## 🛠️ 开发工具推荐

### 代码编辑器
- **VS Code**：推荐插件 Python、GitLens、YAML
- **PyCharm**：专业Python IDE
- **Vim/Neovim**：轻量级编辑器

### 调试工具
```bash
# 使用pdb调试
python -m pdb main.py server

# 使用日志调试
tail -f logs/server/server.log
```

### 测试工具
```bash
# 运行单元测试
python -m pytest test/

# 运行特定测试
python test/simple_test.py
```

## 📚 扩展学习资源

### Python相关
- [Python官方文档](https://docs.python.org/3/)
- [Real Python](https://realpython.com/)
- [Python设计模式](https://python-patterns.guide/)

### 网络编程
- [Socket编程指南](https://docs.python.org/3/howto/sockets.html)
- [网络协议基础](https://www.rfc-editor.org/)

### 数据库
- [SQLite官方文档](https://www.sqlite.org/docs.html)
- [SQL教程](https://www.w3schools.com/sql/)

### UI开发
- [Textual文档](https://textual.textualize.io/)
- [Rich库文档](https://rich.readthedocs.io/)

## 🎉 完成检查清单

完成快速上手后，你应该能够：

- [ ] 成功启动服务器和客户端
- [ ] 注册和登录用户账号
- [ ] 发送和接收聊天消息
- [ ] 创建和加入聊天组
- [ ] 上传和下载文件
- [ ] 与AI进行对话
- [ ] 使用所有基本命令
- [ ] 理解项目的基本架构
- [ ] 解决常见的技术问题

## 🚀 下一步学习

恭喜你完成了快速上手！现在你可以：

1. **深入学习共享模块** → [../02-shared-modules/](../02-shared-modules/)
2. **了解服务器实现** → [../03-server-modules/](../03-server-modules/)
3. **学习客户端设计** → [../04-client-modules/](../04-client-modules/)

记住：**实践是最好的老师**！不要害怕修改代码，每一次尝试都是学习的机会。

---

**准备好深入学习了吗？** 让我们从共享模块开始吧！ 🎓
