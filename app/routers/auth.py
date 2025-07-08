from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db, get_user_by_username, get_user_by_email
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash
)
from app.models.base import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    Registrar un nuevo usuario
    """
    storage = get_db()
    
    # Verificar si el usuario ya existe
    existing_user = get_user_by_username(user.username) or get_user_by_email(user.email)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario o email ya está registrado"
        )
    
    # Crear nuevo usuario
    user_id = storage.user_id_counter
    storage.user_id_counter += 1
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=user_id,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False,
        created_at=datetime.now()
    )
    
    storage.users[user_id] = db_user
    
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Iniciar sesión y obtener token de acceso
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60  # 30 minutos en segundos
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Obtener información del usuario actual
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar información del usuario actual
    """
    storage = get_db()
    
    # Verificar si el nuevo username o email ya existe
    if "username" in user_update:
        existing_user = get_user_by_username(user_update["username"])
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
        current_user.username = user_update["username"]
    
    if "email" in user_update:
        existing_user = get_user_by_email(user_update["email"])
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso"
            )
        current_user.email = user_update["email"]
    
    if "password" in user_update:
        current_user.hashed_password = get_password_hash(user_update["password"])
    
    storage.users[current_user.id] = current_user
    
    return current_user 