# ==============================================================================
# Policy Crawler Pro - 广东省法规爬虫
# ==============================================================================
#
# 项目名称: Policy Crawler Pro (政策爬虫专业版)
# 项目地址: https://github.com/ViVi141/policy-crawler-pro
# 作者: ViVi141
# 许可证: MIT License
#
# 描述: 广东省法规爬虫，适配广东省人大常委会法工委API
#       基于 gd-law-crawler 项目的爬虫逻辑
#
# ==============================================================================

"""
广东省法规爬虫
适配广东省人大常委会法工委API
"""

import logging
import time
from typing import Dict, List, Optional, Callable, Tuple
from datetime import datetime, timezone
from collections import defaultdict

from .gd_api_client import GDAPIClient
from .config import Config
from .models import Policy, PolicyDetail, FileAttachment

logger = logging.getLogger(__name__)

# 广东省政策类型配置
GD_LAW_RULE_TYPES = {
    1: {"name": "地方性法规", "code": "1"},
    2: {"name": "政府规章", "code": "2"},
    3: {"name": "规范性文件", "code": "3"},
}


class GDDataValidator:
    """广东省数据验证器 - 用于自动化检查数据质量和逻辑正确性"""

    def __init__(self):
        self.stats = {
            "total_policies": 0,
            "valid_policies": 0,
            "invalid_policies": 0,
            "duplicate_policies": 0,
            "missing_title": 0,
            "missing_id": 0,
            "missing_date": 0,
            "invalid_date_format": 0,
            "missing_url": 0,
            "duplicate_gd_ids": defaultdict(int),
            "type_distribution": defaultdict(int),
            "validation_errors": [],
        }

    def validate_policy(
        self, policy: Policy, law_rule_type: int
    ) -> Tuple[bool, List[str]]:
        """验证单个政策数据的完整性和正确性

        Args:
            policy: 政策对象
            law_rule_type: 政策类型

        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        is_valid = True

        # 检查必需字段
        if not policy.title or not policy.title.strip():
            errors.append("标题为空")
            self.stats["missing_title"] += 1
            is_valid = False

        if not hasattr(policy, "_gd_id") or not policy._gd_id:
            errors.append("缺少_gd_id字段")
            self.stats["missing_id"] += 1
            is_valid = False

        if not policy.pub_date:
            errors.append("发布日期为空")
            self.stats["missing_date"] += 1
            is_valid = False
        else:
            # 验证日期格式 (YYYY-MM-DD)
            try:
                datetime.strptime(policy.pub_date[:10], "%Y-%m-%d")
            except (ValueError, IndexError):
                errors.append(f"日期格式无效: {policy.pub_date}")
                self.stats["invalid_date_format"] += 1
                is_valid = False

        if not policy.source and not policy.link and not policy.url:
            errors.append("缺少URL")
            self.stats["missing_url"] += 1
            is_valid = False

        # 检查URL格式
        if policy.source:
            if not policy.source.startswith("http"):
                errors.append(f"URL格式无效: {policy.source}")
                is_valid = False

        # 检查政策类型一致性
        if hasattr(policy, "_gd_law_rule_type"):
            if policy._gd_law_rule_type != law_rule_type:
                errors.append(
                    f"政策类型不一致: 期望 {law_rule_type}, 实际 {policy._gd_law_rule_type}"
                )
                is_valid = False

        # 检查category是否匹配
        expected_category = GD_LAW_RULE_TYPES.get(law_rule_type, {}).get("name", "")
        if policy.category != expected_category:
            errors.append(
                f"分类不匹配: 期望 '{expected_category}', 实际 '{policy.category}'"
            )
            is_valid = False

        return is_valid, errors

    def check_duplicates(self, policies: List[Policy]) -> Dict[str, List[Policy]]:
        """检查重复政策

        Args:
            policies: 政策列表

        Returns:
            重复政策的字典 {unique_id: [policy1, policy2, ...]}
        """
        seen_ids = {}
        duplicates = {}

        for policy in policies:
            # 使用_gd_id进行去重检查
            if hasattr(policy, "_gd_id") and policy._gd_id:
                unique_id = f"gd_{policy._gd_id}"
            else:
                unique_id = policy.id

            if unique_id in seen_ids:
                if unique_id not in duplicates:
                    duplicates[unique_id] = [seen_ids[unique_id]]
                duplicates[unique_id].append(policy)
                self.stats["duplicate_policies"] += 1
                self.stats["duplicate_gd_ids"][unique_id] += 1
            else:
                seen_ids[unique_id] = policy

        return duplicates

    def validate_batch(
        self, policies: List[Policy], law_rule_type: int
    ) -> Tuple[List[Policy], List[Policy], Dict[str, any]]:
        """批量验证政策数据

        Args:
            policies: 政策列表
            law_rule_type: 政策类型

        Returns:
            (有效政策列表, 无效政策列表, 验证报告)
        """
        valid_policies = []
        invalid_policies = []
        validation_report = {
            "total": len(policies),
            "valid": 0,
            "invalid": 0,
            "errors_by_type": defaultdict(int),
            "invalid_policy_details": [],
        }

        for policy in policies:
            is_valid, errors = self.validate_policy(policy, law_rule_type)
            self.stats["total_policies"] += 1

            if is_valid:
                valid_policies.append(policy)
                self.stats["valid_policies"] += 1
                validation_report["valid"] += 1
            else:
                invalid_policies.append(policy)
                self.stats["invalid_policies"] += 1
                validation_report["invalid"] += 1
                for error in errors:
                    validation_report["errors_by_type"][error] += 1
                validation_report["invalid_policy_details"].append(
                    {
                        "title": policy.title[:50] if policy.title else "无标题",
                        "gd_id": getattr(policy, "_gd_id", "无ID"),
                        "errors": errors,
                    }
                )

        # 检查重复
        duplicates = self.check_duplicates(valid_policies)
        if duplicates:
            validation_report["duplicates"] = {
                unique_id: len(policies) for unique_id, policies in duplicates.items()
            }
            logger.warning(f"发现 {len(duplicates)} 个重复政策")

        return valid_policies, invalid_policies, validation_report

    def get_statistics(self) -> Dict[str, any]:
        """获取统计信息

        Returns:
            统计信息字典
        """
        stats = self.stats.copy()
        if stats["total_policies"] > 0:
            stats["validity_rate"] = (
                stats["valid_policies"] / stats["total_policies"] * 100
            )
            stats["duplicate_rate"] = (
                stats["duplicate_policies"] / stats["total_policies"] * 100
            )
        else:
            stats["validity_rate"] = 0.0
            stats["duplicate_rate"] = 0.0

        return stats

    def reset(self):
        """重置统计信息"""
        self.stats = {
            "total_policies": 0,
            "valid_policies": 0,
            "invalid_policies": 0,
            "duplicate_policies": 0,
            "missing_title": 0,
            "missing_id": 0,
            "missing_date": 0,
            "invalid_date_format": 0,
            "missing_url": 0,
            "duplicate_gd_ids": defaultdict(int),
            "type_distribution": defaultdict(int),
            "validation_errors": [],
        }


class GDSpider:
    """
    广东省法规爬虫
    适配 https://www.gdpc.gov.cn/
    """

    def __init__(self, config: Config, api_client: Optional[GDAPIClient] = None):
        """初始化爬虫

        Args:
            config: 配置对象
            api_client: API客户端（可选，如果不提供则创建新的）
        """
        self.config = config
        self.api_client = api_client or GDAPIClient(config)

        # 从配置获取参数（优先使用数据源配置）
        data_sources = config.get("data_sources", [])
        enabled_source = next(
            (
                ds
                for ds in data_sources
                if ds.get("enabled", True) and ds.get("name") == "广东省法规"
            ),
            None,
        )

        if enabled_source:
            self.api_base_url = enabled_source.get(
                "api_base_url", "https://www.gdpc.gov.cn:443/bascdata"
            )
            self.data_source = enabled_source  # 保存数据源配置
        else:
            # 使用默认配置
            self.api_base_url = config.get(
                "api_base_url", "https://www.gdpc.gov.cn:443/bascdata"
            )
            self.data_source = {
                "name": "广东省法规",
                "api_base_url": self.api_base_url,
                "level": "广东省",
            }

        self.level = "广东省"
        self.law_rule_types = GD_LAW_RULE_TYPES.copy()
        self.max_pages = config.get("max_pages", 999999)

        # 更新 API 客户端的配置
        if hasattr(self.api_client, "config"):
            self.api_client.config.set("api_base_url", self.api_base_url)

        # 初始化数据验证器
        self.validator = GDDataValidator()

    def crawl_policies(
        self,
        keywords: Optional[List[str]] = None,
        callback: Optional[Callable] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        law_rule_types: Optional[List[int]] = None,
        stop_callback: Optional[Callable] = None,
        policy_callback: Optional[Callable] = None,
    ) -> List[Policy]:
        """
        爬取广东省法规政策

        Args:
            keywords: 关键词列表（暂不支持，保留接口兼容性）
            callback: 进度回调函数
            start_date: 起始日期 yyyy-MM-dd（暂不支持，保留接口兼容性）
            end_date: 结束日期 yyyy-MM-dd（暂不支持，保留接口兼容性）
            law_rule_types: 政策类型列表 [1, 2, 3]，None表示爬取所有类型
            stop_callback: 停止回调函数
            policy_callback: 政策数据回调函数，每解析到一条政策时调用

        Returns:
            政策列表
        """
        if law_rule_types is None:
            law_rule_types = [1, 2, 3]  # 默认爬取所有类型

        results = []
        seen_ids = set()  # 用于去重（使用_gd_id，因为同一政策可能在不同类型下出现）

        if callback:
            if keywords:
                callback(
                    f"搜索关键词: {' '.join(keywords)} (注意：广东省API暂不支持关键词搜索)"
                )
            else:
                callback("全量爬取模式: 将爬取所有政策")
            callback(
                f"政策类型: {[GD_LAW_RULE_TYPES.get(t, {}).get('name', f'类型{t}') for t in law_rule_types]}"
            )

        # 遍历每个政策类型
        try:
            for law_rule_type in law_rule_types:
                if stop_callback and stop_callback():
                    if callback:
                        callback("停止爬取")
                    break

                type_name = GD_LAW_RULE_TYPES.get(law_rule_type, {}).get(
                    "name", f"类型{law_rule_type}"
                )
                if callback:
                    callback(f"\n开始爬取【{type_name}】...")

                # 获取该类型的所有政策（使用try-except确保单个类型失败不影响其他类型）
                try:
                    policies = self._search_all_policies(
                        law_rule_type=law_rule_type,
                        callback=callback,
                        stop_callback=stop_callback,
                        policy_callback=policy_callback,
                    )
                except Exception as type_error:
                    logger.error(
                        f"爬取【{type_name}】时发生异常: {type_error}", exc_info=True
                    )
                    if callback:
                        callback(
                            f"[错误] 爬取【{type_name}】时发生异常: {str(type_error)[:100]}，跳过该类型"
                        )
                    # 继续处理下一个类型，不中断整个流程
                    policies = []

                # 数据验证和去重
                # 先进行批量验证
                valid_policies, invalid_policies, validation_report = (
                    self.validator.validate_batch(policies, law_rule_type)
                )

                # 记录验证结果
                if invalid_policies:
                    logger.warning(
                        f"【{type_name}】发现 {len(invalid_policies)} 条无效政策数据"
                    )
                    if callback:
                        callback(
                            f"[数据检查] 【{type_name}】发现 {len(invalid_policies)} 条无效政策数据"
                        )

                # 去重并添加到结果列表
                # 注意：对于广东省数据源，使用_gd_id进行去重，因为同一政策可能在不同类型下出现
                # policy.id包含lawRuleType参数，会导致同一政策被重复计数
                deduplicated_count = 0
                for policy in valid_policies:
                    # 优先使用_gd_id进行去重（API返回的原始ID）
                    if hasattr(policy, "_gd_id") and policy._gd_id:
                        unique_id = f"gd_{policy._gd_id}"
                    else:
                        # 如果没有_gd_id，回退到使用policy.id
                        unique_id = policy.id

                    if unique_id not in seen_ids:
                        seen_ids.add(unique_id)
                        results.append(policy)
                    else:
                        deduplicated_count += 1
                        logger.debug(
                            f"跳过重复政策: {policy.title[:50]} (gd_id: {getattr(policy, '_gd_id', 'N/A')})"
                        )

                # 记录去重统计
                if deduplicated_count > 0:
                    logger.info(
                        f"【{type_name}】去重: 原始 {len(valid_policies)} 条，去重后 {len(valid_policies) - deduplicated_count} 条，"
                        f"重复 {deduplicated_count} 条"
                    )

                if callback:
                    callback(
                        f"【{type_name}】爬取完成: 原始 {len(policies)} 条，"
                        f"有效 {len(valid_policies)} 条，"
                        f"去重后累计 {len(results)} 条"
                    )
        except Exception as e:
            # 捕获所有未预期的异常，记录日志
            logger.error(f"爬取广东省政策时发生未预期异常: {e}", exc_info=True)
            if callback:
                callback(f"[严重错误] 爬取过程中发生异常: {str(e)[:100]}，已停止爬取")
            # 如果已经获取到一些政策，返回已获取的结果；否则重新抛出异常
            if len(results) > 0:
                logger.warning(
                    f"爬取过程中发生异常，但已获取 {len(results)} 条政策，返回部分结果"
                )
                return results
            else:
                # 如果没有获取到任何政策，重新抛出异常，让上层处理
                raise

        # 生成最终统计报告
        final_stats = self.validator.get_statistics()
        logger.info(
            f"广东省爬取完成统计: "
            f"总计 {final_stats['total_policies']} 条，"
            f"有效 {final_stats['valid_policies']} 条 ({final_stats.get('validity_rate', 0):.1f}%)，"
            f"无效 {final_stats['invalid_policies']} 条，"
            f"重复 {final_stats['duplicate_policies']} 条 ({final_stats.get('duplicate_rate', 0):.1f}%)"
        )

        # 记录详细的验证错误（如果有）
        if final_stats["validation_errors"]:
            error_summary = defaultdict(int)
            for error_detail in final_stats["validation_errors"]:
                for error in error_detail.get("errors", []):
                    error_summary[error] += 1
            logger.warning(f"数据验证错误汇总: {dict(error_summary)}")

        if callback:
            callback(
                f"\n总计爬取 {len(results)} 条政策（已去重）\n"
                f"[数据检查] 总计 {final_stats['total_policies']} 条，"
                f"有效 {final_stats['valid_policies']} 条，"
                f"无效 {final_stats['invalid_policies']} 条，"
                f"重复 {final_stats['duplicate_policies']} 条"
            )

        return results

    def _search_all_policies(
        self,
        law_rule_type: int,
        callback: Optional[Callable] = None,
        stop_callback: Optional[Callable] = None,
        policy_callback: Optional[Callable] = None,
    ) -> List[Policy]:
        """搜索指定类型的所有政策

        Args:
            law_rule_type: 政策类型 (1/2/3)
            callback: 进度回调函数
            stop_callback: 停止回调函数
            policy_callback: 政策数据回调函数

        Returns:
            政策列表
        """
        policies = []
        page_num = 1
        page_size = self.config.get("page_size", 20)

        type_name = GD_LAW_RULE_TYPES.get(law_rule_type, {}).get(
            "name", f"类型{law_rule_type}"
        )

        if callback:
            callback(f"正在获取【{type_name}】列表...")

        try:
            while True:
                # 检查停止标志
                if stop_callback and stop_callback():
                    if callback:
                        callback(f"停止获取 {type_name} 列表")
                    break

                # 检查最大页数限制
                if page_num > self.max_pages:
                    if callback:
                        callback(f"达到最大页数限制: {self.max_pages}")
                    break

                # 调用API搜索政策列表
                try:
                    result = self.api_client.search_policies(
                        law_rule_type, page_num, page_size
                    )
                except Exception as api_error:
                    logger.error(f"调用API搜索政策列表失败: {api_error}", exc_info=True)
                    if callback:
                        callback(
                            f"第 {page_num} 页API调用异常: {str(api_error)[:100]}，停止翻页"
                        )
                    break

                if not result:
                    if callback:
                        callback(f"第 {page_num} 页获取失败，停止翻页")
                    break

                data = result.get("data", {}) or {}
                rows = data.get("rows") or []
                total = data.get("total", 0)

                if not rows:
                    if callback:
                        callback(f"第 {page_num} 页无数据，停止翻页")
                    break

                # 转换为Policy对象并进行数据验证
                for row in rows:
                    try:
                        policy = self._parse_policy_from_row(row, law_rule_type)
                        if policy:
                            # 验证政策数据
                            is_valid, errors = self.validator.validate_policy(
                                policy, law_rule_type
                            )
                            if not is_valid:
                                logger.warning(
                                    f"政策数据验证失败: {policy.title[:50] if policy.title else '无标题'}, "
                                    f"错误: {', '.join(errors)}"
                                )
                                # 记录验证错误但继续处理（允许部分数据不完整）
                                self.validator.stats["validation_errors"].extend(
                                    [
                                        {
                                            "policy_title": (
                                                policy.title[:100]
                                                if policy.title
                                                else "无标题"
                                            ),
                                            "gd_id": getattr(policy, "_gd_id", "无ID"),
                                            "errors": errors,
                                        }
                                    ]
                                )

                            policies.append(policy)
                            self.validator.stats["type_distribution"][
                                law_rule_type
                            ] += 1

                            # 调用政策回调
                            if policy_callback:
                                try:
                                    policy_callback(policy)
                                except Exception as cb_error:
                                    logger.warning(
                                        f"调用policy_callback失败: {cb_error}"
                                    )
                    except Exception as parse_error:
                        logger.error(
                            f"解析政策数据失败: {parse_error}, row: {row}",
                            exc_info=True,
                        )
                        # 继续处理下一条，不中断整个流程
                        continue

                if callback:
                    callback(
                        f"列表第 {page_num} 页: {len(rows)} 条，累计 {len(policies)}/{total} 条"
                    )

                # 如果已获取所有数据，退出
                if len(rows) < page_size or len(policies) >= total:
                    break

                page_num += 1
                time.sleep(self.config.get("request_delay", 2))
        except Exception as e:
            # 捕获所有未预期的异常，记录日志但不中断整个流程
            logger.error(
                f"获取【{type_name}】政策列表时发生未预期异常: {e}", exc_info=True
            )
            if callback:
                callback(
                    f"[错误] 获取【{type_name}】列表时发生异常: {str(e)[:100]}，已停止"
                )
            # 返回已获取的政策列表，不抛出异常

        if callback:
            callback(f"完成获取【{type_name}】列表，共 {len(policies)} 条政策")

        return policies

    def _parse_policy_from_row(self, row: Dict, law_rule_type: int) -> Optional[Policy]:
        """从API响应行数据解析Policy对象

        Args:
            row: API返回的行数据
            law_rule_type: 政策类型

        Returns:
            Policy对象
        """
        try:
            # 提取基本信息
            policy_id = str(row.get("id", ""))
            title = row.get("title", "")
            office = (
                row.get("officeVo", {}).get("groupName", "")
                if row.get("officeVo")
                else ""
            )
            pass_date = row.get("passDate", "")
            formulate_mode = row.get("formulateMode", "")
            timeliness = row.get("timeliness", "")
            file_type = row.get("fileType", "")
            tag_names = row.get("tagNames", "")

            # 构建详情URL
            detail_url = f"https://www.gdpc.gov.cn:443/bascdata/securityJsp/nfrr_inner/internet/lawRule/lawRuleDetail.jsp?id={policy_id}&lawRuleType={law_rule_type}"

            # 创建Policy对象
            policy = Policy(
                title=title,
                pub_date=pass_date[:10] if pass_date else "",
                doc_number="",  # 广东省API中没有发文字号字段
                source=detail_url,
                link=detail_url,
                url=detail_url,
                content="",  # 内容需要从详情API获取
                category=GD_LAW_RULE_TYPES.get(law_rule_type, {}).get("name", ""),
                level=self.level,
                validity=timeliness,
                effective_date="",  # 需要从详情API获取
                publisher=office,
                crawl_time=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                _data_source=self.data_source,
            )

            # 添加额外的属性（用于后续详情爬取）
            policy._gd_id = policy_id  # 保存原始ID
            policy._gd_law_rule_type = law_rule_type  # 保存政策类型
            policy._gd_formulate_mode = formulate_mode
            policy._gd_file_type = file_type
            policy._gd_tag_names = tag_names

            return policy

        except Exception as e:
            logger.error(f"解析政策数据失败: {e}, row: {row}")
            return None

    def get_policy_detail(self, policy: Policy) -> Optional[PolicyDetail]:
        """获取政策详情

        Args:
            policy: 政策对象（必须包含 _gd_id 属性）

        Returns:
            PolicyDetail对象，如果失败返回None
        """
        if not hasattr(policy, "_gd_id"):
            logger.error("政策对象缺少 _gd_id 属性")
            return None

        policy_id = policy._gd_id

        # 调用API获取详情
        detail_data = self.api_client.get_policy_detail(policy_id)
        if not detail_data:
            logger.error(f"获取政策详情失败: {policy_id}")
            return None

        law_rule = detail_data.get("lawRule", {})
        file_list = detail_data.get("list", [])

        # 更新政策信息
        policy.content = law_rule.get("content", "")
        policy.effective_date = (
            law_rule.get("effectiveDate", "")[:10]
            if law_rule.get("effectiveDate")
            else ""
        )

        # 转换附件列表
        attachments = []
        for f in file_list:
            attachment = FileAttachment(
                file_name=f.get("fileName", ""),
                file_url=f.get("filePath", ""),
                file_ext=f.get("fileExt", ""),
            )
            attachments.append(attachment)

        # 创建PolicyDetail对象
        detail = PolicyDetail(
            policy=policy,
            attachments=attachments,
        )

        # 保存额外的详情信息（用于后续处理）
        detail._gd_law_rule = law_rule
        detail._gd_keywords = law_rule.get("keywords", "")
        detail._gd_associate_id = law_rule.get("associate", "")

        return detail
