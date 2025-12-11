"""
任务模型
"""

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Task(Base):
    """任务表"""

    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, index=True)
    task_name = Column(String(255), nullable=False)
    task_type = Column(String(50), nullable=False, index=True)  # manual/scheduled
    status = Column(
        String(50), nullable=False, index=True
    )  # pending/running/completed/failed/cancelled
    config_json = Column(JSON)  # 任务配置
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    policy_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    error_message = Column(Text)
    progress_message = Column(Text)  # 实时进度消息（列表爬取状态等）
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 关系
    user = relationship("User", backref="tasks")

    __table_args__ = (
        Index("idx_tasks_status", "status"),
        Index("idx_tasks_created_at", "created_at"),
    )


class TaskPolicy(Base):
    """任务政策关联表"""

    __tablename__ = "task_policies"

    task_id = Column(
        BigInteger, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    policy_id = Column(
        BigInteger, ForeignKey("policies.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    task = relationship("Task", backref="task_policies")
    policy = relationship("Policy", backref="task_policies")
