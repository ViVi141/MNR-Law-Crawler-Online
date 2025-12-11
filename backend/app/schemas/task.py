"""
任务Schema（Pydantic模型）
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """创建任务Schema"""

    task_name: str = Field(..., description="任务名称")
    task_type: str = Field(..., description="任务类型 (manual/scheduled)")
    config: Dict[str, Any] = Field(..., description="任务配置")

    class Config:
        json_schema_extra = {
            "example": {
                "task_name": "爬取2024年政策",
                "task_type": "manual",
                "config": {
                    "keywords": ["土地"],
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "limit_pages": 10,
                },
            }
        }


class TaskResponse(BaseModel):
    """任务响应Schema"""

    id: int
    task_name: str
    task_type: str
    status: str
    config_json: Optional[Dict[str, Any]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    policy_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    error_message: Optional[str] = None
    progress_message: Optional[str] = None  # 实时进度消息
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
        # 避免访问延迟加载的关系
        arbitrary_types_allowed = True


class TaskListItem(BaseModel):
    """任务列表项Schema"""

    id: int
    task_name: str
    task_type: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    policy_count: int = 0
    success_count: int = 0
    failed_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应"""

    items: List[TaskListItem]
    total: int
    skip: int
    limit: int
