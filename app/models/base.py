from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"
    ERROR = "error"

class TestCaseResultStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    TIMEOUT = "timeout"

class User(BaseModel):
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime

class Problem(BaseModel):
    id: int
    title: str
    description: str
    difficulty: Difficulty
    time_limit: int = 1000  # milisegundos
    memory_limit: int = 256  # MB
    created_at: datetime
    test_cases: List['TestCase'] = []

class TestCase(BaseModel):
    id: int
    problem_id: int
    input_data: str
    expected_output: str
    is_sample: bool = False
    created_at: datetime

class Submission(BaseModel):
    id: int
    user_id: int
    problem_id: int
    code: str
    language: str
    status: SubmissionStatus = SubmissionStatus.PENDING
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None
    score: float = 0.0
    created_at: datetime
    test_case_results: List['TestCaseResult'] = []

class TestCaseResult(BaseModel):
    id: int
    submission_id: int
    test_case_id: int
    status: TestCaseResultStatus
    execution_time: Optional[float] = None
    memory_used: Optional[float] = None
    output: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

# Actualizar referencias circulares
Problem.model_rebuild()
Submission.model_rebuild() 