# Chat-Room API 文档

## 概述

Chat-Room 使用基于JSON的自定义协议进行客户端-服务器通信。所有消息都通过TCP Socket传输，采用换行符分隔的JSON格式。

## 通信协议

### 消息格式

所有消息都继承自基础消息格式：

```json
{
    "message_type": "消息类型",
    "timestamp": 1640995200.0
}
```

### 消息类型

#### 认证相关

##### 登录请求 (LOGIN_REQUEST)
```json
{
    "message_type": "login_request",
    "timestamp": 1640995200.0,
    "username": "用户名",
    "password": "密码"
}
```

##### 登录响应 (LOGIN_RESPONSE)
```json
{
    "message_type": "login_response",
    "timestamp": 1640995200.0,
    "success": true,
    "user_id": 123,
    "username": "alice",
    "error_message": null
}
```

##### 注册请求 (REGISTER_REQUEST)
```json
{
    "message_type": "register_request",
    "timestamp": 1640995200.0,
    "username": "新用户名",
    "password": "密码"
}
```

##### 注册响应 (REGISTER_RESPONSE)
```json
{
    "message_type": "register_response",
    "timestamp": 1640995200.0,
    "success": true,
    "user_id": 124,
    "username": "bob",
    "error_message": null
}
```

#### 聊天相关

##### 聊天消息 (CHAT_MESSAGE)
```json
{
    "message_type": "chat_message",
    "timestamp": 1640995200.0,
    "message_id": 456,
    "sender_id": 123,
    "sender_username": "alice",
    "chat_group_id": 1,
    "chat_group_name": "public",
    "content": "Hello everyone!"
}
```

#### 信息查询

##### 用户信息请求 (USER_INFO_REQUEST)
```json
{
    "message_type": "user_info_request",
    "timestamp": 1640995200.0
}
```

##### 用户信息响应 (USER_INFO_RESPONSE)
```json
{
    "message_type": "user_info_response",
    "timestamp": 1640995200.0,
    "user_info": {
        "user_id": 123,
        "username": "alice",
        "is_online": true
    },
    "joined_chats_count": 3,
    "private_chats_count": 1,
    "group_chats_count": 2,
    "total_users_count": 50,
    "online_users_count": 15,
    "total_chats_count": 20
}
```

##### 用户列表请求 (LIST_USERS_REQUEST)
```json
{
    "message_type": "list_users_request",
    "timestamp": 1640995200.0
}
```

##### 用户列表响应 (LIST_USERS_RESPONSE)
```json
{
    "message_type": "list_users_response",
    "timestamp": 1640995200.0,
    "users": [
        {
            "user_id": 123,
            "username": "alice",
            "is_online": true
        },
        {
            "user_id": 124,
            "username": "bob",
            "is_online": false
        }
    ]
}
```

#### 聊天组管理

##### 创建聊天组请求 (CREATE_CHAT_REQUEST)
```json
{
    "message_type": "create_chat_request",
    "timestamp": 1640995200.0,
    "chat_name": "项目讨论",
    "member_usernames": ["bob", "charlie"]
}
```

##### 加入聊天组请求 (JOIN_CHAT_REQUEST)
```json
{
    "message_type": "join_chat_request",
    "timestamp": 1640995200.0,
    "chat_name": "技术交流"
}
```

##### 进入聊天组请求 (ENTER_CHAT_REQUEST)
```json
{
    "message_type": "enter_chat_request",
    "timestamp": 1640995200.0,
    "chat_name": "public"
}
```

#### 系统消息

##### 系统消息 (SYSTEM_MESSAGE)
```json
{
    "message_type": "system_message",
    "timestamp": 1640995200.0,
    "content": "欢迎加入聊天室！",
    "level": "info"
}
```

##### 错误消息 (ERROR_MESSAGE)
```json
{
    "message_type": "error_message",
    "timestamp": 1640995200.0,
    "error_code": 1001,
    "error_message": "用户名或密码错误"
}
```

## 错误代码

| 错误代码 | 说明 |
|---------|------|
| 0 | 成功 |
| 1001 | 认证失败 |
| 1002 | 用户已存在 |
| 1003 | 用户不存在 |
| 1004 | 聊天组不存在 |
| 1005 | 权限不足 |
| 1006 | 文件不存在 |
| 1007 | 文件过大 |
| 1008 | 无效命令 |
| 1009 | 服务器内部错误 |
| 1010 | 网络连接错误 |

## 连接流程

### 1. 建立连接
客户端通过TCP Socket连接到服务器指定端口（默认8888）。

### 2. 用户认证
客户端发送登录或注册请求，服务器验证后返回响应。

### 3. 消息交互
认证成功后，客户端可以发送各种请求消息，服务器处理后返回相应响应。

### 4. 实时消息
服务器会主动向客户端推送聊天消息、系统通知等。

### 5. 断开连接
客户端发送登出请求或直接关闭连接。

## 使用示例

### Python客户端示例

```python
import socket
import json
from shared.messages import LoginRequest, parse_message

# 连接服务器
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8888))

# 发送登录请求
login_msg = LoginRequest(username="alice", password="password123")
sock.send((login_msg.to_json() + '\n').encode('utf-8'))

# 接收响应
response_data = sock.recv(4096).decode('utf-8')
response = parse_message(response_data.strip())

if response.success:
    print(f"登录成功: {response.username}")
else:
    print(f"登录失败: {response.error_message}")

sock.close()
```

## 注意事项

1. **消息分隔**: 所有消息以换行符(\n)结尾
2. **编码格式**: 使用UTF-8编码
3. **JSON格式**: 严格遵循JSON格式，确保可解析
4. **时间戳**: 使用Unix时间戳（浮点数）
5. **错误处理**: 客户端应妥善处理各种错误响应
6. **连接管理**: 客户端应实现重连机制
7. **消息顺序**: 服务器不保证消息的严格顺序
8. **缓冲处理**: 客户端应正确处理TCP缓冲区的消息分片

## 扩展性

协议设计考虑了扩展性，新的消息类型可以通过以下方式添加：

1. 在`shared/constants.py`中定义新的消息类型常量
2. 在`shared/messages.py`中定义新的消息类
3. 在服务器和客户端中添加相应的处理逻辑

这种设计确保了向后兼容性和功能扩展的便利性。
