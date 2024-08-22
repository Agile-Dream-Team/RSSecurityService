import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer()


async def has_access(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Function that is used to validate the token in the case that it requires it
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, key='secret', algorithms=["HS256"], options={"verify_signature": False,
                                                                                 "verify_aud": False,
                                                                                 "verify_iss": False})
        print("payload => ", payload)
    except InvalidTokenError as e:  # catches any exception
        raise HTTPException(
            status_code=401,
            detail=str(e))

