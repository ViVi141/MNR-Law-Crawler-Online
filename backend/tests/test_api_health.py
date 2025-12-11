"""
API健康检查测试
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
def test_health_endpoint(client: TestClient):
    """测试健康检查端点"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data or "healthy" in str(data).lower()


@pytest.mark.api
def test_health_endpoint_via_proxy(client: TestClient):
    """测试通过代理访问健康检查端点"""
    # 模拟Nginx代理路径
    response = client.get("/api/health/")
    # 应该返回200或307（重定向）
    assert response.status_code in [200, 307]

