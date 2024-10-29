from pydantic import BaseModel


class UserMapper(BaseModel):
    cognito_sub: str
    email: str
    name: str
    family_name: str
    created_at: str
