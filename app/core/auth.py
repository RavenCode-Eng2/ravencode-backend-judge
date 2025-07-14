from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.database import get_db, get_user_by_username
from app.models.base import User

# Configuración de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar si la contraseña coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generar hash de la contraseña"""
    return pwd_context.hash(password)

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Autenticar usuario con username/email y contraseña"""
    # Buscar por username o email
    user = await get_user_by_username(username)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token JWT de acceso"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

async def get_default_user() -> User:
    """Obtener usuario por defecto para desarrollo"""
    from app.core.database import get_user_by_username
    
    # Intentar obtener el usuario admin
    admin_user = await get_user_by_username("admin")
    if admin_user:
        return admin_user
    
    # Si no existe, crear uno por defecto
    return User(
        id=1,
        username="test_user",
        email="test@example.com",
        hashed_password="",
        is_active=True,
        is_admin=False,
        created_at=datetime.now()
    )

async def get_current_user_optional(token: str = Depends(oauth2_scheme)) -> User:
    """Obtener usuario actual (simplificado ya que el email viene en el request body)."""
    from datetime import datetime
    from app.models.base import User
    
    # Ya no necesitamos extraer el email del JWT, solo validar que hay un token
    if token is None:
        print("DEBUG: No se proporcionó token JWT")
        return User(id=None, username="anonymous", email="anonymous@example.com", hashed_password="", is_active=False, is_admin=False, created_at=datetime.now())
    
    # Si hay token, consideramos al usuario como autenticado
    print("DEBUG: Token JWT proporcionado, usuario autenticado")
    return User(id=None, username="authenticated", email="authenticated@example.com", hashed_password="", is_active=True, is_admin=False, created_at=datetime.now())

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Obtener usuario actual desde el token (requiere autenticación)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception
    
    username = verify_token(token)
    if username is None:
        raise credentials_exception
    
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Obtener usuario activo actual"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user 