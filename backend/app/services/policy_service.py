"""
政策服务 - 整合爬虫和数据库操作
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.policy import Policy as PolicyModel
from ..models.attachment import Attachment
from .storage_service import StorageService

logger = logging.getLogger(__name__)


class PolicyService:
    """政策服务"""

    def __init__(self):
        """初始化政策服务"""
        self.storage_service = StorageService()

    def save_policy(
        self, db: Session, policy_data: Dict[str, Any], task_id: Optional[int] = None
    ) -> Optional[PolicyModel]:
        """保存政策到数据库

        Args:
            db: 数据库会话
            policy_data: 政策数据字典（来自爬虫）
            task_id: 关联的任务ID

        Returns:
            PolicyModel对象，如果已存在则返回现有对象
        """
        try:
            # 解析日期
            pub_date = self._parse_date(policy_data.get("pub_date"))
            effective_date = self._parse_date(policy_data.get("effective_date"))
            crawl_time = datetime.now(timezone.utc)

            # 检查政策是否已存在（基于任务ID，确保每个任务的数据独立）
            if task_id:
                # 如果提供了task_id，检查是否存在相同的(title, source_url, pub_date, task_id)
                existing_policy = (
                    db.query(PolicyModel)
                    .filter(
                        PolicyModel.title == policy_data.get("title", ""),
                        PolicyModel.source_url
                        == policy_data.get("source", policy_data.get("url", "")),
                        PolicyModel.pub_date == pub_date,
                        PolicyModel.task_id == task_id,
                    )
                    .first()
                )
            else:
                # 如果没有task_id，检查是否存在相同的(title, source_url, pub_date)且task_id为NULL（兼容旧数据）
                existing_policy = (
                    db.query(PolicyModel)
                    .filter(
                        PolicyModel.title == policy_data.get("title", ""),
                        PolicyModel.source_url
                        == policy_data.get("source", policy_data.get("url", "")),
                        PolicyModel.pub_date == pub_date,
                        PolicyModel.task_id.is_(None),
                    )
                    .first()
                )

            if existing_policy:
                logger.debug(
                    f"政策已存在，跳过: {existing_policy.title} (Task: {task_id})"
                )
                return existing_policy

            # 计算字数
            content = policy_data.get("content", "")
            word_count = len(content) if content else 0

            # 处理关键词（JSON数组字符串）
            keywords = policy_data.get("keywords", [])
            if isinstance(keywords, list):
                keywords_str = json.dumps(keywords, ensure_ascii=False)
            elif isinstance(keywords, str):
                keywords_str = keywords
            else:
                keywords_str = "[]"

            # 处理source_name：优先使用policy_data中的source_name，如果没有则从_data_source获取
            source_name = policy_data.get("source_name", "")
            if not source_name:
                # 尝试从_data_source获取数据源名称
                data_source = policy_data.get("_data_source") or policy_data.get(
                    "data_source"
                )
                if data_source and isinstance(data_source, dict):
                    source_name = data_source.get("name", "")

            # 如果还是没有，尝试从source_url推断（兼容旧数据）
            if not source_name:
                source_url = policy_data.get("source", policy_data.get("url", ""))
                if source_url:
                    # 根据URL判断数据源
                    if "gi.mnr.gov.cn" in source_url:
                        source_name = "政府信息公开平台"
                    elif "f.mnr.gov.cn" in source_url:
                        source_name = "政策法规库"
                    else:
                        from urllib.parse import urlparse

                        parsed = urlparse(source_url)
                        source_name = parsed.netloc or "未知来源"

            # 创建政策记录（包含task_id，确保每个任务的数据独立）
            policy = PolicyModel(
                title=policy_data.get("title", ""),
                doc_number=policy_data.get("doc_number", ""),
                pub_date=pub_date,
                effective_date=effective_date,
                category=policy_data.get("category", ""),
                category_code=policy_data.get("category_code", ""),
                level=policy_data.get("level", ""),
                validity=policy_data.get("validity", ""),
                source_url=policy_data.get("source", policy_data.get("url", "")),
                source_name=source_name,
                content=content,
                content_summary=policy_data.get("content_summary", ""),
                publisher=policy_data.get("publisher", ""),
                keywords=keywords_str,
                word_count=word_count,
                crawl_time=crawl_time,
                is_indexed=False,
                task_id=task_id,  # 添加task_id，确保每个任务的数据独立
            )

            # 保存文件路径信息（如果有）
            # 兼容多种字段名
            if "json_path" in policy_data:
                policy.json_local_path = policy_data.get("json_path")
            elif "json_local_path" in policy_data:
                policy.json_local_path = policy_data.get("json_local_path")

            if "markdown_path" in policy_data:
                policy.markdown_local_path = policy_data.get("markdown_path")
            elif "markdown_local_path" in policy_data:
                policy.markdown_local_path = policy_data.get("markdown_local_path")

            if "docx_path" in policy_data:
                policy.docx_local_path = policy_data.get("docx_path")
            elif "docx_local_path" in policy_data:
                policy.docx_local_path = policy_data.get("docx_local_path")

            db.add(policy)
            db.flush()  # 获取policy.id

            # 保存附件（如果有）
            attachments = policy_data.get("attachments", [])
            if attachments:
                for att_data in attachments:
                    attachment = Attachment(
                        policy_id=policy.id,
                        file_name=att_data.get("file_name", ""),
                        file_url=att_data.get("file_url", ""),
                        file_size=att_data.get("file_size", 0),
                        file_type=att_data.get("file_ext", ""),
                        storage_path=att_data.get("storage_path", ""),
                    )
                    db.add(attachment)
                policy.attachment_count = len(attachments)

            # 标记为已索引（PostgreSQL会自动维护GIN索引）
            policy.is_indexed = True

            db.commit()
            db.refresh(policy)

            logger.info(f"政策保存成功: {policy.title} (ID: {policy.id})")
            return policy

        except IntegrityError:
            db.rollback()
            logger.warning(
                f"政策已存在（唯一约束冲突）: {policy_data.get('title', 'Unknown')} (Task: {task_id})"
            )
            # 尝试查找并返回现有政策（基于task_id）
            if task_id:
                existing_policy = (
                    db.query(PolicyModel)
                    .filter(
                        PolicyModel.title == policy_data.get("title", ""),
                        PolicyModel.source_url
                        == policy_data.get("source", policy_data.get("url", "")),
                        PolicyModel.pub_date == pub_date,
                        PolicyModel.task_id == task_id,
                    )
                    .first()
                )
            else:
                existing_policy = (
                    db.query(PolicyModel)
                    .filter(
                        PolicyModel.title == policy_data.get("title", ""),
                        PolicyModel.source_url
                        == policy_data.get("source", policy_data.get("url", "")),
                        PolicyModel.pub_date == pub_date,
                        PolicyModel.task_id.is_(None),
                    )
                    .first()
                )
            return existing_policy

        except Exception as e:
            db.rollback()
            logger.error(f"保存政策失败: {e}", exc_info=True)
            return None

    def save_policies_batch(
        self,
        db: Session,
        policies_data: List[Dict[str, Any]],
        task_id: Optional[int] = None,
    ) -> Dict[str, int]:
        """批量保存政策

        Returns:
            {
                "total": 总数,
                "saved": 成功保存数,
                "skipped": 跳过数（已存在）,
                "failed": 失败数
            }
        """
        result = {"total": len(policies_data), "saved": 0, "skipped": 0, "failed": 0}

        for policy_data in policies_data:
            try:
                policy = self.save_policy(db, policy_data, task_id)
                if policy:
                    # 检查是否是新创建的
                    if (
                        policy.crawl_time
                        and (
                            datetime.now(timezone.utc) - policy.crawl_time
                        ).total_seconds()
                        < 5
                    ):
                        result["saved"] += 1
                    else:
                        result["skipped"] += 1
                else:
                    result["failed"] += 1
            except Exception as e:
                logger.error(f"批量保存政策失败: {e}")
                result["failed"] += 1

        return result

    def get_policy_by_id(self, db: Session, policy_id: int) -> Optional[PolicyModel]:
        """根据ID获取政策"""
        return db.query(PolicyModel).filter(PolicyModel.id == policy_id).first()

    def get_policies(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        level: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        keyword: Optional[str] = None,
        publisher: Optional[str] = None,
        source_name: Optional[str] = None,
        task_id: Optional[int] = None,
    ) -> tuple[List[PolicyModel], int]:
        """获取政策列表（带筛选）

        Args:
            source_name: 数据源名称筛选（如"政府信息公开平台"、"政策法规库"）
            task_id: 任务ID筛选，只返回该任务爬取的政策

        Returns:
            (政策列表, 总数)
        """
        # 如果指定了task_id，直接通过policy.task_id筛选（更高效）
        if task_id:
            query = db.query(PolicyModel).filter(PolicyModel.task_id == task_id)
        else:
            query = db.query(PolicyModel)

        # 应用筛选条件
        if category:
            query = query.filter(PolicyModel.category == category)
        if level:
            query = query.filter(PolicyModel.level == level)
        if publisher:
            query = query.filter(PolicyModel.publisher == publisher)
        if source_name:
            query = query.filter(PolicyModel.source_name == source_name)
        if start_date:
            query = query.filter(PolicyModel.pub_date >= start_date)
        if end_date:
            query = query.filter(PolicyModel.pub_date <= end_date)
        if keyword:
            # 使用全文搜索服务进行关键词搜索（如果有复杂搜索需求）
            # 对于简单查询，使用LIKE搜索；对于复杂查询，可以调用SearchService
            keyword_pattern = f"%{keyword}%"
            query = query.filter(
                (PolicyModel.title.ilike(keyword_pattern))
                | (PolicyModel.content.ilike(keyword_pattern))
                | (PolicyModel.keywords.ilike(keyword_pattern))
            )

        # 由于policy.task_id直接关联任务，不需要去重

        # 获取总数
        total = query.count()

        # 分页和排序
        policies = (
            query.order_by(PolicyModel.pub_date.desc()).offset(skip).limit(limit).all()
        )

        return policies, total

    def delete_policy(self, db: Session, policy_id: int) -> bool:
        """删除政策"""
        try:
            policy = db.query(PolicyModel).filter(PolicyModel.id == policy_id).first()
            if not policy:
                return False

            # 删除关联的附件记录
            db.query(Attachment).filter(Attachment.policy_id == policy_id).delete()

            # 删除文件（如果需要）
            # TODO: 调用storage_service删除文件

            # 删除政策记录
            db.delete(policy)
            db.commit()

            logger.info(f"政策已删除: {policy_id}")
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"删除政策失败: {e}", exc_info=True)
            return False

    def get_categories(
        self, db: Session, source_name: Optional[str] = None
    ) -> List[str]:
        """获取分类列表

        Args:
            db: 数据库会话
            source_name: 可选的数据源名称，如果提供则只返回该数据源的分类

        Returns:
            分类列表
        """
        query = (
            db.query(PolicyModel.category)
            .distinct()
            .filter(PolicyModel.category.isnot(None), PolicyModel.category != "")
        )

        # 如果指定了数据源，只返回该数据源的分类
        if source_name:
            query = query.filter(PolicyModel.source_name == source_name)

        categories = query.all()
        return [cat[0] for cat in categories if cat[0]]

    def get_levels(self, db: Session) -> List[str]:
        """获取所有效力级别列表"""
        levels = (
            db.query(PolicyModel.level)
            .distinct()
            .filter(PolicyModel.level.isnot(None), PolicyModel.level != "")
            .all()
        )
        return [level[0] for level in levels]

    def get_source_names(self, db: Session) -> List[str]:
        """获取所有数据源名称列表"""
        source_names = (
            db.query(PolicyModel.source_name)
            .distinct()
            .filter(PolicyModel.source_name.isnot(None), PolicyModel.source_name != "")
            .all()
        )
        return [name[0] for name in source_names]

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """解析日期字符串"""
        if not date_str:
            return None

        try:
            # 尝试多种日期格式
            formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S", "%Y年%m月%d日"]

            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str.strip(), fmt)
                    return dt.date()
                except ValueError:
                    continue

            logger.warning(f"无法解析日期: {date_str}")
            return None

        except Exception as e:
            logger.error(f"日期解析错误: {e}")
            return None
