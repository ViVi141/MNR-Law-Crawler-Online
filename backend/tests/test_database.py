"""
数据库测试
"""

import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.task import Task
from app.models.policy import Policy


@pytest.mark.unit
def test_database_connection(db_session: Session):
    """测试数据库连接"""
    from sqlalchemy import text

    result = db_session.execute(text("SELECT 1"))
    assert result.fetchone()[0] == 1


@pytest.mark.unit
def test_user_model(db_session: Session):
    """测试用户模型"""
    from app.models.user import User
    from app.services.auth_service import AuthService

    user = AuthService.create_default_user(
        db_session,
        username="test_user",
        password="test_password",
        email="test@example.com",
    )

    assert user.id is not None
    assert user.username == "test_user"
    assert user.email == "test@example.com"
    assert user.is_active is True


@pytest.mark.unit
def test_database_tables_exist(db_session: Session):
    """测试数据库表是否存在"""
    from sqlalchemy import inspect
    from app.database import engine

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    required_tables = ["users", "tasks", "policies", "backup_records"]
    for table in required_tables:
        assert table in tables, f"表 {table} 不存在"
