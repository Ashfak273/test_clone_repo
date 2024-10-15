from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, status

from app.models.schemas.impersonate import GoogleAuthUserInfoSchema
from app.core.config import settings

async def fetch_verified_google_user_info(token: str) -> GoogleAuthUserInfoSchema:
    """
    Validates the Google OAuth token, extracts user information, and verifies the email status.

    Parameters:
    ----------
    token : str
        The Google OAuth token provided by the client during login.

    Returns:
    -------
    GoogleAuthUserInfoSchema
        A Pydantic model containing the user's email and email verification status. 

    Raises:
    -------
    HTTPException:
        Raises 400 if the token's issuer is invalid (not Google).
        Raises 401 if the token is invalid, expired, or if the email is not verified.
        
    """
    try:
        id_info = id_token.verify_oauth2_token(token, requests.Request(), settings.google_oauth_client_id)
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise HTTPException(status_code=400, detail="wrong issuer")
        
        user_info = GoogleAuthUserInfoSchema(
            email=id_info.get("email"),
            email_verified=id_info.get("email_verified")
        )
        
        if user_info.email_verified is False:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email account is not verified")
        
        return user_info
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid google oauth token")