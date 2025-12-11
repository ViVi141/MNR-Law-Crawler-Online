"""
配置管理模块 - Web版本
支持环境变量和配置文件
"""

import logging
from pathlib import Path
from typing import Optional, Any
from pydantic_settings import BaseSettings
from pydantic import Field
import json

# 确定.env文件路径（优先当前工作目录，然后是backend目录）
_env_file = None
# 1. 先检查当前工作目录
if (Path.cwd() / ".env").exists():
    _env_file = Path.cwd() / ".env"
# 2. 检查backend目录
elif (Path(__file__).parent.parent / ".env").exists():
    _env_file = Path(__file__).parent.parent / ".env"
# 3. 检查backend/app目录的父目录
elif (Path(__file__).parent.parent.parent / ".env").exists():
    _env_file = Path(__file__).parent.parent.parent / ".env"
else:
    _env_file = Path.cwd() / ".env"  # 默认使用当前目录


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    app_name: str = "MNR Law Crawler Web"
    app_version: str = "3.0.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # 数据库配置
    database_url: str = Field(
        default="postgresql://mnr_user:mnr_password@localhost:5432/mnr_crawler",
        env="DATABASE_URL"
    )
    
    # JWT配置
    jwt_secret_key: str = Field(
        default="change-me-in-production",
        env="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=1440, env="JWT_EXPIRE_MINUTES")  # 24小时
    
    # 存储配置
    storage_mode: str = Field(default="local", env="STORAGE_MODE")  # local/s3
    storage_local_dir: str = Field(default="./crawled_data", env="STORAGE_LOCAL_DIR")
    
    # 缓存配置
    cache_enabled: bool = Field(default=True, env="CACHE_ENABLED")
    cache_dir: str = Field(default="./cache", env="CACHE_DIR")
    cache_ttl_seconds: int = Field(default=86400, env="CACHE_TTL_SECONDS")  # 24小时
    cache_max_size_gb: int = Field(default=10, env="CACHE_MAX_SIZE_GB")
    
    # S3配置（可选）
    s3_enabled: bool = Field(default=False, env="S3_ENABLED")
    s3_provider: str = Field(default="aws", env="S3_PROVIDER")  # aws/minio/aliyun
    s3_bucket_name: str = Field(default="", env="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", env="S3_REGION")
    s3_endpoint_url: Optional[str] = Field(default=None, env="S3_ENDPOINT_URL")
    s3_access_key_id: Optional[str] = Field(default=None, env="S3_ACCESS_KEY_ID")
    s3_secret_access_key: Optional[str] = Field(default=None, env="S3_SECRET_ACCESS_KEY")
    
    # 邮件配置（可选）
    email_enabled: bool = Field(default=False, env="EMAIL_ENABLED")
    email_smtp_host: Optional[str] = Field(default=None, env="EMAIL_SMTP_HOST")
    email_smtp_port: int = Field(default=587, env="EMAIL_SMTP_PORT")
    email_smtp_user: Optional[str] = Field(default=None, env="EMAIL_SMTP_USER")
    email_smtp_password: Optional[str] = Field(default=None, env="EMAIL_SMTP_PASSWORD")
    email_from_address: Optional[str] = Field(default=None, env="EMAIL_FROM_ADDRESS")
    email_to_addresses: str = Field(default="[]", env="EMAIL_TO_ADDRESSES")  # JSON数组字符串
    
    # 定时任务配置
    scheduler_enabled: bool = Field(default=False, env="SCHEDULER_ENABLED")
    
    # 日志配置
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./logs/app.log", env="LOG_FILE")
    
    # CORS配置（允许前端直接访问）
    cors_origins: str = Field(
        default='["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"]',
        env="CORS_ORIGINS"
    )
    
    class Config:
        env_file = str(_env_file) if _env_file.exists() else ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> list:
        """解析CORS origins"""
        try:
            return json.loads(self.cors_origins)
        except Exception:
            return ["http://localhost:3000", "http://localhost:8080"]
    
    @property
    def email_to_addresses_list(self) -> list:
        """解析邮件收件人列表"""
        try:
            return json.loads(self.email_to_addresses)
        except Exception:
            return []


# 全局配置实例
settings = Settings()


class ConfigManager:
    """配置管理器（从数据库读取系统配置）"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self._cache = {}
    
    def get(self, key: str, default: Any = None, category: str = None) -> Any:
        """获取配置值"""
        if self.db_session is None:
            return default
        
        try:
            from .models.system_config import SystemConfig
            config = self.db_session.query(SystemConfig).filter(SystemConfig.key == key).first()
            if config:
                return config.value
            return default
        except Exception as e:
            logging.error(f"获取配置失败: {e}")
            return default
    
    def set(self, key: str, value: Any, category: str = "system") -> bool:
        """设置配置值"""
        if self.db_session is None:
            return False
        
        try:
            from .models.system_config import SystemConfig
            from datetime import datetime
            
            config = self.db_session.query(SystemConfig).filter(SystemConfig.key == key).first()
            if config:
                config.value = str(value)
                config.updated_at = datetime.utcnow()
            else:
                config = SystemConfig(
                    key=key,
                    value=str(value),
                    category=category
                )
                self.db_session.add(config)
            
            self.db_session.commit()
            return True
        except Exception as e:
            logging.error(f"保存配置失败: {e}")
            self.db_session.rollback()
            return False
    
    def get_feature_enabled(self, feature_name: str) -> bool:
        """获取功能开关状态"""
        value = self.get(f"feature_{feature_name}.enabled", "false", "feature")
        return value.lower() == "true"
    
    def set_feature_enabled(self, feature_name: str, enabled: bool) -> bool:
        """设置功能开关状态"""
        return self.set(f"feature_{feature_name}.enabled", str(enabled).lower(), "feature")

