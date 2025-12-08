from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User, Student
from app.models.academic import Enrollment, Grade, Class
from app.schemas.academic import Enrollment as EnrollmentSchema, StudentGradeView, Class as ClassSchema, MobileGradeResponse, MobileClassResponse
from app.schemas.user import UserUpdate, User as UserSchema
from app.models.enums import UserRole

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/me", response_model=UserSchema)
def read_student_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    department_name = None
    if current_user.student and current_user.student.department:
        department_name = current_user.student.department.name
    
    user_dict = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "role": current_user.role,
        "student_code": current_user.student.student_code if current_user.student else None,
        "department_name": department_name,
        "is_active": True
    }
    return user_dict

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

@router.get("/my-grades", response_model=List[MobileGradeResponse])
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
        
        display_grade = None
        for g in enrollment.grades:
            if g.grade_type == 'final':
                display_grade = g.score
                break
        if display_grade is None and enrollment.grades:
             display_grade = enrollment.grades[0].score

        grade_details = [
            {
                'grade_type': g.grade_type,
                'score': g.score,
                'weight': g.weight
            }
            for g in enrollment.grades
        ]

        results.append(MobileGradeResponse(
            course_name=course_info.name,
            credits=course_info.credits,
            grade=display_grade,
            details=grade_details
        ))
    return results

@router.get("/my-classes", response_model=List[MobileClassResponse])
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
    results = []
    for item in enrollments:
        cls = item.class_
        results.append(MobileClassResponse(
            id=cls.id,
            course_name=cls.course.name,
            lecturer_name=cls.lecturer.user.full_name if cls.lecturer else "Unknown",
            room="Online", # Placeholder
            day_of_week=cls.day_of_week,
            start_week=cls.start_week,
            end_week=cls.end_week,
            start_period=cls.start_period,
            end_period=cls.end_period
        ))
    return results
