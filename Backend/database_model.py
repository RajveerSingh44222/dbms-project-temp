from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, TIMESTAMP, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


# ---------------- STUDENT ----------------
class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    semester = Column(Integer, nullable=False)

    # NEW FIELDS (as per updated schema)
    branch = Column(String(50), nullable=False)
    cgpa = Column(Float, nullable=False)

    marks = relationship("Mark", back_populates="student", cascade="all, delete")
    attendance = relationship("Attendance", back_populates="student", cascade="all, delete")
    user = relationship("User", back_populates="student", uselist=False)


# ---------------- SUBJECT ----------------
class Subject(Base):
    __tablename__ = "subjects"

    subject_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_name = Column(String(100), nullable=False)
    credits = Column(Integer, nullable=False)

    # NEW FIELD
    code = Column(String(20), unique=True, nullable=True)

    marks = relationship("Mark", back_populates="subject", cascade="all, delete")
    attendance = relationship("Attendance", back_populates="subject", cascade="all, delete")


# ---------------- USER ----------------
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("admin", "student", name="user_roles"), nullable=False)

    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=True, unique=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    student = relationship("Student", back_populates="user")


# ---------------- MARKS ----------------
class Mark(Base):
    __tablename__ = "marks"
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_marks_student_subject"),
    )

    mark_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)

    internal_marks = Column(Integer, nullable=False)
    external_marks = Column(Integer, nullable=False)
    total_marks = Column(Integer, nullable=False)
    grade = Column(String(10), nullable=False)

    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject", back_populates="marks")


# ---------------- ATTENDANCE ----------------
class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_attendance_student_subject"),
    )

    attendance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    student_id = Column(Integer, ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.subject_id", ondelete="CASCADE"), nullable=False)

    total_classes = Column(Integer, nullable=False)

    # FIXED FIELD NAMES
    attended = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)

    student = relationship("Student", back_populates="attendance")
    subject = relationship("Subject", back_populates="attendance")