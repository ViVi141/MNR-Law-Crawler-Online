#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
密码重置脚本（最后手段）
用于在用户忘记密码且无法通过邮件重置时，直接重置密码

使用方法:
    python reset_password.py [username] [new_password]
    或
    python reset_password.py [username] --generate
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.services.auth_service import AuthService
from app.models.user import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_password(username: str, new_password: str = None):
    """重置用户密码"""
    db = SessionLocal()
    try:
        # 查找用户
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.error(f"用户不存在: {username}")
            return False

        # 生成随机密码或使用提供的密码
        if new_password is None:
            new_password = AuthService.generate_random_password(12)
            logger.info(f"生成随机密码: {new_password}")

        # 重置密码
        success = AuthService.reset_password(db, user, new_password)
        if success:
            logger.info(f"密码重置成功！")
            logger.info(f"用户名: {user.username}")
            logger.info(f"新密码: {new_password}")
            logger.info(f"请妥善保存新密码，并尽快登录修改")
            return True
        else:
            logger.error("密码重置失败")
            return False
    except Exception as e:
        logger.error(f"重置密码时发生错误: {e}", exc_info=True)
        return False
    finally:
        db.close()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("=" * 60)
        print("Policy Crawler Pro - 密码重置工具")
        print("=" * 60)
        print()
        print("使用方法:")
        print("  1. 生成随机密码:")
        print("     python reset_password.py <用户名> --generate")
        print()
        print("  2. 设置指定密码:")
        print("     python reset_password.py <用户名> <新密码>")
        print()
        print("示例:")
        print("     python reset_password.py admin --generate")
        print("     python reset_password.py admin MyNewPassword123")
        print()
        sys.exit(1)

    username = sys.argv[1]

    if len(sys.argv) == 3 and sys.argv[2] == "--generate":
        # 生成随机密码
        new_password = None
    elif len(sys.argv) == 3:
        # 使用指定的密码
        new_password = sys.argv[2]
        if len(new_password) < 6:
            logger.error("密码长度至少6位")
            sys.exit(1)
    else:
        logger.error("参数错误，请使用 --generate 或提供新密码")
        sys.exit(1)

    print("=" * 60)
    print("正在重置密码...")
    print("=" * 60)
    print()

    success = reset_password(username, new_password)

    if success:
        print()
        print("=" * 60)
        print("密码重置完成！")
        print("=" * 60)
        sys.exit(0)
    else:
        print()
        print("=" * 60)
        print("密码重置失败！")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
