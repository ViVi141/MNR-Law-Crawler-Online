"""
本地缓存服务
"""

import os
import shutil
import time
import logging
from pathlib import Path
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """本地缓存服务"""

    def __init__(self):
        """初始化缓存服务"""
        self.cache_dir = Path(settings.cache_dir)
        self.cache_ttl = settings.cache_ttl_seconds
        self.max_size_gb = settings.cache_max_size_gb
        self.enabled = settings.cache_enabled

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"缓存服务初始化: {self.cache_dir}")

    def is_enabled(self) -> bool:
        """检查缓存是否启用"""
        return self.enabled

    def get_cache_path(self, policy_id: int, file_type: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / "policies" / str(policy_id) / f"{policy_id}.{file_type}"

    def get_policy_file(self, policy_id: int, file_type: str) -> Optional[Path]:
        """获取政策文件（优先从缓存读取）"""
        if not self.is_enabled():
            return None

        cache_path = self.get_cache_path(policy_id, file_type)

        if cache_path.exists() and self._is_cache_valid(cache_path):
            logger.debug(f"从缓存读取: {cache_path}")
            return cache_path

        return None

    def cache_policy_file(
        self, policy_id: int, file_type: str, source_path: str
    ) -> bool:
        """缓存政策文件"""
        if not self.is_enabled():
            return False

        try:
            cache_path = self.get_cache_path(policy_id, file_type)
            cache_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source_path, cache_path)
            logger.debug(f"文件已缓存: {cache_path}")
            return True
        except Exception as e:
            logger.error(f"缓存文件失败: {e}")
            return False

    def _is_cache_valid(self, file_path: Path) -> bool:
        """检查缓存是否有效（未过期）"""
        if not file_path.exists():
            return False

        file_age = time.time() - file_path.stat().st_mtime
        return file_age < self.cache_ttl

    def cleanup_cache(self) -> dict:
        """清理过期缓存"""
        if not self.is_enabled():
            return {"cleaned": 0, "freed_mb": 0}

        try:
            cleaned_count = 0
            freed_bytes = 0
            policies_dir = self.cache_dir / "policies"

            if not policies_dir.exists():
                return {"cleaned": 0, "freed_mb": 0}

            current_time = time.time()

            # 清理过期文件
            for policy_dir in policies_dir.iterdir():
                if not policy_dir.is_dir():
                    continue

                for cache_file in policy_dir.iterdir():
                    if not cache_file.is_file():
                        continue

                    file_age = current_time - cache_file.stat().st_mtime
                    if file_age > self.cache_ttl:
                        file_size = cache_file.stat().st_size
                        cache_file.unlink()
                        cleaned_count += 1
                        freed_bytes += file_size
                        logger.debug(f"删除过期缓存: {cache_file}")

            freed_mb = freed_bytes / (1024 * 1024)
            logger.info(
                f"缓存清理完成: 删除 {cleaned_count} 个文件, 释放 {freed_mb:.2f} MB"
            )

            return {"cleaned": cleaned_count, "freed_mb": round(freed_mb, 2)}
        except Exception as e:
            logger.error(f"清理缓存时发生错误: {e}")
            return {"cleaned": 0, "freed_mb": 0}

    def get_cache_size(self) -> dict:
        """获取缓存大小"""
        if not self.is_enabled():
            return {"size_mb": 0, "file_count": 0}

        try:
            total_size = 0
            file_count = 0
            policies_dir = self.cache_dir / "policies"

            if policies_dir.exists():
                for policy_dir in policies_dir.iterdir():
                    if not policy_dir.is_dir():
                        continue

                    for cache_file in policy_dir.iterdir():
                        if cache_file.is_file():
                            total_size += cache_file.stat().st_size
                            file_count += 1

            size_mb = total_size / (1024 * 1024)
            return {"size_mb": round(size_mb, 2), "file_count": file_count}
        except Exception as e:
            logger.error(f"获取缓存大小时发生错误: {e}")
            return {"size_mb": 0, "file_count": 0}

    def clear_cache(self) -> bool:
        """清空所有缓存"""
        if not self.is_enabled():
            return False

        try:
            policies_dir = self.cache_dir / "policies"
            if policies_dir.exists():
                shutil.rmtree(policies_dir)
                logger.info("缓存已清空")
            return True
        except Exception as e:
            logger.error(f"清空缓存时发生错误: {e}")
            return False

    def get_attachment_cache_path(
        self, policy_id: int, attachment_filename: str
    ) -> Path:
        """获取附件缓存文件路径"""
        return (
            self.cache_dir
            / "policies"
            / str(policy_id)
            / "attachments"
            / attachment_filename
        )

    def get_attachment_file(
        self, policy_id: int, attachment_filename: str
    ) -> Optional[Path]:
        """获取附件文件（优先从缓存读取）"""
        if not self.is_enabled():
            return None

        cache_path = self.get_attachment_cache_path(policy_id, attachment_filename)

        if cache_path.exists() and self._is_cache_valid(cache_path):
            logger.debug(f"从缓存读取附件: {cache_path}")
            return cache_path

        return None

    def cache_attachment_file(
        self, policy_id: int, attachment_filename: str, source_path: str
    ) -> bool:
        """缓存附件文件"""
        if not self.is_enabled():
            return False

        try:
            cache_path = self.get_attachment_cache_path(policy_id, attachment_filename)
            cache_path.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(source_path, cache_path)
            logger.debug(f"附件已缓存: {cache_path}")
            return True
        except Exception as e:
            logger.error(f"缓存附件失败: {e}")
            return False
