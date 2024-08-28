import logging

from fastapi import APIRouter, HTTPException, Depends

from app.dto.webhook_in_dto import WebhookDTO
from app.responses.custom_responses import SuccessModel, ErrorModel
from app.services.webhook_receiver_service import WebhookReceiverService
from kafka_rs.client import KafkaClient

router = APIRouter()

response_models = {
    400: {"model": ErrorModel},
    401: {"model": ErrorModel},
    500: {"model": ErrorModel}
}


def get_kafka_client() -> KafkaClient:
    return KafkaClient.instance()


def get_webhook_receiver_service(client: KafkaClient = Depends(get_kafka_client)) -> WebhookReceiverService:
    return WebhookReceiverService(client)


def handle_webhook_data(webhook_data: WebhookDTO, client: KafkaClient) -> SuccessModel:
    if not webhook_data.data:
        raise HTTPException(status_code=400, detail="Webhook data is empty")
    received_data = WebhookReceiverService(client).receive_webhook(webhook_data)
    if received_data:
        return SuccessModel(data=received_data.dict())
    else:
        raise HTTPException(status_code=500, detail="Failed to process webhook data")


@router.post("/save")
async def save(webhook: WebhookDTO, service: WebhookReceiverService = Depends(get_webhook_receiver_service)):
    received_data = service.receive_webhook(webhook)
    logging.info(f"Received data: {received_data}")
    if not received_data or received_data[0]["status_code"] == 400:
        raise HTTPException(status_code=400, detail=f"{received_data[0]["error"]}")

    return received_data[0]


@router.get("/get_device_data")
async def get_all(service: WebhookReceiverService = Depends(get_webhook_receiver_service)):
    fetch_data = service.get_all()
    return fetch_data


@router.get("/get_device_data/{device_id}", response_model=SuccessModel, responses=response_models)
async def get_by_id(device_id: int, client: KafkaClient = Depends(get_kafka_client)):
    pass
