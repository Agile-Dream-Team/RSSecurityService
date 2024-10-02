from typing import Optional, Union, Dict
from pydantic import BaseModel
from app.api.utils import TopicEvent, TopicActionRequest


class SensorDataDTO(BaseModel):
    temperature_global: Optional[str] = None
    temperature_local: Optional[str] = None
    humidity_global: Optional[str] = None
    humidity_local: Optional[str] = None
    movement: Optional[bool] = None
    electrical_conductivity: Optional[str] = None
    air_flow: Optional[str] = None
    weight: Optional[str] = None
    light_intensity: Optional[str] = None


class SaveDTO(BaseModel):
    event_id: str
    data: SensorDataDTO
    date_time: str
    bucket_id: str
    uuid: str

