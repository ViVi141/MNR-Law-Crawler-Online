"""
文件清理服务 - 定期清理临时生成的文件
"""

import os
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict

logger = logging.getLogger(__name__)


class FileCleanupService:
    """文件清理服务"""

    def __init__(self):
        """初始化清理服务"""
        self.temp_file_registry: Dict[str, datetime] = {}  # 文件路径 -> 生成时间
        self.storage_service = None  # 延迟初始化

    def register_temp_file(self, file_path: str):
        """注册临时文件，记录生成时间"""
        if file_path and os.path.exists(file_path):
            self.temp_file_registry[file_path] = datetime.now(timezone.utc)
            logger.debug(f"注册临时文件: {file_path}")

    def cleanup_old_files(self, max_age_hours: int = 24):
        """清理超过指定时间的临时文件

        Args:
            max_age_hours: 文件最大保留时间（小时），默认24小时
        """
        if not self.storage_service:
            from .storage_service import StorageService

            self.storage_service = StorageService()

        current_time = datetime.now(timezone.utc)
        max_age = timedelta(hours=max_age_hours)
        cleaned_count = 0
        failed_count = 0

        # 清理注册表中的文件
        files_to_remove = []
        for file_path, created_time in list(self.temp_file_registry.items()):
            age = current_time - created_time
            if age > max_age:
                try:
                    if os.path.exists(file_path):
                        # 检查是否是临时目录中的文件
                        if "tmp" in file_path.lower() or "temp" in file_path.lower():
                            os.remove(file_path)
                            logger.debug(f"删除临时文件: {file_path}")
                            cleaned_count += 1
                        # 检查是否是临时目录本身
                        if os.path.isdir(file_path):
                            try:
                                os.rmdir(file_path)
                                logger.debug(f"删除临时目录: {file_path}")
                            except OSError:
                                pass  # 目录不为空，跳过
                    files_to_remove.append(file_path)
                except Exception as e:
                    logger.error(f"删除文件失败 {file_path}: {e}")
                    failed_count += 1

        # 从注册表中移除
        for file_path in files_to_remove:
            self.temp_file_registry.pop(file_path, None)

        # 清理storage_service中的临时文件（如果存在）
        try:
            if self.storage_service.storage_mode == "local":
                temp_dir = self.storage_service.local_dir / "temp_generated"
                if temp_dir.exists():
                    self._cleanup_directory(temp_dir, max_age, current_time)
        except Exception as e:
            logger.error(f"清理存储服务临时文件失败: {e}")

        logger.info(
            f"文件清理完成: 删除 {cleaned_count} 个文件, 失败 {failed_count} 个"
        )
        return cleaned_count, failed_count

    def _cleanup_directory(
        self, directory: Path, max_age: timedelta, current_time: datetime
    ):
        """清理目录中超过指定时间的文件"""
        if not directory.exists():
            return

        cleaned_count = 0
        for item in directory.iterdir():
            try:
                if item.is_file():
                    # 检查文件修改时间
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    age = current_time - mtime
                    if age > max_age:
                        item.unlink()
                        cleaned_count += 1
                        logger.debug(f"删除过期文件: {item}")
                elif item.is_dir():
                    # 递归清理子目录
                    self._cleanup_directory(item, max_age, current_time)
                    # 如果目录为空，尝试删除
                    try:
                        item.rmdir()
                    except OSError:
                        pass  # 目录不为空，保留
            except Exception as e:
                logger.warning(f"清理文件失败 {item}: {e}")

        return cleaned_count


# 单例实例
_cleanup_service: FileCleanupService = None


def get_cleanup_service() -> FileCleanupService:
    """获取清理服务单例"""
    global _cleanup_service
    if _cleanup_service is None:
        _cleanup_service = FileCleanupService()
    return _cleanup_service
