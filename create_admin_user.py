#!/usr/bin/env python3
"""
Script para crear un usuario administrador en MongoDB
"""
import asyncio
from datetime import datetime
from bson import ObjectId
from app.core.mongodb import connect_to_mongo, close_mongo_connection, get_database
from app.core.auth import get_password_hash

async def create_admin_user():
    """Crear un usuario administrador"""
    try:
        # Conectar a MongoDB
        await connect_to_mongo()
        db = get_database()
        
        # Datos del usuario admin
        admin_data = {
            "username": "admin",
            "email": "admin@ravencode.com",
            "hashed_password": get_password_hash("admin123"),  # Cambia esta contraseña
            "is_active": True,
            "is_admin": True,
            "created_at": datetime.now()
        }
        
        # Verificar si ya existe un usuario admin
        existing_admin = await db.users.find_one({"username": "admin"})
        if existing_admin:
            print("Ya existe un usuario admin con username 'admin'")
            return
        
        # Insertar el usuario admin
        result = await db.users.insert_one(admin_data)
        
        if result.inserted_id:
                    print("Usuario admin creado exitosamente!")
        print(f"   Username: admin")
        print(f"   Email: admin@ravencode.com")
        print(f"   Password: admin123")
        print(f"   ID: {result.inserted_id}")
        print("\nAhora puedes hacer login con estas credenciales")
        else:
            print("Error al crear el usuario admin")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cerrar conexión
        await close_mongo_connection()

if __name__ == "__main__":
    print("Creando usuario administrador...")
    asyncio.run(create_admin_user()) 