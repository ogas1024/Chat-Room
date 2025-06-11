# Chat-Room 日志系统文档

## 📖 概述

Chat-Room项目集成了完整的日志系统，提供结构化日志记录、敏感信息脱敏、日志轮转归档等功能，支持问题排查、性能分析和安全审计。

## 🏗️ 系统架构

### 核心组件

- **LoggerManager**: 统一日志管理器，负责日志系统初始化和配置
- **结构化日志**: 采用JSON格式，便于查询和分析
- **敏感信息脱敏**: 自动处理密码、API密钥等敏感数据
- **日志分类**: 按功能模块分类存储（数据库、AI、安全、网络等）
- **日志轮转**: 自动按大小和时间轮转，压缩归档

### 技术栈

- **日志库**: loguru (高性能、功能丰富)
- **格式**: JSON结构化格式
- **存储**: 文件系统，按日期和类型分类
- **压缩**: gzip压缩归档

## 📁 日志文件结构

```
logs/
├── server/                     # 服务器日志
│   ├── server.log             # 主日志文件
│   ├── server_error.log       # 错误日志
│   ├── server_database.log    # 数据库操作日志
│   ├── server_ai.log          # AI功能日志
│   ├── server_security.log    # 安全事件日志
│   └── archived/              # 归档日志
├── client/                    # 客户端日志
│   ├── client.log            # 客户端主日志
│   └── archived/             # 归档日志
└── analysis/                  # 日志分析结果
    └── daily_reports/         # 每日统计报告
```

## 🔧 配置说明

### 服务器日志配置 (config/server_config.yaml)

```yaml
logging:
  level: INFO                    # 日志级别: DEBUG, INFO, WARNING, ERROR
  file_enabled: true             # 启用文件日志
  console_enabled: true          # 启用控制台日志
  file_max_size: 10485760       # 单个日志文件最大大小 (10MB)
  file_backup_count: 5          # 保留的备份文件数量
  
  # 详细日志配置
  categories:
    database:
      enabled: true
      level: DEBUG
    ai:
      enabled: true
      level: INFO
    security:
      enabled: true
      level: WARNING
    performance:
      enabled: true
      level: INFO
    network:
      enabled: true
      level: INFO
  
  # 日志保留策略
  retention:
    days: 30                     # 保留天数
    max_size_gb: 1.0            # 最大总大小
  
  # 敏感信息脱敏
  sanitization:
    enabled: true
    patterns:
      - password
      - api_key
      - token
      - secret
      - auth
```

### 客户端日志配置 (config/client_config.yaml)

```yaml
logging:
  level: INFO
  file_enabled: false            # 客户端默认不启用文件日志
  console_enabled: true
  file_max_size: 5242880        # 5MB
  file_backup_count: 3
```

## 📝 日志记录范围

### 1. 网络通信日志
- 客户端连接/断开事件
- 消息收发记录
- 连接错误和超时
- 网络性能指标

### 2. 用户操作日志
- 用户注册、登录、登出
- 聊天组创建、加入、进入
- 消息发送和接收
- 文件上传下载操作

### 3. 数据库操作日志
- 所有CRUD操作记录
- 查询性能统计
- 数据库连接状态
- 事务执行情况

### 4. AI功能日志
- API调用记录
- 响应时间统计
- 错误和异常处理
- 上下文管理操作

### 5. 安全事件日志
- 认证失败记录
- 权限验证事件
- 异常访问尝试
- 敏感操作审计

### 6. 系统性能日志
- 关键操作耗时
- 资源使用情况
- 错误率统计
- 系统健康状态

## 🔍 日志格式说明

### JSON结构化格式

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "level": "INFO",
  "module": "server.core.server",
  "function": "handle_login",
  "line": 245,
  "message": "用户登录成功",
  "user_id": 123,
  "username": "alice",
  "client_ip": "192.168.1.100",
  "action": "login"
}
```

### 字段说明

- **timestamp**: ISO格式时间戳
- **level**: 日志级别 (DEBUG/INFO/WARNING/ERROR)
- **module**: 模块名称
- **function**: 函数名称
- **line**: 代码行号
- **message**: 日志消息
- **额外字段**: 根据具体场景添加的上下文信息

## 🛠️ 使用方法

### 1. 初始化日志系统

```python
from shared.logger import init_logger, get_logger
from server.config.server_config import get_server_config

# 初始化日志系统
config = get_server_config()
logging_config = config.get_logging_config()
init_logger(logging_config, "server")

# 获取logger实例
logger = get_logger("module_name")
```

### 2. 记录不同类型的日志

```python
from shared.logger import (
    log_user_action, log_database_operation, 
    log_ai_operation, log_security_event,
    log_network_event, log_performance
)

# 用户操作日志
log_user_action(user_id, username, "login", client_ip="192.168.1.100")

# 数据库操作日志
log_database_operation("create", "users", user_id=123)

# AI操作日志
log_ai_operation("generate_reply", "glm-4-flash", response_time=1.5)

# 安全事件日志
log_security_event("login_failed", username="alice", reason="invalid_password")

# 网络事件日志
log_network_event("client_connected", client_ip="192.168.1.100")

# 性能日志
log_performance("database_query", 0.05)
```

### 3. 使用装饰器自动记录

```python
from shared.logger import log_function_call, log_performance_decorator

@log_function_call(event_type="user_registration", log_args=True)
def register_user(username, password):
    # 函数实现
    pass

@log_performance_decorator("file_upload")
def upload_file(file_data):
    # 函数实现
    pass
```

## 🔍 日志查看和分析

### 使用日志查看工具

```bash
# 列出所有日志文件
python tools/log_viewer.py list

# 查看特定日志文件
python tools/log_viewer.py view server/server.log --lines 100

# 搜索日志
python tools/log_viewer.py search "登录失败" --level ERROR --start-time "2024-01-01T00:00:00"

# 分析日志统计
python tools/log_viewer.py analyze --hours 24
```

### 常用查询示例

```bash
# 查看最近的错误日志
python tools/log_viewer.py search "ERROR" --hours 1

# 查看特定用户的操作
python tools/log_viewer.py search "user_id.*123"

# 查看AI操作统计
python tools/log_viewer.py search "ai.*operation"

# 查看数据库操作
python tools/log_viewer.py view server/server_database.log --lines 50
```

## 📊 日志分析和监控

### 1. 性能分析
- 响应时间统计
- 数据库查询性能
- AI API调用延迟
- 文件传输速度

### 2. 错误分析
- 错误频率统计
- 错误类型分布
- 错误趋势分析
- 异常堆栈跟踪

### 3. 用户行为分析
- 用户活跃度统计
- 功能使用频率
- 操作路径分析
- 异常行为检测

### 4. 安全审计
- 登录失败统计
- 权限违规记录
- 异常访问模式
- 敏感操作审计

## 🔒 安全和隐私

### 敏感信息脱敏

系统自动对以下信息进行脱敏处理：
- 密码字段
- API密钥
- 认证令牌
- 其他敏感配置

### 访问控制

- 日志文件权限控制
- 敏感日志加密存储
- 审计日志不可篡改
- 定期安全检查

## 🚀 最佳实践

### 1. 日志级别使用
- **DEBUG**: 详细的调试信息，仅开发环境使用
- **INFO**: 一般信息记录，正常业务流程
- **WARNING**: 警告信息，需要关注但不影响功能
- **ERROR**: 错误信息，需要立即处理

### 2. 性能考虑
- 使用异步日志写入
- 合理设置日志级别
- 定期清理过期日志
- 监控日志文件大小

### 3. 故障排查
- 记录足够的上下文信息
- 使用结构化数据便于查询
- 保持日志格式一致性
- 建立日志关联机制

## 📋 维护和运维

### 日志轮转配置

日志系统自动进行轮转：
- 按文件大小轮转 (默认10MB)
- 保留指定数量的备份文件
- 自动压缩归档文件
- 定期清理过期日志

### 监控和告警

建议设置以下监控：
- 错误日志数量告警
- 日志文件大小监控
- 磁盘空间使用率
- 日志写入性能

### 备份策略

- 定期备份重要日志
- 异地存储安全日志
- 建立日志恢复机制
- 测试备份有效性

## 🔧 故障排除

### 常见问题

1. **日志文件过大**
   - 检查轮转配置
   - 调整日志级别
   - 增加清理频率

2. **日志写入失败**
   - 检查磁盘空间
   - 验证文件权限
   - 查看系统资源

3. **性能影响**
   - 启用异步写入
   - 优化日志格式
   - 减少不必要的日志

4. **查询缓慢**
   - 使用索引工具
   - 分割大日志文件
   - 优化查询条件

## 📚 相关文档

- [配置系统文档](configuration_system.md)
- [开发指南](Development.md)
- [API文档](api/README.md)
- [部署指南](deployment.md)
