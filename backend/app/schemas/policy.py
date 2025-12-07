"""
政策Schema（Pydantic模型）
"""

import json
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator


class PolicyBase(BaseModel):
    """政策基础Schema"""
    title: str = Field(..., description="标题")
    doc_number: Optional[str] = Field(None, description="发文字号")
    pub_date: Optional[date] = Field(None, description="发布日期")
    effective_date: Optional[date] = Field(None, description="生效日期")
    category: Optional[str] = Field(None, description="分类")
    category_code: Optional[str] = Field(None, description="分类代码")
    level: Optional[str] = Field(None, description="效力级别")
    validity: Optional[str] = Field(None, description="有效性")
    source_url: str = Field(..., description="来源URL")
    source_name: Optional[str] = Field(None, description="来源名称")
    content: str = Field(..., description="全文内容")
    content_summary: Optional[str] = Field(None, description="摘要")
    publisher: Optional[str] = Field(None, description="发布机构")
    keywords: Optional[List[str]] = Field(None, description="关键词列表")
    
    @field_validator('keywords', mode='before')
    @classmethod
    def parse_keywords(cls, v):
        """解析keywords字段：如果是从数据库读取的JSON字符串，转换为列表"""
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                # 尝试解析JSON字符串
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return []
            except (json.JSONDecodeError, TypeError):
                # 如果不是有效的JSON，返回空列表
                return []
        # 其他类型，返回空列表
        return []


class PolicyCreate(PolicyBase):
    """创建政策Schema"""
    pass


class PolicyUpdate(BaseModel):
    """更新政策Schema"""
    title: Optional[str] = None
    doc_number: Optional[str] = None
    pub_date: Optional[date] = None
    effective_date: Optional[date] = None
    category: Optional[str] = None
    category_code: Optional[str] = None
    level: Optional[str] = None
    validity: Optional[str] = None
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    content: Optional[str] = None
    content_summary: Optional[str] = None
    publisher: Optional[str] = None
    keywords: Optional[List[str]] = None


class PolicyResponse(PolicyBase):
    """政策响应Schema"""
    id: int
    word_count: int = Field(0, description="字数")
    attachment_count: int = Field(0, description="附件数量")
    crawl_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PolicyListItem(BaseModel):
    """政策列表项Schema（列表视图优化版）
    
    包含列表展示所需的核心字段，相比PolicyResponse减少了详细内容字段
    以提升列表查询性能和减少数据传输量
    """
    id: int
    title: str
    doc_number: Optional[str] = None
    pub_date: Optional[date] = None
    effective_date: Optional[date] = None  # 生效日期
    category: Optional[str] = None
    category_code: Optional[str] = None  # 分类代码
    level: Optional[str] = None
    validity: Optional[str] = None  # 有效性（如：部门规范性文件、行政法规等）
    publisher: Optional[str] = None  # 发布机构
    source_name: Optional[str] = None  # 数据源名称
    source_url: Optional[str] = None  # 来源URL（用于跳转）
    content_summary: Optional[str] = None  # 内容摘要（如果有）
    word_count: int = 0
    attachment_count: int = 0
    crawl_time: Optional[datetime] = None
    created_at: Optional[datetime] = None  # 创建时间
    updated_at: Optional[datetime] = None  # 更新时间
    
    def model_dump(self, **kwargs):
        """重写dump方法，添加publish_date字段和组合显示字段用于前端兼容"""
        data = super().model_dump(**kwargs)
        if self.pub_date:
            data['publish_date'] = self.pub_date.isoformat()
        else:
            data['publish_date'] = None
        
        # 添加数据源-分类组合显示字段（用于区分不同数据源的分类）
        if self.source_name and self.category:
            # 如果分类是"全部"，只显示数据源名称
            if self.category == "全部":
                data['category_display'] = self.source_name
            else:
                data['category_display'] = f"{self.source_name}-{self.category}"
        elif self.category:
            data['category_display'] = self.category
        elif self.source_name:
            data['category_display'] = self.source_name
        else:
            data['category_display'] = "-"
        
        return data
    
    class Config:
        from_attributes = True


class PolicyListResponse(BaseModel):
    """政策列表响应"""
    items: List[PolicyListItem]
    total: int
    skip: int
    limit: int


class PolicySearchRequest(BaseModel):
    """政策搜索请求"""
    keyword: Optional[str] = Field(None, description="关键词")
    category: Optional[str] = Field(None, description="分类")
    level: Optional[str] = Field(None, description="效力级别")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(20, ge=1, le=100, description="每页数量")


class AttachmentResponse(BaseModel):
    """附件响应Schema"""
    id: int
    policy_id: int
    file_name: str
    file_url: str
    file_size: int
    file_type: Optional[str]
    
    class Config:
        from_attributes = True


class PolicyDetailResponse(PolicyResponse):
    """政策详情响应Schema"""
    attachments: List[AttachmentResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True

