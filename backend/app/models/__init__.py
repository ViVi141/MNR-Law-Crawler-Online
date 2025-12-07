"""数据库模型模块"""

from .user import User
from .policy import Policy
from .task import Task, TaskPolicy
from .attachment import Attachment
from .scheduled_task import ScheduledTask, ScheduledTaskRun
from .system_config import SystemConfig, BackupRecord

# 导入所有模型以确保它们被注册
__all__ = [
    "User",
    "Policy",
    "Task",
    "TaskPolicy",
    "Attachment",
    "ScheduledTask",
    "ScheduledTaskRun",
    "SystemConfig",
    "BackupRecord",
]
