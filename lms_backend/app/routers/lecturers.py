from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User, Lecturer
from app.models.academic import Class, Enrollment, Grade
from app.schemas.academic import GradeCreate
from app.schemas.user import UserUpdate, User as UserSchema
from app.models.enums import UserRole

router = APIRouter(prefix="/lecturers", tags=["lecturers"])

@router.get("/me", response_model=UserSchema)
def read_lecturer_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.put("/me", response_model=UserSchema)
def update_lecturer_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.email:
        current_user.email = user_update.email
    if user_update.phone_number:
        current_user.phone_number = user_update.phone_number
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/my-classes", response_model=List[dict])
def read_lecturer_classes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    lecturer = current_user.lecturer
    if not lecturer:
        raise HTTPException(status_code=404, detail="Lecturer profile not found")

    return lecturer.classes

@router.get("/classes/{class_id}/students", response_model=List[dict])
def read_class_students(
    class_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if lecturer owns class
    class_obj = db.query(Class).filter(Class.id == class_id, Class.lecturer_id == current_user.id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found or not taught by you")
    
    enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
    students = [e.student.user for e in enrollments] # Return user info
    return students

@router.post("/grades", response_model=dict)
def add_or_update_grade(
    grade_data: GradeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if enrollment belongs to a class taught by lecturer
    enrollment = db.query(Enrollment).filter(Enrollment.id == grade_data.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    class_obj = enrollment.class_
    if class_obj.lecturer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to grade this class")

    # Add grade
    grade = Grade(
        enrollment_id=grade_data.enrollment_id,
        grade_type=grade_data.grade_type,
        score=grade_data.score,
        weight=grade_data.weight
    )
    db.add(grade)
    db.commit()
    return {"message": "Grade added successfully"}
