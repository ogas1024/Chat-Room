# Chat-Room AI集成指南

## 📖 概述

Chat-Room聊天室集成了智谱AI的GLM-4系列模型，为用户提供智能对话功能。本指南将详细介绍如何配置和使用AI功能。

## 🚀 快速开始

### 1. 获取API密钥

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并登录
3. 在控制台创建API密钥
4. 复制API密钥备用

### 2. 配置环境

#### 方式一：环境变量（推荐）
```bash
# Linux/Mac
export ZHIPU_API_KEY='your-api-key-here'

# Windows
set ZHIPU_API_KEY=your-api-key-here
```

#### 方式二：代码配置
```python
from server.config.ai_config import get_ai_config
config = get_ai_config()
config.set_api_key('your-api-key-here')
```

### 3. 安装依赖

```bash
# 安装智谱AI官方SDK（推荐）
pip install zhipuai

# 或者安装所有依赖
pip install -r requirements.txt
```

### 4. 启动服务

```bash
# 启动服务器
python -m server.main

# 启动客户端
python -m client.main
```

## 🤖 支持的模型

| 模型名称 | 特点 | 适用场景 | 费用 |
|---------|------|----------|------|
| glm-4-flash | 速度快，免费 | 日常聊天，快速问答 | 免费 |
| glm-4 | 平衡性能和质量 | 通用对话，内容生成 | 付费 |
| glm-4-plus | 质量更高 | 复杂推理，专业问答 | 付费 |
| glm-4-air | 轻量级 | 简单对话 | 付费 |
| glm-4-airx | 轻量增强 | 中等复杂度对话 | 付费 |
| glm-4-long | 长文本支持 | 长文档分析，长对话 | 付费 |

**默认使用：** `glm-4-flash`（免费模型）

## 💬 使用方式

### 群聊中使用AI

1. **@AI触发**
   ```
   用户: @AI 你好，请介绍一下自己
   AI: 你好！我是Chat-Room的AI助手...
   ```

2. **关键词触发**
   ```
   用户: AI能帮我解释一下Python吗？
   AI: 当然可以！Python是一门...
   ```

3. **问号结尾触发**
   ```
   用户: 什么是人工智能？
   AI: 人工智能是指...
   ```

### 私聊中使用AI

在私聊中，AI会回复所有消息：
```
用户: 你好
AI: 你好！有什么可以帮助你的吗？

用户: 请帮我写一个Python函数
AI: 好的，我来帮你写一个Python函数...
```

## ⚙️ 配置选项

### AI配置参数

```python
from server.config.ai_config import get_ai_config

config = get_ai_config()

# 模型配置
config.model = "glm-4-flash"        # 使用的模型
config.max_tokens = 1024            # 最大输出长度
config.temperature = 0.7            # 创造性（0-1）
config.top_p = 0.9                  # 多样性控制

# 功能开关
config.enable_group_chat = True     # 群聊中启用AI
config.enable_private_chat = True   # 私聊中启用AI
config.auto_reply = True            # 自动回复

# 触发条件
config.trigger_keywords = [         # 触发关键词
    "ai", "人工智能", "助手", "机器人", "智能", "问答"
]
config.require_at_mention = False   # 群聊是否需要@才回复

# 上下文管理
config.max_context_length = 10      # 最大上下文长度
config.context_timeout = 3600       # 上下文超时时间（秒）
```

### 模型切换

```python
from server.ai.zhipu_client import ZhipuClient

client = ZhipuClient(api_key)

# 查看可用模型
models = client.get_available_models()
print(models)

# 切换模型
client.set_model("glm-4-plus")
```

## 🔧 高级功能

### 上下文管理

AI会自动管理对话上下文：
- **群聊上下文**：每个群聊独立维护对话历史
- **私聊上下文**：每个用户独立维护对话历史
- **自动清理**：超时的上下文会自动清理

### 系统提示词

AI使用不同的系统提示词：
- **群聊提示词**：适合群聊场景的行为指导
- **私聊提示词**：适合一对一对话的行为指导

### 错误处理

- **API密钥错误**：自动降级为非AI模式
- **网络错误**：自动重试和错误提示
- **模型错误**：自动回退到默认模型

## 🧪 测试和调试

### 运行AI功能测试

```bash
# 基础功能测试
python test_ai_improvements.py

# 完整功能演示
python demo_ai_features.py

# 真实API测试（需要API密钥）
ZHIPU_API_KEY='your-key' python demo_ai_features.py
```

### 调试模式

```bash
# 启用调试模式
python -m server.main --debug
```

### 查看AI状态

在客户端中使用命令：
```
用户> /ai status    # 查看AI状态
用户> /ai help      # 查看AI帮助
```

## 📊 性能优化

### 请求频率控制

- 避免频繁请求，建议间隔1-2秒
- 使用上下文管理减少重复信息
- 合理设置max_tokens控制响应长度

### 成本控制

- 优先使用免费的`glm-4-flash`模型
- 设置合理的上下文长度限制
- 在群聊中使用关键词触发而非全量回复

## 🔒 安全考虑

### API密钥安全

- 不要在代码中硬编码API密钥
- 使用环境变量存储敏感信息
- 定期轮换API密钥

### 内容过滤

- AI会自动过滤不当内容
- 可以自定义敏感词过滤
- 记录和监控AI对话内容

## 🐛 常见问题

### Q: AI不回复消息？
A: 检查以下项目：
1. API密钥是否正确设置
2. 网络连接是否正常
3. 是否触发了回复条件（群聊需要@AI或关键词）
4. 查看服务器日志中的错误信息

### Q: API调用失败？
A: 可能的原因：
1. API密钥无效或过期
2. 账户余额不足（付费模型）
3. 请求频率过高
4. 网络连接问题

### Q: 如何切换模型？
A: 有两种方式：
1. 修改配置文件中的model参数
2. 使用代码动态切换：`client.set_model("glm-4")`

### Q: 上下文丢失？
A: 上下文会在以下情况清理：
1. 超过设定的超时时间
2. 服务器重启
3. 手动清理上下文

## 📚 更多资源

- [智谱AI官方文档](https://open.bigmodel.cn/dev/api)
- [GLM-4模型介绍](https://open.bigmodel.cn/dev/api/normal-model/glm-4)
- [Python SDK文档](https://github.com/zhipuai/zhipuai-python)
- [Chat-Room项目文档](../README.md)

## 🤝 贡献

如果您在使用过程中发现问题或有改进建议，欢迎：
1. 提交Issue报告问题
2. 提交Pull Request贡献代码
3. 完善文档和示例

---

**最后更新**: 2025年1月
**版本**: v1.0
