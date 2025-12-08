from typing import List

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User, Lecturer
from app.models.academic import Class, Enrollment, Grade
from app.schemas.academic import GradeCreate, Class as ClassSchema, MobileStudentResponse, MobileClassResponse
from app.schemas.user import UserUpdate, User as UserSchema
from app.models.enums import UserRole
from typing import Optional, Union
from pydantic import BaseModel

router = APIRouter(prefix="/lecturers", tags=["lecturers"])

@router.get("/me", response_model=UserSchema)
def read_lecturer_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Add department name if exists
    department_name = None
    if current_user.lecturer and current_user.lecturer.department:
        department_name = current_user.lecturer.department.name
    
    user_dict = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "role": current_user.role,
        "student_code": None,
        "department_name": department_name,
        "is_active": True
    }
    return user_dict

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

@router.get("/my-classes", response_model=List[MobileClassResponse])
def read_lecturer_classes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    lecturer = current_user.lecturer
    if not lecturer:
        raise HTTPException(status_code=404, detail="Lecturer profile not found")

    results = []
    for cls in lecturer.classes:
        results.append(MobileClassResponse(
            id=cls.id,
            course_name=cls.course.name if cls.course else f"Class {cls.id}",
            lecturer_name=current_user.full_name,
            room="Online",
            day_of_week=cls.day_of_week,
            start_week=cls.start_week,
            end_week=cls.end_week,
            start_period=cls.start_period,
            end_period=cls.end_period
        ))
    return results

@router.get("/classes/{class_id}/students", response_model=List[MobileStudentResponse])
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
    results = []
    for e in enrollments:
        student_user = e.student.user
        
        midterm = None
        final = None
        # Logic to pick grades
        for g in e.grades:
            if g.grade_type == 'midterm':
                midterm = g.score
            elif g.grade_type == 'final':
                final = g.score
        
        # Display grade logic (Total or Final?) - Let's keep it null or calc average if needed.
        # User wants to edit Mid/Final.

        results.append(MobileStudentResponse(
            enrollment_id=e.id,
            student_id=e.student.student_code or str(student_user.id),
            student_name=student_user.full_name,
            midterm_grade=midterm,
            final_grade=final,
            grade=final if final is not None else midterm # Backward compat
        ))
    return results

@router.put("/grades", response_model=dict)
@router.post("/grades", response_model=dict)
def add_or_update_grade(
    enrollment_id: int = Form(...),
    grade_type: str = Form(...),
    score: float = Form(...),
    weight: Optional[float] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.LECTURER:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if enrollment belongs to a class taught by lecturer
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    class_obj = enrollment.class_
    if class_obj.lecturer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to grade this class")

    # Set default weight if not provided
    if weight is None:
        weight = 0.3 if grade_type == 'midterm' else 0.7

    # Check existing
    existing = db.query(Grade).filter(
        Grade.enrollment_id == enrollment_id,
        Grade.grade_type == grade_type
    ).first()

    if existing:
        existing.score = score
        existing.weight = weight
    else:
        new_grade = Grade(
            enrollment_id=enrollment_id,
            grade_type=grade_type,
            score=score,
            weight=weight
        )
        db.add(new_grade)
        
    db.commit()
    return {"message": "Grade updated successfully"}
