"""
附件模型
"""

from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from ..database import Base


class Attachment(Base):
    """附件表"""

    __tablename__ = "attachments"

    id = Column(BigInteger, primary_key=True, index=True)
    policy_id = Column(
        BigInteger,
        ForeignKey("policies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name = Column(String(500), nullable=False)
    file_url = Column(Text, nullable=False)
    file_path = Column(String(500))  # 本地路径
    file_s3_key = Column(String(500))  # S3键
    file_type = Column(String(50))  # docx/pdf/doc
    file_size = Column(BigInteger)  # 字节
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("idx_attachments_policy_id", "policy_id"),)
