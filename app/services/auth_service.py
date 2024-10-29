import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError
from warrant_lite import WarrantLite
from time import gmtime, strftime

from RSKafkaWrapper.client import KafkaClient
from app.api.utils import parse_and_flatten_messages
from app.mapper.auth_mapper import UserMapper
from app.shared import lock_user_response, messages_user_response, messages_consumed_user_event


class AuthService:
    def __init__(self, client: KafkaClient, user_cognito_pool_id, cognito_client_id):
        """
        Initialize the Auth Service with Cognito configuration
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.user_cognito_pool_id = user_cognito_pool_id
        self.client_id = cognito_client_id
        self.client = client
        # Initialize regular Cognito client
        self.cognito_client = boto3.client('cognito-idp')

    async def register_user(self, register_user: Dict[str, Any]) -> Dict[str, str]:
        """Register a new user in Cognito with required name attributes"""
        try:
            cognito_response = self.cognito_client.sign_up(
                ClientId=self.client_id,
                Username=register_user['email'],
                Password=register_user['password'],
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': register_user['email']
                    },
                    {
                        'Name': 'given_name',
                        'Value': register_user['given_name']
                    },
                    {
                        'Name': 'family_name',
                        'Value': register_user['family_name']
                    },
                    {
                        'Name': 'name',  # Full name
                        'Value': f"{register_user['given_name']} {register_user['family_name']}".strip()
                    }
                ]
            )

            with lock_user_response:
                messages_user_response.clear()
            messages_consumed_user_event.clear()

            now = strftime("%Y-%m-%d %H:%M:%S", gmtime())

            user_mapper = UserMapper(
                cognito_sub=cognito_response['UserSub'],
                email=register_user['email'],
                name=register_user['given_name'],
                family_name=register_user['family_name'],
                created_at=now
            )

            self.logger.info(cognito_response)

            self.client.send_message("user_request", user_mapper.model_dump())

            messages_consumed_user_event.wait(timeout=10)  # Add a timeout for safety
            # messages_consumed_sensor_data_event.wait()
            logging.info("Event set, proceeding to parse messages.")

            with lock_user_response:
                response = parse_and_flatten_messages(messages_user_response)
            logging.info(f"Received data SAVE: {response}")
            return {
                'user_id': cognito_response['UserSub'],
                'status': 'CONFIRMATION_PENDING',
                'message': 'User registration successful. Please check your email for verification code.',
                'response': response[0]
            }

        except ClientError as e:
            self.logger.error(f"Error in Cognito registration: {str(e)}")
            raise Exception(f"Error registering user: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error in registration: {str(e)}")
            raise

    async def confirm_registration(self, email: str, confirmation_code: str) -> Dict[str, Any]:
        """
        Confirm user registration with verification code
        """
        try:
            self.cognito_client.confirm_sign_up(
                ClientId=self.client_id,
                Username=email,
                ConfirmationCode=confirmation_code
            )

            return {
                'status': 'SUCCESS',
                'message': 'Email verified successfully. You can now login.'
            }

        except ClientError as e:
            self.logger.error(f"Error confirming registration: {str(e)}")
            error_code = e.response['Error']['Code']

            if error_code == 'CodeMismatchException':
                raise Exception("Invalid verification code")
            elif error_code == 'ExpiredCodeException':
                raise Exception("Verification code has expired")
            else:
                raise Exception(f"Error confirming registration: {str(e)}")

    async def resend_confirmation_code(self, email: str) -> Dict[str, Any]:
        """
        Resend confirmation code to user's email
        """
        try:
            self.cognito_client.resend_confirmation_code(
                ClientId=self.client_id,
                Username=email
            )

            return {
                'status': 'SUCCESS',
                'message': 'Verification code has been resent to your email.'
            }

        except ClientError as e:
            self.logger.error(f"Error resending code: {str(e)}")
            raise Exception(f"Error resending verification code: {str(e)}")

    async def login_user_srp(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user using SRP authentication flow with warrant-lite
        """
        try:
            # Initialize WarrantLite client
            warrant = WarrantLite(
                username=email,
                password=password,
                pool_id=self.user_cognito_pool_id,
                client_id=self.client_id,
                client=self.cognito_client
            )

            self.logger.debug(f"Initiating auth for user: {email}")

            # Get tokens using warrant-lite's implementation
            tokens = warrant.authenticate_user()

            if not tokens:
                raise Exception('Failed to authenticate')

            return {
                'access_token': tokens['AuthenticationResult']['AccessToken'],
                'id_token': tokens['AuthenticationResult']['IdToken'],
                'refresh_token': tokens['AuthenticationResult']['RefreshToken'],
                'expires_in': tokens['AuthenticationResult']['ExpiresIn']
            }

        except ClientError as e:
            self.logger.error(f"Error during SRP authentication: {str(e)}")
            error_code = e.response['Error']['Code']

            if error_code == 'UserNotConfirmedException':
                raise Exception("Email not verified. Please verify your email first.")
            elif error_code == 'NotAuthorizedException':
                raise Exception("Incorrect username or password")
            elif error_code == 'UserNotFoundException':
                raise Exception("User does not exist")
            else:
                raise Exception(f"Error during SRP authentication: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error during SRP authentication: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh the access token using a refresh token
        """
        try:
            response = self.cognito_client.initiate_auth(
                AuthFlow='REFRESH_TOKEN_AUTH',
                ClientId=self.client_id,
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )

            return {
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn']
            }

        except ClientError as e:
            self.logger.error(f"Error refreshing tokens: {str(e)}")
            raise Exception(f"Error refreshing tokens: {str(e)}")
