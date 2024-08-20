import logging

from app.config.kafka_manager import KafkaManager
from app.exceptions.custom_exceptions import BadRequestException
from app.services.kafka_producer_service import KafkaProducerService


class KafkaConsumerService:
    def __init__(self, kafka_manager: KafkaManager):
        self.producer_service = KafkaProducerService(kafka_manager)

    def process_message(self, kafka_in_dto):
        try:
            message = f"Processing message: {kafka_in_dto}"
            logging.info(message)

        except Exception as e:
            logging.error(f"Error processing message: {e}")
            raise BadRequestException(f"Failed to process message: {e}")