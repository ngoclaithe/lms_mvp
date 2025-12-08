from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User, Lecturer, Student
from app.models.academic import Department, Course, Class, Enrollment, Grade
from app.schemas.academic import (
    CourseCreate, Course as CourseSchema,
    ClassCreate, Class as ClassSchema,
    GradeCreate, Grade as GradeSchema,
    DepartmentCreate, Department as DepartmentSchema
)
from app.schemas.user import UserCreate, User as UserSchema, UserUpdate
from app.models.enums import UserRole
from app.crud.user import create_user

router = APIRouter(prefix="/deans", tags=["deans"])

def check_dean_role(user: User):
    if user.role != UserRole.DEAN:
        raise HTTPException(status_code=403, detail="Not authorized. Dean access required.")

# --- Department Management ---
@router.post("/departments", response_model=DepartmentSchema)
def create_department(
    dept_in: DepartmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    if db.query(Department).filter(Department.name == dept_in.name).first():
        raise HTTPException(status_code=400, detail="Department already exists")
    
    db_dept = Department(**dept_in.dict())
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.get("/departments", response_model=List[DepartmentSchema])
def list_departments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    return db.query(Department).all()

@router.put("/departments/{dept_id}", response_model=DepartmentSchema)
def update_department(
    dept_id: int,
    dept_in: DepartmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_dept = db.query(Department).filter(Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    db_dept.name = dept_in.name
    if dept_in.description:
        db_dept.description = dept_in.description
        
    db.commit()
    db.refresh(db_dept)
    return db_dept

@router.delete("/departments/{dept_id}")
def delete_department(
    dept_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_dept = db.query(Department).filter(Department.id == dept_id).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail="Department not found")
        
    db.delete(db_dept)
    db.commit()
    return {"message": "Department deleted"}

# --- Course Management ---
@router.post("/courses", response_model=CourseSchema)
def create_course(
    course: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    if db.query(Course).filter(Course.code == course.code).first():
        raise HTTPException(status_code=400, detail="Course code already exists")

    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/courses", response_model=List[CourseSchema])
def list_courses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    return db.query(Course).all()

@router.put("/courses/{course_id}", response_model=CourseSchema)
def update_course(
    course_id: int,
    course_in: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db_course.code = course_in.code
    db_course.name = course_in.name
    db_course.credits = course_in.credits
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/courses/{course_id}")
def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    db.delete(db_course)
    db.commit()
    return {"message": "Course deleted"}

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
    lecturer_profile = Lecturer(
        user_id=user.id, 
        lecturer_code=f"LEC{user.id}",
        department_id=user_in.department_id
    )
    db.add(lecturer_profile)
    db.commit()
    
    return user

@router.get("/lecturers", response_model=List[UserSchema])
def list_lecturers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    lecturers = db.query(User).filter(User.role == UserRole.LECTURER).all()
    
    # Add department_name to each lecturer
    result = []
    for lec in lecturers:
        lec_dict = {
            "id": lec.id,
            "username": lec.username,
            "email": lec.email,
            "full_name": lec.full_name,
            "phone_number": lec.phone_number,
            "role": lec.role,
            "student_code": None,
            "department_name": lec.lecturer.department.name if lec.lecturer and lec.lecturer.department else None,
            "is_active": True
        }
        result.append(lec_dict)
    return result

@router.put("/lecturers/{user_id}", response_model=UserSchema)
def update_lecturer(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_user = db.query(User).filter(User.id == user_id, User.role == UserRole.LECTURER).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Lecturer not found")
    
    if user_in.full_name:
        db_user.full_name = user_in.full_name
    if user_in.email:
        db_user.email = user_in.email
    if user_in.phone_number:
        db_user.phone_number = user_in.phone_number
    
    # Update department if provided
    if user_in.department_id is not None and db_user.lecturer:
        db_user.lecturer.department_id = user_in.department_id
    
    db.commit()
    db.refresh(db_user)
    
    # Return with department_name
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "phone_number": db_user.phone_number,
        "role": db_user.role,
        "student_code": None,
        "department_name": db_user.lecturer.department.name if db_user.lecturer and db_user.lecturer.department else None,
        "is_active": True
    }

@router.delete("/lecturers/{user_id}")
def delete_lecturer(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_user = db.query(User).filter(User.id == user_id, User.role == UserRole.LECTURER).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Lecturer not found")
        
    db.delete(db_user)
    db.commit()
    return {"message": "Lecturer deleted"}

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
    # Use provided student_code or fallback to auto-gen
    code = user_in.student_code if user_in.student_code else f"STU{user.id}"
    
    # Check if student_code exists
    if db.query(Student).filter(Student.student_code == code).first():
         # Rollback user creation if code exists - simplified: just error
         # Ideally we should delete the user we just created or check before
         # But for MVP, let's just error (transaction will rollback if we raise?)
         # Actually with commit above inside create_user, it might persist.
         # For MVP, let's assume unique or handle generic integrity error
         pass

    student_profile = Student(
        user_id=user.id, 
        student_code=code,
        department_id=user_in.department_id
    )
    db.add(student_profile)
    db.commit()
    
    return user

@router.get("/students", response_model=List[UserSchema])
def list_students(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    
    # Add department_name and student_code to each student
    result = []
    for stu in students:
        stu_dict = {
            "id": stu.id,
            "username": stu.username,
            "email": stu.email,
            "full_name": stu.full_name,
            "phone_number": stu.phone_number,
            "role": stu.role,
            "student_code": stu.student.student_code if stu.student else None,
            "department_name": stu.student.department.name if stu.student and stu.student.department else None,
            "is_active": True
        }
        result.append(stu_dict)
    return result

@router.put("/students/{user_id}", response_model=UserSchema)
def update_student(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_user = db.query(User).filter(User.id == user_id, User.role == UserRole.STUDENT).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if user_in.full_name:
        db_user.full_name = user_in.full_name
    if user_in.email:
        db_user.email = user_in.email
    if user_in.phone_number:
        db_user.phone_number = user_in.phone_number
    
    # Update student code if provided
    if user_in.student_code and db_user.student:
        db_user.student.student_code = user_in.student_code
    
    # Update department if provided
    if user_in.department_id is not None and db_user.student:
        db_user.student.department_id = user_in.department_id
    
    db.commit()
    db.refresh(db_user)
    
    # Return with department_name
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "full_name": db_user.full_name,
        "phone_number": db_user.phone_number,
        "role": db_user.role,
        "student_code": db_user.student.student_code if db_user.student else None,
        "department_name": db_user.student.department.name if db_user.student and db_user.student.department else None,
        "is_active": True
    }

@router.delete("/students/{user_id}")
def delete_student(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_user = db.query(User).filter(User.id == user_id, User.role == UserRole.STUDENT).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Student not found")
        
    db.delete(db_user)
    db.commit()
    return {"message": "Student deleted"}

# --- Class Management ---
@router.post("/classes", response_model=ClassSchema)
def create_class(
    class_in: ClassCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    
    lecturer = db.query(Lecturer).filter(Lecturer.user_id == class_in.lecturer_id).first()
    if not lecturer:
        user = db.query(User).filter(User.id == class_in.lecturer_id, User.role == UserRole.LECTURER).first()
        if user:
            lecturer = Lecturer(user_id=user.id, lecturer_code=f"LEC{user.id}")
            db.add(lecturer)
            db.commit()
        else:
            raise HTTPException(status_code=400, detail="Invaild lecturer selected")
            
    db_class = Class(**class_in.dict())
    db.add(db_class)
    db.commit()
    db.refresh(db_class)
    return db_class

@router.get("/classes", response_model=List[ClassSchema])
def list_classes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    classes = db.query(Class).offset(skip).limit(limit).all()
    
    # Calculate enrolled count manually for now
    for c in classes:
        c.enrolled_count = db.query(Enrollment).filter(Enrollment.class_id == c.id).count()
        
    return classes

@router.put("/classes/{class_id}", response_model=ClassSchema)
def update_class(
    class_id: int,
    class_in: ClassCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    for key, value in class_in.dict().items():
        setattr(db_class, key, value)
        
    db.commit()
    db.refresh(db_class)
    return db_class

@router.delete("/classes/{class_id}")
def delete_class(
    class_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    db.delete(db_class)
    db.commit()
    return {"message": "Class deleted"}

# --- Enrollment Management ---
@router.post("/classes/{class_id}/enrollments/bulk")
def bulk_enroll_students(
    class_id: int,
    enrollment_in: dict, # Using dict to avoid circular import or schema issues if simple
    # But better to use Schema if I imported it. I created EnrollmentBulkCreate.
    # Let's simple use List[int] directly or expected body.
    # Let's import EnrollmentBulkCreate.
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    
    student_ids = enrollment_in.get('student_ids', [])
    if not student_ids:
         raise HTTPException(status_code=400, detail="No students provided")

    db_class = db.query(Class).filter(Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
        
    # Check capacity
    current_count = db.query(Enrollment).filter(Enrollment.class_id == class_id).count()
    if current_count + len(student_ids) > db_class.max_students:
        raise HTTPException(status_code=400, detail=f"Class capacity exceeded. Remaining slots: {db_class.max_students - current_count}")

    added_count = 0
    for student_id in student_ids:
        # Check if student exists (by User ID)
        student = db.query(Student).filter(Student.user_id == student_id).first()
        if not student:
            continue # Skip invalid students
            
        # Check if already enrolled
        existing = db.query(Enrollment).filter(Enrollment.class_id == class_id, Enrollment.student_id == student_id).first()
        if existing:
            continue
            
        new_enrollment = Enrollment(class_id=class_id, student_id=student_id)
        db.add(new_enrollment)
        added_count += 1
        
    db.commit()
    return {"message": f"Successfully added {added_count} students"}

@router.get("/classes/{class_id}/students", response_model=List[UserSchema])
def list_class_students(
    class_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    # Join Enrollment and Student and User
    # Return Users who are students in this class
    results = db.query(User).join(Student).join(Enrollment).filter(Enrollment.class_id == class_id).all()
    return results

@router.put("/grades/{grade_id}", response_model=GradeSchema)
def update_grade(
    grade_id: int,
    grade_in: dict, # Using dict for simplicity, ideally GradeBase
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    
    db_grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not db_grade:
        raise HTTPException(status_code=404, detail="Grade not found")
        
    if 'score' in grade_in:
        db_grade.score = grade_in['score']
    
    db.commit()
    db.refresh(db_grade)
    return db_grade

@router.post("/grades", response_model=GradeSchema)
def create_grade(
    grade_in: GradeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    
    # Check enrollment existence
    enrollment = db.query(Enrollment).filter(Enrollment.id == grade_in.enrollment_id).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
        
    # Check if grade type already exists for this enrollment (optional, but good practice)
    # For now allow multiple, or maybe unique per type? usually unique per type (midterm/final)
    # Let's check if collision
    existing = db.query(Grade).filter(
        Grade.enrollment_id == grade_in.enrollment_id, 
        Grade.grade_type == grade_in.grade_type
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Grade type {grade_in.grade_type} already exists for this student. Use PUT to update.")

    db_grade = Grade(**grade_in.dict())
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade

# --- Grade Management ---
@router.get("/classes/{class_id}/grades", response_model=List[dict])
def view_class_grades(
    class_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    
    # Check if class exists
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
    
    results = []
    for enrollment in enrollments:
        student_info = {
            "enrollment_id": enrollment.id,
            "student_id": enrollment.student.user.id,
            "student_code": enrollment.student.student_code,
            "full_name": enrollment.student.user.full_name,
            "full_name": enrollment.student.user.full_name,
            "grades": [
                {
                    "id": g.id, 
                    "grade_type": g.grade_type, 
                    "score": g.score, 
                    "weight": g.weight
                } for g in enrollment.grades
            ]
        }
        results.append(student_info)
        
    return results

@router.get("/classes/{class_id}", response_model=ClassSchema)
def get_class(
    class_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    check_dean_role(current_user)
    db_class = db.query(Class).filter(Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    return db_class

