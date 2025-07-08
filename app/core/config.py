from pydantic_settings import BaseSettings
from typing import List
import os
import logging
import platform

logger = logging.getLogger(__name__)

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
    
    # Configuración de Docker
    DOCKER_HOST: str = "npipe:////./pipe/docker_engine" if platform.system() == "Windows" else "unix:///var/run/docker.sock"
    DOCKER_PLATFORM: str = "windows/amd64" if platform.system() == "Windows" else "linux/amd64"
    DOCKER_API_VERSION: str = "1.41"
    DOCKER_TLS_VERIFY: bool = False
    DOCKER_CERT_PATH: str = ""
    
    # Configuración de archivos
    UPLOAD_DIR: str = "./uploads"
    TEMP_DIR: str = "./temp"
    
    # Configuración de MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "ravencode_judge"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignorar campos extra en lugar de fallar

# Instancia global de configuración
try:
    settings = Settings()
    logger.info("Configuración cargada exitosamente")
except Exception as e:
    logger.error(f"Error cargando configuración: {e}")
    # Usar configuración por defecto si hay error
    settings = Settings()

# Crear directorios necesarios
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True) 