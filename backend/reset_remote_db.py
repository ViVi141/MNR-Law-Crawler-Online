"""
重置远程数据库脚本
用于开发环境：删除所有表并重新创建（包含新字段）
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.database import Base
from app.models import (
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
from app.services.auth_service import AuthService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_remote_database(database_url: str):
    """重置远程数据库：删除所有表并重新创建"""
    logger.info(
        f"连接到数据库: {database_url.split('@')[1] if '@' in database_url else '***'}"
    )

    # 创建数据库引擎
    engine = create_engine(database_url, pool_pre_ping=True, echo=False)

    try:
        # 测试连接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

    try:
        # 1. 删除所有表
        logger.info("删除所有表...")
        Base.metadata.drop_all(bind=engine)
        logger.info("所有表已删除")

        # 2. 重新创建所有表
        logger.info("创建所有表...")
        Base.metadata.create_all(bind=engine)
        logger.info("所有表已创建")

        # 3. 创建默认用户
        logger.info("创建默认用户...")
        # 使用新的数据库连接创建会话
        from sqlalchemy.orm import sessionmaker

        SessionRemote = sessionmaker(bind=engine)
        db = SessionRemote()

        try:
            user_count = db.query(User).count()
            if user_count == 0:
                AuthService.create_default_user(
                    db, username="admin", password="admin123", email="admin@example.com"
                )
                logger.info("默认用户已创建: admin/admin123")
            else:
                logger.info(f"数据库已有 {user_count} 个用户，跳过创建默认用户")
        finally:
            db.close()

        # 4. 删除有问题的索引（如果存在）
        try:
            logger.info("清理有问题的索引...")
            with engine.connect() as conn:
                # 删除有问题的全文搜索索引（content字段太大，超过btree索引限制）
                conn.execute(text("DROP INDEX IF EXISTS idx_policies_fts"))
                conn.commit()
                logger.info("已删除有问题的索引")
        except Exception as e:
            logger.warning(f"清理索引时出错（可忽略）: {e}")

        # 5. 初始化数据库扩展（如果支持）
        try:
            logger.info("初始化数据库扩展...")
            with engine.connect() as conn:
                # 尝试创建扩展（可能已存在，忽略错误）
                try:
                    conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pg_trgm"'))
                    logger.info("pg_trgm 扩展已启用")
                except Exception as e:
                    logger.warning(f"pg_trgm 扩展可能不支持: {e}")

                conn.commit()
        except Exception as e:
            logger.warning(f"初始化扩展时出错（可忽略）: {e}")

        logger.info("数据库重置完成！")
        print("\n" + "=" * 50)
        print("远程数据库重置成功！")
        print("=" * 50)
        print("默认用户：admin / admin123")
        print("=" * 50)

    except Exception as e:
        logger.error(f"数据库重置失败: {e}", exc_info=True)
        print(f"\n错误: {e}")
        raise


if __name__ == "__main__":
    print("=" * 50)
    print("远程数据库重置工具")
    print("=" * 50)
    print("警告：此操作将删除所有数据库表和数据！")
    print("=" * 50)

    # 默认远程数据库配置
    default_db_url = "postgresql://test:6p6deyczXK55FYQN@43.143.43.251:5432/test"

    print(
        f"\n默认数据库: {default_db_url.split('@')[1] if '@' in default_db_url else default_db_url}"
    )

    response = input("\n确认要继续吗？(yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        print("已取消")
        sys.exit(0)

    # 检查环境变量或使用默认配置
    database_url = os.getenv("DATABASE_URL", default_db_url)

    print(
        f"\n使用数据库连接: {database_url.split('@')[1] if '@' in database_url else '***'}"
    )

    reset_remote_database(database_url)
