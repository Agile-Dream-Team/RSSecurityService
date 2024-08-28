# app/dto/webhook_in_dto.py
from typing import Optional, Union
from pydantic import BaseModel, model_validator, ValidationInfo
from app.api.v1.utils import TopicEvent, TopicActionRequest


class WebhookDataDTO(BaseModel):
    temperature_global: Optional[str] = None
    temperature_local: Optional[str] = None
    humidity_global: Optional[str] = None
    humidity_local: Optional[str] = None
    movement: Optional[bool] = None
    electrical_conductivity: Optional[str] = None
    air_flow: Optional[str] = None
    weight: Optional[str] = None


class WebhookDTO(BaseModel):
    event: Union[TopicEvent, TopicActionRequest]
    data: WebhookDataDTO
    date_time: str
    client_id: str
    uuid: str
