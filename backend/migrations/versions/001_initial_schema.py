"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-12-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 用户表
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 政策表
    op.create_table(
        'policies',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('doc_number', sa.String(length=200), nullable=True),
        sa.Column('pub_date', sa.Date(), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('category', sa.String(length=200), nullable=True),
        sa.Column('category_code', sa.String(length=50), nullable=True),
        sa.Column('level', sa.String(length=100), nullable=True),
        sa.Column('validity', sa.String(length=100), nullable=True),  # 有效性（如：部门规范性文件）- 从50增加到100
        sa.Column('source_url', sa.Text(), nullable=False),
        sa.Column('source_name', sa.String(length=200), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_summary', sa.Text(), nullable=True),
        sa.Column('publisher', sa.String(length=200), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('json_s3_key', sa.String(length=500), nullable=True),
        sa.Column('markdown_s3_key', sa.String(length=500), nullable=True),
        sa.Column('docx_s3_key', sa.String(length=500), nullable=True),
        sa.Column('attachments_s3_keys', sa.Text(), nullable=True),
        sa.Column('json_local_path', sa.String(length=500), nullable=True),
        sa.Column('markdown_local_path', sa.String(length=500), nullable=True),
        sa.Column('docx_local_path', sa.String(length=500), nullable=True),
        sa.Column('attachments_local_path', sa.Text(), nullable=True),
        sa.Column('storage_mode', sa.String(length=20), nullable=True),
        sa.Column('s3_bucket', sa.String(length=100), nullable=True),
        sa.Column('s3_region', sa.String(length=50), nullable=True),
        sa.Column('word_count', sa.BigInteger(), nullable=True),
        sa.Column('attachment_count', sa.Integer(), nullable=True),
        sa.Column('is_indexed', sa.Boolean(), nullable=True),
        sa.Column('crawl_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_policies_id'), 'policies', ['id'], unique=False)
    op.create_index(op.f('ix_policies_title'), 'policies', ['title'], unique=False)
    op.create_index(op.f('ix_policies_category'), 'policies', ['category'], unique=False)
    op.create_index(op.f('ix_policies_level'), 'policies', ['level'], unique=False)
    op.create_index(op.f('ix_policies_source_name'), 'policies', ['source_name'], unique=False)
    op.create_index(op.f('ix_policies_created_at'), 'policies', ['created_at'], unique=False)
    op.create_index('idx_policy_unique', 'policies', ['title', 'source_url', 'pub_date'], unique=True)
    # 注意：全文搜索应该使用PostgreSQL的GIN索引和tsvector，而不是普通的btree索引
    # content字段太大，无法用btree索引（会超过2704字节限制）
    # 全文搜索功能在search_service中使用tsvector实现

    # 任务表
    op.create_table(
        'tasks',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('task_name', sa.String(length=255), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('config_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('policy_count', sa.Integer(), nullable=True),
        sa.Column('success_count', sa.Integer(), nullable=True),
        sa.Column('failed_count', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('progress_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index('idx_tasks_status', 'tasks', ['status'], unique=False)
    op.create_index('idx_tasks_created_at', 'tasks', ['created_at'], unique=False)
    op.create_index(op.f('ix_tasks_task_type'), 'tasks', ['task_type'], unique=False)

    # 任务政策关联表
    op.create_table(
        'task_policies',
        sa.Column('task_id', sa.BigInteger(), nullable=False),
        sa.Column('policy_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'policy_id')
    )

    # 附件表
    op.create_table(
        'attachments',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('policy_id', sa.BigInteger(), nullable=False),
        sa.Column('file_name', sa.String(length=500), nullable=False),
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_s3_key', sa.String(length=500), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['policy_id'], ['policies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_attachments_id'), 'attachments', ['id'], unique=False)
    op.create_index('idx_attachments_policy_id', 'attachments', ['policy_id'], unique=False)

    # 定时任务表
    op.create_table(
        'scheduled_tasks',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('task_name', sa.String(length=255), nullable=False),
        sa.Column('cron_expression', sa.String(length=100), nullable=False),
        sa.Column('config_json', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('next_run_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_run_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_run_status', sa.String(length=50), nullable=True),
        sa.Column('last_run_result', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_name')
    )
    op.create_index(op.f('ix_scheduled_tasks_id'), 'scheduled_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_scheduled_tasks_is_enabled'), 'scheduled_tasks', ['is_enabled'], unique=False)

    # 定时任务执行历史表
    op.create_table(
        'scheduled_task_runs',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('task_id', sa.BigInteger(), nullable=False),
        sa.Column('run_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('result_json', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['scheduled_tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheduled_task_runs_id'), 'scheduled_task_runs', ['id'], unique=False)
    op.create_index('idx_task_runs_task_id', 'scheduled_task_runs', ['task_id'], unique=False)
    op.create_index('idx_task_runs_run_time', 'scheduled_task_runs', ['run_time'], unique=False)

    # 系统配置表
    op.create_table(
        'system_config',
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('key')
    )
    op.create_index(op.f('ix_system_config_category'), 'system_config', ['category'], unique=False)

    # 备份记录表
    op.create_table(
        'backup_records',
        sa.Column('id', sa.String(length=100), nullable=False),
        sa.Column('backup_type', sa.String(length=50), nullable=False),
        sa.Column('s3_key', sa.String(length=500), nullable=True),
        sa.Column('local_path', sa.String(length=500), nullable=True),
        sa.Column('file_size', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_backup_records_created_at'), 'backup_records', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_backup_records_created_at'), table_name='backup_records')
    op.drop_table('backup_records')
    op.drop_index(op.f('ix_system_config_category'), table_name='system_config')
    op.drop_table('system_config')
    op.drop_index('idx_task_runs_run_time', table_name='scheduled_task_runs')
    op.drop_index('idx_task_runs_task_id', table_name='scheduled_task_runs')
    op.drop_index(op.f('ix_scheduled_task_runs_id'), table_name='scheduled_task_runs')
    op.drop_table('scheduled_task_runs')
    op.drop_index(op.f('ix_scheduled_tasks_is_enabled'), table_name='scheduled_tasks')
    op.drop_index(op.f('ix_scheduled_tasks_id'), table_name='scheduled_tasks')
    op.drop_table('scheduled_tasks')
    op.drop_index('idx_attachments_policy_id', table_name='attachments')
    op.drop_index(op.f('ix_attachments_id'), table_name='attachments')
    op.drop_table('attachments')
    op.drop_table('task_policies')
    op.drop_index(op.f('ix_tasks_task_type'), table_name='tasks')
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_index('idx_policy_unique', table_name='policies')
    op.drop_index(op.f('ix_policies_created_at'), table_name='policies')
    op.drop_index(op.f('ix_policies_source_name'), table_name='policies')
    op.drop_index(op.f('ix_policies_level'), table_name='policies')
    op.drop_index(op.f('ix_policies_category'), table_name='policies')
    op.drop_index(op.f('ix_policies_title'), table_name='policies')
    op.drop_index(op.f('ix_policies_id'), table_name='policies')
    op.drop_table('policies')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

