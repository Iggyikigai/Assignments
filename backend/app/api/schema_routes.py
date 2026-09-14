from fastapi import APIRouter, Request, status

from app.models.schema import SchemaCreateRequest, SchemaDefinition, SchemaResponse

router = APIRouter()


@router.post("/schema", status_code=status.HTTP_201_CREATED, response_model=SchemaResponse)
def register_schema(request: Request, body: SchemaCreateRequest) -> SchemaResponse:
    container = request.app.state.container
    schema = SchemaDefinition(name=body.name, fields=body.fields)
    result = container.schema_service.register(schema)
    return SchemaResponse(name=result.name)
