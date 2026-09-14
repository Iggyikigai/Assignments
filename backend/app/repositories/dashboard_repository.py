from app.models.dashboard import DashboardDefinition


class DashboardRepository:
    def __init__(self) -> None:
        self._dashboards: dict[str, DashboardDefinition] = {}

    def save(self, dashboard: DashboardDefinition) -> None:
        self._dashboards[dashboard.name] = dashboard

    def get(self, name: str) -> DashboardDefinition | None:
        return self._dashboards.get(name)

    def exists(self, name: str) -> bool:
        return name in self._dashboards
