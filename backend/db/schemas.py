from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.db.models import AttendanceStatus


# ---------- Class ----------
class ClassCreate(BaseModel):
    class_code: str
    class_name: str


class ClassOut(ClassCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Student ----------
class StudentCreate(BaseModel):
    student_code: str
    full_name: str
    class_id: int


class StudentOut(StudentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    face_registered: bool


# ---------- Camera ----------
class CameraCreate(BaseModel):
    camera_code: str
    name: str
    location: str | None = None


class CameraOut(CameraCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool


class CameraUpdateStatus(BaseModel):
    is_active: bool


# ---------- Attendance ----------
class AttendanceCheckinResponse(BaseModel):
    """
    Response trả về sau khi xử lý xong pipeline (Detect -> Recognize -> Ghi MySQL),
    đúng theo bước 7-8 trong sơ đồ luồng xử lý.
    """
    success: bool
    status: AttendanceStatus
    student_code: str | None = None
    full_name: str | None = None
    class_name: str | None = None
    similarity_score: float | None = None
    checkin_time: datetime
    message: str


class AttendanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int | None
    camera_id: int | None
    status: AttendanceStatus
    similarity_score: float | None
    checkin_time: datetime
