"""
存储服务抽象（整合本地存储和S3）
"""

import shutil
import logging
from pathlib import Path
from typing import Optional, List
from .cache_service import CacheService
from ..config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """存储服务抽象"""
    
    def __init__(self):
        """初始化存储服务"""
        self.storage_mode = settings.storage_mode
        self.local_dir = Path(settings.storage_local_dir)
        from .s3_service import get_s3_service
        self.s3_service = get_s3_service()  # 使用单例
        self.cache_service = CacheService()
        
        # 创建本地存储目录
        if self.storage_mode == "local":
            self.local_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"存储服务初始化: mode={self.storage_mode}")
    
    def save_policy_file(
        self,
        policy_id: int,
        file_type: str,
        source_path: str,
        content_type: Optional[str] = None,
        task_id: Optional[int] = None
    ) -> dict:
        """保存政策文件（到本地和/或S3）"""
        result = {
            "local_path": None,
            "s3_key": None,
            "cache_path": None,
            "success": False
        }
        
        try:
            # 将文件类型转换为实际扩展名
            file_ext = "md" if file_type == "markdown" else file_type
            # 确定文件名
            file_name = f"{policy_id}.{file_ext}"
            
            # 文件路径包含task_id（如果提供），确保每个任务的文件独立
            if task_id:
                # 路径格式：policies/{task_id}/{policy_id}/{policy_id}.md
                file_dir = f"{task_id}/{policy_id}"
            else:
                # 兼容旧数据：policies/{policy_id}/{policy_id}.md
                file_dir = str(policy_id)
            
            # 1. 保存到本地存储（如果使用本地模式）
            if self.storage_mode == "local":
                local_path = self.local_dir / "policies" / file_dir / file_name
                local_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, local_path)
                result["local_path"] = str(local_path)
                logger.debug(f"文件保存到本地: {local_path}")
            
            # 2. 上传到S3（如果启用S3）
            if self.s3_service.is_enabled():
                s3_key = f"policies/{file_dir}/{file_name}"
                if self.s3_service.upload_file(source_path, s3_key, content_type):
                    result["s3_key"] = s3_key
                    logger.debug(f"文件上传到S3: {s3_key}")
            
            # 3. 缓存文件（如果启用缓存）
            if self.cache_service.is_enabled():
                cache_path = self.cache_service.cache_policy_file(policy_id, file_type, source_path)
                if cache_path:
                    result["cache_path"] = str(cache_path)
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"保存政策文件失败: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result
    
    def get_policy_file_path(
        self,
        policy_id: int,
        file_type: str,
        task_id: Optional[int] = None
    ) -> Optional[str]:
        """获取政策文件路径（优先缓存，然后本地，最后从S3下载）"""
        # 1. 检查缓存
        cache_path = self.cache_service.get_policy_file(policy_id, file_type)
        if cache_path:
            return str(cache_path)
        
        # 将文件类型转换为实际扩展名
        file_ext = "md" if file_type == "markdown" else file_type
        
        # 文件路径包含task_id（如果提供）
        if task_id:
            file_dir = f"{task_id}/{policy_id}"
        else:
            file_dir = str(policy_id)
        
        # 2. 检查本地存储
        if self.storage_mode == "local":
            local_path = self.local_dir / "policies" / file_dir / f"{policy_id}.{file_ext}"
            if local_path.exists():
                # 更新缓存
                if self.cache_service.is_enabled():
                    self.cache_service.cache_policy_file(policy_id, file_type, str(local_path))
                return str(local_path)
        
        # 3. 从S3下载（如果启用S3）
        if self.s3_service.is_enabled():
            s3_key = f"policies/{file_dir}/{policy_id}.{file_ext}"
            
            # 下载到缓存
            if self.cache_service.is_enabled():
                cache_path = self.cache_service.get_cache_path(policy_id, file_type)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                
                if self.s3_service.download_file(s3_key, str(cache_path)):
                    return str(cache_path)
            else:
                # 下载到临时目录
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}")
                temp_path = temp_file.name
                temp_file.close()
                
                if self.s3_service.download_file(s3_key, temp_path):
                    return temp_path
        
        return None
    
    def get_policy_file_url(
        self,
        policy_id: int,
        file_type: str,
        expiration: int = 3600,
        task_id: Optional[int] = None
    ) -> Optional[str]:
        """获取政策文件URL（用于直接访问）"""
        # 将文件类型转换为实际扩展名
        file_ext = "md" if file_type == "markdown" else file_type
        
        # 文件路径包含task_id（如果提供）
        if task_id:
            file_dir = f"{task_id}/{policy_id}"
        else:
            file_dir = str(policy_id)
        
        # 如果使用S3，生成预签名URL
        if self.s3_service.is_enabled():
            s3_key = f"policies/{file_dir}/{policy_id}.{file_ext}"
            return self.s3_service.get_presigned_url(s3_key, expiration)
        
        # 本地存储返回相对路径（需要前端处理）
        if self.storage_mode == "local":
            local_path = self.local_dir / "policies" / file_dir / f"{policy_id}.{file_ext}"
            if local_path.exists():
                # 返回API端点路径
                return f"/api/files/policies/{policy_id}/{file_type}"
        
        return None
    
    def delete_policy_file(self, policy_id: int, file_type: str, task_id: Optional[int] = None) -> bool:
        """删除政策文件"""
        success = True
        
        # 将文件类型转换为实际扩展名
        file_ext = "md" if file_type == "markdown" else file_type
        
        # 文件路径包含task_id（如果提供）
        if task_id:
            file_dir = f"{task_id}/{policy_id}"
        else:
            file_dir = str(policy_id)
        
        # 1. 删除本地文件
        if self.storage_mode == "local":
            local_path = self.local_dir / "policies" / file_dir / f"{policy_id}.{file_ext}"
            if local_path.exists():
                try:
                    local_path.unlink()
                except Exception as e:
                    logger.error(f"删除本地文件失败: {e}")
                    success = False
        
        # 2. 删除S3文件
        if self.s3_service.is_enabled():
            s3_key = f"policies/{file_dir}/{policy_id}.{file_ext}"
            if not self.s3_service.delete_file(s3_key):
                success = False
        
        # 3. 删除缓存
        if self.cache_service.is_enabled():
            cache_path = self.cache_service.get_cache_path(policy_id, file_type)
            if cache_path.exists():
                try:
                    cache_path.unlink()
                except Exception as e:
                    logger.error(f"删除缓存文件失败: {e}")
        
        return success
    
    def cleanup_policy_files(self, policy_id: int, task_id: Optional[int] = None) -> bool:
        """清理政策的所有文件（包括所有类型文件和附件）"""
        success = True
        
        # 1. 删除所有类型的文件
        file_types = ['markdown', 'docx']
        for file_type in file_types:
            if not self.delete_policy_file(policy_id, file_type, task_id=task_id):
                success = False
        
        # 2. 删除附件目录
        if self.storage_mode == "local":
            # 附件路径包含task_id（如果提供）
            if task_id:
                attachments_dir = self.local_dir / "policies" / str(task_id) / str(policy_id) / "attachments"
                policy_dir = self.local_dir / "policies" / str(task_id) / str(policy_id)
            else:
                attachments_dir = self.local_dir / "policies" / str(policy_id) / "attachments"
                policy_dir = self.local_dir / "policies" / str(policy_id)
            
            if attachments_dir.exists():
                try:
                    shutil.rmtree(attachments_dir)
                except Exception as e:
                    logger.error(f"删除附件目录失败: {e}")
                    success = False
            
            # 删除政策目录（如果为空）
            if policy_dir.exists():
                try:
                    # 检查目录是否为空
                    if not any(policy_dir.iterdir()):
                        policy_dir.rmdir()
                except Exception as e:
                    logger.warning(f"删除政策目录失败: {e}")
        
        # 3. 删除S3中的附件
        if self.s3_service.is_enabled():
            # S3路径包含task_id（如果提供）
            if task_id:
                prefix = f"policies/{task_id}/{policy_id}/attachments/"
            else:
                prefix = f"policies/{policy_id}/attachments/"
            s3_files = self.s3_service.list_files(prefix)
            for s3_key in s3_files:
                if not self.s3_service.delete_file(s3_key):
                    success = False
        
        return success
    
    def save_attachment(
        self,
        policy_id: int,
        attachment_filename: str,
        source_path: str,
        task_id: Optional[int] = None
    ) -> dict:
        """保存附件"""
        result = {
            "local_path": None,
            "s3_key": None,
            "success": False
        }
        
        try:
            # 附件路径包含task_id（如果提供），确保每个任务的附件独立
            if task_id:
                file_dir = f"{task_id}/{policy_id}"
            else:
                file_dir = str(policy_id)
            
            # 1. 保存到本地存储
            if self.storage_mode == "local":
                local_path = self.local_dir / "policies" / file_dir / "attachments" / attachment_filename
                local_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, local_path)
                result["local_path"] = str(local_path)
            
            # 2. 上传到S3
            if self.s3_service.is_enabled():
                s3_key = f"policies/{file_dir}/attachments/{attachment_filename}"
                if self.s3_service.upload_file(source_path, s3_key):
                    result["s3_key"] = s3_key
            
            result["success"] = True
            return result
            
        except Exception as e:
            logger.error(f"保存附件失败: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result
    
    def get_attachment_file_path(
        self,
        policy_id: int,
        attachment_filename: str,
        task_id: Optional[int] = None
    ) -> Optional[str]:
        """获取附件文件路径（优先缓存，然后本地，最后从S3下载）"""
        # 1. 检查缓存
        cache_path = self.cache_service.get_attachment_file(policy_id, attachment_filename)
        if cache_path:
            return str(cache_path)
        
        # 附件路径包含task_id（如果提供）
        if task_id:
            file_dir = f"{task_id}/{policy_id}"
        else:
            file_dir = str(policy_id)
        
        # 2. 检查本地存储
        if self.storage_mode == "local":
            local_path = self.local_dir / "policies" / file_dir / "attachments" / attachment_filename
            if local_path.exists():
                # 更新缓存
                if self.cache_service.is_enabled():
                    self.cache_service.cache_attachment_file(policy_id, attachment_filename, str(local_path))
                return str(local_path)
        
        # 3. 从S3下载（如果启用S3）
        if self.s3_service.is_enabled():
            s3_key = f"policies/{file_dir}/attachments/{attachment_filename}"
            
            # 下载到缓存
            if self.cache_service.is_enabled():
                cache_path = self.cache_service.get_attachment_cache_path(policy_id, attachment_filename)
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                
                if self.s3_service.download_file(s3_key, str(cache_path)):
                    return str(cache_path)
            else:
                # 下载到临时目录
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{attachment_filename}")
                temp_path = temp_file.name
                temp_file.close()
                
                if self.s3_service.download_file(s3_key, temp_path):
                    return temp_path
        
        return None
    
    def list_attachments(self, policy_id: int, task_id: Optional[int] = None) -> List[str]:
        """列出政策的所有附件"""
        attachments = []
        
        # 附件路径包含task_id（如果提供）
        if task_id:
            file_dir = f"{task_id}/{policy_id}"
        else:
            file_dir = str(policy_id)
        
        # 从本地存储列出
        if self.storage_mode == "local":
            attachments_dir = self.local_dir / "policies" / file_dir / "attachments"
            if attachments_dir.exists():
                attachments.extend([f.name for f in attachments_dir.iterdir() if f.is_file()])
        
        # 从S3列出
        if self.s3_service.is_enabled():
            prefix = f"policies/{file_dir}/attachments/"
            s3_files = self.s3_service.list_files(prefix)
            for s3_key in s3_files:
                filename = s3_key.split("/")[-1]
                if filename not in attachments:
                    attachments.append(filename)
        
        return attachments
    
    def cleanup_old_files(self, days: int = 30) -> dict:
        """清理旧文件"""
        result = {
            "cleaned_local": 0,
            "cleaned_s3": 0,
            "cleaned_cache": 0
        }
        
        # 清理本地文件
        if self.storage_mode == "local":
            cleaned_local = 0
            try:
                policies_dir = self.local_dir / "policies"
                if policies_dir.exists():
                    # 遍历所有政策目录
                    for policy_dir in policies_dir.iterdir():
                        if policy_dir.is_dir():
                            try:
                                _policy_id = int(policy_dir.name)  # 用于类型检查
                                # 检查政策是否已删除（需要查询数据库）
                                # 这里假设调用者已经删除了数据库记录
                                # 删除超过指定天数的文件
                                import time
                                current_time = time.time()
                                for file_path in policy_dir.rglob("*"):
                                    if file_path.is_file():
                                        file_mtime = file_path.stat().st_mtime
                                        days_old = (current_time - file_mtime) / (24 * 3600)
                                        if days_old > days:
                                            file_path.unlink()
                                            cleaned_local += 1
                                
                                # 如果目录为空，删除目录
                                if not any(policy_dir.iterdir()):
                                    policy_dir.rmdir()
                            except (ValueError, OSError) as e:
                                logger.warning(f"清理政策目录失败 {policy_dir}: {e}")
                                continue
                
                result["cleaned_local"] = cleaned_local
            except Exception as e:
                logger.error(f"清理本地文件失败: {e}", exc_info=True)
                result["cleaned_local"] = 0
        
        # 清理缓存
        if self.cache_service.is_enabled():
            cache_result = self.cache_service.cleanup_cache()
            result["cleaned_cache"] = cache_result.get("cleaned", 0)
        
        return result

