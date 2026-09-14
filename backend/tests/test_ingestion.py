from fastapi.testclient import TestClient

from tests.conftest import register_trade_schema


def test_valid_row_accepted(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [{"tradeId": "T001", "amount": 1000, "status": "OPEN"}],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"ingested": 1}


def test_missing_required_field_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={"schema": "trade", "rows": [{"tradeId": "T001"}]},
    )
    assert response.status_code == 422
    assert response.json()["error"] == "VALIDATION_ERROR"
    details = response.json()["details"]
    assert any(d["code"] == "REQUIRED_FIELD_MISSING" for d in details)


def test_required_field_null_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [{"tradeId": "T001", "amount": None}],
        },
    )
    assert response.status_code == 422
    details = response.json()["details"]
    assert any(d["code"] == "REQUIRED_FIELD_NULL" for d in details)


def test_optional_field_omitted_accepted(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={"schema": "trade", "rows": [{"tradeId": "T001", "amount": 100}]},
    )
    assert response.status_code == 200


def test_optional_field_null_accepted(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [{"tradeId": "T001", "amount": 100, "status": None}],
        },
    )
    assert response.status_code == 200


def test_wrong_string_type_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [{"tradeId": 123, "amount": 100}],
        },
    )
    assert response.status_code == 422
    details = response.json()["details"]
    assert any(d["field"] == "tradeId" and d["code"] == "INVALID_TYPE" for d in details)


def test_wrong_number_type_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [{"tradeId": "T001", "amount": "100"}],
        },
    )
    assert response.status_code == 422
    details = response.json()["details"]
    assert any(d["field"] == "amount" and d["code"] == "INVALID_TYPE" for d in details)


def test_boolean_not_accepted_as_number(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [{"tradeId": "T001", "amount": True}],
        },
    )
    assert response.status_code == 422
    details = response.json()["details"]
    assert any(d["field"] == "amount" and d["code"] == "INVALID_TYPE" for d in details)


def test_unknown_field_rejected(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [
                {"tradeId": "T001", "amount": 1000, "unexpected": "foo"},
            ],
        },
    )
    assert response.status_code == 422
    details = response.json()["details"]
    assert any(d["code"] == "UNKNOWN_FIELD" for d in details)


def test_schema_not_found_returns_404(client: TestClient) -> None:
    response = client.post(
        "/ingest",
        json={"schema": "missing", "rows": [{"tradeId": "T001", "amount": 1}]},
    )
    assert response.status_code == 404
    assert response.json()["error"] == "SCHEMA_NOT_FOUND"


def test_atomic_ingestion_no_partial_persist(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [
                {"tradeId": "T001", "amount": 100},
                {"tradeId": "T002", "amount": "bad"},
                {"tradeId": "T003", "amount": 300},
            ],
        },
    )
    assert response.status_code == 422
    details = response.json()["details"]
    assert any(d["row"] == 1 and d["field"] == "amount" for d in details)

    dashboard_response = _register_and_get_table(client)
    assert dashboard_response["views"][0]["rows"] == []


def test_atomic_ingestion_returns_all_errors(client: TestClient) -> None:
    register_trade_schema(client)
    response = client.post(
        "/ingest",
        json={
            "schema": "trade",
            "rows": [
                {"tradeId": "T001"},
                {"amount": 100},
            ],
        },
    )
    assert response.status_code == 422
    details = response.json()["details"]
    rows_with_errors = {d["row"] for d in details}
    assert 0 in rows_with_errors
    assert 1 in rows_with_errors


def _register_and_get_table(client: TestClient) -> dict:
    client.post(
        "/dashboard",
        json={
            "name": "trade-dashboard",
            "schema": "trade",
            "views": [{"type": "table", "columns": ["tradeId", "amount"]}],
        },
    )
    return client.get("/dashboard/trade-dashboard").json()
