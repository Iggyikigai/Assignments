from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class IngestRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    schema_name: str = Field(alias="schema")
    rows: list[dict[str, Any]]


class IngestResponse(BaseModel):
    ingested: int


class ValidationErrorDetail(BaseModel):
    row: int
    field: Optional[str] = None
    code: str
    message: str


class ValidationErrorResponse(BaseModel):
    error: str = "VALIDATION_ERROR"
    details: list[ValidationErrorDetail]
