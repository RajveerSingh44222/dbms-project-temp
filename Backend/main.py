from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from database_model import Base, User, Student, Subject, Mark, Attendance
from models import (
    LoginRequest, LoginResponse,
    StudentCreate, StudentResponse,
    SubjectCreate, SubjectResponse,
    MarkCreate, MarkUpdate, MarkResponse,
    AttendanceCreate, AttendanceResponse,
    StudentPerformanceRow
)

app = FastAPI(
    title="Academic Portal API",
    version="2.0.0"
)

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


# ---------------- DB ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- UTILS ----------------

def calculate_total(internal: int, external: int) -> int:
    return internal + external


def calculate_grade(total: int) -> str:
    if total >= 120:
        return "A+"
    elif total >= 100:
        return "A"
    elif total >= 85:
        return "B+"
    elif total >= 70:
        return "B"
    elif total >= 55:
        return "C"
    return "F"


def calculate_attendance_percentage(attended: int, total: int) -> float:
    if total == 0:
        return 0
    return round((attended / total) * 100, 2)


# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"message": "Academic Portal API Running 🚀"}


# ---------------- AUTH ----------------
@app.post("/auth/login", response_model=LoginResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == data.username,
        User.password == data.password,
        User.role == data.role
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user


# ---------------- STUDENTS ----------------
@app.get("/students", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@app.post("/students", response_model=StudentResponse)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    if db.query(Student).filter(Student.student_id == data.student_id).first():
        raise HTTPException(400, "Student already exists")

    student = Student(**data.model_dump())
    db.add(student)

    # auto create login
    user = User(
        username=data.username,
        password=data.password,
        role="student",
        student_id=data.student_id
    )
    db.add(user)

    db.commit()
    db.refresh(student)
    return student


# ---------------- SUBJECTS ----------------
@app.get("/subjects", response_model=list[SubjectResponse])
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()


@app.post("/subjects", response_model=SubjectResponse)
def create_subject(data: SubjectCreate, db: Session = Depends(get_db)):
    subject = Subject(**data.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


# ---------------- MARKS ----------------
@app.get("/marks", response_model=list[MarkResponse])
def get_marks(student_id: int | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(Mark)
    if student_id:
        query = query.filter(Mark.student_id == student_id)
    return query.all()


@app.post("/marks", response_model=MarkResponse)
def create_mark(data: MarkCreate, db: Session = Depends(get_db)):
    total = calculate_total(data.internal_marks, data.external_marks)
    grade = calculate_grade(total)

    mark = Mark(
        student_id=data.student_id,
        subject_id=data.subject_id,
        internal_marks=data.internal_marks,
        external_marks=data.external_marks,
        total_marks=total,
        grade=grade
    )

    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark


@app.put("/marks/{mark_id}", response_model=MarkResponse)
def update_mark(mark_id: int, data: MarkUpdate, db: Session = Depends(get_db)):
    mark = db.query(Mark).filter(Mark.mark_id == mark_id).first()
    if not mark:
        raise HTTPException(404, "Mark not found")

    mark.internal_marks = data.internal_marks
    mark.external_marks = data.external_marks

    mark.total_marks = calculate_total(data.internal_marks, data.external_marks)
    mark.grade = calculate_grade(mark.total_marks)

    db.commit()
    db.refresh(mark)
    return mark


# ---------------- ATTENDANCE ----------------
@app.get("/attendance", response_model=list[AttendanceResponse])
def get_attendance(student_id: int | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(Attendance)
    if student_id:
        query = query.filter(Attendance.student_id == student_id)
    return query.all()


@app.post("/attendance", response_model=AttendanceResponse)
def create_attendance(data: AttendanceCreate, db: Session = Depends(get_db)):
    percentage = calculate_attendance_percentage(
        data.attended,
        data.total_classes
    )

    attendance = Attendance(
        student_id=data.student_id,
        subject_id=data.subject_id,
        total_classes=data.total_classes,
        attended=data.attended,
        percentage=percentage
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


# ---------------- STUDENT PERFORMANCE ----------------
@app.get("/student/{student_id}/performance", response_model=list[StudentPerformanceRow])
def get_student_performance(student_id: int, db: Session = Depends(get_db)):

    marks = db.query(Mark).filter(Mark.student_id == student_id).all()
    attendance = db.query(Attendance).filter(Attendance.student_id == student_id).all()

    attendance_map = {a.subject_id: a.percentage for a in attendance}
    subjects = {s.subject_id: s.subject_name for s in db.query(Subject).all()}

    result = []
    for m in marks:
        result.append(
            StudentPerformanceRow(
                subject_id=m.subject_id,
                subject_name=subjects.get(m.subject_id),
                total_marks=m.total_marks,
                grade=m.grade,
                attendance_percentage=attendance_map.get(m.subject_id)
            )
        )

    return result