from pydantic import BaseModel


class CameraMapper(BaseModel):
    image_b64: str
    sensor_data_id: str
