import logging
import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

from app.api.v1.auth_controller import auth_router
from app.config.config import Settings
from app.shared import (
    messages_consumed_user_event,
    messages_user_response,
    lock_user_response,
)
from RSKafkaWrapper.client import KafkaClient

# Constants
base_path = '/auth'


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


configure_logging()
logger = logging.getLogger(__name__)

# Initialize settings
app_settings = Settings()

# Initialize FastAPI with custom docs URL
app = FastAPI(
    title="Auth Service API",
    description="Authentication Service API",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# Initialize KafkaClient
kafka_client = KafkaClient.instance(
    app_settings.kafka_bootstrap_servers,
    app_settings.kafka_group_id
)


# Custom documentation endpoints
@app.get(f"{base_path}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{base_path}/openapi.json",
        title="Auth Service API Documentation",
    )


@app.get(f"{base_path}/openapi.json", include_in_schema=False)
async def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Auth Service API",
        version="1.0.0",
        description="Authentication Service API documentation",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return app.openapi_schema


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    try:
        local_settings = Settings()
        existing_topics = kafka_client.list_topics()
        logger.info(f"Creating Kafka topics: {local_settings.kafka_topics}")

        for topic in local_settings.kafka_topics:
            if topic not in existing_topics:
                kafka_client.create_topic(topic)
            else:
                logger.info(f"Topic '{topic}' already exists.")

        yield

    except ValidationError as e:
        logger.error(f"Environment variable validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


app.router.lifespan_context = lifespan

# Include the router with the complete prefix
app.include_router(
    auth_router,
    prefix=f"{base_path}/api/v1"  # Add the complete prefix here
)


class HealthCheck(BaseModel):
    webhook_status: str = "OK"
    kafka_status: str = "Not implemented"
    msg: str = "Hello world"


@app.get(
    base_path,
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    tags=["Health Check"]
)
async def get_health() -> HealthCheck:
    logger.info("Health check endpoint called")
    return HealthCheck()


@kafka_client.topic('user_response')
def consume_message_save_user(msg):
    try:
        with lock_user_response:
            messages_user_response.append(msg)
        logger.info(f"Consumed message in user_response: {msg}")
        messages_consumed_user_event.set()
        logger.info("Event set after consuming message.")
    except Exception as e:
        logger.error(f"Error processing message in user_response: {e}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_settings.webhook_host,
        port=app_settings.webhook_port,
        reload=app_settings.environment == 'dev',
        log_level="info"
    )
