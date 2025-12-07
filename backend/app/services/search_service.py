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
        end_date: Optional[str] = None
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
            results = base_query.order_by(Policy.pub_date.desc()).offset(skip).limit(limit).all()
            return results, total
        
        # 清理搜索词
        query = query.strip()
        
        # 尝试使用PostgreSQL全文搜索，如果失败则降级到简单搜索
        try:
            # 使用PostgreSQL全文搜索（使用原始SQL）
            # 对于中文分词，搜索词会被zhparser自动分词
            # tsquery格式：对于中文，直接使用查询词，zhparser会自动分词
            # 使用plainto_tsquery可以自动处理中文分词和AND逻辑
            # 但我们先尝试简单的格式
            tsquery_str = query  # zhparser会自动分词，不需要手动分割
            
            # 使用PostgreSQL的ts_rank进行相关性排序
            # 构建完整SQL查询，包含相关性评分
            # search_terms 已在上面定义
            
            # 构建WHERE条件
            where_conditions = []
            params = {"tsquery": tsquery_str}
            
            # 全文搜索条件（使用中文分词配置 jiebacfg）
            # 使用 plainto_tsquery 自动处理中文分词，会将多个词自动用 AND 连接
            where_conditions.append("""
                to_tsvector('jiebacfg', 
                    COALESCE(title, '') || ' ' || 
                    COALESCE(content, '') || ' ' || 
                    COALESCE(keywords, '')
                ) @@ plainto_tsquery('jiebacfg', :tsquery)
            """)
            
            # 添加其他筛选条件
            if category:
                where_conditions.append("category = :category")
                params["category"] = category
            if level:
                where_conditions.append("level = :level")
                params["level"] = level
            if start_date:
                where_conditions.append("pub_date >= :start_date")
                params["start_date"] = start_date
            if end_date:
                where_conditions.append("pub_date <= :end_date")
                params["end_date"] = end_date
            
            # 使用ts_rank计算相关性得分，按相关性降序，然后按日期降序
            # 使用中文分词配置 jiebacfg
            search_sql = text(f"""
                SELECT policies.*,
                    ts_rank(
                        to_tsvector('jiebacfg', 
                            COALESCE(policies.title, '') || ' ' || 
                            COALESCE(policies.content, '') || ' ' || 
                            COALESCE(policies.keywords, '')
                        ),
                        plainto_tsquery('jiebacfg', :tsquery)
                    ) AS rank
                FROM policies
                WHERE {' AND '.join(where_conditions)}
                ORDER BY rank DESC, pub_date DESC
                LIMIT :limit OFFSET :skip
            """)
            
            params["limit"] = limit
            params["skip"] = skip
            
            # 执行查询
            result_proxy = db.execute(search_sql.bindparams(**params))
            
            # 将结果转换为Policy对象
            results = []
            for row in result_proxy:
                policy_dict = dict(row._mapping)
                # 移除rank字段，它不是Policy模型的属性
                policy_dict.pop('rank', None)
                # 创建Policy对象
                policy = Policy(**{k: v for k, v in policy_dict.items() if hasattr(Policy, k)})
                results.append(policy)
            
        except Exception as e:
            logger.warning(f"PostgreSQL全文搜索失败，降级到简单搜索: {e}")
            # 降级到简单搜索
            return self.search_simple(db, query, skip, limit)
        
        # 获取总数（需要单独的查询，因为带分页的count会有问题）
        try:
            # 使用原始SQL进行计数
            # 对于中文分词，搜索词会被zhparser自动分词
            tsquery_str = query  # zhparser会自动分词
            
            # 添加筛选条件到SQL（使用中文分词配置 jiebacfg）
            # 使用 plainto_tsquery 自动处理中文分词和AND逻辑
            conditions = ["to_tsvector('jiebacfg', COALESCE(title, '') || ' ' || COALESCE(content, '') || ' ' || COALESCE(keywords, '')) @@ plainto_tsquery('jiebacfg', :tsquery)"]
            params = {"tsquery": tsquery_str}
            
            if category:
                conditions.append("category = :category")
                params["category"] = category
            if level:
                conditions.append("level = :level")
                params["level"] = level
            if start_date:
                conditions.append("pub_date >= :start_date")
                params["start_date"] = start_date
            if end_date:
                conditions.append("pub_date <= :end_date")
                params["end_date"] = end_date
            
            count_sql = text(f"SELECT COUNT(*) FROM policies WHERE {' AND '.join(conditions)}").bindparams(**params)
            
            total = db.execute(count_sql).scalar() or 0
            
        except Exception as e:
            logger.warning(f"获取搜索结果总数失败: {e}")
            # 使用简单计数
            keyword_pattern = f"%{query}%"
            total = base_query.filter(
                (Policy.title.ilike(keyword_pattern)) |
                (Policy.content.ilike(keyword_pattern)) |
                (Policy.keywords.ilike(keyword_pattern))
            ).count()
        
        return results, total
    
    def search_simple(
        self,
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        level: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[Policy], int]:
        """简单全文搜索（降级方案）
        
        如果PostgreSQL全文搜索不可用，可以使用这个简化版本
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
            results = base_query.order_by(Policy.pub_date.desc()).offset(skip).limit(limit).all()
            return results, total
        
        query = query.strip()
        keyword_pattern = f"%{query}%"
        
        # 使用LIKE搜索（作为全文搜索的降级方案）
        # 支持多关键词搜索：将查询词分割，每个词都要匹配
        from sqlalchemy import or_, and_
        
        search_terms = query.split()
        if len(search_terms) > 1:
            # 多关键词：所有词都要在title或content中
            title_conditions = [Policy.title.ilike(f"%{term}%") for term in search_terms]
            content_conditions = [Policy.content.ilike(f"%{term}%") for term in search_terms]
            keywords_conditions = [Policy.keywords.ilike(f"%{term}%") for term in search_terms]
            
            # 至少一个字段包含所有关键词
            search_filter = or_(
                and_(*title_conditions),
                and_(*content_conditions),
                and_(*keywords_conditions)
            )
        else:
            # 单关键词：任意字段匹配即可
            search_filter = (
                (Policy.title.ilike(keyword_pattern)) |
                (Policy.content.ilike(keyword_pattern)) |
                (Policy.keywords.ilike(keyword_pattern))
            )
        
        results = base_query.filter(search_filter).order_by(
            Policy.pub_date.desc()
        ).offset(skip).limit(limit).all()
        
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
            indexed_count = db.query(func.count(Policy.id)).filter(
                Policy.is_indexed.is_(True)
            ).scalar() or 0
            
            total_count = db.query(func.count(Policy.id)).scalar() or 0
            
            return {
                "success": True,
                "total_policies": total_count,
                "indexed_policies": indexed_count,
                "message": "索引更新完成"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"构建搜索索引失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

