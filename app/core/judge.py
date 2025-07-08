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
                "command": "python" if os.name == "nt" else "python3",  # Use python on Windows, python3 on Unix
                "docker_image": "python:3.10-slim"
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
            print(f"\nIniciando evaluación para problema {problem_id}")
            
            # Obtener el problema y sus casos de prueba
            problem = await get_problem_by_id(problem_id)
            if not problem:
                print("❌ Problema no encontrado")
                return {
                    "status": "error",
                    "message": "Problema no encontrado"
                }

            test_cases = await get_test_cases_by_problem_id(problem_id)
            if not test_cases:
                print("❌ No hay casos de prueba para este problema")
                return {
                    "status": "error",
                    "message": "No hay casos de prueba para este problema"
                }
            
            print(f"✅ Encontrados {len(test_cases)} casos de prueba")
            
            # Verificar que el lenguaje es soportado
            if language not in self.supported_languages:
                print(f"❌ Lenguaje {language} no soportado")
                return {
                    "status": "error",
                    "message": f"Lenguaje {language} no soportado"
                }
            
            print(f"✅ Lenguaje {language} soportado")
            
            total_test_cases = len(test_cases)
            passed_test_cases = 0
            total_execution_time = 0
            total_memory_used = 0
            test_case_results = []
            
            # Evaluar cada caso de prueba
            print("\nEjecutando casos de prueba...")
            for i, test_case in enumerate(test_cases, 1):
                print(f"\nCaso de prueba {i}/{total_test_cases}")
                result = await self._run_test_case(
                    code=code,
                    language=language,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output,
                    time_limit=problem.time_limit,
                    memory_limit=problem.memory_limit
                )
                
                test_case_results.append(result)
                
                if result["status"] == "accepted":  # Verificar estado "accepted"
                    passed_test_cases += 1
                    print(f"✅ Caso {i} pasado")
                else:
                    print(f"❌ Caso {i} fallido")
                
                if result.get("execution_time"):
                    total_execution_time += result["execution_time"]
                
                if result.get("memory_used"):
                    total_memory_used = max(total_memory_used, result["memory_used"])
            
            # Calcular puntuación y estado final
            score = (passed_test_cases / total_test_cases) * 100 if total_test_cases > 0 else 0
            
            if passed_test_cases == total_test_cases:
                final_status = "accepted"
                print("\n✅ Todos los casos pasaron!")
            else:
                final_status = "wrong_answer"
                if passed_test_cases > 0:
                    print(f"\n⚠️ Pasaron {passed_test_cases} de {total_test_cases} casos")
                else:
                    print("\n❌ Ningún caso pasó")
            
            print(f"Score final: {score}%")
            
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
            print(f"❌ Error en evaluate: {str(e)}")
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
        code_file = None
        input_file = None
        
        try:
            print("\n=== EJECUTANDO CASO DE PRUEBA ===")
            print("Código a ejecutar:")
            print("-------------------")
            print(code)
            print("-------------------")
            print("Input data:")
            print("-------------------")
            print(input_data)
            print("-------------------")
            print("Output esperado:")
            print("-------------------")
            print(expected_output)
            print("-------------------")
            
            # Crear archivo temporal con el código
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix=self.supported_languages[language]["extension"],
                    delete=False,
                    encoding='utf-8'
                ) as f:
                    f.write(code)
                    code_file = f.name
                    print(f"Código guardado en archivo temporal: {code_file}")
                
                # Asegurar permisos de lectura
                os.chmod(code_file, 0o644)
                
                # Crear archivo temporal con la entrada
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    delete=False,
                    encoding='utf-8'
                ) as f:
                    f.write(input_data)
                    input_file = f.name
                    print(f"Input guardado en archivo temporal: {input_file}")
                
                # Asegurar permisos de lectura
                os.chmod(input_file, 0o644)
            except Exception as e:
                print(f"Error al crear archivos temporales: {str(e)}")
                raise
            
            # Ejecutar el código
            start_time = time.time()
            
            if settings.DEBUG:
                print("\nEjecutando en modo DEBUG (local)")
                # Modo desarrollo: ejecutar directamente
                result = await self._execute_locally(
                    code_file=code_file,
                    input_file=input_file,
                    language=language,
                    time_limit=time_limit
                )
            else:
                print("\nEjecutando en Docker")
                # Modo producción: ejecutar en Docker
                result = await self._execute_in_docker(
                    code_file=code_file,
                    input_file=input_file,
                    language=language,
                    time_limit=time_limit,
                    memory_limit=memory_limit
                )
            
            execution_time = int((time.time() - start_time) * 1000)  # Convertir a milisegundos
            
            print("\n=== RESULTADO DE EJECUCIÓN ===")
            print(f"Status: {result['status']}")
            print("Output obtenido:")
            print("-------------------")
            print(result.get('output', ''))
            print("-------------------")
            
            if result["status"] == "success":
                actual_output = result["output"].strip()
                expected_output = expected_output.strip()
                
                if actual_output == expected_output:
                    print("✅ Output coincide con el esperado")
                    return {
                        "status": "accepted",  # Cambiado de "passed" a "accepted"
                        "execution_time": execution_time,
                        "memory_used": result.get("memory_used"),
                        "output": actual_output
                    }
                else:
                    print("❌ Output NO coincide con el esperado")
                    return {
                        "status": "wrong_answer",  # Cambiado de "failed" a "wrong_answer"
                        "execution_time": execution_time,
                        "memory_used": result.get("memory_used"),
                        "output": actual_output,
                        "expected_output": expected_output
                    }
            else:
                error_status = result["status"]
                if error_status == "timeout":
                    error_status = "time_limit_exceeded"
                elif error_status not in ["runtime_error", "compilation_error"]:
                    error_status = "error"
                    
                print(f"❌ Error en ejecución: {result.get('error_message', 'Unknown error')}")
                return {
                    "status": error_status,
                    "execution_time": execution_time,
                    "memory_used": result.get("memory_used"),
                    "error_message": result.get("error_message")
                }
                
        except Exception as e:
            print(f"\n❌ Error ejecutando caso de prueba: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            }
        finally:
            # Limpiar archivos temporales
            try:
                if code_file and os.path.exists(code_file):
                    os.chmod(code_file, 0o666)  # Dar permisos de lectura/escritura
                    os.unlink(code_file)
                if input_file and os.path.exists(input_file):
                    os.chmod(input_file, 0o666)  # Dar permisos de lectura/escritura
                    os.unlink(input_file)
            except Exception as e:
                print(f"Error al limpiar archivos temporales en _run_test_case: {str(e)}")
    
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
            cmd = None
            
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
            
            if cmd is None:
                return {
                    "status": "error",
                    "error_message": f"Lenguaje no soportado: {language}"
                }
            
            print(f"Ejecutando comando: {' '.join(cmd)}")
            
            try:
                # Asegurarse de que los archivos existen y tienen los permisos correctos
                if not os.path.exists(code_file):
                    raise FileNotFoundError(f"Archivo de código no encontrado: {code_file}")
                if not os.path.exists(input_file):
                    raise FileNotFoundError(f"Archivo de entrada no encontrado: {input_file}")
                
                # Leer el contenido del archivo de entrada como texto
                with open(input_file, 'r', encoding='utf-8') as input_f:
                    input_data = input_f.read()
                
                # Ejecutar el proceso con timeout
                process = subprocess.run(
                    cmd,
                    input=input_data,
                    capture_output=True,
                    timeout=time_limit / 1000.0,  # Convertir a segundos
                    text=True,  # Automáticamente decodifica la salida como texto
                    encoding='utf-8'  # Especificar codificación
                )
                
                if process.returncode == 0:
                    output = process.stdout.strip()
                    print(f"Salida del programa: '{output}'")
                    return {
                        "status": "success",
                        "output": output,
                        "memory_used": 0  # No medimos memoria en modo local
                    }
                else:
                    error_msg = process.stderr.strip()
                    print(f"Error del programa: {error_msg}")
                    return {
                        "status": "runtime_error",
                        "error_message": error_msg
                    }
                    
            except subprocess.TimeoutExpired:
                print("Tiempo de ejecución excedido")
                return {
                    "status": "timeout",
                    "error_message": "Tiempo de ejecución excedido"
                }
            except Exception as e:
                print(f"Error al ejecutar el proceso: {str(e)}")
                return {
                    "status": "error",
                    "error_message": f"Error al ejecutar el código: {str(e)}"
                }
            finally:
                # Limpiar archivos temporales
                try:
                    if os.path.exists(code_file):
                        os.chmod(code_file, 0o666)  # Dar permisos de lectura/escritura
                        os.unlink(code_file)
                    if os.path.exists(input_file):
                        os.chmod(input_file, 0o666)  # Dar permisos de lectura/escritura
                        os.unlink(input_file)
                except Exception as e:
                    print(f"Error al limpiar archivos temporales: {str(e)}")
                    
        except Exception as e:
            print(f"Error general: {str(e)}")
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