"""
重置数据库脚本
用于开发环境：删除所有表并重新创建（包含新字段）
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, drop_db, init_db
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
from app.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_database():
    """重置数据库：删除所有表并重新创建"""
    logger.info("开始重置数据库...")

    try:
        # 1. 删除所有表
        logger.info("删除所有表...")
        drop_db()
        logger.info("所有表已删除")

        # 2. 重新创建所有表
        logger.info("创建所有表...")
        init_db()
        logger.info("所有表已创建")

        # 3. 创建默认用户
        logger.info("创建默认用户...")
        db = SessionLocal()
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

        logger.info("数据库重置完成！")
        print("\n" + "=" * 50)
        print("数据库重置成功！")
        print("=" * 50)
        print("默认用户：admin / admin123")
        print("=" * 50)

    except Exception as e:
        logger.error(f"数据库重置失败: {e}", exc_info=True)
        print(f"\n错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 50)
    print("数据库重置工具")
    print("=" * 50)
    print("警告：此操作将删除所有数据库表和数据！")
    print("=" * 50)

    response = input("\n确认要继续吗？(yes/no): ").strip().lower()
    if response not in ["yes", "y"]:
        print("已取消")
        sys.exit(0)

    reset_database()
