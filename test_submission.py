#!/usr/bin/env python3
"""
Script para probar la creación de submisiones
"""
import asyncio
import aiohttp
import json

async def test_submission():
    """Probar la creación de una submisión"""
    base_url = "http://localhost:8000"
    
    print("Probando creación de submisión...")
    
    # 1. Autenticación
    try:
        async with aiohttp.ClientSession() as session:
            auth_data = {
                "username": "admin",
                "password": "admin123"
            }
            async with session.post(
                f"{base_url}/api/v1/auth/login",
                data=auth_data
            ) as response:
                if response.status == 200:
                    auth_result = await response.json()
                    token = auth_result.get("access_token")
                    print(f"Autenticación exitosa: {auth_result}")
                else:
                    print(f"Autenticación falló: {response.status}")
                    return
    except Exception as e:
        print(f"Error en autenticación: {e}")
        return
    
    # 2. Obtener problemas
    try:
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/api/v1/problems/",
                headers=headers
            ) as response:
                if response.status == 200:
                    problems = await response.json()
                    print(f"Problemas obtenidos: {len(problems)} problemas")
                    
                    # Debug: mostrar estructura del primer problema
                    if problems:
                        print(f"Estructura del primer problema: {json.dumps(problems[0], indent=2)}")
                    
                    # Buscar el problema de promedio
                    promedio_problem = None
                    for problem in problems:
                        if problem.get("title") == "Cálculo de Promedio":
                            promedio_problem = problem
                            break
                    
                    if promedio_problem:
                        print(f"Problema de promedio encontrado: {promedio_problem.get('_id', promedio_problem.get('id'))}")
                        
                        # 3. Crear submisión
                        submission_data = {
                            "problem_id": promedio_problem.get('_id', promedio_problem.get('id')),
                            "code": """nombre = input()
nota1 = float(input())
nota2 = float(input())
nota3 = float(input())
promedio = (nota1 + nota2 + nota3) / 3
print(f"{nombre} tiene un promedio de {promedio:.2f}")""",
                            "language": "python"
                        }
                        
                        print(f"Datos de submisión: {json.dumps(submission_data, indent=2)}")
                        
                        async with session.post(
                            f"{base_url}/api/v1/submissions/",
                            headers=headers,
                            json=submission_data
                        ) as sub_response:
                            print(f"Status de respuesta: {sub_response.status}")
                            if sub_response.status == 201:
                                submission = await sub_response.json()
                                submission_id = submission.get('_id', submission.get('id'))
                                print(f"Submisión creada exitosamente: {submission_id}")
                                print(f"Respuesta completa: {json.dumps(submission, indent=2)}")
                            else:
                                error_text = await sub_response.text()
                                print(f"Error creando submisión: {sub_response.status}")
                                print(f"Error detallado: {error_text}")
                    else:
                        print("Problema de promedio no encontrado")
                else:
                    print(f"Error obteniendo problemas: {response.status}")
    except Exception as e:
        print(f"Error en pruebas: {e}")

if __name__ == "__main__":
    print("Iniciando prueba de submisión...")
    asyncio.run(test_submission()) 