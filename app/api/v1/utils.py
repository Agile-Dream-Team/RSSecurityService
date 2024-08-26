import json

from fastapi import Request, HTTPException, Header
from functools import wraps
from app.exceptions.custom_exceptions import BadRequestException
from enum import Enum

# In `app/api/v1/utils.py`
from app.shared import messages_consumed_event


def clear(response_list):
    response_list.clear()
    messages_consumed_event.clear()  # Clear the event before waiting
    messages_consumed_event.wait()


async def validate_webhook(request: Request):
    if not request.json():
        raise BadRequestException(detail="Not a valid request")
    return await request.json()


async def validate_x_authorization_header(x_authorization: str = Header(...)):
    if x_authorization != "test":
        raise HTTPException(status_code=401, detail="Invalid x-Authorization header")


def parse_and_flatten_messages(messages):
    parsed_messages = [json.loads(message) for message in messages]

    flattened_messages = []
    for message in parsed_messages:
        if isinstance(message, list):
            flattened_messages.extend(message)
        else:
            flattened_messages.append(message)

    return flattened_messages


class TopicEvent(str, Enum):
    HIGH_TEMP = "high_temp"
    LOW_TEMP = "low_temp"
    HIGH_HUMIDITY = "high_humidity"
    LOW_HUMIDITY = "low_humidity"
    HIGH_CO2 = "high_co2"
    LOW_CO2 = "low_co2"
    HIGH_ELECTRICITY = "high_electricity"
    LOW_ELECTRICITY = "low_electricity"
    CAM_ALERT = "cam_alert"
    UNKNOWN = "unknown"


class TopicActionRequest(str, Enum):
    SAVE = "save"
    UPDATE = "update"
    DELETE = "delete"
    GET_ALL = "get_all"
    GET_BY_ID = "get_by_id"


class TopicActionResponse(str, Enum):
    SAVE_RESPONSE = "save_response"
    GET_ALL_RESPONSE = "get_all_response"
    GET_BY_ID_RESPONSE = "get_by_id_response"
