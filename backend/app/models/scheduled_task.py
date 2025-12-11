"""
定时任务模型
"""

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    JSON,
    Index,
    ForeignKey,
)
from sqlalchemy.sql import func
from ..database import Base


class ScheduledTask(Base):
    """定时任务配置表"""

    __tablename__ = "scheduled_tasks"

    id = Column(BigInteger, primary_key=True, index=True)
    task_type = Column(String(50), nullable=False)  # crawl_task/backup_task等
    task_name = Column(String(255), nullable=False, unique=True)
    cron_expression = Column(String(100), nullable=False)
    config_json = Column(JSON, nullable=False)
    is_enabled = Column(Boolean, default=False, index=True)
    next_run_time = Column(DateTime(timezone=True))
    last_run_time = Column(DateTime(timezone=True))
    last_run_status = Column(String(50))  # success/failed
    last_run_result = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ScheduledTaskRun(Base):
    """定时任务执行历史"""

    __tablename__ = "scheduled_task_runs"

    id = Column(BigInteger, primary_key=True, index=True)
    task_id = Column(
        BigInteger,
        ForeignKey("scheduled_tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_time = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # running/completed/failed
    result_json = Column(JSON)
    error_message = Column(Text)
    duration_seconds = Column(Integer)  # 执行耗时（秒）
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_task_runs_task_id", "task_id"),
        Index("idx_task_runs_run_time", "run_time"),
    )
