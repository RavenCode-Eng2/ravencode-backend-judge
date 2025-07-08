from typing import Dict, List, Optional
from datetime import datetime
from bson import ObjectId

from app.models.base import User, Problem, TestCase, Submission, TestCaseResult
from app.core.mongodb import get_database

def convert_object_ids(data: dict) -> dict:
    """Convierte todos los ObjectId a string en un diccionario"""
    if not data:
        return data
    result = {}
    for key, value in data.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, list):
            result[key] = [convert_object_ids(item) if isinstance(item, dict) else str(item) if isinstance(item, ObjectId) else item for item in value]
        elif isinstance(value, dict):
            result[key] = convert_object_ids(value)
        else:
            result[key] = value
    return result

# Funciones de conveniencia para MongoDB
def get_db():
    """Obtener instancia de la base de datos"""
    return get_database()

async def get_user_by_username(username: str) -> Optional[User]:
    """Obtener usuario por username"""
    db = get_database()
    user_data = await db.users.find_one({"username": username})
    if user_data:
        user_data = convert_object_ids(user_data)
        return User(**user_data)
    return None

async def get_user_by_email(email: str) -> Optional[User]:
    """Obtener usuario por email"""
    db = get_database()
    user_data = await db.users.find_one({"email": email})
    if user_data:
        user_data = convert_object_ids(user_data)
        return User(**user_data)
    return None

async def get_problem_by_id(problem_id: str) -> Optional[Problem]:
    """Obtener problema por ID"""
    db = get_database()
    problem_data = await db.problems.find_one({"_id": ObjectId(problem_id)})
    if problem_data:
        problem_data = convert_object_ids(problem_data)
        return Problem(**problem_data)
    return None

async def get_test_cases_by_problem_id(problem_id: str) -> List[TestCase]:
    """Obtener casos de prueba por ID del problema"""
    db = get_database()
    test_cases_cursor = db.test_cases.find({"problem_id": ObjectId(problem_id)})
    test_cases_data = await test_cases_cursor.to_list(length=None)
    test_cases_data = [convert_object_ids(tc) for tc in test_cases_data]
    return [TestCase(**tc) for tc in test_cases_data]

async def get_submissions_by_user_id(user_id: str) -> List[Submission]:
    """Obtener submisiones por ID del usuario"""
    db = get_database()
    submissions_cursor = db.submissions.find({"user_id": ObjectId(user_id)})
    submissions_data = await submissions_cursor.to_list(length=None)
    submissions_data = [convert_object_ids(s) for s in submissions_data]
    return [Submission(**s) for s in submissions_data]

async def get_submission_by_id(submission_id: str) -> Optional[Submission]:
    """Obtener submisión por ID"""
    db = get_database()
    submission_data = await db.submissions.find_one({"_id": ObjectId(submission_id)})
    if submission_data:
        submission_data = convert_object_ids(submission_data)
        return Submission(**submission_data)
    return None 