from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"


class AggregationType(str, Enum):
    SUM = "sum"


class FieldDefinition(BaseModel):
    name: str
    type: FieldType
    required: bool = False
    aggregation: Optional[AggregationType] = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field name must not be blank.")
        return v


class SchemaDefinition(BaseModel):
    name: str
    fields: list[FieldDefinition]

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Schema name must not be blank.")
        return v


class SchemaCreateRequest(BaseModel):
    name: str
    fields: list[FieldDefinition]

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Schema name must not be blank.")
        return v


class SchemaResponse(BaseModel):
    name: str
