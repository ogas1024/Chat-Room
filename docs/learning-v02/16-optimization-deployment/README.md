# 第11章：部署与性能优化

## 🎯 学习目标

通过本章学习，您将能够：
- 掌握Chat-Room项目的部署策略
- 学会性能监控和优化技术
- 实现系统的可扩展性设计
- 掌握容器化部署方法
- 了解云平台部署选项
- 确保生产环境的稳定运行

## 📚 章节内容

### 1. 部署基础
- [生产环境部署指南](production-deployment.md)
- [容器化与Docker部署](docker-deployment.md)

### 2. 性能优化
- [系统性能监控](performance-monitoring.md)
- [性能优化策略](optimization-strategies.md)

### 3. 运维管理
- [日志管理与监控](logging-monitoring.md)
- [故障排除与恢复](troubleshooting.md)

## 🚀 部署架构设计

```mermaid
graph TD
    A[Chat-Room部署架构] --> B[负载均衡层]
    A --> C[应用服务层]
    A --> D[数据存储层]
    A --> E[监控运维层]
    
    B --> B1[Nginx负载均衡]
    B --> B2[SSL/TLS终端]
    B --> B3[静态资源服务]
    
    C --> C1[Chat-Room服务器集群]
    C --> C2[AI服务集群]
    C --> C3[文件服务集群]
    C --> C4[WebSocket网关]
    
    D --> D1[主数据库]
    D --> D2[读副本数据库]
    D --> D3[Redis缓存]
    D --> D4[文件存储]
    
    E --> E1[Prometheus监控]
    E --> E2[Grafana仪表板]
    E --> E3[ELK日志栈]
    E --> E4[告警系统]
    
    style A fill:#e8f5e8
    style B fill:#fff3cd
    style C fill:#f8d7da
    style D fill:#e1f5fe
    style E fill:#f3e5f5
```

## 🐳 容器化部署

### Docker配置

```dockerfile
# Chat-Room服务器Dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 chatroom && \
    chown -R chatroom:chatroom /app
USER chatroom

# 暴露端口
EXPOSE 8888

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 8888)); s.close()" || exit 1

# 启动命令
CMD ["python", "-m", "server.main"]
```

```yaml
# docker-compose.yml - 完整部署配置
version: '3.8'

services:
  # Chat-Room服务器
  chatroom-server:
    build: .
    ports:
      - "8888:8888"
    environment:
      - DATABASE_URL=postgresql://chatroom:password@postgres:5432/chatroom
      - REDIS_URL=redis://redis:6379/0
      - AI_API_KEY=${AI_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    networks:
      - chatroom-network
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

  # 数据库
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=chatroom
      - POSTGRES_USER=chatroom
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - chatroom-network
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.3'

  # Redis缓存
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped
    networks:
      - chatroom-network
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.1'

  # Nginx负载均衡
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - chatroom-server
    restart: unless-stopped
    networks:
      - chatroom-network

  # 监控系统
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped
    networks:
      - chatroom-network

  # Grafana仪表板
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped
    networks:
      - chatroom-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  chatroom-network:
    driver: bridge
```

## 📊 性能监控实现

### 系统监控

```python
"""
Chat-Room性能监控系统
实现全面的系统监控和性能指标收集
"""

import psutil
import time
import threading
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import sqlite3
from shared.logger import get_logger

logger = get_logger("monitoring")

@dataclass
class SystemMetrics:
    """系统指标"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    load_average: List[float]

@dataclass
class ApplicationMetrics:
    """应用指标"""
    timestamp: float
    active_users: int
    total_messages: int
    messages_per_minute: int
    ai_requests_per_minute: int
    file_transfers_active: int
    database_connections: int
    response_time_avg: float
    error_rate: float

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, collection_interval: float = 60.0):
        self.collection_interval = collection_interval
        self.running = False
        self.metrics_history: List[SystemMetrics] = []
        self.app_metrics_history: List[ApplicationMetrics] = []
        self.max_history_size = 1440  # 24小时的分钟数
        
        # 网络统计基线
        self.network_baseline = psutil.net_io_counters()
        
        # 应用指标回调
        self.app_metrics_callback: Optional[callable] = None
    
    def start_collection(self):
        """开始收集指标"""
        self.running = True
        
        collection_thread = threading.Thread(
            target=self._collection_loop,
            daemon=True
        )
        collection_thread.start()
        
        logger.info("指标收集器已启动")
    
    def stop_collection(self):
        """停止收集指标"""
        self.running = False
        logger.info("指标收集器已停止")
    
    def _collection_loop(self):
        """指标收集循环"""
        while self.running:
            try:
                # 收集系统指标
                system_metrics = self._collect_system_metrics()
                self.metrics_history.append(system_metrics)
                
                # 收集应用指标
                if self.app_metrics_callback:
                    app_metrics = self.app_metrics_callback()
                    if app_metrics:
                        self.app_metrics_history.append(app_metrics)
                
                # 限制历史记录大小
                if len(self.metrics_history) > self.max_history_size:
                    self.metrics_history.pop(0)
                
                if len(self.app_metrics_history) > self.max_history_size:
                    self.app_metrics_history.pop(0)
                
                # 记录关键指标
                self._log_metrics(system_metrics)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"指标收集失败: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 网络统计
        network = psutil.net_io_counters()
        
        # 网络连接数
        connections = len(psutil.net_connections())
        
        # 系统负载
        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            # Windows系统不支持getloadavg
            load_avg = [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_usage_percent=disk.percent,
            disk_free_gb=disk.free / 1024 / 1024 / 1024,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            active_connections=connections,
            load_average=load_avg
        )
    
    def _log_metrics(self, metrics: SystemMetrics):
        """记录关键指标"""
        
        # 记录高CPU使用率
        if metrics.cpu_percent > 80:
            logger.warning(f"高CPU使用率: {metrics.cpu_percent:.1f}%")
        
        # 记录高内存使用率
        if metrics.memory_percent > 85:
            logger.warning(f"高内存使用率: {metrics.memory_percent:.1f}%")
        
        # 记录磁盘空间不足
        if metrics.disk_usage_percent > 90:
            logger.warning(f"磁盘空间不足: {metrics.disk_usage_percent:.1f}%")
        
        # 记录高连接数
        if metrics.active_connections > 1000:
            logger.warning(f"高连接数: {metrics.active_connections}")
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """获取当前指标"""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """获取指标摘要"""
        
        if not self.metrics_history:
            return {}
        
        # 计算时间范围
        cutoff_time = time.time() - (hours * 3600)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
        
        # 计算统计信息
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        return {
            "time_range_hours": hours,
            "sample_count": len(recent_metrics),
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "current": asdict(recent_metrics[-1])
        }

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.optimization_rules = []
        self.running = False
        
        # 注册优化规则
        self._register_optimization_rules()
    
    def _register_optimization_rules(self):
        """注册优化规则"""
        
        self.optimization_rules = [
            {
                "name": "高CPU使用率优化",
                "condition": lambda m: m.cpu_percent > 80,
                "action": self._optimize_cpu_usage,
                "cooldown": 300  # 5分钟冷却时间
            },
            {
                "name": "高内存使用率优化",
                "condition": lambda m: m.memory_percent > 85,
                "action": self._optimize_memory_usage,
                "cooldown": 300
            },
            {
                "name": "连接数优化",
                "condition": lambda m: m.active_connections > 500,
                "action": self._optimize_connections,
                "cooldown": 600  # 10分钟冷却时间
            }
        ]
    
    def start_optimization(self):
        """开始性能优化"""
        self.running = True
        
        optimization_thread = threading.Thread(
            target=self._optimization_loop,
            daemon=True
        )
        optimization_thread.start()
        
        logger.info("性能优化器已启动")
    
    def stop_optimization(self):
        """停止性能优化"""
        self.running = False
        logger.info("性能优化器已停止")
    
    def _optimization_loop(self):
        """优化循环"""
        rule_last_triggered = {}
        
        while self.running:
            try:
                current_metrics = self.metrics_collector.get_current_metrics()
                if not current_metrics:
                    time.sleep(60)
                    continue
                
                current_time = time.time()
                
                # 检查优化规则
                for rule in self.optimization_rules:
                    rule_name = rule["name"]
                    
                    # 检查冷却时间
                    last_triggered = rule_last_triggered.get(rule_name, 0)
                    if current_time - last_triggered < rule["cooldown"]:
                        continue
                    
                    # 检查触发条件
                    if rule["condition"](current_metrics):
                        logger.info(f"触发优化规则: {rule_name}")
                        
                        try:
                            rule["action"](current_metrics)
                            rule_last_triggered[rule_name] = current_time
                        except Exception as e:
                            logger.error(f"执行优化规则失败 {rule_name}: {e}")
                
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                logger.error(f"优化循环失败: {e}")
                time.sleep(60)
    
    def _optimize_cpu_usage(self, metrics: SystemMetrics):
        """优化CPU使用率"""
        logger.info("执行CPU优化策略")
        
        # 实施CPU优化策略
        # 1. 降低非关键任务的优先级
        # 2. 启用CPU缓存
        # 3. 优化算法复杂度
        
        # 示例：触发垃圾回收
        import gc
        gc.collect()
        
        logger.info("CPU优化策略执行完成")
    
    def _optimize_memory_usage(self, metrics: SystemMetrics):
        """优化内存使用率"""
        logger.info("执行内存优化策略")
        
        # 实施内存优化策略
        # 1. 清理缓存
        # 2. 释放不必要的对象
        # 3. 优化数据结构
        
        # 示例：强制垃圾回收
        import gc
        collected = gc.collect()
        logger.info(f"垃圾回收释放了 {collected} 个对象")
        
        logger.info("内存优化策略执行完成")
    
    def _optimize_connections(self, metrics: SystemMetrics):
        """优化连接数"""
        logger.info("执行连接优化策略")
        
        # 实施连接优化策略
        # 1. 清理空闲连接
        # 2. 启用连接池
        # 3. 实施连接限制
        
        logger.info("连接优化策略执行完成")

class AlertManager:
    """告警管理器"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.alert_rules = []
        self.alert_history = []
        self.running = False
        
        # 注册告警规则
        self._register_alert_rules()
    
    def _register_alert_rules(self):
        """注册告警规则"""
        
        self.alert_rules = [
            {
                "name": "CPU使用率过高",
                "condition": lambda m: m.cpu_percent > 90,
                "severity": "critical",
                "message": "CPU使用率超过90%"
            },
            {
                "name": "内存使用率过高",
                "condition": lambda m: m.memory_percent > 95,
                "severity": "critical",
                "message": "内存使用率超过95%"
            },
            {
                "name": "磁盘空间不足",
                "condition": lambda m: m.disk_usage_percent > 95,
                "severity": "warning",
                "message": "磁盘使用率超过95%"
            }
        ]
    
    def start_monitoring(self):
        """开始监控告警"""
        self.running = True
        
        monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        monitoring_thread.start()
        
        logger.info("告警监控已启动")
    
    def stop_monitoring(self):
        """停止监控告警"""
        self.running = False
        logger.info("告警监控已停止")
    
    def _monitoring_loop(self):
        """监控循环"""
        while self.running:
            try:
                current_metrics = self.metrics_collector.get_current_metrics()
                if not current_metrics:
                    time.sleep(30)
                    continue
                
                # 检查告警规则
                for rule in self.alert_rules:
                    if rule["condition"](current_metrics):
                        self._trigger_alert(rule, current_metrics)
                
                time.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                logger.error(f"告警监控失败: {e}")
                time.sleep(30)
    
    def _trigger_alert(self, rule: Dict[str, Any], metrics: SystemMetrics):
        """触发告警"""
        
        alert = {
            "timestamp": time.time(),
            "rule_name": rule["name"],
            "severity": rule["severity"],
            "message": rule["message"],
            "metrics": asdict(metrics)
        }
        
        self.alert_history.append(alert)
        
        # 记录告警日志
        log_level = logger.critical if rule["severity"] == "critical" else logger.warning
        log_level(f"告警触发: {rule['name']} - {rule['message']}")
        
        # 发送告警通知（邮件、短信、Webhook等）
        self._send_alert_notification(alert)
    
    def _send_alert_notification(self, alert: Dict[str, Any]):
        """发送告警通知"""
        # TODO: 实现告警通知机制
        # 可以集成邮件、短信、Slack、钉钉等通知方式
        pass

# 使用示例
def setup_monitoring_system():
    """设置监控系统"""
    
    # 创建指标收集器
    metrics_collector = MetricsCollector(collection_interval=60.0)
    
    # 创建性能优化器
    optimizer = PerformanceOptimizer(metrics_collector)
    
    # 创建告警管理器
    alert_manager = AlertManager(metrics_collector)
    
    # 启动监控系统
    metrics_collector.start_collection()
    optimizer.start_optimization()
    alert_manager.start_monitoring()
    
    logger.info("监控系统已启动")
    
    return {
        "metrics_collector": metrics_collector,
        "optimizer": optimizer,
        "alert_manager": alert_manager
    }

if __name__ == "__main__":
    monitoring_system = setup_monitoring_system()
    
    try:
        # 保持程序运行
        while True:
            time.sleep(60)
            
            # 显示当前指标
            current_metrics = monitoring_system["metrics_collector"].get_current_metrics()
            if current_metrics:
                print(f"CPU: {current_metrics.cpu_percent:.1f}%, "
                      f"内存: {current_metrics.memory_percent:.1f}%, "
                      f"连接数: {current_metrics.active_connections}")
    
    except KeyboardInterrupt:
        logger.info("停止监控系统")
        monitoring_system["metrics_collector"].stop_collection()
        monitoring_system["optimizer"].stop_optimization()
        monitoring_system["alert_manager"].stop_monitoring()
```

## 📋 学习检查清单

完成本章学习后，请确认您能够：

### 部署基础
- [ ] 理解生产环境部署的要求和挑战
- [ ] 掌握Docker容器化部署方法
- [ ] 配置负载均衡和反向代理
- [ ] 实现数据库和缓存的部署

### 性能监控
- [ ] 实现系统指标的收集和监控
- [ ] 设置性能告警和通知机制
- [ ] 使用监控工具分析系统状态
- [ ] 建立性能基线和趋势分析

### 优化策略
- [ ] 识别性能瓶颈和优化点
- [ ] 实现自动化性能优化
- [ ] 优化数据库查询和连接
- [ ] 实现缓存策略和CDN加速

### 运维管理
- [ ] 建立日志管理和分析系统
- [ ] 实现故障检测和自动恢复
- [ ] 制定备份和灾难恢复计划
- [ ] 建立运维监控和告警体系

## 🔗 相关资源

- [Docker官方文档](https://docs.docker.com/)
- [Kubernetes部署指南](https://kubernetes.io/docs/)
- [Prometheus监控系统](https://prometheus.io/docs/)
- [Nginx配置指南](https://nginx.org/en/docs/)

## 📚 下一步

部署与性能优化学习完成后，请继续学习：
- [生产环境部署指南](production-deployment.md)

---

**掌握部署和优化技能，让Chat-Room在生产环境中稳定高效运行！** 🚀
