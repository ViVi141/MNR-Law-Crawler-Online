"""
系统配置模型
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base


class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = "system_config"
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)  # feature/s3/email/scheduler/backup/cache/storage
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)  # 敏感信息加密存储
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BackupRecord(Base):
    """数据库备份记录"""
    __tablename__ = "backup_records"
    
    id = Column(String(100), primary_key=True)
    backup_type = Column(String(50), nullable=False)  # full/incremental
    s3_key = Column(String(500))
    local_path = Column(String(500))
    file_size = Column(String(50))  # 文件大小（字节）
    status = Column(String(50), default="pending")  # pending/completed/failed
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    # 新增字段：备份来源信息
    source_type = Column(String(50))  # manual/task/scheduled - 备份来源类型
    source_id = Column(String(100))  # 关联的任务ID或定时任务ID
    backup_strategy = Column(String(50))  # always/on_success/on_new_policies/daily/weekly/monthly - 备份策略
    source_deleted = Column(Boolean, default=False)  # 来源是否已删除
    source_name = Column(String(255))  # 备份时保存的任务名称（用于追溯，即使任务删除也能知道来源）

