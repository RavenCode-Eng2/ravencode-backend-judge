#!/usr/bin/env python3
"""
Script para verificar la conexión a MongoDB Atlas y el estado del backend
"""
import asyncio
from dotenv import load_dotenv
import os
import pymongo

async def verificar_conexion():
    """Verificar la conexión a MongoDB Atlas"""
    print("Verificando conexión a MongoDB Atlas...")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener configuración
    mongodb_url = os.getenv('MONGODB_URL')
    database_name = os.getenv('MONGODB_DATABASE', 'ravencode_judge')
    
    if not mongodb_url:
        print("Error: MONGODB_URL no encontrada en el archivo .env")
        return False
    
    try:
        # Conectar a MongoDB Atlas
        client = pymongo.MongoClient(mongodb_url)
        client.admin.command('ping')
        print("✅ Conexión a MongoDB Atlas exitosa")
        
        # Verificar base de datos
        db = client[database_name]
        print(f"✅ Base de datos '{database_name}' accesible")
        
        # Verificar colecciones
        collections = db.list_collection_names()
        print(f"✅ Colecciones encontradas: {collections}")
        
        # Verificar problemas
        problems_count = db.problems.count_documents({})
        print(f"✅ Problemas en la base de datos: {problems_count}")
        
        # Verificar casos de prueba
        test_cases_count = db.test_cases.count_documents({})
        print(f"✅ Casos de prueba en la base de datos: {test_cases_count}")
        
        # Verificar usuarios
        users_count = db.users.count_documents({})
        print(f"✅ Usuarios en la base de datos: {users_count}")
        
        # Verificar submisiones
        submissions_count = db.submissions.count_documents({})
        print(f"✅ Submisiones en la base de datos: {submissions_count}")
        
        print("\n" + "=" * 50)
        print("✅ Todo está configurado correctamente!")
        print("\nPróximos pasos:")
        print("1. Ejecuta: python -m app.main")
        print("2. El servidor estará disponible en: http://localhost:8000")
        print("3. Prueba la integración desde el frontend")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a MongoDB Atlas: {e}")
        print("Verifica tu configuración en el archivo .env")
        return False

if __name__ == "__main__":
    success = asyncio.run(verificar_conexion())
    if not success:
        exit(1) 