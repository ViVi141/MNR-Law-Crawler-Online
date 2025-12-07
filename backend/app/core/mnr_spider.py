"""
自然资源部政府信息公开平台爬虫
适配 https://gi.mnr.gov.cn/
"""

from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time
from typing import Dict, List, Optional, Callable

from .api_client import APIClient
from .config import Config
from .models import Policy
from .html_parsers import get_parser_for_data_source

logger = logging.getLogger(__name__)

# 自然资源部分类配置（政府信息公开平台）
MNR_CATEGORIES = {
    '自然资源调查监测': {'code': '1318', 'name': '自然资源调查监测'},
    '自然资源确权登记': {'code': '1319', 'name': '自然资源确权登记'},
    '自然资源合理开发利用': {'code': '1320', 'name': '自然资源合理开发利用'},
    '自然资源有偿使用': {'code': '1321', 'name': '自然资源有偿使用'},
    '国土空间规划': {'code': '1322', 'name': '国土空间规划'},
    '国土空间用途管制': {'code': '1663', 'name': '国土空间用途管制'},
    '国土空间生态修复': {'code': '1324', 'name': '国土空间生态修复'},
    '耕地保护': {'code': '1325', 'name': '耕地保护'},
    '地质勘查': {'code': '1326', 'name': '地质勘查'},
    '矿产勘查': {'code': '1327', 'name': '矿产勘查'},
    '矿产保护': {'code': '1328', 'name': '矿产保护'},
    '矿产开发': {'code': '1329', 'name': '矿产开发'},
    '地质环境保护': {'code': '1330', 'name': '地质环境保护'},
    '海洋资源': {'code': '1331', 'name': '海洋资源'},
    '测绘地理信息': {'code': '1332', 'name': '测绘地理信息'},
    '地质灾害防治': {'code': '1334', 'name': '地质灾害防治'},
    '地质公园': {'code': '1335', 'name': '地质公园'},
    '地质遗迹保护': {'code': '1336', 'name': '地质遗迹保护'},
    '矿业权评估': {'code': '1338', 'name': '矿业权评估'},
    '机构建设': {'code': '1339', 'name': '机构建设'},
    '综合管理': {'code': '1340', 'name': '综合管理'},
    '其他': {'code': '1341', 'name': '其他'}
}


class MNRSpider:
    """
    自然资源部政府信息公开平台爬虫
    适配 https://gi.mnr.gov.cn/
    """
    
    def __init__(self, config: Config, api_client: Optional[APIClient] = None):
        """初始化爬虫
        
        Args:
            config: 配置对象
            api_client: API客户端（可选，如果不提供则创建新的）
        """
        self.config = config
        self.api_client = api_client or APIClient(config)
        
        # 从配置获取参数（优先使用数据源配置）
        data_sources = config.get("data_sources", [])
        enabled_source = next((ds for ds in data_sources if ds.get("enabled", True)), None)
        
        if enabled_source:
            self.base_url = enabled_source.get("base_url", "https://gi.mnr.gov.cn/")
            self.search_api = enabled_source.get("search_api", "https://search.mnr.gov.cn/was5/web/search")
            self.ajax_api = enabled_source.get("ajax_api", "https://search.mnr.gov.cn/was/ajaxdata_jsonp.jsp")
            self.channel_id = enabled_source.get("channel_id", "216640")
            self.data_source = enabled_source  # 保存数据源配置
        else:
            # 使用默认配置
            self.base_url = config.get("base_url", "https://gi.mnr.gov.cn/")
            self.search_api = config.get("search_api", "https://search.mnr.gov.cn/was5/web/search")
            self.ajax_api = config.get("ajax_api", "https://search.mnr.gov.cn/was/ajaxdata_jsonp.jsp")
            self.channel_id = config.get("channel_id", "216640")
            self.data_source = {
                'base_url': self.base_url,
                'level': '自然资源部'
            }
        
        self.level = "自然资源部"
        self.categories = MNR_CATEGORIES.copy()
        self.max_pages = config.get("max_pages", 999999)
        
        # 根据数据源获取对应的HTML解析器
        self.html_parser = get_parser_for_data_source(self.data_source)
        
        # 更新 API 客户端的 Referer
        if hasattr(self.api_client, 'session'):
            self.api_client.session.headers.update({
                'Referer': self.base_url
            })
    
    def crawl_policies(
        self,
        keywords: Optional[List[str]] = None,
        callback: Optional[Callable] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        stop_callback: Optional[Callable] = None,
        policy_callback: Optional[Callable] = None
    ) -> List[Policy]:
        """
        爬取自然资源部政府信息公开平台政策
        
        Args:
            keywords: 关键词列表
            callback: 进度回调函数
            start_date: 起始日期 yyyy-MM-dd
            end_date: 结束日期 yyyy-MM-dd
            category: 分类名称，None表示搜索全部分类
            stop_callback: 停止回调函数
            policy_callback: 政策数据回调函数，每解析到一条政策时调用
            
        Returns:
            政策列表
        """
        if keywords is None:
            keywords = []
        
        dt_start = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        dt_end = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        
        results = []
        seen_ids = set()  # 用于去重
        
        # 构建搜索关键词
        search_word = ' '.join(keywords) if keywords else ''
        
        if callback:
            if search_word:
                callback(f"搜索关键词: {search_word}")
            else:
                callback("全量爬取模式: 无关键词限制，将爬取所有政策")
            if category:
                callback(f"指定分类: {category}")
            else:
                callback("分类范围: 全部分类")
            if start_date or end_date:
                callback(f"时间范围: {start_date or '不限'} 至 {end_date or '不限'}")
            else:
                callback("时间范围: 无限制（全量爬取）")
        
        # 分页获取数据
        page = 1
        max_consecutive_empty = self.config.get("max_empty_pages", 3)
        consecutive_empty_pages = 0
        
        while page <= self.max_pages:
            if stop_callback and stop_callback():
                break
            
            if callback:
                callback(f"正在抓取第{page}页...")
            
            try:
                # 构建搜索参数
                params = {
                    'channelid': self.channel_id,
                    'searchword': search_word,
                    'page': page,
                    'perpage': self.config.get("perpage", 20),
                    'searchtype': 'title',
                    'orderby': 'RELEVANCE'
                }
                
                # 添加时间过滤
                if start_date:
                    params['starttime'] = start_date
                if end_date:
                    params['endtime'] = end_date
                
                # 发送搜索请求
                result = self.api_client.search_policies(
                    keywords, page, start_date, end_date,
                    data_source={
                        'base_url': self.base_url,
                        'search_api': self.search_api,
                        'channel_id': self.channel_id
                    }
                )
                
                if not result:
                    consecutive_empty_pages += 1
                    if callback:
                        callback(f"第{page}页API请求失败或无响应")
                    if consecutive_empty_pages >= max_consecutive_empty:
                        if callback:
                            callback(f"连续{max_consecutive_empty}页无数据，停止爬取")
                        break
                    page += 1
                    continue
                
                # 解析响应数据
                page_policies = []
                if result['type'] == 'json':
                    page_policies = self._parse_json_results(result['data'], callback)
                elif result['type'] == 'html':
                    soup = BeautifulSoup(result['data'], 'html.parser')
                    # 使用专门的HTML解析器
                    page_policies = self.html_parser.parse(soup, callback, category or '全部')
                
                if not page_policies:
                    consecutive_empty_pages += 1
                    if callback:
                        callback(f"第{page}页无数据")
                    if consecutive_empty_pages >= max_consecutive_empty:
                        if callback:
                            callback(f"连续{max_consecutive_empty}页无数据，停止爬取")
                        break
                    page += 1
                    continue
                else:
                    consecutive_empty_pages = 0
                
                # 过滤和验证数据
                new_policies_count = 0
                for policy_data in page_policies:
                    # 转换为 Policy 对象
                    if isinstance(policy_data, dict):
                        policy = Policy(
                            title=policy_data.get('title', ''),
                            pub_date=policy_data.get('pub_date', ''),
                            doc_number=policy_data.get('doc_number', ''),
                            source=policy_data.get('link', '') or policy_data.get('source', ''),
                            link=policy_data.get('link', '') or policy_data.get('source', ''),
                            url=policy_data.get('link', '') or policy_data.get('source', ''),
                            content=policy_data.get('content', ''),
                            category=policy_data.get('category', ''),
                            level=self.level,
                            validity=policy_data.get('validity', ''),
                            effective_date=policy_data.get('effective_date', ''),
                            crawl_time=policy_data.get('crawl_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        )
                    else:
                        policy = policy_data
                    
                    # 去重检查
                    policy_id = policy.id
                    if policy_id in seen_ids:
                        if callback:
                            callback(f"跳过重复政策: {policy.title}")
                        continue
                    
                    # 时间过滤
                    if policy.pub_date:
                        pub_date_fmt = self._parse_date(policy.pub_date)
                        if pub_date_fmt:
                            if dt_start and pub_date_fmt < dt_start:
                                continue
                            if dt_end and pub_date_fmt > dt_end:
                                continue
                    
                    # 关键词过滤
                    if keywords and not any(kw in policy.title for kw in keywords):
                        continue
                    
                    # 获取详情页内容（如果还没有）
                    if not policy.content and policy.link:
                        if callback:
                            callback(f"获取详情: {policy.title[:30]}...")
                        logger.debug(f"获取政策详情: {policy.title[:50]}...")
                        detail_result = self.api_client.get_policy_detail(
                            policy.link,
                            data_source={
                                'base_url': self.base_url
                            }
                        )
                        policy.content = detail_result.get('content', '')
                        
                        # 更新元信息
                        metadata = detail_result.get('metadata', {})
                        if metadata:
                            if metadata.get('pub_date') and not policy.pub_date:
                                parsed_date = self._parse_date(metadata['pub_date'])
                                if parsed_date:
                                    policy.pub_date = parsed_date.strftime('%Y-%m-%d')
                            if metadata.get('level'):
                                policy.level = metadata['level']
                            if metadata.get('validity'):
                                policy.validity = metadata['validity']
                            if metadata.get('category'):
                                policy.category = metadata['category']
                            if metadata.get('publisher'):
                                policy.publisher = metadata['publisher']
                            if metadata.get('effective_date'):
                                parsed_eff_date = self._parse_date(metadata['effective_date'])
                                if parsed_eff_date:
                                    policy.effective_date = parsed_eff_date.strftime('%Y-%m-%d')
                            if metadata.get('doc_number') and not policy.doc_number:
                                policy.doc_number = metadata['doc_number']
                    
                    # 添加到结果
                    seen_ids.add(policy_id)
                    results.append(policy)
                    new_policies_count += 1
                    
                    # 调用回调
                    if policy_callback:
                        try:
                            policy_callback(policy)
                        except Exception as cb_error:
                            logger.warning(f"调用 policy_callback 失败: {cb_error}")
                    
                    if callback:
                        callback(f"POLICY_DATA:{policy.title}|{policy.pub_date}|{policy.link}||{policy.category}")
                
                if callback:
                    callback(f"第{page}页获取{len(page_policies)}条政策（新增{new_policies_count}条）")
                
                # 控制速度
                time.sleep(self.config.get("request_delay", 2))
                
                page += 1
                
            except Exception as e:
                if callback:
                    callback(f"第{page}页抓取失败: {e}")
                logger.error(f"第{page}页抓取异常: {e}", exc_info=True)
                break
        
        if callback:
            callback(f"爬取完成，共获取{len(results)}条政策")
        
        return results
    
    def _parse_json_results(self, data: Dict, callback: Optional[Callable] = None) -> List[Dict]:
        """解析JSON格式的搜索结果"""
        policies = []
        
        try:
            # 根据实际返回的JSON结构解析
            if 'results' in data:
                items = data['results']
            elif 'data' in data:
                items = data['data']
            elif isinstance(data, list):
                items = data
            else:
                items = []
            
            for item in items:
                # 解析日期
                raw_date = item.get('pubdate', item.get('publishdate', ''))
                pub_date = ''
                if raw_date:
                    parsed_date = self._parse_date(raw_date)
                    if parsed_date:
                        pub_date = parsed_date.strftime('%Y-%m-%d')
                    else:
                        pub_date = raw_date.strip()
                
                policy = {
                    'level': self.level,
                    'title': item.get('title', '') or '',
                    'pub_date': pub_date or '',
                    'doc_number': item.get('filenum', '') or '',
                    'source': item.get('url', '') or '',
                    'link': item.get('url', '') or '',
                    'url': item.get('url', '') or '',
                    'content': item.get('content', '').strip() or item.get('summary', '').strip() or '',
                    'category': item.get('category', '') or '',
                    'validity': item.get('status', '') or '',
                    'effective_date': item.get('effectivedate', '') or '',
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                policies.append(policy)
                    
        except Exception as e:
            if callback:
                callback(f"解析JSON结果失败: {e}")
            logger.error(f"解析JSON结果失败: {e}", exc_info=True)
        
        return policies
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串为datetime对象"""
        if not date_str:
            return None
        for fmt in ('%Y年%m月%d日', '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d'):
            try:
                return datetime.strptime(date_str, fmt)
            except Exception:
                continue
        return None
    
    def get_available_categories(self) -> List[str]:
        """获取可用的分类列表"""
        return list(self.categories.keys())
    
    def test_search_api(self, callback: Optional[Callable] = None) -> bool:
        """测试搜索API是否可用"""
        if callback:
            callback("测试搜索API...")
        
        try:
            result = self.api_client.search_policies(
                ['土地'], 1, None, None,
                data_source={
                    'base_url': self.base_url,
                    'search_api': self.search_api,
                    'channel_id': self.channel_id
                }
            )
            
            if result:
                if callback:
                    callback(f"API测试成功，返回类型: {result['type']}")
                return True
            else:
                if callback:
                    callback("API测试失败: 无响应")
                return False
                
        except Exception as e:
            if callback:
                callback(f"API测试异常: {e}")
            logger.error(f"API测试异常: {e}", exc_info=True)
            return False
