# Schema-Driven Dashboard Platform

---

A lightweight, generic, schema-driven dashboard backend. Business domains such as Trade or Customer are expressed as registered schemas and dashboard configurations rather than hard-coded backend modules.

## Running the project

```bash
cd backend
python -m venv .venv
```

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**macOS/Linux:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API documentation.

---

## Frontend

A lightweight React UI is available in `frontend/` for demoing the full workflow.

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The frontend calls the backend at `http://127.0.0.1:8000` by default.

To use a different backend URL, copy `.env.example` to `.env` and set:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the backend before using the UI. CORS is enabled for `http://localhost:5173` and `http://127.0.0.1:5173` during local development.

## Running tests

```bash
cd backend
pytest
```



## API examples



### Register a schema

```bash
curl -X POST http://127.0.0.1:8000/schema \
  -H "Content-Type: application/json" \
  -d '{
    "name": "trade",
    "fields": [
      {"name": "tradeId", "type": "string", "required": true},
      {"name": "amount", "type": "number", "required": true},
      {"name": "status", "type": "string"}
    ]
  }'
```



### Ingest data

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "trade",
    "rows": [
      {"tradeId": "T001", "amount": 1000, "status": "OPEN"},
      {"tradeId": "T002", "amount": 2500, "status": "CLOSED"}
    ]
  }'
```



### Register a dashboard

```bash
curl -X POST http://127.0.0.1:8000/dashboard \
  -H "Content-Type: application/json" \
  -d '{
    "name": "trade-dashboard",
    "schema": "trade",
    "views": [
      {"type": "summary", "field": "amount", "aggregation": "sum"},
      {"type": "table", "columns": ["tradeId", "amount", "status"]}
    ]
  }'
```



### Retrieve dashboard data

```bash
curl http://127.0.0.1:8000/dashboard/trade-dashboard
```

---

## Architecture

```text
Routes
  -> Services
    -> Validators / dashboard evaluation
      -> In-memory repositories
```

- **Routes** handle HTTP transport: request parsing, response serialization, and delegation to services.
- **Services** coordinate application behavior (schema registration, atomic ingestion, dashboard generation).
- **Validators** enforce domain rules (row validation, dashboard configuration validation).
- **Repositories** encapsulate in-memory storage.



## Workflows and backend services

Each UI workflow maps to a Python application service in `backend/app/services/`:


| Workflow           | Endpoint                | Service                                                                  | Purpose                                                                                                           |
| ------------------ | ----------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| Register Schema    | `POST /schema`          | `[SchemaService](backend/app/services/schema_service.py)`                | Validates schema definitions (unique name, unique field names, at least one field) and persists them immutably.   |
| Ingest Data        | `POST /ingest`          | `[IngestionService](backend/app/services/ingestion_service.py)`          | Resolves the target schema, validates every row in the batch, and appends rows only if the entire batch passes.   |
| Register Dashboard | `POST /dashboard`       | `[DashboardService.register](backend/app/services/dashboard_service.py)` | Validates dashboard configuration against the referenced schema (fields, view types, aggregations) and stores it. |
| View Dashboard     | `GET /dashboard/{name}` | `[DashboardService.generate](backend/app/services/dashboard_service.py)` | Loads a dashboard config, fetches ingested rows for its schema, and evaluates summary (`sum`) and table views.    |


---

## Design decisions

**Registration**


| Rule                      | Behavior                                     |
| ------------------------- | -------------------------------------------- |
| Schemas                   | Immutable after registration                 |
| Duplicate schema names    | `409 Conflict`                               |
| Dashboards                | Immutable after registration                 |
| Duplicate dashboard names | `409 Conflict`                               |
| Schema reference          | Dashboard config names the schema explicitly |
| Dashboard validation      | At registration, not deferred to GET         |


**Ingestion**


| Rule             | Behavior                                                         |
| ---------------- | ---------------------------------------------------------------- |
| Atomicity        | Entire batch succeeds or nothing is persisted                    |
| Validation order | All rows validated before any mutation                           |
| Error reporting  | All discovered errors returned together (zero-based row indices) |
| Unknown fields   | Rejected                                                         |
| Type coercion    | Not performed                                                    |
| Optional fields  | May be omitted or set to `null`                                  |
| Required fields  | May not be omitted or set to `null`                              |
| Supported types  | `string`, `number`, `boolean`                                    |


**Dashboards and storage**


| Rule                          | Behavior                                                       |
| ----------------------------- | -------------------------------------------------------------- |
| Aggregations                  | Only `sum` is implemented                                      |
| Schema `aggregation` metadata | Descriptive only; dashboard config is authoritative at runtime |
| Empty dataset                 | `200 OK` with a warning                                        |
| Empty `sum`                   | `null`, not zero                                               |
| Table views                   | Preserve ingestion order                                       |
| Storage                       | In memory only                                                 |




## Tradeoffs

**I implemented Atomic ingestion** because it provides a simpler client/server contract, where a failed validation request leaves application data unchanged. This avoids partial-success semantics, and sidesteps retry/deduplication questions. With in-memory storage, validating the full batch before appending is straightforward and safe.

**Partial ingestion** could be appropriate for large-scale bulk import systems, but would require additional API semantics (per-row status, idempotency keys, etc.) so it is outside this assignment's scope.

## Future extensions

Possible extensions not implemented here:

- Additional aggregations: `count`, `avg`, `min`, `max`
- Schema versioning and migrations
- Persistent repositories (database)
- Filtering, sorting, and pagination
- Additional primitive types (`date`, `datetime`, `array`, `object`)
- Richer dashboard view types

