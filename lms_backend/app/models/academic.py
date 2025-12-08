from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, Time
from sqlalchemy.orm import relationship
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    students = relationship("Student", back_populates="department")
    lecturers = relationship("Lecturer", back_populates="department")
    courses = relationship("Course", back_populates="department")

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False) # e.g. CS101
    name = Column(String, nullable=False)
    credits = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))

    department = relationship("Department", back_populates="courses")
    classes = relationship("Class", back_populates="course")

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False) # e.g. CS101-2023-1
    course_id = Column(Integer, ForeignKey("courses.id"))
    lecturer_id = Column(Integer, ForeignKey("lecturers.user_id"))
    semester = Column(String) # e.g. "2023.1"
    max_students = Column(Integer, default=50)

    course = relationship("Course", back_populates="classes")
    lecturer = relationship("Lecturer", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="class_")
    schedules = relationship("Schedule", back_populates="class_")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    day_of_week = Column(String) # Monday, Tuesday...
    start_time = Column(Time)
    end_time = Column(Time)
    room = Column(String)

    class_ = relationship("Class", back_populates="schedules")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.user_id"))
    class_id = Column(Integer, ForeignKey("classes.id"))

    student = relationship("Student", back_populates="enrollments")
    class_ = relationship("Class", back_populates="enrollments")
    grades = relationship("Grade", back_populates="enrollment")

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    grade_type = Column(String) # 'midterm', 'final'
    score = Column(Float)
    weight = Column(Float, default=1.0)

    enrollment = relationship("Enrollment", back_populates="grades")
