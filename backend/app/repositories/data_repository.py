from typing import Any


class DataRepository:
    def __init__(self) -> None:
        self._rows: dict[str, list[dict[str, Any]]] = {}

    def append(self, schema_name: str, rows: list[dict[str, Any]]) -> None:
        if schema_name not in self._rows:
            self._rows[schema_name] = []
        self._rows[schema_name].extend(rows)

    def get_all(self, schema_name: str) -> list[dict[str, Any]]:
        return list(self._rows.get(schema_name, []))
