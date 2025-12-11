"""
工具函数
"""

import re
from typing import Any


def sanitize_error_message(error: Exception) -> str:
    """清理错误消息，移除敏感信息

    Args:
        error: 异常对象

    Returns:
        清理后的错误消息
    """
    error_str = str(error)

    # 移除可能的敏感信息
    # 密码
    error_str = re.sub(
        r"password[=:]\s*\S+", "password=***", error_str, flags=re.IGNORECASE
    )
    # API密钥
    error_str = re.sub(
        r"api[_-]?key[=:]\s*\S+", "api_key=***", error_str, flags=re.IGNORECASE
    )
    # 数据库连接字符串中的密码
    error_str = re.sub(r"://[^:]+:([^@]+)@", r"://***:***@", error_str)
    # 令牌
    error_str = re.sub(r"token[=:]\s*\S+", "token=***", error_str, flags=re.IGNORECASE)
    # 密钥
    error_str = re.sub(
        r"secret[=:]\s*\S+", "secret=***", error_str, flags=re.IGNORECASE
    )

    return error_str
