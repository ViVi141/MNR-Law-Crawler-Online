"""Add progress_message to tasks

Revision ID: 002
Revises: 001
Create Date: 2024-12-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加进度消息字段到tasks表
    op.add_column('tasks', sa.Column('progress_message', sa.Text(), nullable=True))


def downgrade() -> None:
    # 移除进度消息字段
    op.drop_column('tasks', 'progress_message')

