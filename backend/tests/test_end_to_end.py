from fastapi.testclient import TestClient


def test_full_trade_flow(client: TestClient) -> None:
    schema_response = client.post(
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
    assert schema_response.status_code == 201

    ingest_response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [
                {"tradeId": "T001", "amount": 1000, "status": "OPEN"},
                {"tradeId": "T002", "amount": 2500, "status": "CLOSED"},
            ],
        },
    )
    assert ingest_response.status_code == 200

    dashboard_response = client.post(
        "/dashboard",
        json={
            "name": "trade-dashboard",
            "schema": "trade",
            "views": [
                {"type": "summary", "field": "amount", "aggregation": "sum"},
                {"type": "table", "columns": ["tradeId", "amount", "status"]},
            ],
        },
    )
    assert dashboard_response.status_code == 201

    result = client.get("/dashboard/trade-dashboard")
    assert result.status_code == 200
    data = result.json()

    assert data["name"] == "trade-dashboard"
    assert data["views"][0]["value"] == 3500
    assert len(data["views"][1]["rows"]) == 2
    assert data["views"][1]["rows"][0]["tradeId"] == "T001"
    assert data["views"][1]["rows"][1]["tradeId"] == "T002"
