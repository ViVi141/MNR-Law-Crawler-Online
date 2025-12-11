"""
备份相关Schema
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BackupCreateRequest(BaseModel):
    """创建备份请求Schema"""

    backup_type: str = Field(default="full", description="备份类型 (full/incremental)")
    backup_name: Optional[str] = Field(None, description="备份名称（可选）")


class BackupRecordResponse(BaseModel):
    """备份记录响应Schema"""

    id: str
    backup_type: str
    s3_key: Optional[str] = None
    local_path: Optional[str] = None
    file_size: Optional[str] = None
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    # 新增字段：备份来源信息
    source_type: Optional[str] = None  # manual/task/scheduled
    source_id: Optional[str] = None  # 关联的任务ID或定时任务ID
    source_name: Optional[str] = None  # 备份时保存的任务名称
    source_deleted: Optional[bool] = False  # 来源是否已删除
    backup_strategy: Optional[str] = None  # 备份策略

    class Config:
        from_attributes = True


class BackupRecordListResponse(BaseModel):
    """备份记录列表响应"""

    items: list[BackupRecordResponse]
    total: int
    skip: int
    limit: int


class BackupRestoreRequest(BaseModel):
    """恢复备份请求Schema"""

    target_database: Optional[str] = Field(
        None, description="目标数据库名称（可选，默认使用原数据库）"
    )


class BackupRestoreResponse(BaseModel):
    """恢复备份响应Schema"""

    success: bool
    message: str
    backup_id: Optional[str] = None
    target_database: Optional[str] = None
    error: Optional[str] = None


class BackupCleanupResponse(BaseModel):
    """清理备份响应Schema"""

    success: bool
    message: str
    deleted_count: int = 0
    kept_count: int = 0
    error: Optional[str] = None
