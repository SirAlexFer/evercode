from fastapi import APIRouter, Body, Depends, Request, Response, status, HTTPException
from app.schemas.user import UserCreate, UserLogin
from app.services.user import UserService, get_user_service
from app.services.auth import AuthService, get_auth_service
from app.services.category import CategoryService, get_category_service
from app.core.jwt import get_current_payload

router = APIRouter()


@router.post(
    '/create',
    status_code=status.HTTP_201_CREATED,
    summary='Создание пользователя и базовых категорий',
    tags=['Авторизация']
)
async def create(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
    category_service: CategoryService = Depends(get_category_service)
):
    """
    Создание пользователя с автоматическим добавлением категорий по умолчанию.
    """
    # Создаем пользователя
    created_new_user = await user_service.create_user(user_create)
    # Добавляем базовые категории для нового пользователя
    await category_service.create_default_categories(created_new_user.id)
    return created_new_user


@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    summary='Авторизация пользователя',
    tags=['Авторизация']
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
        return tokens
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Неверный email или пароль'
    )
