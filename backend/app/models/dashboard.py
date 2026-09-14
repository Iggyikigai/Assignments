from typing import Annotated, Any, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.schema import AggregationType


class SummaryView(BaseModel):
    type: Literal["summary"] = "summary"
    field: str
    aggregation: AggregationType


class TableView(BaseModel):
    type: Literal["table"] = "table"
    columns: list[str]


ViewDefinition = Annotated[
    Union[SummaryView, TableView],
    Field(discriminator="type"),
]


class DashboardDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    schema_name: str = Field(alias="schema")
    views: list[ViewDefinition]

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Dashboard name must not be blank.")
        return v


class DashboardCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    schema_name: str = Field(alias="schema")
    views: list[ViewDefinition]

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Dashboard name must not be blank.")
        return v


class DashboardResponse(BaseModel):
    name: str


class SummaryViewResult(BaseModel):
    type: Literal["summary"] = "summary"
    field: str
    aggregation: AggregationType
    value: Optional[float] = None


class TableViewResult(BaseModel):
    type: Literal["table"] = "table"
    columns: list[str]
    rows: list[dict[str, Any]]


ViewResult = Union[SummaryViewResult, TableViewResult]


class DashboardResult(BaseModel):
    name: str
    warning: Optional[str] = None
    views: list[ViewResult]
