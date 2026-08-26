from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IDMixin(BaseModel):
    id: UUID


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
