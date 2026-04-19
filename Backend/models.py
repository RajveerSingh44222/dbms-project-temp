from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional


# ---------------- AUTH ----------------

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str


class LoginResponse(BaseModel):
    username: str
    role: str
    student_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------- STUDENTS ----------------

class StudentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    semester: int = Field(..., ge=1, le=8)
    branch: str = Field(..., min_length=2, max_length=50)
    cgpa: float = Field(..., ge=0, le=10)


class StudentCreate(StudentBase):
    student_id: int
    username: str
    password: str


class StudentResponse(StudentBase):
    student_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------- SUBJECTS ----------------

class SubjectBase(BaseModel):
    subject_name: str = Field(..., min_length=2, max_length=100)
    credits: int = Field(..., ge=1, le=10)
    code: Optional[str] = None


class SubjectCreate(SubjectBase):
    pass


class SubjectResponse(SubjectBase):
    subject_id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------- MARKS ----------------

class MarkBase(BaseModel):
    student_id: int
    subject_id: int
    internal_marks: int = Field(..., ge=0, le=50)
    external_marks: int = Field(..., ge=0, le=100)


class MarkCreate(MarkBase):
    pass


class MarkUpdate(BaseModel):
    internal_marks: int = Field(..., ge=0, le=50)
    external_marks: int = Field(..., ge=0, le=100)


class MarkResponse(BaseModel):
    mark_id: int
    student_id: int
    subject_id: int
    internal_marks: int
    external_marks: int
    total_marks: int
    grade: str

    model_config = ConfigDict(from_attributes=True)


# ---------------- ATTENDANCE ----------------

class AttendanceBase(BaseModel):
    student_id: int
    subject_id: int
    total_classes: int = Field(..., ge=1)
    attended: int = Field(..., ge=0)


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(BaseModel):
    attendance_id: int
    student_id: int
    subject_id: int
    total_classes: int
    attended: int
    percentage: float

    model_config = ConfigDict(from_attributes=True)


# ---------------- STUDENT PERFORMANCE ----------------

class StudentPerformanceRow(BaseModel):
    subject_id: int
    subject_name: str
    total_marks: int
    grade: str
    attendance_percentage: Optional[float] = None