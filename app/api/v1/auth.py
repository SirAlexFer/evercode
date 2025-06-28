from fastapi import APIRouter, Body, Depends, Request, Response, status, HTTPException
from pydantic import BaseModel
from pydantic import ConfigDict
from app.schemas.user import UserCreate, UserLogin, TokenResponse, TokenRefreshRequest
from app.services.user import UserService, get_user_service
from app.services.auth import AuthService, get_auth_service
from app.services.category import CategoryService, get_category_service
from app.core.jwt import get_current_payload

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    summary="Создание пользователя и базовых категорий",
    tags=["Авторизация"],
)
async def create(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    category_service: CategoryService = Depends(get_category_service),
):
    """
    Создание пользователя с автоматическим добавлением категорий по умолчанию.

    """
    if not await auth_service.get_user_by_email(user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    created_new_user = await user_service.create_user(user_create)
    await category_service.create_default_categories(created_new_user.id)
    return created_new_user


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Авторизация пользователя",
    tags=["Авторизация"],
)
async def login(
    request: Request,
    response: Response,
    user_login: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Аутентификация пользователя и получение пары JWT.
    """

    user = await auth_service.get_user_by_email(user_login.email)
    if user:
        tokens = await auth_service.login(user_login.email, user_login.password)
        if tokens:
            return tokens
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
    )


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Получение информации о текущем пользователе",
    tags=["Авторизация"],
)
async def get_current_user(
    payload: dict = Depends(get_current_payload),
    user_service: AuthService = Depends(get_auth_service),
):
    """
    Возвращает информацию о текущем пользователе.
    """
    email = payload.get("email")
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    return user


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Обновление токенов",
    tags=["Авторизация"],
)
async def refresh_tokens(
    request: Request,
    data: TokenRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Принимает refresh_token и возвращает новую пару токенов.
    """
    payload = auth_service.verify_jwt(data.refresh_token)
    user = await auth_service.get_user_by_email(payload.get("email"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден"
        )
    tokens = await auth_service.create_tokens_pair(user)
    return tokens
