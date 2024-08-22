from fastapi import Request, HTTPException, Header
from functools import wraps
from app.exceptions.custom_exceptions import BadRequestException
from enum import Enum


async def validate_webhook(request: Request):
    if not request.json():
        raise BadRequestException(detail="Not a valid request")
    return await request.json()


async def validate_x_authorization_header(x_authorization: str = Header(...)):
    if x_authorization != "test":
        raise HTTPException(status_code=401, detail="Invalid x-Authorization header")


class EventType(str, Enum):
    NORMAL = "normal"
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


class EventActionConsume(str, Enum):
    SAVE = "save"
    UPDATE = "update"
    DELETE = "delete"
    GET_ALL = "get_all"
    GET_BY_ID = "get_by_id"


class EventActionProduce(str, Enum):
    GET_ALL_PRODUCE = "get_all_produce"
    GET_BY_ID_PRODUCE = "get_by_id_produce"

