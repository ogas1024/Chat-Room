#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试运行和报告生成功能
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def setup_environment():
    """设置测试环境"""
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # 创建必要的目录
    test_dir = Path(__file__).parent
    (test_dir / "logs").mkdir(exist_ok=True)
    (test_dir / "reports").mkdir(exist_ok=True)
    (test_dir / "test_data").mkdir(exist_ok=True)
    
    # 设置环境变量
    os.environ["PYTHONPATH"] = str(project_root)
    os.environ["TESTING"] = "1"


def run_unit_tests(verbose=False, coverage=True):
    """运行单元测试"""
    print("🧪 运行单元测试...")
    
    cmd = ["python", "-m", "pytest", "test/unit/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=server", "--cov=client", "--cov=shared"])
    
    cmd.extend(["-m", "unit"])
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_integration_tests(verbose=False):
    """运行集成测试"""
    print("🔗 运行集成测试...")
    
    cmd = ["python", "-m", "pytest", "test/integration/"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["-m", "integration"])
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_functional_tests(verbose=False):
    """运行功能测试"""
    print("⚙️ 运行功能测试...")
    
    cmd = ["python", "-m", "pytest", "test/functional/"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["-m", "functional"])
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_performance_tests(verbose=False):
    """运行性能测试"""
    print("🚀 运行性能测试...")
    
    cmd = ["python", "-m", "pytest", "test/performance/"]
    
    if verbose:
        cmd.append("-v")
    
    cmd.extend(["-m", "performance", "--durations=0"])
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_all_tests(verbose=False, coverage=True, html_report=True):
    """运行所有测试"""
    print("🎯 运行所有测试...")
    
    cmd = ["python", "-m", "pytest", "test/"]
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=server",
            "--cov=client", 
            "--cov=shared",
            "--cov-report=html:test/reports/coverage",
            "--cov-report=term-missing"
        ])
    
    if html_report:
        cmd.extend([
            "--html=test/reports/report.html",
            "--self-contained-html"
        ])
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_specific_test(test_path, verbose=False):
    """运行特定测试"""
    print(f"🎯 运行特定测试: {test_path}")
    
    cmd = ["python", "-m", "pytest", test_path]
    
    if verbose:
        cmd.append("-v")
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def run_tests_by_marker(marker, verbose=False):
    """按标记运行测试"""
    print(f"🏷️ 运行标记为 '{marker}' 的测试...")
    
    cmd = ["python", "-m", "pytest", "-m", marker]
    
    if verbose:
        cmd.append("-v")
    
    return subprocess.run(cmd, cwd=Path(__file__).parent.parent)


def generate_coverage_report():
    """生成覆盖率报告"""
    print("📊 生成覆盖率报告...")
    
    # HTML报告
    subprocess.run([
        "python", "-m", "pytest",
        "--cov=server", "--cov=client", "--cov=shared",
        "--cov-report=html:test/reports/coverage",
        "--cov-report=term",
        "test/"
    ], cwd=Path(__file__).parent.parent)
    
    print("📊 覆盖率报告已生成: test/reports/coverage/index.html")


def clean_test_artifacts():
    """清理测试产物"""
    print("🧹 清理测试产物...")
    
    test_dir = Path(__file__).parent
    project_root = test_dir.parent
    
    # 清理目录列表
    cleanup_dirs = [
        test_dir / "reports",
        test_dir / "logs", 
        test_dir / ".pytest_cache",
        test_dir / "test_data",
        project_root / ".coverage",
        project_root / "htmlcov",
    ]
    
    # 清理文件模式
    cleanup_patterns = [
        "**/*.pyc",
        "**/__pycache__",
        "**/.coverage*",
        "**/junit.xml",
    ]
    
    import shutil
    
    for dir_path in cleanup_dirs:
        if dir_path.exists():
            if dir_path.is_file():
                dir_path.unlink()
            else:
                shutil.rmtree(dir_path, ignore_errors=True)
            print(f"  已清理: {dir_path}")
    
    # 清理匹配模式的文件
    for pattern in cleanup_patterns:
        for file_path in project_root.glob(pattern):
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path, ignore_errors=True)
    
    print("✅ 清理完成")


def check_dependencies():
    """检查测试依赖"""
    print("🔍 检查测试依赖...")
    
    required_packages = [
        "pytest",
        "pytest-cov",
        "pytest-html",
        "pytest-mock",
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下测试依赖:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 所有测试依赖已安装")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Chat-Room 项目测试运行器")
    
    parser.add_argument(
        "command",
        choices=["unit", "integration", "functional", "performance", "all", "clean", "coverage", "check"],
        help="要执行的测试命令"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="禁用覆盖率报告"
    )
    
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="禁用HTML报告"
    )
    
    parser.add_argument(
        "-t", "--test",
        help="运行特定测试文件或目录"
    )
    
    parser.add_argument(
        "-m", "--marker",
        help="按标记运行测试"
    )
    
    args = parser.parse_args()
    
    # 设置环境
    setup_environment()
    
    # 执行命令
    if args.command == "check":
        if not check_dependencies():
            sys.exit(1)
        return
    
    if args.command == "clean":
        clean_test_artifacts()
        return
    
    if args.command == "coverage":
        generate_coverage_report()
        return
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 运行测试
    result = None
    
    if args.test:
        result = run_specific_test(args.test, args.verbose)
    elif args.marker:
        result = run_tests_by_marker(args.marker, args.verbose)
    elif args.command == "unit":
        result = run_unit_tests(args.verbose, not args.no_coverage)
    elif args.command == "integration":
        result = run_integration_tests(args.verbose)
    elif args.command == "functional":
        result = run_functional_tests(args.verbose)
    elif args.command == "performance":
        result = run_performance_tests(args.verbose)
    elif args.command == "all":
        result = run_all_tests(args.verbose, not args.no_coverage, not args.no_html)
    
    if result:
        if result.returncode == 0:
            print("✅ 测试运行成功")
        else:
            print("❌ 测试运行失败")
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()
