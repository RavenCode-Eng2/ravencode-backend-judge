from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import asyncio
from datetime import datetime

from app.core.database import get_db, get_problem_by_id, get_submissions_by_user_id, get_submission_by_id
from app.core.judge import CodeJudge
from app.models.base import User, Submission
from app.schemas.submission import (
    SubmissionCreate, 
    SubmissionResponse, 
    SubmissionList,
    SubmissionUpdate
)
from app.core.auth import get_current_user_optional

router = APIRouter()

@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission: SubmissionCreate,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Crear una nueva submisión de código y evaluarla automáticamente
    """
    # Verificar que el problema existe
    problem = get_problem_by_id(submission.problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    # Obtener almacenamiento
    storage = get_db()
    
    # Crear la submisión
    submission_id = storage.submission_id_counter
    storage.submission_id_counter += 1
    
    db_submission = Submission(
        id=submission_id,
        user_id=current_user.id,
        problem_id=submission.problem_id,
        code=submission.code,
        language=submission.language,
        status="pending",
        created_at=datetime.now()
    )
    
    storage.submissions[submission_id] = db_submission
    
    # Ejecutar la evaluación en segundo plano
    asyncio.create_task(evaluate_submission(submission_id))
    
    return db_submission

@router.get("/", response_model=List[SubmissionList])
async def get_submissions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obtener lista de submisiones del usuario actual
    """
    submissions = get_submissions_by_user_id(current_user.id)
    return submissions[skip:skip + limit]

@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obtener detalles de una submisión específica
    """
    submission = get_submission_by_id(submission_id)
    
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submisión no encontrada"
        )
    
    return submission

@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: int,
    submission_update: SubmissionUpdate,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Actualizar una submisión (solo si está pendiente)
    """
    storage = get_db()
    submission = get_submission_by_id(submission_id)
    
    if not submission or submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submisión no encontrada"
        )
    
    if submission.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una submisión que ya fue evaluada"
        )
    
    # Actualizar campos
    if submission_update.code is not None:
        submission.code = submission_update.code
    if submission_update.language is not None:
        submission.language = submission_update.language
    
    # Actualizar en almacenamiento
    storage.submissions[submission_id] = submission
    
    return submission

async def evaluate_submission(submission_id: int):
    """
    Función asíncrona para evaluar una submisión
    """
    try:
        storage = get_db()
        submission = get_submission_by_id(submission_id)
        if not submission:
            return
        
        # Actualizar estado a "running"
        submission.status = "running"
        storage.submissions[submission_id] = submission
        
        # Crear instancia del juez
        judge = CodeJudge()
        
        # Evaluar el código
        result = await judge.evaluate(
            code=submission.code,
            language=submission.language,
            problem_id=submission.problem_id
        )
        
        # Actualizar la submisión con los resultados
        submission.status = result["status"]
        submission.execution_time = result.get("execution_time")
        submission.memory_used = result.get("memory_used")
        submission.score = result.get("score", 0.0)
        
        storage.submissions[submission_id] = submission
        
    except Exception as e:
        # En caso de error, marcar como error
        storage = get_db()
        submission = get_submission_by_id(submission_id)
        if submission:
            submission.status = "error"
            storage.submissions[submission_id] = submission
        print(f"Error evaluando submisión {submission_id}: {str(e)}") 