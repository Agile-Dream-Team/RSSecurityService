import logging
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any

from RSKafkaWrapper.client import KafkaClient
from app.api.utils import get_kafka_client
from app.dto.auth_dto import (
    RegisterUserDTO,
    LoginUserDTO,
    ConfirmUserDTO,
    ResendCodeDTO, ResetPasswordRequestDTO, ResetPasswordConfirmDTO
)
from app.responses.custom_responses import SuccessModel, ErrorModel
from app.services.auth_service import AuthService
from app.config.config import Settings

logger = logging.getLogger(__name__)

# Add the /api/v1 prefix here
auth_router = APIRouter(tags=["Authentication"])

response_models = {
    400: {"model": ErrorModel},
    401: {"model": ErrorModel},
    403: {"model": ErrorModel},
    500: {"model": ErrorModel}
}


def get_auth_service(client: KafkaClient = Depends(get_kafka_client)) -> AuthService:
    cognito_settings = Settings()
    return AuthService(client, cognito_settings.user_cognito_pool_id, cognito_settings.cognito_client_id)


@auth_router.post(
    "/register",
    response_model=SuccessModel,
    responses={**response_models}
)
async def register_user(
        user_data: RegisterUserDTO,
        auth_service: AuthService = Depends(get_auth_service)
) -> SuccessModel:
    """
    Register a new user in Cognito with required name fields
    """
    try:
        logger.info(f"Registering user with email: {user_data.email}")
        result = await auth_service.register_user(user_data.dict())
        return SuccessModel(
            message="User registered successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@auth_router.post(
    "/confirm_registration",
    response_model=SuccessModel,
    responses={**response_models}
)
async def confirm_user(
        confirmation_data: ConfirmUserDTO,
        auth_service: AuthService = Depends(get_auth_service)
) -> SuccessModel:
    """
    Confirm user registration
    """
    try:
        logger.info(f"Confirming user: {confirmation_data.email}")
        result = await auth_service.confirm_registration(
            confirmation_data.email,
            confirmation_data.confirmation_code
        )
        return SuccessModel(
            message="User confirmed successfully",
            data={"confirmed": result}
        )
    except Exception as e:
        logger.error(f"Confirmation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@auth_router.post(
    "/resend_code",
    response_model=SuccessModel,
    responses={**response_models}
)
async def resend_code(
        code: ResendCodeDTO,
        auth_service: AuthService = Depends(get_auth_service)
) -> SuccessModel:
    try:
        logger.info(f"Resending code to: {code.email}")
        result = await auth_service.resend_confirmation_code(code.email)
        return SuccessModel(
            message="Code sent successfully",
            data={"confirmed": result}
        )
    except Exception as e:
        logger.error(f'Resend code failed: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@auth_router.post(
    "/login",
    response_model=SuccessModel,
    responses={**response_models}
)
async def login_user(
        credentials: LoginUserDTO,
        auth_service: AuthService = Depends(get_auth_service)
) -> SuccessModel:
    """
    Authenticate user using SRP authentication
    """
    try:
        logger.info(f"Attempting SRP login for user: {credentials.email}")
        result = await auth_service.login_user_srp(
            credentials.email,
            credentials.password
        )
        return SuccessModel(
            message="Login successful",
            data=result
        )
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        if "NEW_PASSWORD_REQUIRED" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "NEW_PASSWORD_REQUIRED",
                    "message": "You must change your password"
                }
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@auth_router.post(
    "/refresh-token",
    response_model=SuccessModel,
    responses={**response_models}
)
async def refresh_token(
        refresh_token: str,
        auth_service: AuthService = Depends(get_auth_service)
) -> SuccessModel:
    """
    Refresh access token using refresh token
    """
    try:
        logger.info("Attempting to refresh token")
        result = await auth_service.refresh_tokens(refresh_token)
        return SuccessModel(
            message="Token refreshed successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@auth_router.post(
    "/reset-password/request",
    response_model=SuccessModel,
    responses={**response_models}
)
async def request_password_reset(
        reset_request: ResetPasswordRequestDTO,
        auth_service: AuthService = Depends(get_auth_service)
) -> SuccessModel:
    """
    Request a password reset code
    """
    try:
        logger.info(f"Password reset requested for: {reset_request.email}")
        result = await auth_service.request_password_reset(reset_request.email)
        return SuccessModel(
            message="Password reset code sent successfully",
            data=result
        )
    except Exception as e:
        logger.error(f"Password reset request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@auth_router.post(
    "/reset-password/confirm",
    response_model=SuccessModel,
    responses={**response_models}
)
async def confirm_password_reset(
    reset_confirm: ResetPasswordConfirmDTO,
    auth_service: AuthService = Depends(get_auth_service)
) -> SuccessModel:
    """
    Confirm password reset with verification code
    """
    try:
        logger.info(f"Confirming password reset for: {reset_confirm.email}")
        result = await auth_service.confirm_password_reset(
            reset_confirm.email,
            reset_confirm.confirmation_code,
            reset_confirm.new_password
        )
        return SuccessModel(
            message="Password reset successful",
            data=result
        )
    except Exception as e:
        logger.error(f"Password reset confirmation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
