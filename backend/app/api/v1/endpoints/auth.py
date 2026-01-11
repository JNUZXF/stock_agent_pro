"""
认证API端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    PasswordChange
)
from app.schemas.user import UserResponse
from app.core.security import get_current_user_id
from app.services.user_service import UserService
from app.core.exceptions import (
    ResourceAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError
)

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(
    register_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    用户注册

    Args:
        register_data: 注册数据
        db: 数据库会话

    Returns:
        Token响应
    """
    try:
        auth_service = AuthService(db)
        return auth_service.register(register_data)
    except ResourceAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    用户登录

    Args:
        login_data: 登录数据
        db: 数据库会话

    Returns:
        Token响应
    """
    try:
        auth_service = AuthService(db)
        return auth_service.login(login_data.username, login_data.password)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    刷新Token

    Args:
        token_data: Token数据
        db: 数据库会话

    Returns:
        新的Token响应
    """
    try:
        auth_service = AuthService(db)
        return auth_service.refresh_token(token_data.refresh_token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前用户信息

    Args:
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        用户信息
    """
    user_service = UserService(db)
    user = user_service.get_user_by_id(int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return user


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    修改密码

    Args:
        password_data: 密码数据
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        成功消息
    """
    try:
        user_service = UserService(db)
        user_service.change_password(
            int(user_id),
            password_data.old_password,
            password_data.new_password
        )

        return {"message": "密码修改成功"}

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
