"""
修复现有数据库的问题
1. 删除有问题的全文搜索索引
2. 不需要重置数据库，只修复问题
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_existing_database(database_url: str = None):
    """修复现有数据库的问题"""
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', settings.database_url)
    
    logger.info(f"连接到数据库: {database_url.split('@')[1] if '@' in database_url else '***'}")
    
    # 创建数据库引擎
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        echo=False
    )
    
    try:
        # 测试连接
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("数据库连接成功")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise
    
    try:
        # 1. 删除有问题的全文搜索索引
        logger.info("删除有问题的索引 idx_policies_fts...")
        with engine.connect() as conn:
            result = conn.execute(text('DROP INDEX IF EXISTS idx_policies_fts'))
            conn.commit()
            logger.info("已删除有问题的索引（如果存在）")
        
        # 2. 更新validity字段长度（如果当前长度是50）
        logger.info("更新validity字段长度...")
        with engine.connect() as conn:
            # 检查当前字段定义
            result = conn.execute(text("""
                SELECT character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'policies' AND column_name = 'validity'
            """))
            row = result.fetchone()
            if row and row[0] == 50:
                conn.execute(text('ALTER TABLE policies ALTER COLUMN validity TYPE VARCHAR(100)'))
                conn.commit()
                logger.info("已更新validity字段长度为100")
            else:
                logger.info(f"validity字段长度已是{row[0] if row else 'N/A'}，无需更新")
        
        logger.info("数据库修复完成！")
        print("\n" + "="*50)
        print("数据库修复成功！")
        print("="*50)
        print("已删除有问题的全文搜索索引")
        print("全文搜索功能将使用PostgreSQL的tsvector实现")
        print("="*50)
        
    except Exception as e:
        logger.error(f"数据库修复失败: {e}", exc_info=True)
        print(f"\n错误: {e}")
        raise


if __name__ == "__main__":
    print("="*50)
    print("数据库修复工具")
    print("="*50)
    print("此操作将删除有问题的全文搜索索引")
    print("不会删除任何数据，只修复索引问题")
    print("="*50)
    
    response = input("\n确认要继续吗？(yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("已取消")
        sys.exit(0)
    
    # 检查环境变量或使用默认配置
    default_db_url = "postgresql://test:6p6deyczXK55FYQN@43.143.43.251:5432/test"
    database_url = os.getenv('DATABASE_URL', default_db_url)
    
    print(f"\n使用数据库连接: {database_url.split('@')[1] if '@' in database_url else '***'}")
    
    fix_existing_database(database_url)

