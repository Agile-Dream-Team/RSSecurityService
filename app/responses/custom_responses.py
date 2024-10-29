# app/responses/custom_responses.py
from pydantic import BaseModel
from typing import Any, Optional


class ErrorModel(BaseModel):
    detail: str


class SuccessModel(BaseModel):
    message: str
    data: Optional[Any] = None
