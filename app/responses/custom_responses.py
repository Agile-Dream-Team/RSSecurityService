from pydantic import BaseModel
from typing import Dict, Any


class SuccessModel(BaseModel):
    status: str = "success"
    data: Dict[str, Any]


class ErrorModel(BaseModel):
    status: str = "error"
    error: str
