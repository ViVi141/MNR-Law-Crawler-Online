"""Remove problematic FTS index

Revision ID: 003
Revises: 002
Create Date: 2024-12-08 13:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 删除有问题的全文搜索索引（因为content字段太大，超过PostgreSQL btree索引限制）
    # 全文搜索应该使用PostgreSQL的GIN索引和tsvector，而不是普通的btree索引
    try:
        op.drop_index("idx_policies_fts", table_name="policies")
    except Exception:
        # 如果索引不存在，忽略错误
        pass


def downgrade() -> None:
    # 不恢复此索引，因为它会导致问题
    pass
