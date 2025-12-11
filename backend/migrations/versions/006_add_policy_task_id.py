"""添加政策任务ID字段

Revision ID: 006
Revises: 005
Create Date: 2024-12-08 15:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade():
    # 添加task_id字段到policies表
    op.add_column("policies", sa.Column("task_id", sa.BigInteger(), nullable=True))

    # 创建外键约束
    op.create_foreign_key(
        "fk_policies_task_id",
        "policies",
        "tasks",
        ["task_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 创建索引以提高查询性能
    op.create_index("idx_policies_task_id", "policies", ["task_id"])

    # 注意：唯一约束需要修改，但由于PostgreSQL不支持部分唯一索引，
    # 我们使用应用层逻辑来确保唯一性
    # 原有的唯一约束 (title, source_url, pub_date) 仍然保留，用于兼容旧数据


def downgrade():
    # 删除索引
    op.drop_index("idx_policies_task_id", table_name="policies")

    # 删除外键约束
    op.drop_constraint("fk_policies_task_id", "policies", type_="foreignkey")

    # 删除字段
    op.drop_column("policies", "task_id")
