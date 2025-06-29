from typing import Dict, List, Optional
from datetime import datetime
import uuid

from app.models.base import User, Problem, TestCase, Submission, TestCaseResult

class InMemoryStorage:
    """Almacenamiento en memoria para desarrollo"""
    
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.problems: Dict[int, Problem] = {}
        self.test_cases: Dict[int, TestCase] = {}
        self.submissions: Dict[int, Submission] = {}
        self.test_case_results: Dict[int, TestCaseResult] = {}
        
        # Contadores para IDs
        self.user_id_counter = 1
        self.problem_id_counter = 1
        self.test_case_id_counter = 1
        self.submission_id_counter = 1
        self.test_case_result_id_counter = 1
        
        # Inicializar con datos de ejemplo
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Inicializar con algunos problemas de ejemplo"""
        # Crear un usuario administrador por defecto
        admin_user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            hashed_password="",
            is_active=True,
            is_admin=True,
            created_at=datetime.now()
        )
        self.users[1] = admin_user
        self.user_id_counter = 2
        
        # Crear un problema de ejemplo
        problem = Problem(
            id=1,
            title="Suma de dos números",
            description="Escribe un programa que lea dos números enteros y muestre su suma.",
            difficulty="easy",
            time_limit=1000,
            memory_limit=256,
            created_at=datetime.now()
        )
        
        # Crear casos de prueba
        test_case_1 = TestCase(
            id=1,
            problem_id=1,
            input_data="5\n3",
            expected_output="8",
            is_sample=True,
            created_at=datetime.now()
        )
        
        test_case_2 = TestCase(
            id=2,
            problem_id=1,
            input_data="10\n20",
            expected_output="30",
            is_sample=False,
            created_at=datetime.now()
        )
        
        # Guardar en almacenamiento
        self.problems[1] = problem
        self.test_cases[1] = test_case_1
        self.test_cases[2] = test_case_2
        
        # Actualizar contadores
        self.problem_id_counter = 2
        self.test_case_id_counter = 3

# Instancia global del almacenamiento
storage = InMemoryStorage()

# Funciones de conveniencia para simular una base de datos
def get_db():
    """Simular dependencia de base de datos"""
    return storage

def get_user_by_username(username: str) -> Optional[User]:
    """Obtener usuario por username"""
    for user in storage.users.values():
        if user.username == username:
            return user
    return None

def get_user_by_email(email: str) -> Optional[User]:
    """Obtener usuario por email"""
    for user in storage.users.values():
        if user.email == email:
            return user
    return None

def get_problem_by_id(problem_id: int) -> Optional[Problem]:
    """Obtener problema por ID"""
    return storage.problems.get(problem_id)

def get_test_cases_by_problem_id(problem_id: int) -> List[TestCase]:
    """Obtener casos de prueba por ID del problema"""
    return [tc for tc in storage.test_cases.values() if tc.problem_id == problem_id]

def get_submissions_by_user_id(user_id: int) -> List[Submission]:
    """Obtener submisiones por ID del usuario"""
    return [s for s in storage.submissions.values() if s.user_id == user_id]

def get_submission_by_id(submission_id: int) -> Optional[Submission]:
    """Obtener submisión por ID"""
    return storage.submissions.get(submission_id) 