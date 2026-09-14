from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import settings
from backend.core.database import Base, engine
from backend.api.api_router import api_router
from backend.db import models  # noqa: F401  (import để SQLAlchemy biết các bảng cần tạo)

# Tạo bảng trong MySQL nếu chưa tồn tại (Class, Student, Camera, Attendance)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="API hệ thống điểm danh khuôn mặt: Camera -> Detect -> Recognize -> MySQL -> Realtime.",
    version=settings.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cho phép truy cập trực tiếp ảnh đã lưu, VD: http://localhost:8000/uploads/xxx.jpg
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

app.include_router(api_router)


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "mock_mode": settings.MOCK_MODE,
        "docs": "/docs",
    }
