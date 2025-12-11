"""
认证相关的Pydantic模型
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """令牌响应模型"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据模型"""

    user_id: Optional[int] = None


class UserLogin(BaseModel):
    """用户登录请求模型"""

    username: str
    password: str


class UserCreate(BaseModel):
    """创建用户请求模型"""

    username: str
    password: str
    email: EmailStr


class UserResponse(BaseModel):
    """用户响应模型"""

    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""

    old_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    """重置密码请求（管理员）"""

    new_password: str


class PasswordResetResponse(BaseModel):
    """重置密码响应"""

    success: bool
    message: str
    new_password: Optional[str] = None  # 仅在生成随机密码时返回


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求"""

    username: str  # 用户名或邮箱
