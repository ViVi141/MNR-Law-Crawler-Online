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

