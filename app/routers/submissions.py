from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import asyncio
from datetime import datetime
from bson import ObjectId

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
    print("Recibida nueva petición de submission")
    
    # Verificar que el problema existe
    problem = await get_problem_by_id(submission.problem_id)
    if not problem:
        print(f"Problema no encontrado: {submission.problem_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problema no encontrado"
        )
    
    print(f"Problema encontrado: {problem.title}")
    
    db = get_db()
    
    # Crear la submisión
    submission_data = {
        "user_id": ObjectId(current_user.id),
        "problem_id": ObjectId(submission.problem_id),
        "code": submission.code,
        "language": submission.language,
        "status": "pending",
        "created_at": datetime.now()
    }
    
    try:
        result = await db.submissions.insert_one(submission_data)
        submission_id = str(result.inserted_id)
        print(f"Submission creada con ID: {submission_id}")
        
        # Ejecutar la evaluación en segundo plano
        print("Iniciando evaluación en segundo plano...")
        asyncio.create_task(evaluate_submission(submission_id))
        
        # Obtener la submisión creada
        created_submission = await get_submission_by_id(submission_id)
        print("Retornando submission al frontend")
        return created_submission
    except Exception as e:
        print(f"Error al crear submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear submission: {str(e)}"
        )

@router.get("/", response_model=List[SubmissionList])
async def get_submissions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obtener lista de submisiones del usuario actual
    """
    submissions = await get_submissions_by_user_id(str(current_user.id))
    return submissions[skip:skip + limit]

@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Obtener detalles de una submisión específica
    """
    submission = await get_submission_by_id(submission_id)
    
    if not submission or str(submission.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submisión no encontrada"
        )
    
    return submission

@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: str,
    submission_update: SubmissionUpdate,
    current_user: User = Depends(get_current_user_optional)
):
    """
    Actualizar una submisión (solo si está pendiente)
    """
    db = get_db()
    submission = await get_submission_by_id(submission_id)
    
    if not submission or str(submission.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submisión no encontrada"
        )
    
    if submission.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar una submisión que ya fue evaluada"
        )
    
    # Preparar datos de actualización
    update_data = {}
    if submission_update.code is not None:
        update_data["code"] = submission_update.code
    if submission_update.language is not None:
        update_data["language"] = submission_update.language
    
    # Actualizar en la base de datos
    await db.submissions.update_one(
        {"_id": ObjectId(submission_id)},
        {"$set": update_data}
    )
    
    # Obtener la submisión actualizada
    updated_submission = await get_submission_by_id(submission_id)
    return updated_submission

async def evaluate_submission(submission_id: str):
    """
    Función asíncrona para evaluar una submisión
    """
    try:
        submission = await get_submission_by_id(submission_id)
        if not submission:
            return
        
        db = get_db()
        
        # Log para depuración
        print("\n=== EVALUANDO SUBMISSION ===")
        print(f"ID: {submission_id}")
        print("Código a evaluar:")
        print("-------------------")
        print(submission.code)
        print("-------------------")
        
        # Actualizar estado a "running"
        await db.submissions.update_one(
            {"_id": ObjectId(submission_id)},
            {"$set": {"status": "running"}}
        )
        
        # Crear instancia del juez
        judge = CodeJudge()
        
        # Evaluar el código
        result = await judge.evaluate(
            code=submission.code,
            language=submission.language,
            problem_id=str(submission.problem_id)
        )
        
        # Log del resultado
        print("\n=== RESULTADO DE EVALUACIÓN ===")
        print(f"Status: {result['status']}")
        print(f"Score: {result.get('score', 0.0)}")
        if result.get('test_case_results'):
            print("\nResultados por caso de prueba:")
            for i, test_result in enumerate(result['test_case_results'], 1):
                print(f"\nCaso {i}:")
                print(f"Status: {test_result['status']}")
                if test_result.get('output'):
                    print(f"Output:\n{test_result['output']}")
                if test_result.get('expected_output'):
                    print(f"Expected:\n{test_result['expected_output']}")
        print("-------------------")
        
        # Actualizar la submisión con los resultados
        update_data = {
            "status": result["status"],
            "execution_time": result.get("execution_time"),
            "memory_used": result.get("memory_used"),
            "score": result.get("score", 0.0)
        }
        
        await db.submissions.update_one(
            {"_id": ObjectId(submission_id)},
            {"$set": update_data}
        )
        
    except Exception as e:
        # En caso de error, marcar como error y mostrar detalles
        print(f"\n=== ERROR EN EVALUACIÓN ===")
        print(f"Error evaluando submisión {submission_id}:")
        print(str(e))
        print("-------------------")
        
        db = get_db()
        await db.submissions.update_one(
            {"_id": ObjectId(submission_id)},
            {"$set": {"status": "error"}}
        ) 