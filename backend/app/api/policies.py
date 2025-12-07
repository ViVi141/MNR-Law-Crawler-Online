"""
政策API路由
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..middleware.auth import get_current_user
from ..models.user import User
from ..schemas.policy import (
    PolicyListItem,
    PolicyListResponse,
    PolicySearchRequest,
    PolicyDetailResponse,
    AttachmentResponse
)
from ..services.policy_service import PolicyService
from ..services.search_service import SearchService

router = APIRouter(prefix="/policies", tags=["policies"])
policy_service = PolicyService()
search_service = SearchService()
logger = logging.getLogger(__name__)


@router.get("/", response_model=PolicyListResponse)
def get_policies(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    level: Optional[str] = Query(None, description="效力级别筛选"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    publisher: Optional[str] = Query(None, description="发布机构筛选"),
    source_name: Optional[str] = Query(None, description="数据源筛选"),
    task_id: Optional[int] = Query(None, description="任务ID筛选，只返回该任务爬取的政策"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取政策列表（带筛选和分页）"""
    try:
        # 过滤空字符串参数，并转换日期格式
        from datetime import date
        parsed_start_date = None
        parsed_end_date = None
        
        if start_date and start_date.strip():
            try:
                parsed_start_date = date.fromisoformat(start_date.strip())
            except ValueError:
                logger.warning(f"无效的开始日期格式: {start_date}")
        
        if end_date and end_date.strip():
            try:
                parsed_end_date = date.fromisoformat(end_date.strip())
            except ValueError:
                logger.warning(f"无效的结束日期格式: {end_date}")
        # 过滤空字符串
        filtered_category = category.strip() if category and category.strip() else None
        filtered_level = level.strip() if level and level.strip() else None
        filtered_keyword = keyword.strip() if keyword and keyword.strip() else None
        filtered_publisher = publisher.strip() if publisher and publisher.strip() else None
        filtered_source_name = source_name.strip() if source_name and source_name.strip() else None
        
        policies, total = policy_service.get_policies(
            db=db,
            skip=skip,
            limit=limit,
            category=filtered_category,
            level=filtered_level,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            keyword=filtered_keyword,
            publisher=filtered_publisher,
            source_name=filtered_source_name,
            task_id=task_id
        )
        
        # 安全序列化，处理可能的None值
        items = []
        for policy in policies:
            try:
                item_dict = PolicyListItem.model_validate(policy).model_dump()
                # 添加 publish_date 字段用于前端兼容（前端期望 publish_date 而不是 pub_date）
                if item_dict.get('pub_date'):
                    item_dict['publish_date'] = item_dict['pub_date'].isoformat() if hasattr(item_dict['pub_date'], 'isoformat') else str(item_dict['pub_date'])
                else:
                    item_dict['publish_date'] = None
                # 添加 law_type 字段（前端期望 law_type 而不是 level）
                item_dict['law_type'] = item_dict.get('level')
                items.append(item_dict)
            except Exception as e:
                logger.warning(f"序列化政策失败 (ID: {policy.id}): {e}")
                continue
        
        # 注意：items 现在是字典列表，但 PolicyListResponse 期望 PolicyListItem 列表
        # 由于 Pydantic 会自动转换，我们可以直接使用字典
        # 但为了类型安全，我们需要手动构造响应
        from typing import Any, Dict
        
        response_dict: Dict[str, Any] = {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
        # 使用 model_validate 来确保类型正确
        return PolicyListResponse.model_validate(response_dict)
    except Exception as e:
        logger.error(f"获取政策列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取政策列表失败: {str(e)}")


@router.post("/search", response_model=PolicyListResponse)
def search_policies(
    request: PolicySearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """搜索政策（全文搜索）"""
    # 如果有搜索关键词，使用全文搜索；否则使用普通筛选
    if request.keyword:
        policies, total = search_service.search(
            db=db,
            query=request.keyword,
            skip=request.skip,
            limit=request.limit,
            category=request.category,
            level=request.level,
            start_date=request.start_date.strftime("%Y-%m-%d") if request.start_date else None,
            end_date=request.end_date.strftime("%Y-%m-%d") if request.end_date else None
        )
    else:
        # 无关键词时使用普通筛选
        policies, total = policy_service.get_policies(
            db=db,
            skip=request.skip,
            limit=request.limit,
            category=request.category,
            level=request.level,
            start_date=request.start_date,
            end_date=request.end_date,
            keyword=None
        )
    
    items = [PolicyListItem.model_validate(policy) for policy in policies]
    
    return PolicyListResponse(
        items=items,
        total=total,
        skip=request.skip,
        limit=request.limit
    )


@router.get("/{policy_id}", response_model=PolicyDetailResponse)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取政策详情"""
    policy = policy_service.get_policy_by_id(db, policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="政策不存在")
    
    # 获取附件
    from ..models.attachment import Attachment
    attachments = db.query(Attachment).filter(Attachment.policy_id == policy_id).all()
    
    detail = PolicyDetailResponse.model_validate(policy)
    detail.attachments = [AttachmentResponse.model_validate(att) for att in attachments]
    
    return detail


@router.delete("/{policy_id}")
def delete_policy(
    policy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除政策"""
    success = policy_service.delete_policy(db, policy_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="政策不存在或删除失败")
    
    return {"message": "政策已删除", "id": policy_id}


@router.get("/meta/categories", response_model=List[str])
def get_categories(
    source_name: Optional[str] = Query(None, description="数据源名称，如果提供则只返回该数据源的分类"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类列表（可选按数据源筛选）"""
    return policy_service.get_categories(db, source_name=source_name)


@router.get("/meta/levels", response_model=List[str])
def get_levels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有效力级别列表"""
    return policy_service.get_levels(db)


@router.get("/meta/source-names", response_model=List[str])
def get_source_names(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有数据源名称列表"""
    return policy_service.get_source_names(db)


@router.post("/search/rebuild-index")
def rebuild_search_index(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """重建全文搜索索引"""
    result = search_service.build_search_index(db)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "索引重建失败"))
    
    return result


@router.get("/{policy_id}/file/{file_type}")
def get_policy_file(
    policy_id: int,
    file_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取政策文件（json/markdown/docx）"""
    policy = policy_service.get_policy_by_id(db, policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="政策不存在")
    
    if file_type not in ["json", "markdown", "docx"]:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    # 使用存储服务获取文件路径
    from ..services.storage_service import StorageService
    storage_service = StorageService()
    file_path = storage_service.get_policy_file_path(policy_id, file_type)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 返回文件
    from fastapi.responses import FileResponse
    import os
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    media_type_map = {
        "json": "application/json",
        "markdown": "text/markdown",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    
    return FileResponse(
        file_path,
        media_type=media_type_map.get(file_type, "application/octet-stream"),
        filename=f"policy_{policy_id}.{file_type}"
    )

