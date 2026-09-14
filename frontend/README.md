# Schema-Driven Dashboard — Optional Frontend

A thin React client for the schema-driven dashboard backend.

## Setup

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Backend URL

The API base URL defaults to `http://127.0.0.1:8000`. Override with:

```bash
# .env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Ensure the FastAPI backend is running before using the UI.

## Demo workflow

1. **Register Schema** — define fields and types
2. **Ingest Data** — paste rows as JSON
3. **Register Dashboard** — add summary and table views
4. **View Dashboard** — load and render results
