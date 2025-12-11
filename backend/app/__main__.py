"""
作为模块运行时启动服务器
python -m app
"""

if __name__ == "__main__":
    from .main import app
    import uvicorn

    print("=" * 60)
    print("MNR Law Crawler Web - 启动中...")
    print("=" * 60)
    print("\n访问地址:")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 健康检查: http://localhost:8000/api/health")
    print("  - 默认账号: admin / admin123")
    print("\n" + "=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
