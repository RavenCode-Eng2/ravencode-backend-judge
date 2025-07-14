from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.models.base import PyObjectId, SubmissionStatus
from app.core.database import get_db, get_problem_by_id, get_submissions_by_user_email, get_submission_by_id

def serialize_object_id(obj_id: ObjectId) -> str:
    return str(obj_id)

class SubmissionBase(BaseModel):
    problem_id: PyObjectId = Field(..., description="ID del problema")
    code: str = Field(..., description="Código fuente del estudiante")
    language: str = Field(..., description="Lenguaje de programación")
    email: Optional[str] = Field(None, description="Email del usuario que hace la submission")

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(BaseModel):
    code: Optional[str] = None
    language: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class TestCaseResultSchema(BaseModel):
    id: PyObjectId = Field(alias="_id")
    test_case_id: PyObjectId
    status: str
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None
    output: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class SubmissionResponse(SubmissionBase):
    id: PyObjectId = Field(alias="_id")
    user_email: str  # Cambiado de user_id
    status: SubmissionStatus
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None
    score: Optional[float] = None
    created_at: datetime
    test_case_results: List[TestCaseResultSchema] = []

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class SubmissionList(BaseModel):
    id: PyObjectId = Field(alias="_id")
    problem_id: PyObjectId
    code: str = Field(..., description="Código fuente del estudiante")
    language: str
    status: SubmissionStatus
    score: Optional[float] = None
    execution_time: Optional[float] = None
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    } 