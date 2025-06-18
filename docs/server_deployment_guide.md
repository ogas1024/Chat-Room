# Chat-Room 服务器部署指南

## 问题诊断结果

✅ **客户端配置正常** - 已正确读取配置文件中的服务器地址 `47.116.210.212:8888`  
✅ **网络连通性正常** - 服务器地址可达（ping成功）  
❌ **服务器端口不可达** - 8888端口连接被拒绝

## 解决方案

### 1. 服务器配置修改

确保服务器配置文件 `config/server_config.yaml` 中的设置正确：

```yaml
server:
  host: 0.0.0.0  # 重要：必须是 0.0.0.0 才能接受外部连接
  port: 8888
  max_connections: 100
  # ... 其他配置
```

**注意：** 
- `host: localhost` 或 `host: 127.0.0.1` 只允许本地连接
- `host: 0.0.0.0` 允许所有网络接口的连接

### 2. 在远程服务器上启动Chat-Room服务

#### 方法1：前台运行（用于测试）
```bash
# 激活conda环境
conda activate chatroom

# 启动服务器
python -m server.main
```

#### 方法2：后台运行（用于生产）
```bash
# 激活conda环境
conda activate chatroom

# 后台启动服务器
nohup python -m server.main > server.log 2>&1 &

# 查看进程
ps aux | grep python

# 查看日志
tail -f server.log
```

#### 方法3：使用systemd服务（推荐生产环境）
创建服务文件 `/etc/systemd/system/chatroom.service`：

```ini
[Unit]
Description=Chat-Room Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/Chat-Room
Environment=PATH=/path/to/conda/envs/chatroom/bin
ExecStart=/path/to/conda/envs/chatroom/bin/python -m server.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable chatroom
sudo systemctl start chatroom
sudo systemctl status chatroom
```

### 3. 防火墙配置

#### Ubuntu/Debian (ufw)
```bash
# 开放8888端口
sudo ufw allow 8888

# 查看防火墙状态
sudo ufw status
```

#### CentOS/RHEL (firewalld)
```bash
# 开放8888端口
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --reload

# 查看开放的端口
sudo firewall-cmd --list-ports
```

#### 直接使用iptables
```bash
# 开放8888端口
sudo iptables -A INPUT -p tcp --dport 8888 -j ACCEPT

# 保存规则
sudo iptables-save > /etc/iptables/rules.v4
```

### 4. 云服务器安全组配置

如果使用云服务器（阿里云、腾讯云、AWS等），需要在控制台配置安全组：

1. 登录云服务器控制台
2. 找到安全组设置
3. 添加入站规则：
   - 协议：TCP
   - 端口：8888
   - 源地址：0.0.0.0/0（允许所有IP）或指定IP段

### 5. 验证部署

#### 在服务器上验证
```bash
# 检查端口监听
netstat -tlnp | grep 8888
# 或
ss -tlnp | grep 8888

# 测试本地连接
telnet localhost 8888
```

#### 从客户端验证
```bash
# 使用诊断工具
python diagnose_connection.py

# 或直接运行客户端
python -m client.main --mode simple
```

## 常见问题排查

### 问题1：连接被拒绝（Connection refused）
- **原因：** 服务器程序未运行或端口未监听
- **解决：** 检查服务器程序是否正常启动

### 问题2：连接超时（Connection timeout）
- **原因：** 防火墙阻止或安全组未开放端口
- **解决：** 检查防火墙和云服务器安全组设置

### 问题3：服务器只能本地连接
- **原因：** 服务器配置 `host: localhost`
- **解决：** 修改为 `host: 0.0.0.0`

### 问题4：权限不足
- **原因：** 用户权限不足或端口被占用
- **解决：** 使用sudo或更换端口

## 部署检查清单

- [ ] 服务器配置文件 `host: 0.0.0.0`
- [ ] 服务器程序正在运行
- [ ] 端口8888正在监听
- [ ] 本地防火墙开放8888端口
- [ ] 云服务器安全组开放8888端口
- [ ] 客户端配置文件指向正确的服务器地址
- [ ] 网络连通性正常（ping通）

## 快速部署命令

```bash
# 1. 修改服务器配置（如果需要）
sed -i 's/host: localhost/host: 0.0.0.0/' config/server_config.yaml

# 2. 启动服务器
conda activate chatroom
nohup python -m server.main > server.log 2>&1 &

# 3. 开放防火墙端口
sudo ufw allow 8888

# 4. 验证部署
python diagnose_connection.py
```

完成以上步骤后，客户端应该能够成功连接到远程服务器。
