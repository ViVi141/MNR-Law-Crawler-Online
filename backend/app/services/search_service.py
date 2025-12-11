"""
全文搜索服务 - PostgreSQL全文搜索
"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from ..models.policy import Policy

logger = logging.getLogger(__name__)


class SearchService:
    """全文搜索服务"""

    def __init__(self):
        """初始化搜索服务"""
        pass

    def search(
        self,
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        level: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[List[Policy], int]:
        """全文搜索政策

        Args:
            db: 数据库会话
            query: 搜索关键词
            skip: 跳过数量
            limit: 每页数量
            category: 分类筛选
            level: 效力级别筛选
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）

        Returns:
            (政策列表, 总数)
        """
        # 构建基础查询
        base_query = db.query(Policy)

        # 应用筛选条件
        if category:
            base_query = base_query.filter(Policy.category == category)
        if level:
            base_query = base_query.filter(Policy.level == level)
        if start_date:
            base_query = base_query.filter(Policy.pub_date >= start_date)
        if end_date:
            base_query = base_query.filter(Policy.pub_date <= end_date)

        # 如果没有搜索词，返回全量结果（应用筛选条件）
        if not query or not query.strip():
            total = base_query.count()
            results = (
                base_query.order_by(Policy.pub_date.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return results, total

        # 清理搜索词
        query = query.strip()

        # 使用简单搜索（LIKE 模式）
        # 注意：已移除中文分词功能，使用 PostgreSQL 的 ILIKE 进行模糊搜索
        return self.search_simple(
            db=db,
            query=query,
            skip=skip,
            limit=limit,
            category=category,
            level=level,
            start_date=start_date,
            end_date=end_date,
        )

    def search_simple(
        self,
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        level: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Tuple[List[Policy], int]:
        """全文搜索（使用 LIKE 模糊匹配）

        支持基本的LIKE搜索和筛选条件
        """
        # 构建基础查询
        base_query = db.query(Policy)

        # 应用筛选条件
        if category:
            base_query = base_query.filter(Policy.category == category)
        if level:
            base_query = base_query.filter(Policy.level == level)
        if start_date:
            base_query = base_query.filter(Policy.pub_date >= start_date)
        if end_date:
            base_query = base_query.filter(Policy.pub_date <= end_date)

        # 如果没有搜索词，返回全量结果（应用筛选条件）
        if not query or not query.strip():
            total = base_query.count()
            results = (
                base_query.order_by(Policy.pub_date.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
            return results, total

        query = query.strip()
        keyword_pattern = f"%{query}%"

        # 使用LIKE搜索（作为全文搜索的降级方案）
        # 支持多关键词搜索：将查询词分割，每个词都要匹配
        from sqlalchemy import or_, and_

        search_terms = query.split()
        if len(search_terms) > 1:
            # 多关键词：所有词都要在title或content中
            title_conditions = [
                Policy.title.ilike(f"%{term}%") for term in search_terms
            ]
            content_conditions = [
                Policy.content.ilike(f"%{term}%") for term in search_terms
            ]
            keywords_conditions = [
                Policy.keywords.ilike(f"%{term}%") for term in search_terms
            ]

            # 至少一个字段包含所有关键词
            search_filter = or_(
                and_(*title_conditions),
                and_(*content_conditions),
                and_(*keywords_conditions),
            )
        else:
            # 单关键词：任意字段匹配即可
            search_filter = (
                (Policy.title.ilike(keyword_pattern))
                | (Policy.content.ilike(keyword_pattern))
                | (Policy.keywords.ilike(keyword_pattern))
            )

        results = (
            base_query.filter(search_filter)
            .order_by(Policy.pub_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        total = base_query.filter(search_filter).count()

        return results, total

    def build_search_index(self, db: Session) -> dict:
        """构建全文搜索索引

        注意：PostgreSQL的全文搜索索引通过GIN索引自动维护，
        这里主要用于触发索引重建或更新统计信息
        """
        try:
            # 更新统计信息
            db.execute(text("ANALYZE policies"))

            # 确保所有政策都已索引
            # PostgreSQL的GIN索引会自动更新，但我们可以手动触发
            db.commit()

            # 统计已索引的政策数量
            indexed_count = (
                db.query(func.count(Policy.id))
                .filter(Policy.is_indexed.is_(True))
                .scalar()
                or 0
            )

            total_count = db.query(func.count(Policy.id)).scalar() or 0

            return {
                "success": True,
                "total_policies": total_count,
                "indexed_policies": indexed_count,
                "message": "索引更新完成",
            }

        except Exception as e:
            db.rollback()
            logger.error(f"构建搜索索引失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
