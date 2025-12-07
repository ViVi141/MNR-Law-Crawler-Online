"""Update validity column length

Revision ID: 004
Revises: 003
Create Date: 2024-12-08 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 将validity字段长度从50增加到100，以支持更长的有效性描述
    # 例如："部门规范性文件"、"行政法规"等
    op.alter_column('policies', 'validity',
                    existing_type=sa.String(length=50),
                    type_=sa.String(length=100),
                    existing_nullable=True)


def downgrade() -> None:
    # 恢复原长度
    op.alter_column('policies', 'validity',
                    existing_type=sa.String(length=100),
                    type_=sa.String(length=50),
                    existing_nullable=True)

