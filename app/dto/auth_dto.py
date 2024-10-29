from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterUserDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    given_name: str = Field(..., description="First name")
    family_name: str = Field(..., description="Last name")
    invitation_code: Optional[str] = Field(None, description="Optional invitation code")


class LoginUserDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., description="User password")


class ConfirmUserDTO(BaseModel):
    email: EmailStr
    confirmation_code: str = Field(..., description="Confirmation code sent to email")


class ResendCodeDTO(BaseModel):
    email: EmailStr


class ResetPasswordRequestDTO(BaseModel):
    email: EmailStr


class ResetPasswordConfirmDTO(BaseModel):
    email: EmailStr
    confirmation_code: str
    new_password: str


class ConfirmPasswordDTO(BaseModel):
    email: EmailStr
    confirmation_code: str = Field(..., description="Password reset confirmation code")
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters long")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "Strongpassword123!",
                "given_name": "John",
                "family_name": "Doe",
                "invitation_code": "ABC123"
            }
        }
