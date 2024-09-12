import logging
from ..dto.kafka_out_dto import KafkaOutDTO
from ..dto.webhook_in_dto import SaveDTO
from confluent_kafka import KafkaException
from kafka_rs.client.kafka_client import KafkaClient
from ..shared import messages_consumed_event


class KafkaProducerService:
    def __init__(self, kafka_client: KafkaClient):
        self.kafka_client = kafka_client
        logging.basicConfig(level=logging.INFO)

    def process_webhook_to_kafka(self, webhook_dto: SaveDTO):
        try:
            kafka_out_dto = KafkaOutDTO(
                event=webhook_dto.event,
                data=webhook_dto.data.dict(),
                date_time=webhook_dto.date_time,
                client_id=webhook_dto.client_id,
                uuid=webhook_dto.uuid
            )
            self.kafka_client.send_message(webhook_dto.event, kafka_out_dto.json())


        except KafkaException as e:
            logging.error(f"Failed to send message: {e}")
            raise

    def get_all(self):
        try:

            self.kafka_client.send_message("get_all", '{"event": "get_all"}')
        except KafkaException as e:
            logging.error(f"Failed to send message: {e}")
            raise
