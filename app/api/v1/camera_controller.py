import logging

from fastapi import APIRouter, HTTPException, Depends

from app.dto.camera_dto import CameraDTO
from app.responses.custom_responses import SuccessModel, ErrorModel
from app.services.camera_service import CameraService
from RSKafkaWrapper.client import KafkaClient

camera_router = APIRouter()

response_models = {
    400: {"model": ErrorModel},
    401: {"model": ErrorModel},
    500: {"model": ErrorModel}
}


def get_kafka_client() -> KafkaClient:
    return KafkaClient.instance()


def get_webhook_receiver_service(client: KafkaClient = Depends(get_kafka_client)) -> CameraService:
    return CameraService(client)


@camera_router.post("/")
async def save_camera(camera: CameraDTO, service: CameraService = Depends(get_webhook_receiver_service)):
    received_data = service.save_camera(camera)
    logging.info(f"Received data: {received_data}")
    if received_data is not None:
        if received_data[0]["status_code"] == 400:
            raise HTTPException(status_code=400, detail=f"{received_data[0]["error"]}")

    return received_data[0]


@camera_router.get("/")
async def get_all_camera(service: CameraService = Depends(get_webhook_receiver_service)):
    fetch_data = service.get_all_camera()
    return fetch_data


@camera_router.get("/{camera_id}", response_model=SuccessModel, responses=response_models)
async def get_by_id_camera(camera_id: int, client: KafkaClient = Depends(get_kafka_client)):
    pass
