from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.core.database import get_db, get_problem_by_id, get_test_cases_by_problem_id
from app.models.base import User, Problem, TestCase
from app.schemas.problem import (
    ProblemCreate,
    ProblemResponse,
    ProblemList,
    ProblemUpdate,
    TestCaseCreate,
    TestCaseResponse
)
from app.core.auth import get_current_user_optional

router = APIRouter()

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
    storage = get_db()
    problems = list(storage.problems.values())
    
    if difficulty:
        problems = [p for p in problems if p.difficulty == difficulty]
    
    return problems[skip:skip + limit]

@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: int,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obtener detalles de un problema específico
    """
    problem = get_problem_by_id(problem_id)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    # Agregar casos de prueba al problema
    test_cases = get_test_cases_by_problem_id(problem_id)
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
    
    storage = get_db()
    
    # Crear el problema
    problem_id = storage.problem_id_counter
    storage.problem_id_counter += 1
    
    db_problem = Problem(
        id=problem_id,
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        time_limit=problem.time_limit,
        memory_limit=problem.memory_limit,
        created_at=datetime.now()
    )
    
    storage.problems[problem_id] = db_problem
    
    # Crear los casos de prueba
    for test_case in problem.test_cases:
        test_case_id = storage.test_case_id_counter
        storage.test_case_id_counter += 1
        
        db_test_case = TestCase(
            id=test_case_id,
            problem_id=problem_id,
            input_data=test_case.input_data,
            expected_output=test_case.expected_output,
            is_sample=test_case.is_sample,
            created_at=datetime.now()
        )
        storage.test_cases[test_case_id] = db_test_case
    
    # Agregar casos de prueba al problema para la respuesta
    db_problem.test_cases = get_test_cases_by_problem_id(problem_id)
    
    return db_problem

@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: int,
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
    
    storage = get_db()
    problem = get_problem_by_id(problem_id)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    # Actualizar campos
    if problem_update.title is not None:
        problem.title = problem_update.title
    if problem_update.description is not None:
        problem.description = problem_update.description
    if problem_update.difficulty is not None:
        problem.difficulty = problem_update.difficulty
    if problem_update.time_limit is not None:
        problem.time_limit = problem_update.time_limit
    if problem_update.memory_limit is not None:
        problem.memory_limit = problem_update.memory_limit
    
    storage.problems[problem_id] = problem
    
    # Agregar casos de prueba al problema para la respuesta
    problem.test_cases = get_test_cases_by_problem_id(problem_id)
    
    return problem

@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: int,
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
    
    storage = get_db()
    problem = get_problem_by_id(problem_id)
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    # Eliminar el problema y sus casos de prueba
    del storage.problems[problem_id]
    
    # Eliminar casos de prueba asociados
    test_cases_to_delete = [tc_id for tc_id, tc in storage.test_cases.items() if tc.problem_id == problem_id]
    for tc_id in test_cases_to_delete:
        del storage.test_cases[tc_id]
    
    return None

@router.post("/{problem_id}/test-cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def add_test_case(
    problem_id: int,
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
    problem = get_problem_by_id(problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    storage = get_db()
    
    # Crear el caso de prueba
    test_case_id = storage.test_case_id_counter
    storage.test_case_id_counter += 1
    
    db_test_case = TestCase(
        id=test_case_id,
        problem_id=problem_id,
        input_data=test_case.input_data,
        expected_output=test_case.expected_output,
        is_sample=test_case.is_sample,
        created_at=datetime.now()
    )
    
    storage.test_cases[test_case_id] = db_test_case
    
    return db_test_case 