"""
数据模型定义 - 适配自然资源部API
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Policy:
    """政策基本信息 - 适配自然资源部API"""
    title: str
    pub_date: str  # 发布日期 YYYY-MM-DD
    doc_number: str = ""  # 发文字号
    source: str = ""  # 来源URL
    link: str = ""  # 链接（兼容字段）
    url: str = ""  # URL（兼容字段）
    content: str = ""  # 正文内容
    category: str = ""  # 分类
    level: str = "自然资源部"  # 机构级别
    validity: str = ""  # 有效性
    effective_date: str = ""  # 生效日期
    publisher: str = ""  # 发布机构
    crawl_time: str = ""  # 爬取时间
    _data_source: Optional[Dict[str, Any]] = None  # 数据源信息（内部使用）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "title": self.title,
            "pub_date": self.pub_date,
            "doc_number": self.doc_number,
            "source": self.source,
            "link": self.link or self.source,
            "url": self.url or self.source,
            "content": self.content,
            "category": self.category,
            "level": self.level,
            "validity": self.validity,
            "effective_date": self.effective_date,
            "publisher": self.publisher,
            "crawl_time": self.crawl_time,
        }
        # 如果存在_data_source，也包含在字典中
        if self._data_source:
            result["_data_source"] = self._data_source
            # 如果有name字段，也作为source_name传递
            if "name" in self._data_source:
                result["source_name"] = self._data_source["name"]
        # 如果存在文件路径属性，也包含在字典中
        if hasattr(self, 'markdown_path'):
            result["markdown_path"] = getattr(self, 'markdown_path', None)
        if hasattr(self, 'docx_path'):
            result["docx_path"] = getattr(self, 'docx_path', None)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Policy":
        """从字典创建"""
        return cls(
            title=data.get("title", ""),
            pub_date=data.get("pub_date", ""),
            doc_number=data.get("doc_number", ""),
            source=data.get("source", data.get("url", data.get("link", ""))),
            link=data.get("link", data.get("url", data.get("source", ""))),
            url=data.get("url", data.get("link", data.get("source", ""))),
            content=data.get("content", ""),
            category=data.get("category", ""),
            level=data.get("level", "自然资源部"),
            validity=data.get("validity", ""),
            effective_date=data.get("effective_date", ""),
            publisher=data.get("publisher", ""),
            crawl_time=data.get("crawl_time", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        )
    
    @property
    def id(self) -> str:
        """获取政策ID（使用标题和链接的组合）"""
        return f"{self.title}|{self.link or self.source}"


@dataclass
class FileAttachment:
    """附件信息"""
    file_name: str
    file_url: str
    file_ext: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "file_name": self.file_name,
            "file_url": self.file_url,
            "file_ext": self.file_ext,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileAttachment":
        """从字典创建"""
        return cls(
            file_name=data.get("file_name", ""),
            file_url=data.get("file_url", ""),
            file_ext=data.get("file_ext", ""),
        )


@dataclass
class PolicyDetail:
    """政策详细信息"""
    policy: Policy
    attachments: List[FileAttachment] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "policy": self.policy.to_dict(),
            "attachments": [att.to_dict() for att in self.attachments],
        }


@dataclass
class CrawlProgress:
    """爬取进度"""
    total_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    current_policy_id: str = ""
    current_policy_title: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    completed_policies: List[str] = field(default_factory=list)
    failed_policies: List[Dict[str, str]] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_count == 0:
            return 0.0
        return (self.completed_count / self.total_count) * 100
    
    @property
    def progress_percentage(self) -> float:
        """进度百分比"""
        if self.total_count == 0:
            return 0.0
        return ((self.completed_count + self.failed_count) / self.total_count) * 100
    
    @property
    def elapsed_time(self) -> Optional[float]:
        """已用时间（秒）"""
        if not self.start_time:
            return None
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_count": self.total_count,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "current_policy_id": self.current_policy_id,
            "current_policy_title": self.current_policy_title,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "completed_policies": self.completed_policies,
            "failed_policies": self.failed_policies,
            "success_rate": self.success_rate,
            "progress_percentage": self.progress_percentage,
            "elapsed_time": self.elapsed_time,
        }
