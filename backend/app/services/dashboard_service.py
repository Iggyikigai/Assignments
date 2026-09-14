from typing import Any

from app.errors import (
    DashboardAlreadyExistsError,
    DashboardNotFoundError,
    InvalidDashboardError,
    SchemaNotFoundError,
)
from app.models.dashboard import (
    DashboardDefinition,
    DashboardResult,
    SummaryView,
    SummaryViewResult,
    TableView,
    TableViewResult,
    ViewDefinition,
)
from app.models.schema import AggregationType
from app.repositories.dashboard_repository import DashboardRepository
from app.repositories.data_repository import DataRepository
from app.repositories.schema_repository import SchemaRepository
from app.validation.dashboard_validator import validate_dashboard


class DashboardService:
    def __init__(
        self,
        dashboard_repository: DashboardRepository,
        schema_repository: SchemaRepository,
        data_repository: DataRepository,
    ) -> None:
        self._dashboard_repository = dashboard_repository
        self._schema_repository = schema_repository
        self._data_repository = data_repository

    def register(self, dashboard: DashboardDefinition) -> DashboardDefinition:
        if self._dashboard_repository.exists(dashboard.name):
            raise DashboardAlreadyExistsError(dashboard.name)

        schema = self._schema_repository.get(dashboard.schema_name)
        if schema is None:
            raise SchemaNotFoundError(dashboard.schema_name)

        validate_dashboard(dashboard, schema)
        self._dashboard_repository.save(dashboard)
        return dashboard

    def generate(self, name: str) -> DashboardResult:
        dashboard = self._dashboard_repository.get(name)
        if dashboard is None:
            raise DashboardNotFoundError(name)

        schema = self._schema_repository.get(dashboard.schema_name)
        if schema is None:
            raise SchemaNotFoundError(dashboard.schema_name)

        rows = self._data_repository.get_all(dashboard.schema_name)
        warning = None
        if not rows:
            warning = f"No data has been ingested for schema '{dashboard.schema_name}'."

        view_results = [
            self._generate_view(view, rows) for view in dashboard.views
        ]

        return DashboardResult(
            name=dashboard.name,
            warning=warning,
            views=view_results,
        )

    def _generate_view(
        self, view: ViewDefinition, rows: list[dict[str, Any]]
    ) -> SummaryViewResult | TableViewResult:
        if isinstance(view, SummaryView):
            return self._generate_summary(view, rows)
        if isinstance(view, TableView):
            return self._generate_table(view, rows)
        raise InvalidDashboardError(f"Unsupported view type '{view.type}'.")

    def _generate_summary(
        self, view: SummaryView, rows: list[dict[str, Any]]
    ) -> SummaryViewResult:
        value: float | None = None
        if rows:
            value = sum(row[view.field] for row in rows)

        return SummaryViewResult(
            type="summary",
            field=view.field,
            aggregation=AggregationType.SUM,
            value=value,
        )

    def _generate_table(
        self, view: TableView, rows: list[dict[str, Any]]
    ) -> TableViewResult:
        projected = [
            {col: row.get(col) for col in view.columns} for row in rows
        ]
        return TableViewResult(
            type="table",
            columns=view.columns,
            rows=projected,
        )
