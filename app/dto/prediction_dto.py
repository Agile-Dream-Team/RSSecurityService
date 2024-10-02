from pydantic import BaseModel


class PredictionDTO(BaseModel):
    camera_id: str
