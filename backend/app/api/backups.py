"""
备份管理API路由
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..services.backup_service import BackupService
from ..schemas.backup import (
    BackupRecordResponse,
    BackupRecordListResponse,
    BackupCreateRequest,
    BackupRestoreRequest,
    BackupRestoreResponse,
    BackupCleanupResponse
)

router = APIRouter(prefix="/backups", tags=["backups"])
backup_service = BackupService()
logger = logging.getLogger(__name__)


@router.post("/", response_model=BackupRecordResponse, status_code=status.HTTP_201_CREATED)
def create_backup(
    request: BackupCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建数据库备份"""
    try:
        backup_record = backup_service.create_backup(
            db=db,
            backup_type=request.backup_type,
            backup_name=request.backup_name
        )
        return BackupRecordResponse.model_validate(backup_record)
    except Exception as e:
        logger.error(f"创建备份失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建备份失败: {str(e)}"
        )


@router.get("/", response_model=BackupRecordListResponse)
def get_backups(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    backup_type: Optional[str] = Query(None, description="备份类型筛选"),
    status_filter: Optional[str] = Query(None, alias="status", description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取备份记录列表"""
    try:
        records, total = backup_service.get_backup_records(
            db=db,
            skip=skip,
            limit=limit,
            backup_type=backup_type,
            status=status_filter
        )
        return BackupRecordListResponse(
            items=[BackupRecordResponse.model_validate(record) for record in records],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"获取备份列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取备份列表失败: {str(e)}"
        )


@router.get("/{backup_id}", response_model=BackupRecordResponse)
def get_backup(
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取备份记录详情"""
    try:
        backup_record = backup_service.get_backup_record(db, backup_id)
        if not backup_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="备份记录不存在"
            )
        return BackupRecordResponse.model_validate(backup_record)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取备份详情失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取备份详情失败: {str(e)}"
        )


@router.post("/{backup_id}/restore", response_model=BackupRestoreResponse)
def restore_backup(
    backup_id: str,
    request: BackupRestoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """恢复数据库备份
    
    ⚠️ 警告：此操作将覆盖目标数据库的所有数据！
    """
    try:
        result = backup_service.restore_backup(
            backup_id=backup_id,
            target_database=request.target_database
        )
        return BackupRestoreResponse(**result)
    except Exception as e:
        logger.error(f"恢复备份失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"恢复备份失败: {str(e)}"
        )


@router.delete("/{backup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_backup(
    backup_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除备份记录和文件"""
    try:
        success = backup_service.delete_backup(db, backup_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="备份记录不存在或无法删除"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除备份失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除备份失败: {str(e)}"
        )


@router.post("/cleanup", response_model=BackupCleanupResponse)
def cleanup_backups(
    keep_count: int = Query(10, ge=1, le=100, description="保留的备份数量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """清理旧备份，保留最新的N个"""
    try:
        result = backup_service.cleanup_old_backups(db, keep_count=keep_count)
        return BackupCleanupResponse(**result)
    except Exception as e:
        logger.error(f"清理备份失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清理备份失败: {str(e)}"
        )

