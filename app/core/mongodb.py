from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging
import ssl
import certifi

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

async def connect_to_mongo():
    """Conectar a MongoDB"""
    try:
        # Primero intentar conexión simple
        logger.info("Intentando conexión simple a MongoDB...")
        MongoDB.client = AsyncIOMotorClient(settings.MONGODB_URL)
        MongoDB.database = MongoDB.client[settings.MONGODB_DATABASE]
        
        # Verificar conexión
        await MongoDB.client.admin.command('ping')
        logger.info("Conexión exitosa a MongoDB")
        
        # Crear índices
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Error con conexión simple: {e}")
        
        try:
            # Si falla, intentar con configuración específica
            logger.info("Intentando conexión con configuración específica...")
            connection_params = {
                'serverSelectionTimeoutMS': 30000,
                'connectTimeoutMS': 30000,
                'socketTimeoutMS': 30000,
                'maxPoolSize': 10,
                'minPoolSize': 1,
                'retryWrites': True,
                'w': 'majority',
                'tls': True,
                'tlsCAFile': certifi.where(),
                'tlsAllowInvalidHostnames': True
            }
            
            MongoDB.client = AsyncIOMotorClient(settings.MONGODB_URL, **connection_params)
            MongoDB.database = MongoDB.client[settings.MONGODB_DATABASE]
            
            # Verificar conexión
            await MongoDB.client.admin.command('ping')
            logger.info("Conexión exitosa a MongoDB con configuración específica")
            
            # Crear índices
            await create_indexes()
            
        except Exception as e2:
            logger.error(f"Error conectando a MongoDB: {e2}")
            raise e2

async def close_mongo_connection():
    """Cerrar conexión a MongoDB"""
    if MongoDB.client:
        MongoDB.client.close()
        logger.info("Conexión a MongoDB cerrada")

async def create_indexes():
    """Crear índices para optimizar consultas"""
    try:
        # Índices para usuarios
        await MongoDB.database.users.create_index("email", unique=True)
        await MongoDB.database.users.create_index("username", unique=True)
        
        # Índices para problemas
        await MongoDB.database.problems.create_index("title")
        await MongoDB.database.problems.create_index("difficulty")
        
        # Índices para submisiones
        await MongoDB.database.submissions.create_index("user_id")
        await MongoDB.database.submissions.create_index("problem_id")
        await MongoDB.database.submissions.create_index("status")
        await MongoDB.database.submissions.create_index("created_at")
        
        # Índices para casos de prueba
        await MongoDB.database.test_cases.create_index("problem_id")
        
        logger.info("Índices creados exitosamente")
        
    except Exception as e:
        logger.error(f"Error creando índices: {e}")

def get_database():
    """Obtener instancia de la base de datos"""
    return MongoDB.database 