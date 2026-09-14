from fastapi import APIRouter, Request, status

from app.models.ingestion import IngestRequest, IngestResponse

router = APIRouter()


@router.post("/ingest", status_code=status.HTTP_200_OK, response_model=IngestResponse)
def ingest_data(request: Request, body: IngestRequest) -> IngestResponse:
    container = request.app.state.container
    count = container.ingestion_service.ingest(body.schema_name, body.rows)
    return IngestResponse(ingested=count)
