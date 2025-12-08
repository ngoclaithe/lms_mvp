# LMS Backend API Documentation

## Authentication
Everything requires a Bearer Token (JWT).
- `POST /auth/login`: `{username, password}` -> `{access_token, token_type}`
- `POST /auth/register`: `{username, email, password, role, full_name, ...}` -> `User` object.

## Roles

### Student
- `GET /students/me/grades`: Get list of grades for enrolled classes.
- `GET /students/me/classes`: Get list of classes enrolled in.
- `PUT /students/me`: Update profile. Body: `{full_name, email, phone_number}`.

### Lecturer
- `GET /lecturers/my-classes`: Get list of classes taught by you.
- `GET /lecturers/classes/{class_id}/students`: Get list of students in a specific class.
- `POST /lecturers/grades`: Add/Update grade. Payload: `{enrollment_id, grade_type, score, weight}`.
- `PUT /lecturers/me`: Update profile. Body: `{full_name, email, phone_number}`.

### Dean
- `GET /deans/courses`: List all courses.
- `POST /deans/courses`: Create a new course. Payload: `{code, name, credits, department_id}`.
- `POST /deans/lecturers`: Create Lecturer. Payload: `UserCreate` object.
- `GET /deans/lecturers`: List all lecturers.
- `POST /deans/students`: Create Student. Payload: `UserCreate` object.
- `GET /deans/students`: List all students.
- `GET /deans/audit-logs`: View system audit logs (Creation of users, courses, etc.).

## Schema Objects
### UserRole
- `student`
- `lecturer`
- `dean`

### GradeView
- `course_name`
- `class_code`
- `grades`: List of `{grade_type, score}`

## Notes for Mobile/Frontend
- Use the `access_token` in the Authorization header: `Bearer <token>`.
- Handle 401 Unauthorized (token expired/invalid) by redirecting to Login.
- Handle 403 Forbidden if a user tries to access a route not for their role.
