from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = Field(..., env='KAFKA_BOOTSTRAP_SERVERS')
    kafka_host: str = Field(..., env='KAFKA_HOST')
    kafka_port: str = Field(..., env='KAFKA_PORT')
    kafka_topics: list[str] = Field(..., env='KAFKA_TOPICS')
    kafka_group_id: str = Field(..., env='KAFKA_GROUP_ID')
    user_cognito_pool_id: str = Field(..., env='USER_COGNITO_POOL_ID')
    cognito_client_id: str = Field(..., env='COGNITO_CLIENT_ID')
    webhook_host: str = Field(..., env='WEBHOOK_HOST')
    webhook_port: int = Field(..., env='WEBHOOK_PORT')
    environment: str = Field(..., env='ENVIRONMENT')

    class Config:
        env_file = ".env"
