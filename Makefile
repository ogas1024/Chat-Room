# Chat-Room 项目 Makefile
# 提供便捷的开发和测试命令

.PHONY: help install test test-unit test-integration test-functional test-performance test-all test-coverage test-clean lint format check-deps run-server run-client clean

# 默认目标
help:
	@echo "Chat-Room 项目命令:"
	@echo ""
	@echo "安装和环境:"
	@echo "  install          安装项目依赖"
	@echo "  install-test     安装测试依赖"
	@echo "  check-deps       检查测试依赖"
	@echo ""
	@echo "测试命令:"
	@echo "  test             运行所有测试"
	@echo "  test-unit        运行单元测试"
	@echo "  test-integration 运行集成测试"
	@echo "  test-functional  运行功能测试"
	@echo "  test-performance 运行性能测试"
	@echo "  test-coverage    生成覆盖率报告"
	@echo "  test-clean       清理测试产物"
	@echo ""
	@echo "代码质量:"
	@echo "  lint             代码检查"
	@echo "  format           代码格式化"
	@echo ""
	@echo "运行应用:"
	@echo "  run-server       启动服务器"
	@echo "  run-client       启动客户端"
	@echo "  run-client-tui   启动TUI客户端"
	@echo ""
	@echo "清理:"
	@echo "  clean            清理所有生成文件"

# 安装依赖
install:
	pip install -r requirements.txt

install-test:
	pip install -r test/requirements-minimal.txt

# 检查测试依赖
check-deps:
	python test/run_tests.py check

# 测试命令
test: check-deps
	python test/run_tests.py all

test-unit: check-deps
	python test/run_tests.py unit

test-integration: check-deps
	python test/run_tests.py integration

test-functional: check-deps
	python test/run_tests.py functional

test-performance: check-deps
	python test/run_tests.py performance

test-coverage: check-deps
	python test/run_tests.py coverage

test-clean:
	python test/run_tests.py clean

# 代码质量检查
lint:
	@echo "运行代码检查..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 server/ client/ shared/ --max-line-length=100 --ignore=E203,W503; \
	else \
		echo "flake8 未安装，跳过代码检查"; \
	fi

format:
	@echo "格式化代码..."
	@if command -v black >/dev/null 2>&1; then \
		black server/ client/ shared/ test/ --line-length=100; \
	else \
		echo "black 未安装，跳过代码格式化"; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort server/ client/ shared/ test/ --profile black; \
	else \
		echo "isort 未安装，跳过导入排序"; \
	fi

# 运行应用
run-server:
	@echo "启动Chat-Room服务器..."
	python server/main.py

run-client:
	@echo "启动Chat-Room客户端（简单模式）..."
	python client/main.py --mode simple

run-client-tui:
	@echo "启动Chat-Room客户端（TUI模式）..."
	python client/main.py --mode tui

# 清理
clean: test-clean
	@echo "清理项目文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	@echo "清理完成"

# 开发环境设置
dev-setup: install install-test
	@echo "开发环境设置完成"
	@echo "运行 'make test' 来验证环境"

# 快速测试（只运行单元测试）
quick-test: check-deps
	python test/run_tests.py unit --no-coverage

# 详细测试（包含覆盖率和报告）
full-test: check-deps
	python test/run_tests.py all -v

# CI/CD 测试（适用于持续集成）
ci-test: check-deps
	python test/run_tests.py all --no-html

# 性能基准测试
benchmark: check-deps
	python test/run_tests.py performance -v

# 测试特定模块
test-server: check-deps
	pytest test/unit/server/ -v

test-client: check-deps
	pytest test/unit/client/ -v

test-shared: check-deps
	pytest test/unit/shared/ -v

# 测试数据库相关功能
test-database: check-deps
	pytest -m database -v

# 测试AI相关功能
test-ai: check-deps
	pytest -m ai -v

# 测试文件传输功能
test-files: check-deps
	pytest -m file_transfer -v

# 生成测试报告
report: test-coverage
	@echo "测试报告已生成:"
	@echo "  覆盖率报告: test/reports/coverage/index.html"
	@echo "  测试报告: test/reports/report.html"

# 监控测试（文件变化时自动运行）
watch-test:
	@echo "监控文件变化并自动运行测试..."
	@if command -v watchdog >/dev/null 2>&1; then \
		watchmedo auto-restart --patterns="*.py" --recursive --signal SIGTERM \
		python test/run_tests.py unit; \
	else \
		echo "watchdog 未安装，无法监控文件变化"; \
		echo "安装: pip install watchdog"; \
	fi

# 调试测试
debug-test:
	pytest --pdb test/unit/ -v

# 只运行失败的测试
retest:
	pytest --lf test/ -v

# 显示测试统计
test-stats: check-deps
	pytest --collect-only test/ | grep "test session starts" -A 20

# 验证项目完整性
verify: lint test
	@echo "项目验证完成"

# 准备发布
prepare-release: clean format lint test
	@echo "发布准备完成"
