from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User, Lecturer, Student
from app.models.academic import Department, Course
from app.models.audit_log import AuditLog
from app.schemas.academic import CourseCreate, Course as CourseSchema
from app.schemas.user import UserCreate, User as UserSchema
from app.models.enums import UserRole
from app.crud.user import create_user
from app.utils.audit import log_action

router = APIRouter(prefix="/deans", tags=["deans"])

def check_dean_role(user: User):
    if user.role != UserRole.DEAN:
        raise HTTPException(status_code=403, detail="Not authorized. Dean access required.")

@router.post("/courses", response_model=CourseSchema)
def create_course(
    course: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    log_action(db, user_id=current_user.id, action="CREATE_COURSE", details=f"Created course {db_course.code}")
    return db_course

@router.get("/courses", response_model=List[CourseSchema])
def list_courses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    return db.query(Course).all()

# --- Lecturer Management ---
@router.post("/lecturers", response_model=UserSchema)
def create_lecturer(
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    if user_in.role != UserRole.LECTURER:
         raise HTTPException(status_code=400, detail="Role must be lecturer")
         
    # Check existing
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
        
    user = create_user(db, user_in)
    # Create Lecturer profile
    lecturer_profile = Lecturer(user_id=user.id, lecturer_code=f"LEC{user.id}") # Auto-gen code
    db.add(lecturer_profile)
    db.commit()
    
    log_action(db, user_id=current_user.id, action="CREATE_LECTURER", details=f"Created lecturer {user.username}")
    return user

@router.get("/lecturers", response_model=List[UserSchema])
def list_lecturers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    return db.query(User).filter(User.role == UserRole.LECTURER).all()

# --- Student Management ---
@router.post("/students", response_model=UserSchema)
def create_student(
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    if user_in.role != UserRole.STUDENT:
         raise HTTPException(status_code=400, detail="Role must be student")
         
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
        
    user = create_user(db, user_in)
    # Create Student profile
    student_profile = Student(user_id=user.id, student_code=f"STU{user.id}") # Auto-gen code
    db.add(student_profile)
    db.commit()
    
    log_action(db, user_id=current_user.id, action="CREATE_STUDENT", details=f"Created student {user.username}")
    return user

@router.get("/students", response_model=List[UserSchema])
def list_students(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    return db.query(User).filter(User.role == UserRole.STUDENT).all()

# --- Audit Logs ---
@router.get("/audit-logs", response_model=List[dict])
def view_audit_logs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    return [{"id": l.id, "action": l.action, "details": l.details, "timestamp": l.timestamp, "user": l.user.username} for l in logs]
