from app.errors import InvalidSchemaError, SchemaAlreadyExistsError
from app.models.schema import SchemaDefinition
from app.repositories.schema_repository import SchemaRepository


class SchemaService:
    def __init__(self, schema_repository: SchemaRepository) -> None:
        self._schema_repository = schema_repository

    def register(self, schema: SchemaDefinition) -> SchemaDefinition:
        if self._schema_repository.exists(schema.name):
            raise SchemaAlreadyExistsError(schema.name)

        self._validate_schema(schema)
        self._schema_repository.save(schema)
        return schema

    def _validate_schema(self, schema: SchemaDefinition) -> None:
        if not schema.fields:
            raise InvalidSchemaError("Schema must have at least one field.")

        seen: set[str] = set()
        for field in schema.fields:
            if field.name in seen:
                raise InvalidSchemaError(
                    f"Duplicate field name '{field.name}' within schema."
                )
            seen.add(field.name)
