"""
数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

# 创建数据库引擎 - 优化内存占用
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 连接前检查
    pool_size=5,  # 减少连接池大小
    max_overflow=10,  # 减少最大溢出连接
    pool_recycle=300,  # 5分钟后回收连接，避免连接失效
    echo=settings.debug,  # 调试模式下打印SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（依赖注入）
    使用方式：
        @app.get("/api/...")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库（创建所有表）"""
    # 导入所有模型以确保它们被注册
    from .models import (
        User,
        Policy,
        Task,
        TaskPolicy,
        Attachment,
        ScheduledTask,
        ScheduledTaskRun,
        SystemConfig,
        BackupRecord,
    )

    Base.metadata.create_all(bind=engine)


def drop_db():
    """删除所有表（谨慎使用）"""
    Base.metadata.drop_all(bind=engine)
