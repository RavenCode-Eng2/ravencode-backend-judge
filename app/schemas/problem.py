from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TestCaseBase(BaseModel):
    input_data: str = Field(..., description="Datos de entrada para el caso de prueba")
    expected_output: str = Field(..., description="Salida esperada")
    is_sample: bool = Field(default=False, description="Si es un caso de ejemplo")

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseResponse(TestCaseBase):
    id: int
    problem_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProblemBase(BaseModel):
    title: str = Field(..., description="Título del problema")
    description: str = Field(..., description="Descripción del problema")
    difficulty: str = Field(..., description="Dificultad: easy, medium, hard")
    time_limit: int = Field(default=1000, description="Límite de tiempo en milisegundos")
    memory_limit: int = Field(default=256, description="Límite de memoria en MB")

class ProblemCreate(ProblemBase):
    test_cases: List[TestCaseCreate] = []

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None

class ProblemResponse(ProblemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    test_cases: List[TestCaseResponse] = []
    
    class Config:
        from_attributes = True

class ProblemList(BaseModel):
    id: int
    title: str
    difficulty: str
    time_limit: int
    memory_limit: int
    created_at: datetime
    
    class Config:
        from_attributes = True 