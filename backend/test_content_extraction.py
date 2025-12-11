"""
测试内容提取和清理逻辑
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import Config
from app.core.api_client import APIClient


def test_content_extraction(url: str):
    """测试从指定URL提取内容"""
    print(f"测试URL: {url}")
    print("=" * 80)

    config = Config()
    config.config = {
        "data_sources": [],
        "base_url": "https://gi.mnr.gov.cn/",
        "search_api": "https://search.mnr.gov.cn/was5/web/search",
        "request_delay": 0.5,
        "timeout": 30,
    }

    api_client = APIClient(config)

    try:
        result = api_client.get_policy_detail(url)
        content = result.get("content", "")
        metadata = result.get("metadata", {})

        print(f"\n提取的内容长度: {len(content)} 字符")
        print(f"\n前500字符预览:")
        print("-" * 80)
        print(content[:500])
        print("-" * 80)

        print(f"\n元数据:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")

        # 检查是否有缺字问题
        print(f"\n\n内容检查:")
        print("-" * 80)

        # 检查是否有被拆分的年份
        import re

        broken_years = re.findall(r"([^\d])\n+(\d{4})\n+([^\d])", content)
        if broken_years:
            print(f"⚠ 发现被拆分的年份: {broken_years[:5]}")
        else:
            print("✓ 未发现被拆分的年份")

        # 检查是否有被拆分的词汇
        broken_words = re.findall(r"([^\n])\n+([^\n]{1,2})\n+([^\n])", content)
        if broken_words:
            print(f"⚠ 发现可能的被拆分词汇: {broken_words[:10]}")
        else:
            print("✓ 未发现被拆分的词汇")

        # 检查是否有不完整的句子
        incomplete_sentences = []
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if len(line) < 5 and i < len(lines) - 1:
                # 检查是否是断句
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if (
                    line
                    and next_line
                    and not line[-1] in "。！？；"
                    and len(next_line) > 20
                ):
                    incomplete_sentences.append((i, line, next_line[:30]))

        if incomplete_sentences:
            print(f"⚠ 发现可能的不完整句子:")
            for idx, line, next_line in incomplete_sentences[:5]:
                print(f"  行{idx}: '{line}' -> '{next_line}...'")
        else:
            print("✓ 未发现明显的不完整句子")

        return content

    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback

        traceback.print_exc()
        return None


if __name__ == "__main__":
    # 测试政府信息公开平台的一个政策详情页
    test_url = "http://gi.mnr.gov.cn/202112/t20211230_2716305.html"

    print("=" * 80)
    print("内容提取测试")
    print("=" * 80)

    content = test_content_extraction(test_url)

    if content:
        print(f"\n\n完整内容已提取（共 {len(content)} 字符）")
        print("=" * 80)
