# CI/CD自动化流水线

## 🎯 学习目标

通过本章学习，您将能够：
- 理解现代CI/CD流水线的设计理念和最佳实践
- 掌握GitHub Actions、GitLab CI等自动化工具
- 学会为Chat-Room项目设计完整的CI/CD流程
- 实现代码质量检查和自动化部署机制

## 🔄 CI/CD流水线架构

### CI/CD流程图

```mermaid
graph LR
    subgraph "持续集成 (CI)"
        A[代码提交<br/>Code Commit] --> B[代码检查<br/>Code Review]
        B --> C[自动构建<br/>Build]
        C --> D[单元测试<br/>Unit Tests]
        D --> E[集成测试<br/>Integration Tests]
        E --> F[代码质量检查<br/>Quality Check]
        F --> G[安全扫描<br/>Security Scan]
    end
    
    subgraph "持续部署 (CD)"
        G --> H[构建镜像<br/>Build Image]
        H --> I[推送镜像<br/>Push Image]
        I --> J[部署到测试环境<br/>Deploy to Test]
        J --> K[自动化测试<br/>Automated Tests]
        K --> L[部署到生产环境<br/>Deploy to Prod]
        L --> M[监控和告警<br/>Monitor & Alert]
    end
    
    style A fill:#e8f5e8
    style M fill:#f8d7da
```

### 流水线阶段详解

```mermaid
graph TB
    subgraph "代码阶段"
        A1[源码管理<br/>Source Control] --> A2[分支策略<br/>Branch Strategy]
        A2 --> A3[代码审查<br/>Code Review]
        A3 --> A4[合并请求<br/>Merge Request]
    end
    
    subgraph "构建阶段"
        B1[依赖安装<br/>Install Dependencies] --> B2[代码编译<br/>Compile Code]
        B2 --> B3[静态分析<br/>Static Analysis]
        B3 --> B4[构建产物<br/>Build Artifacts]
    end
    
    subgraph "测试阶段"
        C1[单元测试<br/>Unit Tests] --> C2[集成测试<br/>Integration Tests]
        C2 --> C3[端到端测试<br/>E2E Tests]
        C3 --> C4[性能测试<br/>Performance Tests]
    end
    
    subgraph "部署阶段"
        D1[镜像构建<br/>Image Build] --> D2[镜像扫描<br/>Image Scan]
        D2 --> D3[环境部署<br/>Environment Deploy]
        D3 --> D4[健康检查<br/>Health Check]
    end
    
    A4 --> B1
    B4 --> C1
    C4 --> D1
    
    style A1 fill:#e8f5e8
    style D4 fill:#f8d7da
```

## 🔧 CI/CD实现

### GitHub Actions配置

```yaml
# .github/workflows/ci-cd.yml - GitHub Actions CI/CD流水线
name: Chat-Room CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'
  DOCKER_REGISTRY: ghcr.io
  IMAGE_NAME: chatroom

jobs:
  # 代码质量检查
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout代码
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: 设置Python环境
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: 安装依赖
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: 代码格式检查
      run: |
        black --check .
        isort --check-only .
        flake8 .

    - name: 类型检查
      run: mypy .

    - name: 安全扫描
      run: |
        bandit -r . -f json -o bandit-report.json
        safety check --json --output safety-report.json

    - name: 上传安全报告
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json

  # 单元测试
  unit-tests:
    runs-on: ubuntu-latest
    needs: code-quality
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - name: Checkout代码
      uses: actions/checkout@v4

    - name: 设置Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: 安装依赖
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: 运行单元测试
      run: |
        pytest tests/unit/ \
          --cov=. \
          --cov-report=xml \
          --cov-report=html \
          --junitxml=junit.xml \
          -v

    - name: 上传覆盖率报告
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

    - name: 上传测试结果
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.python-version }}
        path: |
          junit.xml
          htmlcov/

  # 集成测试
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: chatroom_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - name: Checkout代码
      uses: actions/checkout@v4

    - name: 设置Python环境
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: 安装依赖
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: 运行集成测试
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/chatroom_test
        REDIS_URL: redis://localhost:6379/0
      run: |
        pytest tests/integration/ \
          --cov=. \
          --cov-append \
          --cov-report=xml \
          --junitxml=integration-junit.xml \
          -v

    - name: 上传集成测试结果
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: integration-test-results
        path: integration-junit.xml

  # Docker镜像构建
  build-image:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    if: github.event_name != 'pull_request'
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    
    steps:
    - name: Checkout代码
      uses: actions/checkout@v4

    - name: 设置Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: 登录Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.DOCKER_REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: 提取元数据
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.DOCKER_REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=semver,pattern={{version}}
          type=semver,pattern={{major}}.{{minor}}
          type=sha,prefix={{branch}}-

    - name: 构建并推送Docker镜像
      id: build
      uses: docker/build-push-action@v5
      with:
        context: .
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: 镜像安全扫描
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ steps.meta.outputs.tags }}
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: 上传安全扫描结果
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

  # 部署到测试环境
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-image
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.chatroom.example.com
    
    steps:
    - name: Checkout代码
      uses: actions/checkout@v4

    - name: 设置kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'

    - name: 配置Kubernetes上下文
      run: |
        echo "${{ secrets.KUBE_CONFIG_STAGING }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: 部署到测试环境
      run: |
        export KUBECONFIG=kubeconfig
        kubectl set image deployment/chatroom-server \
          chatroom-server=${{ needs.build-image.outputs.image-tag }} \
          -n chatroom-staging
        kubectl rollout status deployment/chatroom-server -n chatroom-staging

    - name: 运行端到端测试
      run: |
        npm install
        npm run test:e2e -- --baseUrl=https://staging.chatroom.example.com

  # 部署到生产环境
  deploy-production:
    runs-on: ubuntu-latest
    needs: [build-image, deploy-staging]
    if: github.event_name == 'release'
    environment:
      name: production
      url: https://chatroom.example.com
    
    steps:
    - name: Checkout代码
      uses: actions/checkout@v4

    - name: 设置kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'

    - name: 配置Kubernetes上下文
      run: |
        echo "${{ secrets.KUBE_CONFIG_PROD }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: 蓝绿部署到生产环境
      run: |
        export KUBECONFIG=kubeconfig
        # 创建新的部署版本
        kubectl patch deployment chatroom-server \
          -p '{"spec":{"template":{"spec":{"containers":[{"name":"chatroom-server","image":"${{ needs.build-image.outputs.image-tag }}"}]}}}}' \
          -n chatroom-production
        
        # 等待部署完成
        kubectl rollout status deployment/chatroom-server -n chatroom-production
        
        # 健康检查
        kubectl wait --for=condition=available --timeout=300s deployment/chatroom-server -n chatroom-production

    - name: 生产环境烟雾测试
      run: |
        curl -f https://chatroom.example.com/health || exit 1
        curl -f https://chatroom.example.com/api/status || exit 1

    - name: 通知部署成功
      uses: 8398a7/action-slack@v3
      with:
        status: success
        text: '🚀 Chat-Room已成功部署到生产环境！'
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  # 性能测试
  performance-tests:
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/develop'
    
    steps:
    - name: Checkout代码
      uses: actions/checkout@v4

    - name: 设置Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ env.NODE_VERSION }}

    - name: 安装K6
      run: |
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6

    - name: 运行性能测试
      run: |
        k6 run tests/performance/load-test.js \
          --env BASE_URL=https://staging.chatroom.example.com \
          --out json=performance-results.json

    - name: 上传性能测试结果
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: performance-results.json

    - name: 分析性能结果
      run: |
        python scripts/analyze-performance.py performance-results.json
```

### GitLab CI配置

```yaml
# .gitlab-ci.yml - GitLab CI/CD流水线
stages:
  - validate
  - test
  - build
  - deploy-staging
  - deploy-production

variables:
  PYTHON_VERSION: "3.11"
  DOCKER_REGISTRY: $CI_REGISTRY
  IMAGE_NAME: $CI_REGISTRY_IMAGE
  POSTGRES_DB: chatroom_test
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres

# 代码质量检查
code-quality:
  stage: validate
  image: python:$PYTHON_VERSION
  before_script:
    - pip install -r requirements-dev.txt
  script:
    - black --check .
    - isort --check-only .
    - flake8 .
    - mypy .
    - bandit -r . -f json -o bandit-report.json
  artifacts:
    reports:
      codequality: bandit-report.json
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_COMMIT_BRANCH == "develop"

# 单元测试
unit-tests:
  stage: test
  image: python:$PYTHON_VERSION
  services:
    - postgres:15
    - redis:7
  variables:
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/chatroom_test
    REDIS_URL: redis://redis:6379/0
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
  script:
    - pytest tests/unit/ --cov=. --cov-report=xml --cov-report=html --junitxml=junit.xml
  coverage: '/TOTAL.+ ([0-9]{1,3}%)/'
  artifacts:
    reports:
      junit: junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
    expire_in: 1 week

# 集成测试
integration-tests:
  stage: test
  image: python:$PYTHON_VERSION
  services:
    - postgres:15
    - redis:7
  variables:
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/chatroom_test
    REDIS_URL: redis://redis:6379/0
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
  script:
    - pytest tests/integration/ --junitxml=integration-junit.xml
  artifacts:
    reports:
      junit: integration-junit.xml
    expire_in: 1 week

# Docker镜像构建
build-image:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker build -t $IMAGE_NAME:latest .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA
    - docker push $IMAGE_NAME:latest
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_COMMIT_BRANCH == "develop"

# 部署到测试环境
deploy-staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging.chatroom.example.com
  before_script:
    - echo $KUBE_CONFIG_STAGING | base64 -d > kubeconfig
    - export KUBECONFIG=kubeconfig
  script:
    - kubectl set image deployment/chatroom-server chatroom-server=$IMAGE_NAME:$CI_COMMIT_SHA -n chatroom-staging
    - kubectl rollout status deployment/chatroom-server -n chatroom-staging
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

# 部署到生产环境
deploy-production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://chatroom.example.com
  before_script:
    - echo $KUBE_CONFIG_PROD | base64 -d > kubeconfig
    - export KUBECONFIG=kubeconfig
  script:
    - kubectl set image deployment/chatroom-server chatroom-server=$IMAGE_NAME:$CI_COMMIT_SHA -n chatroom-production
    - kubectl rollout status deployment/chatroom-server -n chatroom-production
    - kubectl wait --for=condition=available --timeout=300s deployment/chatroom-server -n chatroom-production
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

## 🎯 实践练习

### 练习1：多分支部署策略
```python
class BranchDeploymentStrategy:
    """
    多分支部署策略练习
    
    要求：
    1. 实现feature分支的临时环境部署
    2. 支持hotfix分支的快速部署
    3. 实现环境的自动清理机制
    4. 添加部署通知和状态跟踪
    """
    
    def deploy_feature_branch(self, branch_name: str) -> Dict[str, Any]:
        """部署feature分支"""
        # TODO: 实现feature分支部署
        pass
    
    def cleanup_temporary_environment(self, env_name: str) -> bool:
        """清理临时环境"""
        # TODO: 实现环境清理
        pass
```

### 练习2：部署质量门禁
```python
class DeploymentQualityGates:
    """
    部署质量门禁练习
    
    要求：
    1. 实现代码覆盖率门禁
    2. 添加安全扫描门禁
    3. 实现性能测试门禁
    4. 支持手动审批流程
    """
    
    def check_coverage_gate(self, coverage_percentage: float) -> bool:
        """检查覆盖率门禁"""
        # TODO: 实现覆盖率门禁
        pass
    
    def security_scan_gate(self, scan_results: Dict[str, Any]) -> bool:
        """安全扫描门禁"""
        # TODO: 实现安全门禁
        pass
```

## ✅ 学习检查

完成本章学习后，请确认您能够：

- [ ] 理解CI/CD流水线的设计原理和最佳实践
- [ ] 配置GitHub Actions和GitLab CI流水线
- [ ] 实现自动化测试和代码质量检查
- [ ] 设计多环境部署和发布策略
- [ ] 配置安全扫描和质量门禁
- [ ] 完成实践练习

## 📚 下一步

CI/CD自动化掌握后，请继续学习：
- [运维监控](./monitoring-operations.md)

---

**恭喜！您已经掌握了现代CI/CD自动化技术！** 🔄
