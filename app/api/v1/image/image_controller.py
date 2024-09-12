import logging

from fastapi import APIRouter, HTTPException, Depends

from app.dto.webhook_in_dto import SaveDTO
from app.responses.custom_responses import SuccessModel, ErrorModel
from app.services.webhook_receiver_service import WebhookReceiverService
from kafka_rs.client import KafkaClient

image_router = APIRouter()

response_models = {
    400: {"model": ErrorModel},
    401: {"model": ErrorModel},
    500: {"model": ErrorModel}
}


def get_kafka_client() -> KafkaClient:
    return KafkaClient.instance()


def get_webhook_receiver_service(client: KafkaClient = Depends(get_kafka_client)) -> WebhookReceiverService:
    return WebhookReceiverService(client)


def handle_webhook_data(webhook_data: SaveDTO, client: KafkaClient) -> SuccessModel:
    if not webhook_data.data:
        raise HTTPException(status_code=400, detail="Webhook data is empty")
    received_data = WebhookReceiverService(client).receive_webhook(webhook_data)
    if received_data:
        return SuccessModel(data=received_data.dict())
    else:
        raise HTTPException(status_code=500, detail="Failed to process webhook data")


@image_router.post("/")
async def save(webhook: SaveDTO, service: WebhookReceiverService = Depends(get_webhook_receiver_service)):
    received_data = service.receive_webhook(webhook)
    logging.info(f"Received data: {received_data}")
    if not received_data or received_data[0]["status_code"] == 400:
        raise HTTPException(status_code=400, detail=f"{received_data[0]["error"]}")

    return received_data[0]


@image_router.get("/")
async def get_all(service: WebhookReceiverService = Depends(get_webhook_receiver_service)):
    fetch_data = service.get_all()
    return fetch_data


@image_router.get("/{image_id}", response_model=SuccessModel, responses=response_models)
async def get_by_id(record_id: int, client: KafkaClient = Depends(get_kafka_client)):
    pass
