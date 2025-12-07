"""
测试脚本：从两个数据源各获取一条数据样本，用于分析数据结构和优化显示
"""
import sys
import os
import json
from pprint import pprint

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Config
from app.core.api_client import APIClient
from app.core.mnr_spider import MNRSpider

def fetch_sample_from_source(source_config):
    """从指定数据源获取一条样本数据"""
    print(f"\n{'='*80}")
    print(f"数据源: {source_config['name']}")
    print(f"URL: {source_config['base_url']}")
    print(f"Channel ID: {source_config['channel_id']}")
    print(f"{'='*80}\n")
    
    # 创建配置
    config = Config()
    config.config = {
        "data_sources": [source_config],
        "base_url": source_config["base_url"],
        "search_api": source_config["search_api"],
        "ajax_api": source_config.get("ajax_api", source_config["search_api"]),
        "channel_id": source_config["channel_id"],
        "request_delay": 0.5,
        "timeout": 30,
        "page_size": 1,  # 只获取1条
        "max_pages": 1,
    }
    
    # 创建爬虫
    api_client = APIClient(config)
    spider = MNRSpider(config, api_client)
    
    # 爬取数据（只获取第一页的第一条）
    print("开始爬取...")
    policies = spider.crawl_policies(
        keywords=None,
        start_date=None,
        end_date=None,
        category=None,
        stop_callback=lambda: False
    )
    
    if policies:
        policy = policies[0]
        print(f"\n✓ 成功获取1条数据")
        
        # 转换为字典以便分析
        policy_dict = policy.to_dict()
        
        # 分析字段
        print(f"\n数据字段分析:")
        print(f"-" * 80)
        for key, value in policy_dict.items():
            if key == "content":
                content_preview = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                print(f"  {key:20s}: {type(value).__name__:15s} = {content_preview}")
            else:
                value_str = str(value)[:60] + "..." if len(str(value)) > 60 else str(value)
                print(f"  {key:20s}: {type(value).__name__:15s} = {value_str}")
        
        # 保存到文件
        output_file = f"sample_{source_config['name'].replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(policy_dict, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n✓ 数据已保存到: {output_file}")
        
        return policy_dict
    else:
        print("\n✗ 未能获取数据")
        return None


if __name__ == "__main__":
    print("="*80)
    print("数据源样本获取工具")
    print("="*80)
    
    # 两个数据源配置
    data_sources = [
        {
            "name": "政府信息公开平台",
            "base_url": "https://gi.mnr.gov.cn/",
            "search_api": "https://search.mnr.gov.cn/was5/web/search",
            "ajax_api": "https://search.mnr.gov.cn/was/ajaxdata_jsonp.jsp",
            "channel_id": "216640",
            "enabled": True
        },
        {
            "name": "政策法规库",
            "base_url": "https://f.mnr.gov.cn/",
            "search_api": "https://search.mnr.gov.cn/was5/web/search",
            "ajax_api": "https://search.mnr.gov.cn/was/ajaxdata_jsonp.jsp",
            "channel_id": "174757",
            "enabled": False
        }
    ]
    
    results = {}
    
    for source in data_sources:
        try:
            sample = fetch_sample_from_source(source)
            if sample:
                results[source['name']] = sample
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            import traceback
            traceback.print_exc()
    
    # 对比分析
    if len(results) == 2:
        print(f"\n\n{'='*80}")
        print("数据字段对比分析")
        print(f"{'='*80}\n")
        
        source1_name = list(results.keys())[0]
        source2_name = list(results.keys())[1]
        
        source1_fields = set(results[source1_name].keys())
        source2_fields = set(results[source2_name].keys())
        
        common_fields = source1_fields & source2_fields
        only_source1 = source1_fields - source2_fields
        only_source2 = source2_fields - source1_fields
        
        print(f"共同字段 ({len(common_fields)}个):")
        for field in sorted(common_fields):
            print(f"  - {field}")
        
        if only_source1:
            print(f"\n仅在 {source1_name} 中的字段 ({len(only_source1)}个):")
            for field in sorted(only_source1):
                print(f"  - {field}")
        
        if only_source2:
            print(f"\n仅在 {source2_name} 中的字段 ({len(only_source2)}个):")
            for field in sorted(only_source2):
                print(f"  - {field}")
        
        # 字段值对比
        print(f"\n\n字段值类型对比:")
        print(f"-" * 80)
        for field in sorted(common_fields):
            val1 = results[source1_name][field]
            val2 = results[source2_name][field]
            type1 = type(val1).__name__
            type2 = type(val2).__name__
            
            if type1 != type2:
                print(f"  {field:20s}: {source1_name:15s} = {type1:15s} | {source2_name:15s} = {type2}")
            else:
                print(f"  {field:20s}: {type1:15s} (一致)")
    
    print(f"\n{'='*80}")
    print("完成！")
    print(f"{'='*80}")

