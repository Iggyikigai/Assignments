from typing import Any

from app.models.ingestion import ValidationErrorDetail
from app.models.schema import FieldDefinition, FieldType, SchemaDefinition


def validate_value(value: Any, field_type: FieldType) -> bool:
    if field_type == FieldType.STRING:
        return isinstance(value, str)

    if field_type == FieldType.NUMBER:
        # bool is a subclass of int in Python; exclude it explicitly.
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if field_type == FieldType.BOOLEAN:
        return isinstance(value, bool)

    return False


def validate_row(
    row: dict[str, Any], schema: SchemaDefinition, row_index: int
) -> list[ValidationErrorDetail]:
    errors: list[ValidationErrorDetail] = []
    field_map = {f.name: f for f in schema.fields}
    schema_field_names = set(field_map.keys())
    row_field_names = set(row.keys())

    for unknown in sorted(row_field_names - schema_field_names):
        errors.append(
            ValidationErrorDetail(
                row=row_index,
                field=unknown,
                code="UNKNOWN_FIELD",
                message=f"Unknown field '{unknown}'.",
            )
        )

    for field_def in schema.fields:
        if field_def.name not in row:
            if field_def.required:
                errors.append(
                    ValidationErrorDetail(
                        row=row_index,
                        field=field_def.name,
                        code="REQUIRED_FIELD_MISSING",
                        message=f"Required field '{field_def.name}' is missing.",
                    )
                )
            continue

        value = row[field_def.name]

        if value is None:
            if field_def.required:
                errors.append(
                    ValidationErrorDetail(
                        row=row_index,
                        field=field_def.name,
                        code="REQUIRED_FIELD_NULL",
                        message=f"Required field '{field_def.name}' may not be null.",
                    )
                )
            continue

        if not validate_value(value, field_def.type):
            errors.append(
                ValidationErrorDetail(
                    row=row_index,
                    field=field_def.name,
                    code="INVALID_TYPE",
                    message=f"Expected {field_def.type.value}.",
                )
            )

    return errors


def validate_batch(
    rows: list[dict[str, Any]], schema: SchemaDefinition
) -> list[ValidationErrorDetail]:
    all_errors: list[ValidationErrorDetail] = []
    for index, row in enumerate(rows):
        all_errors.extend(validate_row(row, schema, index))
    return all_errors
