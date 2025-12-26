"""
定时任务Schema
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class ScheduledTaskCreate(BaseModel):
    """创建定时任务Schema"""

    task_type: str = Field(..., description="任务类型 (crawl_task/backup_task)")
    task_name: str = Field(..., description="任务名称（唯一）")
    cron_expression: str = Field(
        ..., description="Cron表达式 (例如: '0 2 * * *' 表示每天凌晨2点)"
    )
    config: Dict[str, Any] = Field(..., description="任务配置")
    is_enabled: bool = Field(default=False, description="是否启用")

    @model_validator(mode="after")
    def validate_config(self) -> "ScheduledTaskCreate":
        """验证配置字段"""
        # 如果 task_type 是 crawl_task，验证 data_sources
        if self.task_type == "crawl_task":
            data_sources = self.config.get("data_sources", [])
            if not data_sources or len(data_sources) == 0:
                raise ValueError("创建爬取任务时必须至少指定一个数据源")
            # 验证数据源配置完整性
            for idx, ds in enumerate(data_sources):
                if not isinstance(ds, dict):
                    raise ValueError(f"数据源配置格式错误（索引 {idx}）: {ds}")

                # 判断数据源类型
                is_gd = ds.get("type") == "gd" or "广东" in ds.get("name", "")

                if is_gd:
                    # GD数据源验证
                    required_fields = ["name", "api_base_url"]
                    missing_fields = [
                        f for f in required_fields if f not in ds or not ds.get(f)
                    ]
                    if missing_fields:
                        raise ValueError(
                            f"数据源 '{ds.get('name', f'索引{idx}')}' 缺少必需字段: {', '.join(missing_fields)}"
                        )
                else:
                    # MNR数据源验证
                    required_fields = ["name", "base_url", "search_api", "ajax_api"]
                    missing_fields = [
                        f for f in required_fields if f not in ds or not ds.get(f)
                    ]
                    if missing_fields:
                        raise ValueError(
                            f"数据源 '{ds.get('name', f'索引{idx}')}' 缺少必需字段: {', '.join(missing_fields)}"
                        )
        return self

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

    @model_validator(mode="after")
    def validate_config(self) -> "ScheduledTaskUpdate":
        """验证配置字段（如果提供了config）"""
        # 如果提供了config，验证data_sources（需要从数据库获取task_type来验证）
        # 注意：在更新时，我们需要从数据库获取task_type，所以这里的验证会在service层进行
        # 这里只做基本的格式验证
        if self.config is not None:
            data_sources = self.config.get("data_sources", [])
            if data_sources:  # 如果提供了data_sources，验证其格式
                for idx, ds in enumerate(data_sources):
                    if not isinstance(ds, dict):
                        raise ValueError(f"数据源配置格式错误（索引 {idx}）: {ds}")

                    # 判断数据源类型
                    is_gd = ds.get("type") == "gd" or "广东" in ds.get("name", "")

                    if is_gd:
                        # GD数据源验证
                        required_fields = ["name", "api_base_url"]
                        missing_fields = [
                            f for f in required_fields if f not in ds or not ds.get(f)
                        ]
                        if missing_fields:
                            raise ValueError(
                                f"数据源 '{ds.get('name', f'索引{idx}')}' 缺少必需字段: {', '.join(missing_fields)}"
                            )
                    else:
                        # MNR数据源验证
                        required_fields = ["name", "base_url", "search_api", "ajax_api"]
                        missing_fields = [
                            f for f in required_fields if f not in ds or not ds.get(f)
                        ]
                        if missing_fields:
                            raise ValueError(
                                f"数据源 '{ds.get('name', f'索引{idx}')}' 缺少必需字段: {', '.join(missing_fields)}"
                            )
        return self


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
