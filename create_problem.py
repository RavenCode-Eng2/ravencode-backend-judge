#!/usr/bin/env python3
"""
Script para crear el problema de promedio con casos de prueba
"""
import asyncio
from datetime import datetime
from bson import ObjectId
from app.core.mongodb import connect_to_mongo, close_mongo_connection, get_database

async def create_promedio_problem():
    """Crear el problema de promedio con casos de prueba"""
    try:
        # Conectar a MongoDB
        await connect_to_mongo()
        db = get_database()
        
        # Verificar si ya existe el problema
        existing_problem = await db.problems.find_one({"title": "Cálculo de Promedio"})
        if existing_problem:
            print("Ya existe un problema con el título 'Cálculo de Promedio'")
            return
        
        # Crear el problema
        problem_data = {
            "title": "Cálculo de Promedio",
            "description": """Escribe un programa que calcule el promedio de tres notas ingresadas por el usuario.

El programa debe:
- Pedir el nombre del estudiante.
- Leer tres notas (pueden ser decimales).
- Calcular el promedio.
- Imprimir el mensaje: [nombre] tiene un promedio de [promedio]

Entrada de ejemplo:
Ana
4.5
3.7
4.2

Salida de ejemplo:
Ana tiene un promedio de 4.13""",
            "difficulty": "easy",
            "time_limit": 1000,
            "memory_limit": 256,
            "created_at": datetime.now()
        }
        
        # Insertar el problema
        problem_result = await db.problems.insert_one(problem_data)
        problem_id = problem_result.inserted_id
        
        print(f"Problema creado exitosamente!")
        print(f"   ID: {problem_id}")
        print(f"   Título: {problem_data['title']}")
        
        # Casos de prueba
        test_cases = [
            {
                "problem_id": problem_id,
                "input_data": "Juan\n3.5\n4.0\n3.5",
                "expected_output": "Juan tiene un promedio de 3.67",
                "is_sample": True,
                "created_at": datetime.now()
            },
            {
                "problem_id": problem_id,
                "input_data": "Sofia\n5.0\n5.0\n5.0",
                "expected_output": "Sofia tiene un promedio de 5.0",
                "is_sample": False,
                "created_at": datetime.now()
            },
            {
                "problem_id": problem_id,
                "input_data": "Carlos\n2.9\n3.1\n3.0",
                "expected_output": "Carlos tiene un promedio de 3.0",
                "is_sample": False,
                "created_at": datetime.now()
            }
        ]
        
        # Insertar casos de prueba
        for i, test_case in enumerate(test_cases):
            result = await db.test_cases.insert_one(test_case)
            sample_text = " (muestra)" if test_case["is_sample"] else " (oculto)"
            print(f"   Caso de prueba {i+1}{sample_text}: {result.inserted_id}")
        
        print(f"\nProblema listo para evaluaciones!")
        print(f"   Total de casos de prueba: {len(test_cases)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cerrar conexión
        await close_mongo_connection()

if __name__ == "__main__":
    print("Creando problema de promedio...")
    asyncio.run(create_promedio_problem()) 