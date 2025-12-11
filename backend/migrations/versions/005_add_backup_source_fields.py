"""添加备份来源字段

Revision ID: 005
Revises: 004
Create Date: 2024-12-08 14:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    # 添加备份来源相关字段
    op.add_column(
        "backup_records", sa.Column("source_type", sa.String(50), nullable=True)
    )
    op.add_column(
        "backup_records", sa.Column("source_id", sa.String(100), nullable=True)
    )
    op.add_column(
        "backup_records", sa.Column("backup_strategy", sa.String(50), nullable=True)
    )
    op.add_column(
        "backup_records",
        sa.Column(
            "source_deleted", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column(
        "backup_records", sa.Column("source_name", sa.String(255), nullable=True)
    )

    # 创建索引以提高查询性能
    op.create_index("idx_backup_source", "backup_records", ["source_type", "source_id"])


def downgrade():
    # 删除索引
    op.drop_index("idx_backup_source", table_name="backup_records")

    # 删除字段
    op.drop_column("backup_records", "source_name")
    op.drop_column("backup_records", "source_deleted")
    op.drop_column("backup_records", "backup_strategy")
    op.drop_column("backup_records", "source_id")
    op.drop_column("backup_records", "source_type")
