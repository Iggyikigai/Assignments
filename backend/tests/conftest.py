import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


TRADE_SCHEMA = {
    "name": "trade",
    "fields": [
        {"name": "tradeId", "type": "string", "required": True},
        {"name": "amount", "type": "number", "required": True},
        {"name": "status", "type": "string"},
    ],
}


def register_trade_schema(client: TestClient) -> None:
    response = client.post("/schema", json=TRADE_SCHEMA)
    assert response.status_code == 201
