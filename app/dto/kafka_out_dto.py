from pydantic import BaseModel
from typing import Dict


class KafkaOutDTO(BaseModel):
    event: str
    data: Dict
    date_time: str
    client_id: str
    uuid: str
