from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.base import User
from app.core.auth import get_current_user_optional
from app.core.database import get_db, get_problem_by_id, get_test_cases_by_problem_id, convert_object_ids
from app.schemas.problem import (
    ProblemCreate,
    ProblemUpdate,
    ProblemResponse,
    ProblemList,
    TestCaseCreate,
    TestCaseResponse
)

router = APIRouter(
    tags=["problems"]
)

@router.get("/", response_model=List[ProblemList])
async def get_problems(
    skip: int = 0,
    limit: int = 100,
    difficulty: str = None,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obtener lista de problemas disponibles
    """
    db = get_db()
    
    # Construir filtro
    filter_query = {}
    if difficulty:
        filter_query["difficulty"] = difficulty
    
    # Obtener problemas
    problems_cursor = db.problems.find(filter_query).skip(skip).limit(limit)
    problems_data = await problems_cursor.to_list(length=limit)
    problems_data = [convert_object_ids(p) for p in problems_data]
    
    return [ProblemList(**problem) for problem in problems_data]

@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: str,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obtener detalles de un problema específico
    """
    problem = await get_problem_by_id(problem_id)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    # Agregar casos de prueba al problema
    test_cases = await get_test_cases_by_problem_id(problem_id)
    problem.test_cases = test_cases
    
    return problem

@router.post("/", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem: ProblemCreate,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Crear un nuevo problema (solo administradores)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear problemas"
        )
    
    db = get_db()
    
    # Crear el problema
    problem_data = {
        "title": problem.title,
        "description": problem.description,
        "difficulty": problem.difficulty,
        "time_limit": problem.time_limit,
        "memory_limit": problem.memory_limit,
        "created_at": datetime.now()
    }
    
    result = await db.problems.insert_one(problem_data)
    problem_id = str(result.inserted_id)
    problem_data["_id"] = result.inserted_id
    
    # Crear los casos de prueba
    test_cases = []
    for test_case in problem.test_cases:
        test_case_data = {
            "problem_id": ObjectId(problem_id),
            "input_data": test_case.input_data,
            "expected_output": test_case.expected_output,
            "is_sample": test_case.is_sample,
            "created_at": datetime.now()
        }
        test_case_result = await db.test_cases.insert_one(test_case_data)
        test_case_data["_id"] = test_case_result.inserted_id
        test_cases.append(test_case_data)
    
    # Convertir todos los ObjectId a string
    problem_data = convert_object_ids(problem_data)
    test_cases = [convert_object_ids(tc) for tc in test_cases]
    
    # Crear la respuesta
    response_data = {**problem_data, "test_cases": test_cases}
    return ProblemResponse(**response_data)

@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: str,
    problem_update: ProblemUpdate,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Actualizar un problema (solo administradores)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden actualizar problemas"
        )
    
    problem = await get_problem_by_id(problem_id)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    # Preparar datos de actualización
    update_data = {}
    if problem_update.title is not None:
        update_data["title"] = problem_update.title
    if problem_update.description is not None:
        update_data["description"] = problem_update.description
    if problem_update.difficulty is not None:
        update_data["difficulty"] = problem_update.difficulty
    if problem_update.time_limit is not None:
        update_data["time_limit"] = problem_update.time_limit
    if problem_update.memory_limit is not None:
        update_data["memory_limit"] = problem_update.memory_limit
    
    # Actualizar en la base de datos
    db = get_db()
    await db.problems.update_one(
        {"_id": ObjectId(problem_id)},
        {"$set": update_data}
    )
    
    # Obtener el problema actualizado
    updated_problem = await get_problem_by_id(problem_id)
    updated_problem.test_cases = await get_test_cases_by_problem_id(problem_id)
    
    return updated_problem

@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: str,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Eliminar un problema (solo administradores)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden eliminar problemas"
        )
    
    problem = await get_problem_by_id(problem_id)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    db = get_db()
    
    # Eliminar el problema
    await db.problems.delete_one({"_id": ObjectId(problem_id)})
    
    # Eliminar casos de prueba asociados
    await db.test_cases.delete_many({"problem_id": ObjectId(problem_id)})
    
    return None

@router.post("/{problem_id}/test-cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def add_test_case(
    problem_id: str,
    test_case: TestCaseCreate,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Agregar un caso de prueba a un problema (solo administradores)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden agregar casos de prueba"
        )
    
    # Verificar que el problema existe
    problem = await get_problem_by_id(problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    db = get_db()
    
    # Crear el caso de prueba
    test_case_data = {
        "problem_id": ObjectId(problem_id),
        "input_data": test_case.input_data,
        "expected_output": test_case.expected_output,
        "is_sample": test_case.is_sample,
        "created_at": datetime.now()
    }
    
    result = await db.test_cases.insert_one(test_case_data)
    test_case_data["_id"] = result.inserted_id
    
    return TestCaseResponse(**test_case_data) 