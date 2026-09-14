from app.models.schema import SchemaDefinition


class SchemaRepository:
    def __init__(self) -> None:
        self._schemas: dict[str, SchemaDefinition] = {}

    def save(self, schema: SchemaDefinition) -> None:
        self._schemas[schema.name] = schema

    def get(self, name: str) -> SchemaDefinition | None:
        return self._schemas.get(name)

    def exists(self, name: str) -> bool:
        return name in self._schemas
