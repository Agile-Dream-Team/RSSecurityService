from typing import Optional
from pydantic import BaseModel


class CameraDTO(BaseModel):
    image_b64: str
    sensor_data_id: str
