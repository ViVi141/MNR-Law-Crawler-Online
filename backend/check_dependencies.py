"""
检查依赖是否已安装
"""

import sys

required_packages = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pydantic",
    "pydantic_settings",
    "psycopg2",
    "python-jose",
    "passlib",
    "boto3",
    "bcrypt",
    "cryptography",
]

missing_packages = []

# 包名到导入名的映射
package_map = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "sqlalchemy": "sqlalchemy",
    "pydantic": "pydantic",
    "pydantic_settings": "pydantic_settings",
    "pydantic-settings": "pydantic_settings",
    "psycopg2": "psycopg2",
    "python-jose": "jose",
    "passlib": "passlib",
    "boto3": "boto3",
    "bcrypt": "bcrypt",
    "cryptography": "cryptography",
}

for package in required_packages:
    try:
        import_name = package_map.get(package, package.replace("-", "_"))
        __import__(import_name)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package} (未安装)")
        missing_packages.append(package)

if missing_packages:
    print(f"\n缺少以下包，请运行: pip install -r requirements.txt")
    print(f"缺少的包: {', '.join(missing_packages)}")
    sys.exit(1)
else:
    print("\n✅ 所有依赖已安装")

