from app.dto.webhook_in_dto import WebhookDTO
from app.api.v1.utils import EventType
from app.services.kafka_producer_service import KafkaProducerService
from app.exceptions.custom_exceptions import BadRequestException


class WebhookReceiverService:

    def __init__(self, kafka_producer_service: KafkaProducerService):
        self.kafka_producer_service = kafka_producer_service

    def receive_webhook(self, webhook_data: WebhookDTO):
        # TODO: Handle validation of webhook data
        return self.kafka_producer_service.process_webhook_to_kafka(webhook_data)

    def get_all(self):
        return self.kafka_producer_service.get_all()
