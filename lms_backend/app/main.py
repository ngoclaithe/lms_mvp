from fastapi import FastAPI, Request
from app.database import engine, Base
from app.models import User, Student, Lecturer, Department, Course, Class, Schedule, Enrollment, Grade

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LMS Backend")

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    print(f"REQUEST: {request.method} {request.url}")
    print(f"HEADERS: {request.headers}")
    print(f"BODY: {body.decode()}")
    response = await call_next(request)
    return response

from app.routers import auth, students, lecturers, deans
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(lecturers.router)
app.include_router(deans.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to LMS Backend"}
