from fastapi import APIRouter, Request, status

from app.models.dashboard import (
    DashboardCreateRequest,
    DashboardDefinition,
    DashboardResponse,
    DashboardResult,
)

router = APIRouter()


@router.post(
    "/dashboard",
    status_code=status.HTTP_201_CREATED,
    response_model=DashboardResponse,
)
def register_dashboard(
    request: Request, body: DashboardCreateRequest
) -> DashboardResponse:
    container = request.app.state.container
    dashboard = DashboardDefinition(
        name=body.name,
        schema_name=body.schema_name,
        views=body.views,
    )
    result = container.dashboard_service.register(dashboard)
    return DashboardResponse(name=result.name)


@router.get("/dashboard/{name}", response_model=DashboardResult)
def get_dashboard(request: Request, name: str) -> DashboardResult:
    container = request.app.state.container
    return container.dashboard_service.generate(name)
