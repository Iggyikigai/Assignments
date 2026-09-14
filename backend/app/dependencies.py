from dataclasses import dataclass

from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.data_repository import DataRepository
from app.repositories.schema_repository import SchemaRepository
from app.services.dashboard_service import DashboardService
from app.services.ingestion_service import IngestionService
from app.services.schema_service import SchemaService


@dataclass
class AppContainer:
    schema_repository: SchemaRepository
    data_repository: DataRepository
    dashboard_repository: DashboardRepository
    schema_service: SchemaService
    ingestion_service: IngestionService
    dashboard_service: DashboardService


def create_container() -> AppContainer:
    schema_repository = SchemaRepository()
    data_repository = DataRepository()
    dashboard_repository = DashboardRepository()

    schema_service = SchemaService(schema_repository)
    ingestion_service = IngestionService(schema_repository, data_repository)
    dashboard_service = DashboardService(
        dashboard_repository, schema_repository, data_repository
    )

    return AppContainer(
        schema_repository=schema_repository,
        data_repository=data_repository,
        dashboard_repository=dashboard_repository,
        schema_service=schema_service,
        ingestion_service=ingestion_service,
        dashboard_service=dashboard_service,
    )
