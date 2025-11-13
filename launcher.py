#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动器 - 维修单工具 Modern Edition
检查依赖并启动应用程序
"""

import sys
import subprocess
import importlib.util


def check_package(package_name, install_name=None):
    """检查包是否已安装"""
    if install_name is None:
        install_name = package_name

    spec = importlib.util.find_spec(package_name)
    return spec is not None, install_name


def main():
    print("="*70)
    print("🚀 维修单工具 Modern Edition v2.0 - 启动器")
    print("="*70)
    print()

    # 检查依赖
    dependencies = [
        ("customtkinter", "customtkinter", True),
        ("PIL", "Pillow", True),
        ("openpyxl", "openpyxl", False),
        ("reportlab", "reportlab", False),
        ("tkinterdnd2", "tkinterdnd2", False),
    ]

    missing_required = []
    missing_optional = []

    print("📦 检查依赖...")
    print()

    for package, install_name, required in dependencies:
        installed, _ = check_package(package, install_name)
        status = "✓" if installed else "✗"
        type_str = "必需" if required else "可选"

        print(f"  {status} {install_name:20s} [{type_str}]")

        if not installed:
            if required:
                missing_required.append(install_name)
            else:
                missing_optional.append(install_name)

    print()

    # 处理缺失的必需依赖
    if missing_required:
        print("❌ 缺少必需依赖:")
        for dep in missing_required:
            print(f"   - {dep}")
        print()
        print("请运行以下命令安装:")
        print(f"   pip install {' '.join(missing_required)}")
        print()

        # 询问是否自动安装
        try:
            response = input("是否现在自动安装? (y/n): ").strip().lower()
            if response == 'y':
                print("\n正在安装...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install"
                ] + missing_required)
                print("\n✓ 安装完成！")
            else:
                print("\n请手动安装后再运行程序。")
                return
        except KeyboardInterrupt:
            print("\n\n取消安装。")
            return
        except Exception as e:
            print(f"\n✗ 安装失败: {e}")
            return

    # 提示可选依赖
    if missing_optional:
        print("ℹ️  缺少可选依赖（程序仍可运行，但某些功能将被禁用）:")
        for dep in missing_optional:
            print(f"   - {dep}")
        print()
        print("如需完整功能，请运行:")
        print(f"   pip install {' '.join(missing_optional)}")
        print()

    # 启动应用
    print("="*70)
    print("🎉 依赖检查完成！启动应用程序...")
    print("="*70)
    print()

    try:
        # 导入并运行
        import repair_report_modern
        repair_report_modern.main()
    except ImportError as e:
        print(f"❌ 无法导入应用程序: {e}")
        print("\n请确保 repair_report_modern.py 在同一目录下。")
    except Exception as e:
        print(f"❌ 应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已退出。")
