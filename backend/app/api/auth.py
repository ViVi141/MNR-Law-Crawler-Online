"""
认证API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
import logging
from ..database import get_db
from ..services.auth_service import AuthService
from ..services.config_service import ConfigService
from ..models.user import User
from ..schemas.auth import (
    Token,
    UserLogin,
    UserResponse,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetResponse,
    ForgotPasswordRequest,
)
from ..middleware.auth import get_current_user
from ..config import settings

router = APIRouter(prefix="/auth", tags=["认证"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = AuthService.authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌（sub必须是字符串）
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    """刷新令牌"""
    access_token = AuthService.create_access_token(
        data={"sub": str(current_user.id), "username": current_user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/change-password")
def change_password(
    password_change: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改当前用户密码"""
    try:
        success = AuthService.update_password(
            db, current_user, password_change.old_password, password_change.new_password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="旧密码不正确"
            )
        return {"message": "密码修改成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"修改密码失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}",
        )


@router.post("/reset-password", response_model=PasswordResetResponse)
def reset_password(
    password_reset: PasswordResetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """重置当前用户密码（不需要旧密码）"""
    try:
        success = AuthService.reset_password(
            db, current_user, password_reset.new_password
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码重置失败"
            )
        return PasswordResetResponse(success=True, message="密码重置成功")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重置密码失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重置密码失败: {str(e)}",
        )


@router.post("/generate-password", response_model=PasswordResetResponse)
def generate_password(
    length: int = 12,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """生成随机密码并重置当前用户密码"""
    try:
        # 生成随机密码
        new_password = AuthService.generate_random_password(length)

        # 重置密码
        success = AuthService.reset_password(db, current_user, new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码生成失败"
            )

        logger.info(f"用户 {current_user.username} 生成了新密码")

        return PasswordResetResponse(
            success=True,
            message="新密码已生成并重置，请妥善保存",
            new_password=new_password,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成密码失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成密码失败: {str(e)}",
        )


@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """忘记密码：通过邮件发送随机密码（如果启用了SMTP）"""
    try:
        # 查找用户（通过用户名或邮箱）
        user = (
            db.query(User)
            .filter(
                (User.username == request.username) | (User.email == request.username)
            )
            .first()
        )

        if not user:
            # 为了安全，不告知用户是否存在
            return PasswordResetResponse(
                success=False,
                message="如果用户存在且已启用邮件服务，重置密码邮件已发送",
            )

        # 检查邮件服务是否启用且有收件人
        config_service = ConfigService()
        # 获取邮件配置（包含密码，用于发送邮件）
        email_config = config_service.get_email_config(db, include_password=True)

        if not email_config.get("enabled"):
            # 邮件未启用，返回提示信息
            return PasswordResetResponse(
                success=False,
                message="邮件服务未启用，无法通过邮件重置密码。请联系管理员使用后端脚本重置密码。",
            )

        # 检查是否有收件人地址
        to_addresses = email_config.get("to_addresses", [])
        if not to_addresses or len(to_addresses) == 0:
            return PasswordResetResponse(
                success=False,
                message="邮件服务未配置收件人地址，无法发送密码重置邮件。请先配置收件人地址。",
            )

        # 生成随机密码
        new_password = AuthService.generate_random_password(12)

        # 重置密码
        success = AuthService.reset_password(db, user, new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="密码重置失败"
            )

        # 发送邮件（使用数据库配置）
        smtp_host = email_config.get("smtp_host") or settings.email_smtp_host
        smtp_port = email_config.get("smtp_port") or settings.email_smtp_port
        smtp_user = email_config.get("smtp_user") or settings.email_smtp_user
        smtp_password = (
            email_config.get("smtp_password") or settings.email_smtp_password
        )
        from_address = email_config.get("from_address") or settings.email_from_address

        if all([smtp_host, smtp_user, smtp_password, from_address]):

            # 获取用户邮箱或使用配置中的收件人
            to_email = user.email
            if not to_email:
                to_emails = email_config.get("to_addresses", [])
                if to_emails:
                    to_email = to_emails[0]

            if to_email:
                # 创建邮件
                msg = MIMEMultipart("alternative")
                msg.attach(
                    MIMEText(
                        f"""
您的密码已重置

用户名: {user.username}
新密码: {new_password}

请尽快登录并修改密码。

此密码由系统自动生成，请妥善保管。登录后请立即修改为您自己的密码。

注意：如果这不是您本人操作，请立即联系管理员。
""",
                        "plain",
                        "utf-8",
                    )
                )
                msg.attach(
                    MIMEText(
                        f"""
<html>
<head><meta charset="utf-8"></head>
<body>
    <h2>密码重置通知</h2>
    <p>您的密码已重置，以下是您的新登录信息：</p>
    <ul>
        <li><strong>用户名:</strong> {user.username}</li>
        <li><strong>新密码:</strong> <code style="background-color: #f0f0f0; padding: 4px 8px; border-radius: 4px; font-size: 16px;">{new_password}</code></li>
    </ul>
    <p><strong>请尽快登录并修改密码。</strong></p>
    <p style="color: #666; font-size: 12px;">此密码由系统自动生成，请妥善保管。登录后请立即修改为您自己的密码。</p>
    <p style="color: #ff6600; font-size: 12px;"><strong>注意：</strong>如果这不是您本人操作，请立即联系管理员。</p>
</body>
</html>
""",
                        "html",
                        "utf-8",
                    )
                )
                msg["Subject"] = "[MNR Law Crawler] 密码重置通知"
                msg["From"] = from_address
                msg["To"] = to_email

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # 发送邮件
                    use_tls = smtp_port == 587
                    smtp = aiosmtplib.SMTP(
                        hostname=smtp_host, port=smtp_port, use_tls=use_tls
                    )

                    loop.run_until_complete(smtp.connect())
                    loop.run_until_complete(smtp.login(smtp_user, smtp_password))
                    loop.run_until_complete(smtp.send_message(msg))
                    # 某些SMTP服务器在发送完成后会立即关闭连接，导致quit()失败
                    # 如果邮件已成功发送，忽略quit()的错误
                    try:
                        loop.run_until_complete(smtp.quit())
                    except Exception:
                        # 邮件已成功发送，quit()失败不影响整体结果
                        pass

                    logger.info(f"密码重置邮件已发送到 {to_email}")
                    return PasswordResetResponse(
                        success=True, message=f"新密码已发送到 {to_email}，请查看邮件"
                    )
                except Exception as e:
                    logger.error(f"发送密码重置邮件失败: {e}", exc_info=True)
                    loop.close()
                    return PasswordResetResponse(
                        success=False, message=f"密码已重置，但发送邮件失败: {str(e)}"
                    )
                finally:
                    loop.close()

            return PasswordResetResponse(
                success=False, message="无法确定收件人邮箱地址"
            )

        # 邮件配置不完整
        return PasswordResetResponse(
            success=False,
            message="邮件服务配置不完整，无法发送密码重置邮件。请联系管理员使用后端脚本重置密码。",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"忘记密码处理失败: {e}", exc_info=True)
        # 为了安全，不暴露详细错误信息
        return PasswordResetResponse(
            success=False, message="处理请求失败，请联系管理员"
        )
