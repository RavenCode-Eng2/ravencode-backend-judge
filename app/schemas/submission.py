from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class SubmissionBase(BaseModel):
    problem_id: int = Field(..., description="ID del problema")
    code: str = Field(..., description="Código fuente del estudiante")
    language: str = Field(..., description="Lenguaje de programación")

class SubmissionCreate(SubmissionBase):
    pass

class SubmissionUpdate(BaseModel):
    code: Optional[str] = None
    language: Optional[str] = None

class TestCaseResultSchema(BaseModel):
    id: int
    test_case_id: int
    status: str
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None
    output: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubmissionResponse(SubmissionBase):
    id: int
    user_id: int
    status: str
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None
    score: float
    created_at: datetime
    test_case_results: List[TestCaseResultSchema] = []
    
    class Config:
        from_attributes = True

class SubmissionList(BaseModel):
    id: int
    problem_id: int
    language: str
    status: str
    score: float
    execution_time: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 