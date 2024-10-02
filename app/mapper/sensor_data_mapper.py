from pydantic import BaseModel
from typing import Dict


class SensorDataMapper(BaseModel):
    event_id: str
    data: Dict
    date_time: str
    bucket_id: str
    uuid: str

