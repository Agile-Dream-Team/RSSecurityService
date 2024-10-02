import logging

from fastapi import APIRouter, HTTPException, Depends

from app.dto.sensor_data_dto import SaveDTO
from app.responses.custom_responses import SuccessModel, ErrorModel
from app.services.sensor_data_service import SensorDataService
from RSKafkaWrapper.client import KafkaClient

sensor_data_router = APIRouter()

response_models = {
    400: {"model": ErrorModel},
    401: {"model": ErrorModel},
    500: {"model": ErrorModel}
}


def get_kafka_client() -> KafkaClient:
    return KafkaClient.instance()


def get_webhook_receiver_service(client: KafkaClient = Depends(get_kafka_client)) -> SensorDataService:
    return SensorDataService(client)


@sensor_data_router.post("/")
async def save(webhook: SaveDTO, service: SensorDataService = Depends(get_webhook_receiver_service)):
    received_data = service.save_sensor_data(webhook)
    logging.info(f"Received data: {received_data}")
    #if received_data is not None:
     #   if received_data[0].get("status_code") == 400:
      #      raise HTTPException(status_code=400, detail=f"{received_data[0].get('error')}")

    return received_data


@sensor_data_router.get("/")
async def get_all(service: SensorDataService = Depends(get_webhook_receiver_service)):
    fetch_data = service.get_all_sensor_data()
    return fetch_data


@sensor_data_router.get("/{record_id}")
async def get_by_id_sensor_data(record_id: int, service: SensorDataService = Depends(get_webhook_receiver_service)):
    received_data = service.get_by_id_sensor_data(record_id)
    logging.info(f"Received data: {received_data}")
    #if received_data is not None:
     #   if received_data[0].get("status_code") == 400:
      #      raise HTTPException(status_code=400, detail=f"{received_data[0].get('error')}")
    return received_data
