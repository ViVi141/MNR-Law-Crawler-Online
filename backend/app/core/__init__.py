"""
核心业务逻辑（复用原有core模块）
"""

__version__ = "2.0.0"

from .crawler import PolicyCrawler
from .converter import DocumentConverter
from .api_client import APIClient
from .config import Config
from .models import Policy, PolicyDetail, FileAttachment, CrawlProgress

__all__ = [
    "PolicyCrawler",
    "DocumentConverter",
    "APIClient",
    "Config",
    "Policy",
    "PolicyDetail",
    "FileAttachment",
    "CrawlProgress",
]
