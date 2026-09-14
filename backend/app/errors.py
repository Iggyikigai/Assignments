from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models.ingestion import ValidationErrorDetail, ValidationErrorResponse


class DomainError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class SchemaAlreadyExistsError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(
            "SCHEMA_ALREADY_EXISTS",
            f"Schema '{name}' already exists.",
            status_code=409,
        )


class SchemaNotFoundError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(
            "SCHEMA_NOT_FOUND",
            f"Schema '{name}' not found.",
            status_code=404,
        )


class InvalidSchemaError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__("INVALID_SCHEMA", message, status_code=422)


class DashboardAlreadyExistsError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(
            "DASHBOARD_ALREADY_EXISTS",
            f"Dashboard '{name}' already exists.",
            status_code=409,
        )


class DashboardNotFoundError(DomainError):
    def __init__(self, name: str) -> None:
        super().__init__(
            "DASHBOARD_NOT_FOUND",
            f"Dashboard '{name}' not found.",
            status_code=404,
        )


class InvalidDashboardError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__("INVALID_DASHBOARD", message, status_code=422)


class DataValidationFailedError(DomainError):
    def __init__(self, details: list[ValidationErrorDetail]) -> None:
        self.details = details
        super().__init__(
            "DATA_VALIDATION_FAILED",
            "One or more rows failed validation.",
            status_code=422,
        )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        if isinstance(exc, DataValidationFailedError):
            return JSONResponse(
                status_code=exc.status_code,
                content=ValidationErrorResponse(
                    error="VALIDATION_ERROR",
                    details=exc.details,
                ).model_dump(),
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.code, "message": exc.message},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "INVALID_REQUEST",
                "details": jsonable_encoder(exc.errors()),
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(
        _request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "INVALID_REQUEST",
                "details": jsonable_encoder(exc.errors()),
            },
        )
