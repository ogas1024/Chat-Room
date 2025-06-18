# 容器化部署

## 🎯 学习目标

通过本章学习，您将能够：
- 理解现代容器化技术的核心概念和优势
- 掌握Docker容器化和Kubernetes编排技术
- 学会为Chat-Room项目设计容器化部署方案
- 实现自动化部署和运维管理流程

## 🐳 容器化架构

### 容器化技术栈

```mermaid
graph TB
    subgraph "容器化技术栈"
        A[应用层<br/>Application Layer] --> A1[Chat-Room服务<br/>Chat-Room Services]
        A --> A2[Web界面<br/>Web Interface]
        A --> A3[API网关<br/>API Gateway]
        
        B[容器层<br/>Container Layer] --> B1[Docker容器<br/>Docker Containers]
        B --> B2[容器镜像<br/>Container Images]
        B --> B3[容器网络<br/>Container Network]
        
        C[编排层<br/>Orchestration Layer] --> C1[Kubernetes<br/>K8s Cluster]
        C --> C2[Docker Compose<br/>Local Development]
        C --> C3[服务发现<br/>Service Discovery]
        
        D[基础设施层<br/>Infrastructure Layer] --> D1[云平台<br/>Cloud Platform]
        D --> D2[虚拟机<br/>Virtual Machines]
        D --> D3[物理服务器<br/>Physical Servers]
    end
    
    A --> B
    B --> C
    C --> D
    
    style A fill:#e8f5e8
    style D fill:#f8d7da
```

### 部署架构图

```mermaid
graph LR
    subgraph "开发环境"
        A[开发者<br/>Developer] --> B[Git仓库<br/>Git Repository]
    end
    
    subgraph "CI/CD流水线"
        B --> C[构建<br/>Build]
        C --> D[测试<br/>Test]
        D --> E[打包<br/>Package]
        E --> F[镜像仓库<br/>Image Registry]
    end
    
    subgraph "部署环境"
        F --> G[Kubernetes集群<br/>K8s Cluster]
        G --> H[Chat-Room服务<br/>Chat-Room Services]
        G --> I[数据库<br/>Database]
        G --> J[监控系统<br/>Monitoring]
    end
    
    style A fill:#e8f5e8
    style G fill:#fff3cd
    style H fill:#f8d7da
```

## 🔧 容器化实现

### Chat-Room Docker配置

```dockerfile
# Dockerfile - Chat-Room服务容器化
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY requirements-dev.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN groupadd -r chatroom && useradd -r -g chatroom chatroom
RUN chown -R chatroom:chatroom /app
USER chatroom

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 暴露端口
EXPOSE 8000 8001

# 启动命令
CMD ["python", "-m", "server.main"]
```

```yaml
# docker-compose.yml - 本地开发环境
version: '3.8'

services:
  # Chat-Room服务器
  chatroom-server:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://chatroom:password@postgres:5432/chatroom
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    depends_on:
      - postgres
      - redis
    networks:
      - chatroom-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=chatroom
      - POSTGRES_USER=chatroom
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - chatroom-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U chatroom"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - chatroom-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./static:/var/www/static
    depends_on:
      - chatroom-server
    networks:
      - chatroom-network
    restart: unless-stopped

  # 监控系统
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - chatroom-network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    depends_on:
      - prometheus
    networks:
      - chatroom-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  chatroom-network:
    driver: bridge
```

### Kubernetes部署配置

```yaml
# k8s/namespace.yaml - 命名空间
apiVersion: v1
kind: Namespace
metadata:
  name: chatroom
  labels:
    name: chatroom
    environment: production

---
# k8s/configmap.yaml - 配置映射
apiVersion: v1
kind: ConfigMap
metadata:
  name: chatroom-config
  namespace: chatroom
data:
  DATABASE_URL: "postgresql://chatroom:password@postgres-service:5432/chatroom"
  REDIS_URL: "redis://redis-service:6379/0"
  LOG_LEVEL: "INFO"
  MAX_CONNECTIONS: "1000"
  WORKER_PROCESSES: "4"

---
# k8s/secret.yaml - 密钥管理
apiVersion: v1
kind: Secret
metadata:
  name: chatroom-secrets
  namespace: chatroom
type: Opaque
data:
  database-password: cGFzc3dvcmQ=  # base64编码的password
  jwt-secret: c2VjcmV0LWtleQ==      # base64编码的secret-key
  api-key: YXBpLWtleS12YWx1ZQ==     # base64编码的api-key-value

---
# k8s/deployment.yaml - 应用部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatroom-server
  namespace: chatroom
  labels:
    app: chatroom-server
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatroom-server
  template:
    metadata:
      labels:
        app: chatroom-server
        version: v1.0.0
    spec:
      containers:
      - name: chatroom-server
        image: chatroom/server:latest
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 8001
          name: websocket
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: chatroom-config
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: chatroom-config
              key: REDIS_URL
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: chatroom-secrets
              key: database-password
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: logs-volume
          mountPath: /app/logs
      volumes:
      - name: config-volume
        configMap:
          name: chatroom-config
      - name: logs-volume
        emptyDir: {}
      restartPolicy: Always

---
# k8s/service.yaml - 服务定义
apiVersion: v1
kind: Service
metadata:
  name: chatroom-service
  namespace: chatroom
  labels:
    app: chatroom-server
spec:
  selector:
    app: chatroom-server
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
  - name: websocket
    port: 8001
    targetPort: 8001
    protocol: TCP
  type: ClusterIP

---
# k8s/ingress.yaml - 入口控制器
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: chatroom-ingress
  namespace: chatroom
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/websocket-services: chatroom-service
spec:
  tls:
  - hosts:
    - chat.example.com
    secretName: chatroom-tls
  rules:
  - host: chat.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: chatroom-service
            port:
              number: 80
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: chatroom-service
            port:
              number: 8001

---
# k8s/hpa.yaml - 水平自动扩缩容
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: chatroom-hpa
  namespace: chatroom
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: chatroom-server
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### 部署脚本

```python
# deploy/deployment_manager.py - 部署管理器
import subprocess
import yaml
import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

class DeploymentManager:
    """
    部署管理器
    
    功能：
    1. Docker镜像构建和推送
    2. Kubernetes资源部署
    3. 部署状态监控
    4. 回滚和故障恢复
    """
    
    def __init__(self, config_path: str = "deploy/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载部署配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # 默认配置
        return {
            "docker": {
                "registry": "docker.io",
                "repository": "chatroom",
                "tag": "latest"
            },
            "kubernetes": {
                "namespace": "chatroom",
                "context": "default"
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("deployment")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def build_docker_image(self, dockerfile: str = "Dockerfile", 
                          tag: Optional[str] = None) -> bool:
        """构建Docker镜像"""
        try:
            if not tag:
                tag = f"{self.config['docker']['repository']}:{self.config['docker']['tag']}"
            
            self.logger.info(f"构建Docker镜像: {tag}")
            
            cmd = ["docker", "build", "-t", tag, "-f", dockerfile, "."]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Docker镜像构建成功")
                return True
            else:
                self.logger.error(f"Docker镜像构建失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"构建Docker镜像时发生错误: {e}")
            return False
    
    def push_docker_image(self, tag: Optional[str] = None) -> bool:
        """推送Docker镜像"""
        try:
            if not tag:
                tag = f"{self.config['docker']['repository']}:{self.config['docker']['tag']}"
            
            self.logger.info(f"推送Docker镜像: {tag}")
            
            cmd = ["docker", "push", tag]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Docker镜像推送成功")
                return True
            else:
                self.logger.error(f"Docker镜像推送失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"推送Docker镜像时发生错误: {e}")
            return False
    
    def deploy_to_kubernetes(self, manifest_dir: str = "k8s") -> bool:
        """部署到Kubernetes"""
        try:
            manifest_path = Path(manifest_dir)
            if not manifest_path.exists():
                self.logger.error(f"Kubernetes清单目录不存在: {manifest_dir}")
                return False
            
            self.logger.info("开始部署到Kubernetes")
            
            # 应用所有YAML文件
            for yaml_file in manifest_path.glob("*.yaml"):
                self.logger.info(f"应用清单文件: {yaml_file}")
                
                cmd = ["kubectl", "apply", "-f", str(yaml_file)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    self.logger.error(f"应用清单文件失败: {result.stderr}")
                    return False
            
            self.logger.info("Kubernetes部署成功")
            return True
            
        except Exception as e:
            self.logger.error(f"部署到Kubernetes时发生错误: {e}")
            return False
    
    def check_deployment_status(self, deployment_name: str = "chatroom-server") -> Dict[str, Any]:
        """检查部署状态"""
        try:
            namespace = self.config["kubernetes"]["namespace"]
            
            cmd = ["kubectl", "get", "deployment", deployment_name, 
                   "-n", namespace, "-o", "json"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                deployment_info = json.loads(result.stdout)
                status = deployment_info.get("status", {})
                
                return {
                    "ready": status.get("readyReplicas", 0),
                    "desired": status.get("replicas", 0),
                    "available": status.get("availableReplicas", 0),
                    "updated": status.get("updatedReplicas", 0),
                    "conditions": status.get("conditions", [])
                }
            else:
                self.logger.error(f"获取部署状态失败: {result.stderr}")
                return {}
                
        except Exception as e:
            self.logger.error(f"检查部署状态时发生错误: {e}")
            return {}
    
    def wait_for_deployment(self, deployment_name: str = "chatroom-server", 
                           timeout: int = 300) -> bool:
        """等待部署完成"""
        try:
            namespace = self.config["kubernetes"]["namespace"]
            
            self.logger.info(f"等待部署完成: {deployment_name}")
            
            cmd = ["kubectl", "rollout", "status", f"deployment/{deployment_name}",
                   "-n", namespace, f"--timeout={timeout}s"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("部署完成")
                return True
            else:
                self.logger.error(f"部署超时或失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"等待部署时发生错误: {e}")
            return False
    
    def rollback_deployment(self, deployment_name: str = "chatroom-server") -> bool:
        """回滚部署"""
        try:
            namespace = self.config["kubernetes"]["namespace"]
            
            self.logger.info(f"回滚部署: {deployment_name}")
            
            cmd = ["kubectl", "rollout", "undo", f"deployment/{deployment_name}",
                   "-n", namespace]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("部署回滚成功")
                return True
            else:
                self.logger.error(f"部署回滚失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"回滚部署时发生错误: {e}")
            return False
    
    def full_deployment_pipeline(self) -> bool:
        """完整部署流水线"""
        self.logger.info("开始完整部署流水线")
        
        # 1. 构建Docker镜像
        if not self.build_docker_image():
            return False
        
        # 2. 推送Docker镜像
        if not self.push_docker_image():
            return False
        
        # 3. 部署到Kubernetes
        if not self.deploy_to_kubernetes():
            return False
        
        # 4. 等待部署完成
        if not self.wait_for_deployment():
            self.logger.error("部署失败，开始回滚")
            self.rollback_deployment()
            return False
        
        # 5. 验证部署状态
        status = self.check_deployment_status()
        if status.get("ready", 0) == status.get("desired", 0):
            self.logger.info("部署流水线完成")
            return True
        else:
            self.logger.error("部署验证失败")
            return False

# 使用示例
def demo_containerization_deployment():
    """容器化部署演示"""
    print("=== Chat-Room容器化部署演示 ===")
    
    deployment_manager = DeploymentManager()
    
    print("1. 构建Docker镜像...")
    # success = deployment_manager.build_docker_image()
    # print(f"构建结果: {'成功' if success else '失败'}")
    
    print("2. 部署到Kubernetes...")
    # success = deployment_manager.deploy_to_kubernetes()
    # print(f"部署结果: {'成功' if success else '失败'}")
    
    print("3. 检查部署状态...")
    # status = deployment_manager.check_deployment_status()
    # print(f"部署状态: {status}")
    
    # 模拟部署状态
    mock_status = {
        "ready": 3,
        "desired": 3,
        "available": 3,
        "updated": 3
    }
    
    print(f"模拟部署状态: {mock_status}")
    print("部署完成！")
    
    print("\n4. 部署配置说明:")
    print("- Docker多阶段构建优化镜像大小")
    print("- Kubernetes水平自动扩缩容")
    print("- 健康检查和就绪探针")
    print("- 配置和密钥管理")
    print("- 服务发现和负载均衡")
    print("- SSL/TLS终端和入口控制")

if __name__ == "__main__":
    demo_containerization_deployment()
```

## 🎯 实践练习

### 练习1：多环境部署策略
```python
class MultiEnvironmentDeployment:
    """
    多环境部署策略练习
    
    要求：
    1. 实现开发、测试、生产环境配置
    2. 支持蓝绿部署和金丝雀发布
    3. 实现环境间的配置管理
    4. 添加部署审批和回滚机制
    """
    
    def deploy_to_environment(self, env: str, strategy: str) -> bool:
        """部署到指定环境"""
        # TODO: 实现多环境部署
        pass
    
    def canary_deployment(self, percentage: int) -> bool:
        """金丝雀部署"""
        # TODO: 实现金丝雀部署
        pass
```

### 练习2：监控和日志集成
```python
class MonitoringIntegration:
    """
    监控和日志集成练习
    
    要求：
    1. 集成Prometheus和Grafana监控
    2. 实现ELK日志收集和分析
    3. 设置告警和通知机制
    4. 添加性能指标和业务指标
    """
    
    def setup_monitoring(self, config: Dict[str, Any]) -> bool:
        """设置监控系统"""
        # TODO: 实现监控设置
        pass
    
    def configure_logging(self, log_config: Dict[str, Any]) -> bool:
        """配置日志系统"""
        # TODO: 实现日志配置
        pass
```

## ✅ 学习检查

完成本章学习后，请确认您能够：

- [ ] 理解容器化技术的核心概念和优势
- [ ] 编写Dockerfile和docker-compose配置
- [ ] 设计Kubernetes部署清单和策略
- [ ] 实现自动化部署和CI/CD流水线
- [ ] 配置服务发现和负载均衡
- [ ] 完成实践练习

## 📚 下一步

容器化部署掌握后，请继续学习：
- [CI/CD自动化](./cicd-automation.md)

---

**恭喜！您已经掌握了现代容器化部署技术！** 🐳
