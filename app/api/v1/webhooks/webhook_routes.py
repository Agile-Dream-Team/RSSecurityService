from fastapi import APIRouter, HTTPException, Depends

from app.dto.webhook_in_dto import WebhookDTO
from app.responses.custom_responses import SuccessModel, ErrorModel
from app.services.webhook_receiver_service import WebhookReceiverService
from kafka_rs.client import KafkaClient  # Assuming kafka_library is the module where KafkaClient is defined

router = APIRouter()

response_models = {
    400: {"model": ErrorModel},
    401: {"model": ErrorModel},
    500: {"model": ErrorModel}
}


def get_kafka_client() -> KafkaClient:
    return KafkaClient.instance()


def handle_webhook_data(webhook_data: WebhookDTO, client: KafkaClient) -> SuccessModel:
    if not webhook_data.data:
        raise HTTPException(status_code=400, detail="Webhook data is empty")
    received_data = WebhookReceiverService(client).receive_webhook(webhook_data)
    if received_data:
        return SuccessModel(data=received_data.dict())
    else:
        raise HTTPException(status_code=500, detail="Failed to process webhook data")


@router.post("/save", response_model=SuccessModel, responses=response_models)
async def save(webhook: WebhookDTO, client: KafkaClient = Depends(get_kafka_client)):
    return handle_webhook_data(webhook, client)


@router.get("/get_device_data")
async def get_all(client: KafkaClient = Depends(get_kafka_client)):
    print(f'Kafka client {get_kafka_client()}')
    fetch_data = WebhookReceiverService(client).get_all()
    return fetch_data


@router.get("/get_device_data/{device_id}", response_model=SuccessModel, responses=response_models)
async def get_by_id(device_id: int, client: KafkaClient = Depends(get_kafka_client)):
    pass
