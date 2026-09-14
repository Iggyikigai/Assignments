from typing import Any

from app.errors import DataValidationFailedError, SchemaNotFoundError
from app.repositories.data_repository import DataRepository
from app.repositories.schema_repository import SchemaRepository
from app.validation.row_validator import validate_batch


class IngestionService:
    def __init__(
        self,
        schema_repository: SchemaRepository,
        data_repository: DataRepository,
    ) -> None:
        self._schema_repository = schema_repository
        self._data_repository = data_repository

    def ingest(self, schema_name: str, rows: list[dict[str, Any]]) -> int:
        schema = self._schema_repository.get(schema_name)
        if schema is None:
            raise SchemaNotFoundError(schema_name)

        errors = validate_batch(rows, schema)
        if errors:
            raise DataValidationFailedError(errors)

        self._data_repository.append(schema_name, rows)
        return len(rows)
