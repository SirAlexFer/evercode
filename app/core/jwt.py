from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth import AuthService, get_auth_service

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_payload(
    auth_service: AuthService = Depends(get_auth_service),
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, Any]:
    """
    Извлекает Bearer-токен из заголовка, декодирует его через AuthService.verify_jwt
    и возвращает payload.
    """
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = creds.credentials
    # вот здесь вызываем ваш метод из AuthService
    payload = auth_service.verify_jwt(token)
    return payload
