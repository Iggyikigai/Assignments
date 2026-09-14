from app.errors import InvalidDashboardError
from app.models.dashboard import DashboardDefinition, SummaryView, TableView
from app.models.schema import AggregationType, FieldType, SchemaDefinition


def validate_dashboard(dashboard: DashboardDefinition, schema: SchemaDefinition) -> None:
    if not dashboard.views:
        raise InvalidDashboardError("Dashboard must have at least one view.")

    field_map = {f.name: f for f in schema.fields}

    for view in dashboard.views:
        if isinstance(view, SummaryView):
            _validate_summary_view(view, field_map)
        elif isinstance(view, TableView):
            _validate_table_view(view, field_map)
        else:
            raise InvalidDashboardError(f"Unsupported view type '{view.type}'.")


def _validate_summary_view(view: SummaryView, field_map: dict) -> None:
    if view.aggregation != AggregationType.SUM:
        raise InvalidDashboardError(
            f"Unsupported aggregation '{view.aggregation}'. Only 'sum' is supported."
        )

    field_def = field_map.get(view.field)
    if field_def is None:
        raise InvalidDashboardError(
            f"Summary field '{view.field}' does not exist in schema."
        )

    if field_def.type != FieldType.NUMBER:
        raise InvalidDashboardError(
            f"Aggregation 'sum' requires a numeric field; '{view.field}' is {field_def.type.value}."
        )


def _validate_table_view(view: TableView, field_map: dict) -> None:
    if not view.columns:
        raise InvalidDashboardError("Table view must specify at least one column.")

    for column in view.columns:
        if column not in field_map:
            raise InvalidDashboardError(
                f"Table column '{column}' does not exist in schema."
            )
