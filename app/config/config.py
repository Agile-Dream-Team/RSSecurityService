from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    kafka_bootstrap_servers: str
    kafka_host: str = Field(..., env='KAFKA_HOST')
    kafka_port: str = Field(..., env='KAFKA_PORT')
    kafka_topics: list[str] = Field(..., env='KAFKA_TOPICS')
    kafka_group_id: str = Field(..., env='KAFKA_GROUP_ID')
    webhook_host: str = Field(..., env='WEBHOOK_HOST')
    webhook_port: int = Field(..., env='WEBHOOK_PORT')
    environment: str = Field(..., env='ENVIRONMENT')

    class Config:
        env_file = ".env"
