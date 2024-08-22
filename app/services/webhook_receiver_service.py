import json
from typing import List, Dict, Any

from app.dto.webhook_in_dto import WebhookDTO
from app.services.kafka_producer_service import KafkaProducerService
from kafka_rs.client import KafkaClient
from app.shared import messages_get_all, messages_get_all_produce, messages_consumed_event


class WebhookReceiverService:

    def __init__(self, client: KafkaClient):
        self.client = client
        self.kafka_producer_service = KafkaProducerService(client)

    def receive_webhook(self, webhook_data: WebhookDTO):
        return self.kafka_producer_service.process_webhook_to_kafka(webhook_data)

    def get_all(self) -> list[Any]:
        self.kafka_producer_service.get_all()
        messages_consumed_event.wait()
        parsed_messages = [json.loads(message) for message in messages_get_all_produce]

        # Flatten the nested array
        flattened_messages = []
        for message in parsed_messages:
            if isinstance(message, list):
                flattened_messages.extend(message)
            else:
                flattened_messages.append(message)

        return flattened_messages
