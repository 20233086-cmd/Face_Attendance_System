from fastapi import APIRouter

from backend.api.endpoints import attendance, students, webcams

api_router = APIRouter()
api_router.include_router(attendance.router)
api_router.include_router(students.router)
api_router.include_router(webcams.router)
