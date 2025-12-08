# Backend Task Specification for LMS System

## Database

PostgreSQL database: `lms_system`

## Modules and Responsibilities

### 1. Student Role

-   Xem điểm cá nhân
-   Cập nhật thông tin cá nhân
-   Xem lớp học, lịch học
-   Xem học phần được đăng ký
-   Cập nhật hồ sơ cá nhân

### 2. Giảng viên Role

-   Nhập điểm, sửa điểm môn dạy
-   Cập nhật thông tin cá nhân
-   Xem danh sách sinh viên lớp mình dạy
-   Quản lý lớp môn học giảng dạy
-   Quản lý học phần môn đang dạy
-   Xem thông tin sinh viên các lớp dạy

### 3. Trưởng khoa Role

-   Xem điểm toàn khoa, phê duyệt/kiểm tra điểm
-   Xem danh sách giảng viên, quản lý hồ sơ giảng viên
-   Quản lý danh sách sinh viên toàn khoa
-   Quản lý lớp học thuộc khoa
-   Quản lý toàn bộ học phần của khoa
-   Quản lý thông tin khoa/viện
-   Cập nhật, phê duyệt hoặc chỉnh sửa thông tin sinh viên toàn khoa

## Backend Agent Tasks

-   Thiết kế ERD và tạo schema PostgreSQL
-   Tạo các bảng: students, lecturers, departments, courses, classes,
    enrollments, grades, schedules
-   Xây dựng REST API theo từng role
-   Middleware phân quyền: student / lecturer / dean
-   Module grade management
-   Module user profile management
-   Module class & course management
-   Module department controls
-   Logging + audit cho trưởng khoa
