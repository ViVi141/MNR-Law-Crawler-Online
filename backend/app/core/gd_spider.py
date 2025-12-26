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
from typing import Dict, List, Optional, Callable
from datetime import datetime, timezone

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
        seen_ids = set()  # 用于去重

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

            # 获取该类型的所有政策
            policies = self._search_all_policies(
                law_rule_type=law_rule_type,
                callback=callback,
                stop_callback=stop_callback,
                policy_callback=policy_callback,
            )

            # 去重并添加到结果列表
            for policy in policies:
                policy_id = policy.id
                if policy_id not in seen_ids:
                    seen_ids.add(policy_id)
                    results.append(policy)

            if callback:
                callback(f"【{type_name}】爬取完成，共 {len(policies)} 条政策")

        if callback:
            callback(f"\n总计爬取 {len(results)} 条政策")

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
            result = self.api_client.search_policies(law_rule_type, page_num, page_size)

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

            # 转换为Policy对象
            for row in rows:
                policy = self._parse_policy_from_row(row, law_rule_type)
                if policy:
                    policies.append(policy)
                    # 调用政策回调
                    if policy_callback:
                        policy_callback(policy)

            if callback:
                callback(
                    f"列表第 {page_num} 页: {len(rows)} 条，累计 {len(policies)}/{total} 条"
                )

            # 如果已获取所有数据，退出
            if len(rows) < page_size or len(policies) >= total:
                break

            page_num += 1
            time.sleep(self.config.get("request_delay", 2))

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
