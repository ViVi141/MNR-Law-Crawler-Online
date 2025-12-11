"""
认证API测试
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_login_success(client: TestClient, test_user):
    """测试成功登录"""
    response = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.api
def test_login_failure_wrong_password(client: TestClient, test_user):
    """测试错误密码登录失败"""
    response = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401


@pytest.mark.api
def test_login_failure_nonexistent_user(client: TestClient):
    """测试不存在的用户登录失败"""
    response = client.post(
        "/api/auth/login", json={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401


@pytest.mark.api
def test_get_current_user(client: TestClient, auth_token):
    """测试获取当前用户信息"""
    response = client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert data["username"] == "testuser"
