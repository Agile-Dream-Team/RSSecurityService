import logging

from fastapi import APIRouter, HTTPException, Depends

from app.dto.camera_dto import CameraDTO
from app.dto.prediction_dto import PredictionDTO
from app.responses.custom_responses import SuccessModel, ErrorModel
from app.services.prediction_service import PredictionService
from RSKafkaWrapper.client import KafkaClient

prediction_router = APIRouter()

response_models = {
    400: {"model": ErrorModel},
    401: {"model": ErrorModel},
    500: {"model": ErrorModel}
}


def get_kafka_client() -> KafkaClient:
    return KafkaClient.instance()


def get_webhook_receiver_service(client: KafkaClient = Depends(get_kafka_client)) -> PredictionService:
    return PredictionService(client)


@prediction_router.get("/{camera_id}")
async def request_prediction(camera_id: int,
                             service: PredictionService = Depends(get_webhook_receiver_service)):
    fetch_data = service.get_prediction(camera_id)
    return fetch_data
