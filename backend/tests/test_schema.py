from fastapi.testclient import TestClient


def test_register_valid_schema(client: TestClient) -> None:
    response = client.post(
        "/schema",
        json={
            "name": "trade",
            "fields": [
                {"name": "tradeId", "type": "string", "required": True},
                {"name": "amount", "type": "number", "required": True},
                {"name": "status", "type": "string"},
            ],
        },
    )
    assert response.status_code == 201
    assert response.json() == {"name": "trade"}


def test_duplicate_schema_returns_409(client: TestClient) -> None:
    payload = {
        "name": "trade",
        "fields": [{"name": "tradeId", "type": "string", "required": True}],
    }
    assert client.post("/schema", json=payload).status_code == 201
    response = client.post("/schema", json=payload)
    assert response.status_code == 409
    assert response.json()["error"] == "SCHEMA_ALREADY_EXISTS"


def test_duplicate_field_names_rejected(client: TestClient) -> None:
    response = client.post(
        "/schema",
        json={
            "name": "trade",
            "fields": [
                {"name": "amount", "type": "number"},
                {"name": "amount", "type": "number"},
            ],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_SCHEMA"


def test_invalid_field_type_rejected(client: TestClient) -> None:
    response = client.post(
        "/schema",
        json={
            "name": "trade",
            "fields": [{"name": "createdAt", "type": "date"}],
        },
    )
    assert response.status_code == 422


def test_blank_schema_name_rejected(client: TestClient) -> None:
    response = client.post(
        "/schema",
        json={
            "name": "   ",
            "fields": [{"name": "id", "type": "string"}],
        },
    )
    assert response.status_code == 422


def test_blank_field_name_rejected(client: TestClient) -> None:
    response = client.post(
        "/schema",
        json={
            "name": "trade",
            "fields": [{"name": "  ", "type": "string"}],
        },
    )
    assert response.status_code == 422


def test_empty_fields_rejected(client: TestClient) -> None:
    response = client.post(
        "/schema",
        json={"name": "trade", "fields": []},
    )
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_SCHEMA"
