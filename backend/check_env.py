"""环境自检脚本：检查关键依赖是否已安装。"""

from importlib.util import find_spec

REQUIRED = [
    "flask",
    "flask_cors",
    "sqlalchemy",
]


def main():
    missing = [name for name in REQUIRED if find_spec(name) is None]
    if not missing:
        print("✅ 环境检查通过：关键依赖已安装。")
        return 0

    print("❌ 缺少以下 Python 依赖：")
    for pkg in missing:
        print(f"  - {pkg}")

    print("\n请先安装依赖后再运行：")
    print("  pip install -r requirements.txt")
    print("\n如果你在中国大陆网络环境，建议使用镜像：")
    print("  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
