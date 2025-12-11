"""
认证服务（JWT）
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
import bcrypt
from sqlalchemy.orm import Session
from ..models.user import User
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            # 按字节截断密码（bcrypt限制72字节）
            password_bytes = plain_password.encode('utf-8')[:72]
            return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        # bcrypt限制密码长度最大72字节，需要按字节截断
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # 生成salt并哈希密码
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建JWT访问令牌"""
        to_encode = data.copy()
        
        # 确保sub是字符串（JWT要求）
        if "sub" in to_encode and not isinstance(to_encode["sub"], str):
            to_encode["sub"] = str(to_encode["sub"])
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """解码JWT令牌，验证有效期"""
        try:
            # 解码令牌并验证签名、过期时间等
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,  # 验证过期时间
                    "verify_iat": True,  # 验证签发时间
                    "require_exp": True,  # 要求必须有过期时间
                }
            )
            
            # 额外检查：确保过期时间在未来
            exp = payload.get("exp")
            if exp:
                from datetime import datetime
                expire_time = datetime.utcfromtimestamp(exp)
                if expire_time < datetime.utcnow():
                    logger.warning(f"令牌已过期: {expire_time}")
                    return None
            
            return payload
        except ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except (JWTError, JWTClaimsError) as e:
            logger.warning(f"无效的令牌: {e}")
            return None
        except Exception as e:
            logger.error(f"解码令牌异常: {e}")
            return None
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not user.is_active:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """从令牌获取当前用户"""
        payload = AuthService.decode_access_token(token)
        if payload is None:
            return None
        
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        
        # 转换为整数（因为sub在JWT中必须是字符串）
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            logger.warning(f"无效的用户ID格式: {user_id_str}")
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    
    @staticmethod
    def create_default_user(db: Session, username: str, password: str, email: str) -> User:
        """创建默认用户（带并发保护）"""
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return existing_user
        
        # 创建新用户
        try:
            hashed_password = AuthService.get_password_hash(password)
            user = User(
                username=username,
                password_hash=hashed_password,
                email=email,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"创建默认用户: {username}")
            return user
        except Exception as e:
            # 如果提交失败（可能是并发创建导致的重复键错误），回滚并重新查询
            db.rollback()
            error_msg = str(e).lower()
            if "duplicate key" in error_msg or "already exists" in error_msg:
                # 其他进程可能已创建，重新查询
                existing_user = db.query(User).filter(User.username == username).first()
                if existing_user:
                    logger.info(f"用户 {username} 已由其他进程创建")
                    return existing_user
            # 重新抛出其他错误
            raise
    
    @staticmethod
    def update_password(db: Session, user: User, old_password: str, new_password: str) -> bool:
        """更新用户密码"""
        # 验证旧密码
        if not AuthService.verify_password(old_password, user.password_hash):
            return False
        
        # 更新为新密码
        user.password_hash = AuthService.get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return True
    
    @staticmethod
    def reset_password(db: Session, user: User, new_password: str) -> bool:
        """重置用户密码（不需要旧密码，用于管理员操作）"""
        user.password_hash = AuthService.get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return True
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """生成随机密码"""
        import secrets
        import string
        
        # 使用大小写字母、数字和特殊字符
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

