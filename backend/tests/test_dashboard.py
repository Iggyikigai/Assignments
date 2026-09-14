from fastapi.testclient import TestClient

from tests.conftest import register_trade_schema

TRADE_DASHBOARD = {
    "name": "trade-dashboard",
    "schema": "trade",
    "views": [
        {"type": "summary", "field": "amount", "aggregation": "sum"},
        {"type": "table", "columns": ["tradeId", "amount", "status"]},
    ],
}


def test_register_valid_dashboard(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post("/dashboard", json=TRADE_DASHBOARD)
    assert response.status_code == 201
    assert response.json() == {"name": "trade-dashboard"}


def test_duplicate_dashboard_returns_409(client: TestClient) -> None:
    register_trade_schema(client)
    client.post("/dashboard", json=TRADE_DASHBOARD)
    response = client.post("/dashboard", json=TRADE_DASHBOARD)
    assert response.status_code == 409
    assert response.json()["error"] == "DASHBOARD_ALREADY_EXISTS"


def test_unknown_schema_rejected(client: TestClient) -> None:
    response = client.post("/dashboard", json=TRADE_DASHBOARD)
    assert response.status_code == 404
    assert response.json()["error"] == "SCHEMA_NOT_FOUND"


def test_unknown_summary_field_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/dashboard",
        json={
            "name": "bad-dashboard",
            "schema": "trade",
            "views": [
                {"type": "summary", "field": "missing", "aggregation": "sum"},
            ],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_DASHBOARD"


def test_unknown_table_column_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/dashboard",
        json={
            "name": "bad-dashboard",
            "schema": "trade",
            "views": [{"type": "table", "columns": ["tradeId", "missing"]}],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_DASHBOARD"


def test_unsupported_view_type_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/dashboard",
        json={
            "name": "bad-dashboard",
            "schema": "trade",
            "views": [{"type": "chart", "field": "amount"}],
        },
    )
    assert response.status_code == 422


def test_unsupported_aggregation_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/dashboard",
        json={
            "name": "bad-dashboard",
            "schema": "trade",
            "views": [{"type": "summary", "field": "amount", "aggregation": "avg"}],
        },
    )
    assert response.status_code == 422


def test_sum_on_string_field_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/dashboard",
        json={
            "name": "bad-dashboard",
            "schema": "trade",
            "views": [{"type": "summary", "field": "tradeId", "aggregation": "sum"}],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_DASHBOARD"


def test_summary_sum(client: TestClient) -> None:
    register_trade_schema(client)
    client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [
                {"tradeId": "T001", "amount": 100},
                {"tradeId": "T002", "amount": 200},
                {"tradeId": "T003", "amount": 300},
            ],
        },
    )
    client.post("/dashboard", json=TRADE_DASHBOARD)
    response = client.get("/dashboard/trade-dashboard")
    assert response.status_code == 200
    summary = response.json()["views"][0]
    assert summary["value"] == 600


def test_table_projection_omits_unconfigured_fields(client: TestClient) -> None:
    register_trade_schema(client)
    client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [{"tradeId": "T001", "amount": 1000, "status": "OPEN"}],
        },
    )
    client.post(
        "/dashboard",
        json={
            "name": "table-only",
            "schema": "trade",
            "views": [{"type": "table", "columns": ["tradeId", "amount"]}],
        },
    )
    response = client.get("/dashboard/table-only")
    row = response.json()["views"][0]["rows"][0]
    assert row == {"tradeId": "T001", "amount": 1000}
    assert "status" not in row


def test_table_preserves_ingestion_order(client: TestClient) -> None:
    register_trade_schema(client)
    client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [
                {"tradeId": "T001", "amount": 1},
                {"tradeId": "T002", "amount": 2},
                {"tradeId": "T003", "amount": 3},
            ],
        },
    )
    client.post(
        "/dashboard",
        json={
            "name": "order-dashboard",
            "schema": "trade",
            "views": [{"type": "table", "columns": ["tradeId"]}],
        },
    )
    response = client.get("/dashboard/order-dashboard")
    ids = [row["tradeId"] for row in response.json()["views"][0]["rows"]]
    assert ids == ["T001", "T002", "T003"]


def test_unknown_dashboard_returns_404(client: TestClient) -> None:
    response = client.get("/dashboard/missing")
    assert response.status_code == 404
    assert response.json()["error"] == "DASHBOARD_NOT_FOUND"


def test_no_data_dashboard(client: TestClient) -> None:
    register_trade_schema(client)
    client.post("/dashboard", json=TRADE_DASHBOARD)
    response = client.get("/dashboard/trade-dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "warning" in data
    assert "No data has been ingested" in data["warning"]
    assert data["views"][0]["value"] is None
    assert data["views"][1]["rows"] == []
    assert len(data["views"]) == 2
