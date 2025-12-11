"""
Pytest配置和fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.config import settings


# 测试数据库URL（使用内存SQLite或测试PostgreSQL）
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args=(
            {"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {}
        ),
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    from app.models.user import User
    from app.services.auth_service import AuthService

    user = AuthService.create_default_user(
        db_session,
        username="testuser",
        password="testpass123",
        email="test@example.com",
    )
    return user


@pytest.fixture
def auth_token(client, test_user):
    """获取认证token"""
    response = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]
