from fastapi import APIRouter, Body, Depends, Request, Response, status
from app.schemas.user import UserCreate, UserLogin
from app.services.user import UserService, get_user_service
from app.services.auth import AuthService, get_auth_service


router = APIRouter()


@router.post(
    '/create',
    status_code=status.HTTP_201_CREATED, 
    summary='Создание пользователя, авторизация', 
    tags=['Авторизация']
)
async def create(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    created_new_user = await user_service.create_user(user_create)
    return created_new_user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    response: Response,
    user_login: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Регистрация пользователя.
    """
    user = await auth_service.get_user_by_email(user_login.email)
    if user:
        tokens = await auth_service.login(user_login.email, user_login.password)
        return tokens
