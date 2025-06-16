# Chat-Room 测试文档

## 📋 概述

本目录包含Chat-Room项目的完整测试套件，采用pytest框架，提供全面的单元测试、集成测试、功能测试和性能测试。

## 🏗️ 测试架构

```
test/
├── unit/                   # 单元测试
│   ├── server/            # 服务器端单元测试
│   ├── client/            # 客户端单元测试
│   └── shared/            # 共享模块单元测试
├── integration/           # 集成测试
├── functional/            # 功能测试
├── performance/           # 性能测试
├── fixtures/              # 测试夹具
├── utils/                 # 测试工具
├── conftest.py           # pytest配置
├── pytest.ini           # pytest设置
├── run_tests.py          # 测试运行脚本
└── requirements.txt      # 测试依赖
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 安装最小依赖
pip install -r test/requirements-minimal.txt

# 或安装完整依赖
pip install -r test/requirements.txt
```

### 2. 运行测试

```bash
# 使用测试脚本（推荐）
python test/run_tests.py all

# 或直接使用pytest
pytest test/
```

## 🧪 测试类型

### 单元测试 (Unit Tests)

测试单个模块和函数的功能：

```bash
# 运行所有单元测试
python test/run_tests.py unit

# 运行特定模块的单元测试
pytest test/unit/server/test_database_models.py
pytest test/unit/client/test_client_core.py
pytest test/unit/shared/test_messages.py
```

**覆盖范围：**
- 服务器端：数据库模型、用户管理、聊天管理、AI处理
- 客户端：网络客户端、命令解析、UI组件
- 共享模块：消息协议、配置管理、工具函数

### 集成测试 (Integration Tests)

测试模块间的交互：

```bash
# 运行集成测试
python test/run_tests.py integration

# 客户端-服务器集成测试
pytest test/integration/test_client_server_integration.py
```

**测试场景：**
- 客户端与服务器通信
- 数据库与业务逻辑集成
- AI功能集成
- 文件传输集成

### 功能测试 (Functional Tests)

测试完整的用户场景：

```bash
# 运行功能测试
python test/run_tests.py functional

# 用户认证功能测试
pytest test/functional/test_user_authentication.py
```

**测试场景：**
- 用户注册登录流程
- 聊天功能端到端测试
- 文件传输功能测试
- AI对话功能测试

### 性能测试 (Performance Tests)

测试系统性能表现：

```bash
# 运行性能测试
python test/run_tests.py performance

# 查看详细性能报告
pytest test/performance/ --durations=0
```

**测试指标：**
- 数据库操作性能
- 并发用户处理能力
- 消息吞吐量
- 内存使用情况

## 🛠️ 测试工具

### 测试运行脚本

`test/run_tests.py` 提供便捷的测试运行功能：

```bash
# 检查测试依赖
python test/run_tests.py check

# 运行所有测试
python test/run_tests.py all

# 运行特定类型测试
python test/run_tests.py unit
python test/run_tests.py integration
python test/run_tests.py functional
python test/run_tests.py performance

# 运行特定测试文件
python test/run_tests.py -t test/unit/server/test_user_manager.py

# 按标记运行测试
python test/run_tests.py -m database
python test/run_tests.py -m ai

# 生成覆盖率报告
python test/run_tests.py coverage

# 清理测试产物
python test/run_tests.py clean

# 详细输出
python test/run_tests.py all -v
```

### 测试夹具

`test/fixtures/` 目录提供测试数据和环境：

- `data_fixtures.py`: 测试数据生成器
- 数据库夹具：临时数据库和测试数据
- 文件夹具：临时文件和目录
- 网络夹具：模拟服务器和客户端

### 测试工具

`test/utils/` 目录提供测试辅助工具：

- `test_helpers.py`: 测试辅助函数和类
- Mock服务器和客户端
- 消息构建器
- 等待条件函数

## 📊 测试报告

### 覆盖率报告

```bash
# 生成HTML覆盖率报告
python test/run_tests.py coverage

# 查看报告
open test/reports/coverage/index.html
```

### HTML测试报告

```bash
# 运行测试并生成HTML报告
python test/run_tests.py all

# 查看报告
open test/reports/report.html
```

### JUnit XML报告

测试结果会自动生成JUnit XML格式报告，用于CI/CD集成：

```
test/reports/junit.xml
```

## 🏷️ 测试标记

使用pytest标记来分类和过滤测试：

```bash
# 按标记运行测试
pytest -m unit           # 单元测试
pytest -m integration    # 集成测试
pytest -m functional     # 功能测试
pytest -m performance    # 性能测试
pytest -m slow           # 慢速测试
pytest -m network        # 需要网络的测试
pytest -m ai             # AI相关测试
pytest -m database       # 数据库相关测试
pytest -m file_transfer  # 文件传输相关测试
```

## 🔧 配置

### pytest.ini

主要配置项：

- 测试发现路径和模式
- 输出格式和详细程度
- 覆盖率配置
- 标记定义
- 日志配置

### conftest.py

全局测试配置：

- 测试夹具定义
- 测试环境设置
- Mock对象配置
- 测试数据准备

## 🚨 测试最佳实践

### 1. 测试命名

```python
def test_user_registration_success():
    """测试用户注册成功场景"""
    pass

def test_user_registration_duplicate_username():
    """测试重复用户名注册失败"""
    pass
```

### 2. 测试结构

```python
def test_function():
    # Arrange - 准备测试数据
    user_data = {"username": "alice", "password": "password123"}
    
    # Act - 执行被测试的操作
    result = user_manager.register_user(**user_data)
    
    # Assert - 验证结果
    assert result.success is True
    assert result.user_id > 0
```

### 3. 使用夹具

```python
def test_database_operation(db_manager, sample_users):
    """使用夹具提供的数据库和测试数据"""
    for user_data in sample_users:
        user_id = db_manager.create_user(**user_data)
        assert user_id > 0
```

### 4. Mock外部依赖

```python
@patch('server.ai.zhipu_client.ZhipuClient')
def test_ai_integration(mock_client):
    """Mock外部AI服务"""
    mock_client.return_value.chat_completion.return_value = "AI回复"
    # 测试逻辑...
```

## 🐛 调试测试

### 运行单个测试

```bash
pytest test/unit/server/test_user_manager.py::TestUserManager::test_register_user_success -v
```

### 调试模式

```bash
pytest --pdb test/unit/server/test_user_manager.py
```

### 查看详细输出

```bash
pytest -v -s test/unit/server/test_user_manager.py
```

### 只运行失败的测试

```bash
pytest --lf test/
```

## 📈 持续集成

测试套件设计为支持CI/CD流水线：

1. **快速反馈**: 单元测试优先运行
2. **并行执行**: 支持并行测试执行
3. **报告生成**: 自动生成多种格式的测试报告
4. **覆盖率跟踪**: 监控代码覆盖率变化
5. **性能监控**: 跟踪性能回归

### GitHub Actions示例

```yaml
- name: Run tests
  run: |
    python test/run_tests.py check
    python test/run_tests.py all --no-html
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: test/reports/coverage.xml
```

## 🔍 故障排除

### 常见问题

1. **导入错误**: 确保项目根目录在Python路径中
2. **数据库锁定**: 确保测试数据库文件权限正确
3. **端口冲突**: 测试使用不同端口避免冲突
4. **依赖缺失**: 运行 `python test/run_tests.py check`

### 清理环境

```bash
# 清理所有测试产物
python test/run_tests.py clean

# 重新安装依赖
pip install -r test/requirements-minimal.txt
```

## 📚 参考资料

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [Python测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [Mock对象使用指南](https://docs.python.org/3/library/unittest.mock.html)
