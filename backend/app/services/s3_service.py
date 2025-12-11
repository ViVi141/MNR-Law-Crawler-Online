"""
S3对象存储服务
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, List, BinaryIO
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class S3Service:
    """S3对象存储服务"""

    def __init__(self):
        """初始化S3客户端"""
        if not settings.s3_enabled:
            self.client = None
            self.bucket_name = None
            return

        try:
            self.bucket_name = settings.s3_bucket_name
            self.region = settings.s3_region

            # 初始化S3客户端
            self.client = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint_url,
                aws_access_key_id=settings.s3_access_key_id,
                aws_secret_access_key=settings.s3_secret_access_key,
                region_name=self.region,
            )
            logger.info(f"S3服务初始化成功: {self.bucket_name}")
        except Exception as e:
            logger.error(f"S3服务初始化失败: {e}")
            self.client = None
            self.bucket_name = None

    def is_enabled(self) -> bool:
        """检查S3是否启用"""
        return self.client is not None and self.bucket_name is not None

    def upload_file(
        self,
        file_path: str,
        s3_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> bool:
        """上传文件到S3"""
        if not self.is_enabled():
            logger.warning("S3服务未启用")
            return False

        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.upload_file(
                file_path, self.bucket_name, s3_key, ExtraArgs=extra_args
            )
            logger.info(f"文件上传成功: {s3_key}")
            return True
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            return False
        except ClientError as e:
            logger.error(f"S3上传失败: {e}")
            return False
        except Exception as e:
            logger.error(f"上传文件时发生错误: {e}")
            return False

    def upload_fileobj(
        self, file_obj: BinaryIO, s3_key: str, content_type: Optional[str] = None
    ) -> bool:
        """上传文件对象到S3"""
        if not self.is_enabled():
            logger.warning("S3服务未启用")
            return False

        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            self.client.upload_fileobj(
                file_obj, self.bucket_name, s3_key, ExtraArgs=extra_args
            )
            logger.info(f"文件对象上传成功: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"S3上传失败: {e}")
            return False
        except Exception as e:
            logger.error(f"上传文件对象时发生错误: {e}")
            return False

    def download_file(self, s3_key: str, local_path: str) -> bool:
        """从S3下载文件"""
        if not self.is_enabled():
            logger.warning("S3服务未启用")
            return False

        try:
            import os

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            self.client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"文件下载成功: {s3_key} -> {local_path}")
            return True
        except ClientError as e:
            logger.error(f"S3下载失败: {e}")
            return False
        except Exception as e:
            logger.error(f"下载文件时发生错误: {e}")
            return False

    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:
        """生成预签名URL（用于直接下载）"""
        if not self.is_enabled():
            logger.warning("S3服务未启用")
            return None

        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"生成预签名URL失败: {e}")
            return None
        except Exception as e:
            logger.error(f"生成预签名URL时发生错误: {e}")
            return None

    def delete_file(self, s3_key: str) -> bool:
        """删除S3文件"""
        if not self.is_enabled():
            logger.warning("S3服务未启用")
            return False

        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"文件删除成功: {s3_key}")
            return True
        except ClientError as e:
            logger.error(f"S3删除失败: {e}")
            return False
        except Exception as e:
            logger.error(f"删除文件时发生错误: {e}")
            return False

    def list_files(self, prefix: str) -> List[str]:
        """列出S3文件"""
        if not self.is_enabled():
            logger.warning("S3服务未启用")
            return []

        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError as e:
            logger.error(f"S3列表失败: {e}")
            return []
        except Exception as e:
            logger.error(f"列出文件时发生错误: {e}")
            return []

    def file_exists(self, s3_key: str) -> bool:
        """检查文件是否存在"""
        if not self.is_enabled():
            return False

        try:
            self.client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError:
            return False
        except Exception as e:
            logger.error(f"检查文件存在性时发生错误: {e}")
            return False

    def get_file_size(self, s3_key: str) -> Optional[int]:
        """获取文件大小"""
        if not self.is_enabled():
            return None

        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return response.get("ContentLength")
        except ClientError:
            return None
        except Exception as e:
            logger.error(f"获取文件大小时发生错误: {e}")
            return None

    def test_connection(self) -> dict:
        """测试S3连接"""
        if not self.is_enabled():
            return {"success": False, "message": "S3服务未启用", "details": {}}

        try:
            # 测试列出bucket
            self.client.head_bucket(Bucket=self.bucket_name)

            # 测试上传和删除
            test_key = "test_connection_file.txt"
            test_content = b"test"

            # 上传测试文件
            self.client.put_object(
                Bucket=self.bucket_name, Key=test_key, Body=test_content
            )

            # 检查文件是否存在
            exists = self.file_exists(test_key)

            # 删除测试文件
            if exists:
                self.delete_file(test_key)

            return {
                "success": True,
                "message": "S3连接测试成功",
                "details": {
                    "bucket_exists": True,
                    "can_read": True,
                    "can_write": True,
                    "test_file_uploaded": True,
                    "test_file_deleted": True,
                },
            }
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            return {
                "success": False,
                "message": f"S3连接测试失败: {str(e)}",
                "error": error_code,
                "details": {"bucket_exists": False, "error_code": error_code},
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"S3连接测试失败: {str(e)}",
                "details": {"bucket_exists": False, "error": str(e)},
            }

    def reinitialize(self):
        """重新初始化S3客户端（用于配置更新后）"""
        # 重新读取配置
        from ..config import settings

        if not settings.s3_enabled:
            self.client = None
            self.bucket_name = None
            logger.info("S3服务已禁用")
            return

        try:
            self.bucket_name = settings.s3_bucket_name
            self.region = settings.s3_region

            # 重新初始化S3客户端
            self.client = boto3.client(
                "s3",
                endpoint_url=settings.s3_endpoint_url,
                aws_access_key_id=settings.s3_access_key_id,
                aws_secret_access_key=settings.s3_secret_access_key,
                region_name=self.region,
            )
            logger.info(f"S3服务重新初始化成功: {self.bucket_name}")
        except Exception as e:
            logger.error(f"S3服务重新初始化失败: {e}")
            self.client = None
            self.bucket_name = None


# 全局S3服务实例
_s3_service: Optional[S3Service] = None


def get_s3_service() -> S3Service:
    """获取S3服务单例"""
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service


def reinitialize_s3_service():
    """重新初始化S3服务（用于配置更新后）"""
    global _s3_service
    if _s3_service is not None:
        _s3_service.reinitialize()
    else:
        _s3_service = S3Service()
