import asyncio
import subprocess
import tempfile
import os
import time
import docker
from typing import Dict, List, Any, Optional

from app.core.config import settings
from app.core.database import get_problem_by_id, get_test_cases_by_problem_id
from app.models.base import Problem, TestCase, TestCaseResult

class CodeJudge:
    """Clase principal para evaluar código de estudiantes"""
    
    def __init__(self):
        """Inicializar el juez con la configuración de Docker"""
        try:
            self.docker_client = docker.from_env()
            self.docker_client.ping()  # Verificar conexión
        except Exception as e:
            print(f"Error inicializando Docker: {str(e)}")
            self.docker_client = None
            
        self.supported_languages = {
            "python": {
                "extension": ".py",
                "command": "python",
                "docker_image": "python:3.11-slim"
            },
            "javascript": {
                "extension": ".js",
                "command": "node",
                "docker_image": "node:18-slim"
            },
            "java": {
                "extension": ".java",
                "command": "java",
                "docker_image": "openjdk:11-slim"
            }
        }
    
    async def evaluate(
        self, 
        code: str, 
        language: str, 
        problem_id: str
    ) -> Dict[str, Any]:
        """
        Evaluar código contra todos los casos de prueba de un problema
        """
        try:
            # Obtener el problema y sus casos de prueba
            problem = await get_problem_by_id(problem_id)
            if not problem:
                return {
                    "status": "error",
                    "message": "Problema no encontrado"
                }

            test_cases = await get_test_cases_by_problem_id(problem_id)
            if not test_cases:
                return {
                    "status": "error",
                    "message": "No hay casos de prueba para este problema"
                }
            
            # Verificar que el lenguaje es soportado
            if language not in self.supported_languages:
                return {
                    "status": "error",
                    "message": f"Lenguaje {language} no soportado"
                }
            
            total_test_cases = len(test_cases)
            passed_test_cases = 0
            total_execution_time = 0
            total_memory_used = 0
            test_case_results = []
            
            # Evaluar cada caso de prueba
            for test_case in test_cases:
                result = await self._run_test_case(
                    code=code,
                    language=language,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output,
                    time_limit=problem.time_limit,
                    memory_limit=problem.memory_limit
                )
                
                test_case_results.append(result)
                
                if result["status"] == "passed":
                    passed_test_cases += 1
                
                if result.get("execution_time"):
                    total_execution_time += result["execution_time"]
                
                if result.get("memory_used"):
                    total_memory_used = max(total_memory_used, result["memory_used"])
            
            # Calcular puntuación y estado final
            score = (passed_test_cases / total_test_cases) * 100 if total_test_cases > 0 else 0
            
            if passed_test_cases == total_test_cases:
                final_status = "accepted"
            elif passed_test_cases > 0:
                final_status = "partial"
            else:
                final_status = "wrong_answer"
            
            return {
                "status": final_status,
                "score": score,
                "execution_time": total_execution_time,
                "memory_used": total_memory_used,
                "passed_test_cases": passed_test_cases,
                "total_test_cases": total_test_cases,
                "test_case_results": test_case_results
            }
        except Exception as e:
            print(f"Error en evaluate: {str(e)}")
            return {
                "status": "error",
                "message": f"Error al evaluar la submisión: {str(e)}",
                "score": 0.0
            }
    
    async def _run_test_case(
        self,
        code: str,
        language: str,
        input_data: str,
        expected_output: str,
        time_limit: int,
        memory_limit: int
    ) -> Dict[str, Any]:
        """
        Ejecutar un caso de prueba específico
        """
        try:
            # Crear archivo temporal con el código
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=self.supported_languages[language]["extension"],
                delete=False
            ) as f:
                f.write(code)
                code_file = f.name
            
            # Crear archivo temporal con la entrada
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(input_data)
                input_file = f.name
            
            # Ejecutar el código
            start_time = time.time()
            
            if settings.DEBUG:
                # Modo desarrollo: ejecutar directamente
                result = await self._execute_locally(
                    code_file=code_file,
                    input_file=input_file,
                    language=language,
                    time_limit=time_limit
                )
            else:
                # Modo producción: ejecutar en Docker
                result = await self._execute_in_docker(
                    code_file=code_file,
                    input_file=input_file,
                    language=language,
                    time_limit=time_limit,
                    memory_limit=memory_limit
                )
            
            execution_time = time.time() - start_time
            
            # Limpiar archivos temporales
            os.unlink(code_file)
            os.unlink(input_file)
            
            # Comparar salida con la esperada
            actual_output = result.get("output", "").strip()
            expected_output = expected_output.strip()
            
            if result["status"] == "success":
                if actual_output == expected_output:
                    return {
                        "status": "passed",
                        "execution_time": execution_time,
                        "memory_used": result.get("memory_used"),
                        "output": actual_output
                    }
                else:
                    return {
                        "status": "failed",
                        "execution_time": execution_time,
                        "memory_used": result.get("memory_used"),
                        "output": actual_output,
                        "expected_output": expected_output
                    }
            else:
                return {
                    "status": result["status"],
                    "execution_time": execution_time,
                    "memory_used": result.get("memory_used"),
                    "error_message": result.get("error_message")
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    async def _execute_locally(
        self,
        code_file: str,
        input_file: str,
        language: str,
        time_limit: int
    ) -> Dict[str, Any]:
        """
        Ejecutar código localmente (modo desarrollo)
        """
        try:
            lang_config = self.supported_languages[language]
            
            # Preparar comando
            if language == "python":
                cmd = [lang_config["command"], code_file]
            elif language == "javascript":
                cmd = [lang_config["command"], code_file]
            elif language == "java":
                # Compilar primero
                class_name = os.path.splitext(os.path.basename(code_file))[0]
                compile_cmd = ["javac", code_file]
                subprocess.run(compile_cmd, check=True, capture_output=True)
                cmd = ["java", "-cp", os.path.dirname(code_file), class_name]
            
            # Ejecutar con timeout
            with open(input_file, 'r') as input_f:
                process = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        *cmd,
                        stdin=input_f,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    ),
                    timeout=time_limit / 1000.0  # Convertir a segundos
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    return {
                        "status": "success",
                        "output": stdout.decode('utf-8'),
                        "memory_used": 0  # No medimos memoria en modo local
                    }
                else:
                    return {
                        "status": "runtime_error",
                        "error_message": stderr.decode('utf-8')
                    }
                    
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "error_message": "Tiempo de ejecución excedido"
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    async def _execute_in_docker(
        self,
        code_file: str,
        input_file: str,
        language: str,
        time_limit: int,
        memory_limit: int
    ) -> Dict[str, Any]:
        """
        Ejecutar código en un contenedor Docker
        """
        if not self.docker_client:
            return {
                "status": "error",
                "error_message": "Docker no está disponible"
            }
            
        try:
            lang_config = self.supported_languages[language]
            container = None
            
            try:
                # Crear y ejecutar contenedor
                container = self.docker_client.containers.run(
                    image=lang_config["docker_image"],
                    command=f"{lang_config['command']} {os.path.basename(code_file)}",
                    volumes={
                        os.path.dirname(code_file): {'bind': '/code', 'mode': 'ro'},
                        os.path.dirname(input_file): {'bind': '/input', 'mode': 'ro'}
                    },
                    working_dir="/code",
                    detach=True,
                    mem_limit=f"{memory_limit}m",
                    network_disabled=True,
                    stdin_open=True,
                    tty=True
                )
                
                # Esperar resultado con timeout
                try:
                    container.wait(timeout=time_limit)
                    output = container.logs().decode('utf-8')
                    return {
                        "status": "success",
                        "output": output,
                        "memory_used": memory_limit  # Por ahora un valor fijo
                    }
                except Exception as e:
                    return {
                        "status": "timeout",
                        "error_message": "Tiempo de ejecución excedido"
                    }
                    
            finally:
                # Limpiar contenedor
                if container:
                    try:
                        container.remove(force=True)
                    except:
                        pass
                        
        except docker.errors.ImageNotFound:
            return {
                "status": "error",
                "error_message": f"Imagen Docker no encontrada: {lang_config['docker_image']}"
            }
        except docker.errors.APIError as e:
            return {
                "status": "error",
                "error_message": f"Error de Docker API: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Error ejecutando código: {str(e)}"
            } 