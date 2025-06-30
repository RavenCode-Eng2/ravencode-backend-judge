from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Configuración de la aplicación
    APP_NAME: str = "RavenCode Judge API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración de seguridad
    SECRET_KEY: str = "tu_clave_secreta_aqui_cambiala_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración de CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Configuración del juez de código
    JUDGE_TIMEOUT: int = 10  # segundos
    MAX_MEMORY: int = 512  # MB
    DOCKER_IMAGE: str = "python:3.11-slim"
    
    # Configuración de archivos
    UPLOAD_DIR: str = "./uploads"
    TEMP_DIR: str = "./temp"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

# Crear directorios necesarios
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True) 