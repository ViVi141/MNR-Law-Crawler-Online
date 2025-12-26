"""
配置管理Schema
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class FeatureFlagsResponse(BaseModel):
    """功能开关响应"""

    s3_enabled: bool
    scheduler_enabled: bool
    email_enabled: bool
    cache_enabled: bool


class FeatureFlagUpdate(BaseModel):
    """更新功能开关"""

    flag_name: str = Field(
        ...,
        description="功能开关名称 (s3_enabled/scheduler_enabled/email_enabled/cache_enabled)",
    )
    enabled: bool = Field(..., description="是否启用")


class S3ConfigResponse(BaseModel):
    """S3配置响应"""

    enabled: bool
    bucket_name: Optional[str] = None
    region: str
    endpoint_url: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None  # 实际返回"***"或不返回


class S3ConfigUpdate(BaseModel):
    """更新S3配置"""

    enabled: Optional[bool] = None
    bucket_name: Optional[str] = None
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None


class S3TestRequest(BaseModel):
    """S3测试请求"""

    bucket_name: Optional[str] = None
    region: Optional[str] = None
    endpoint_url: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None


class EmailConfigResponse(BaseModel):
    """邮件配置响应"""

    enabled: bool
    smtp_host: Optional[str] = None
    smtp_port: int
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None  # 实际返回"***"或不返回
    from_address: Optional[str] = None
    to_addresses: List[str] = []


class EmailConfigUpdate(BaseModel):
    """更新邮件配置"""

    enabled: Optional[bool] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_address: Optional[str] = None
    to_addresses: Optional[List[str]] = None


class EmailTestRequest(BaseModel):
    """邮件测试请求"""

    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_address: Optional[str] = None


class TestEmailRequest(BaseModel):
    """发送测试邮件请求"""

    to_address: str = Field(..., description="收件人地址")
    config: Optional[EmailTestRequest] = None


class TestResponse(BaseModel):
    """测试响应"""

    success: bool
    message: str
    error: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class CrawlerConfigResponse(BaseModel):
    """爬虫配置响应"""

    request_delay: float = Field(0.5, description="爬取延迟（秒）")
    use_proxy: bool = Field(False, description="是否使用代理")
    kuaidaili_secret_id: Optional[str] = Field(None, description="快代理SecretId")
    kuaidaili_secret_key: Optional[str] = Field(None, description="快代理SecretKey")
    # 兼容旧字段（向后兼容）
    kuaidaili_api_key: Optional[str] = Field(
        None,
        description="快代理API密钥（格式：secret_id:secret_key，已废弃，使用secret_id和secret_key）",
    )


class CrawlerConfigUpdate(BaseModel):
    """更新爬虫配置"""

    request_delay: Optional[float] = Field(
        None, ge=0, description="爬取延迟（秒），最小值0"
    )
    use_proxy: Optional[bool] = Field(None, description="是否使用代理")
    kuaidaili_secret_id: Optional[str] = Field(None, description="快代理SecretId")
    kuaidaili_secret_key: Optional[str] = Field(None, description="快代理SecretKey")
    # 兼容旧字段（向后兼容）
    kuaidaili_api_key: Optional[str] = Field(
        None,
        description="快代理API密钥（格式：secret_id:secret_key，已废弃，使用secret_id和secret_key）",
    )


class KDLTestRequest(BaseModel):
    """快代理测试请求"""

    secret_id: str = Field(..., description="SecretId")
    secret_key: str = Field(..., description="SecretKey")
