"""
定时任务Schema
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class ScheduledTaskCreate(BaseModel):
    """创建定时任务Schema"""

    task_type: str = Field(..., description="任务类型 (crawl_task/backup_task)")
    task_name: str = Field(..., description="任务名称（唯一）")
    cron_expression: str = Field(
        ..., description="Cron表达式 (例如: '0 2 * * *' 表示每天凌晨2点)"
    )
    config: Dict[str, Any] = Field(..., description="任务配置")
    is_enabled: bool = Field(default=False, description="是否启用")

    class Config:
        json_schema_extra = {
            "example": {
                "task_type": "crawl_task",
                "task_name": "每日爬取政策",
                "cron_expression": "0 2 * * *",
                "config": {"keywords": ["土地"], "limit_pages": 10},
                "is_enabled": True,
            }
        }


class ScheduledTaskUpdate(BaseModel):
    """更新定时任务Schema"""

    task_name: Optional[str] = Field(None, description="任务名称")
    cron_expression: Optional[str] = Field(None, description="Cron表达式")
    config: Optional[Dict[str, Any]] = Field(None, description="任务配置")
    is_enabled: Optional[bool] = Field(None, description="是否启用")


class ScheduledTaskRunResponse(BaseModel):
    """定时任务执行历史响应"""

    id: int
    task_id: int
    run_time: datetime
    status: str
    result_json: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScheduledTaskResponse(BaseModel):
    """定时任务响应Schema"""

    id: int
    task_type: str
    task_name: str
    cron_expression: str
    config_json: Dict[str, Any]
    is_enabled: bool
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    last_run_status: Optional[str] = None
    last_run_result: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduledTaskListItem(BaseModel):
    """定时任务列表项Schema"""

    id: int
    task_type: str
    task_name: str
    cron_expression: str
    is_enabled: bool
    next_run_time: Optional[datetime] = None
    last_run_time: Optional[datetime] = None
    last_run_status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ScheduledTaskListResponse(BaseModel):
    """定时任务列表响应"""

    items: List[ScheduledTaskListItem]
    total: int
    skip: int
    limit: int


class ScheduledTaskRunsResponse(BaseModel):
    """定时任务执行历史列表响应"""

    items: List[ScheduledTaskRunResponse]
    total: int
    skip: int
    limit: int
