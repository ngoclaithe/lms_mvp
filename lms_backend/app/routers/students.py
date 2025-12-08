from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User, Student
from app.models.academic import Enrollment, Grade, Class
from app.schemas.academic import Enrollment as EnrollmentSchema, StudentGradeView
from app.schemas.user import UserUpdate, User as UserSchema
from app.models.enums import UserRole

router = APIRouter(prefix="/students", tags=["students"])

@router.put("/me", response_model=UserSchema)
def update_student_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.STUDENT:
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

@router.get("/me/grades", response_model=List[StudentGradeView])
def read_student_grades(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    student = current_user.student
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Fetch enrollments with grades
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student.user_id).all()
    
    results = []
    for enrollment in enrollments:
        class_info = enrollment.class_
        course_info = class_info.course
        grades = enrollment.grades
        results.append(StudentGradeView(
            course_name=course_info.name,
            class_code=class_info.code,
            grades=grades
        ))
    return results

@router.get("/me/classes", response_model=List[dict]) # Simply return class info
def read_student_classes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    student = current_user.student
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student.user_id).all()
    classes = [item.class_ for item in enrollments]
    return classes
