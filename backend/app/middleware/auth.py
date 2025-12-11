"""
认证中间件
"""

from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.auth_service import AuthService
from ..models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """获取当前用户（依赖注入）"""
    try:
        token = credentials.credentials

        user = AuthService.get_current_user(db, token)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="用户已被禁用"
            )
        # 确保用户对象的所有字段都已加载（避免延迟加载问题）
        _ = user.id, user.username, user.email, user.is_active
        return user
    except HTTPException:
        raise
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"获取当前用户失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="认证失败"
        )


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """获取当前用户（可选，用于公开API）"""
    if credentials is None:
        return None

    try:
        token = credentials.credentials
        user = AuthService.get_current_user(db, token)
        return user if user and user.is_active else None
    except Exception:
        return None
