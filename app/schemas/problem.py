from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
from bson import ObjectId

def serialize_object_id(obj_id: ObjectId) -> str:
    return str(obj_id)

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return str(v)
        elif isinstance(v, str):
            return v
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> Any:
        return handler(str)

class TestCaseBase(BaseModel):
    input_data: str = Field(..., description="Datos de entrada para el caso de prueba")
    expected_output: str = Field(..., description="Salida esperada")
    is_sample: bool = Field(default=False, description="Si es un caso de ejemplo")

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseResponse(TestCaseBase):
    id: str = Field(alias="_id")
    problem_id: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }

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
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: Optional[datetime] = None
    test_cases: List[TestCaseResponse] = []

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    }

class ProblemList(BaseModel):
    id: str = Field(alias="_id")
    title: str
    difficulty: str
    time_limit: int
    memory_limit: int
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}
    } 