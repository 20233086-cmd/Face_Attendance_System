import random
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.core.security import verify_api_key
from backend.db.models import Attendance, AttendanceStatus, Camera
from backend.db.schemas import AttendanceCheckinResponse, AttendanceOut

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance"])

# Danh sách sinh viên mock để trả về xoay vòng (khớp dữ liệu mẫu trong schema.sql)
_MOCK_STUDENTS = [
    {"student_code": "SV001", "full_name": "Nguyễn Văn An", "class_name": "CNTT-K17"},
    {"student_code": "SV002", "full_name": "Trần Thị Bình", "class_name": "CNTT-K17"},
    {"student_code": "SV003", "full_name": "Lê Hoàng Nam", "class_name": "CNTT-K17"},
]


def _save_upload(image: UploadFile) -> str:
    """Lưu ảnh gửi lên vào thư mục uploads/, trả về đường dẫn đã lưu."""
    ext = Path(image.filename).suffix or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = settings.UPLOAD_DIR / filename
    with dest_path.open("wb") as f:
        shutil.copyfileobj(image.file, f)
    return str(dest_path)


@router.post(
    "/checkin",
    response_model=AttendanceCheckinResponse,
    summary="[MOCK] Điểm danh khuôn mặt",
    description=(
        "API giả lập (Mock) dùng cho Tuần 1. Chưa nhận diện khuôn mặt thật — "
        "chỉ trả về JSON mẫu đúng cấu trúc thật để Frontend dựng UI trước, "
        "và để TV1/TV2 biết trước format response cần khớp khi ghép nối ở Tuần 2."
    ),
    dependencies=[Depends(verify_api_key)],
)
def mock_checkin(
    image: UploadFile = File(..., description="Frame ảnh chụp từ Camera"),
    camera_code: str = Form(..., description="Mã camera, VD: CAM-01"),
    db: Session = Depends(get_db),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File tải lên phải là ảnh")

    image_path = _save_upload(image)
    camera = db.query(Camera).filter(Camera.camera_code == camera_code).first()
    now = datetime.now(timezone.utc)

    # Giả lập ngẫu nhiên: ~80% nhận diện thành công, ~20% "người lạ / unknown"
    is_recognized = random.random() < 0.8

    if is_recognized:
        student = random.choice(_MOCK_STUDENTS)
        similarity_score = round(random.uniform(0.15, 0.39), 4)  # < 0.4 => đạt threshold

        record = Attendance(
            student_id=None,  # dữ liệu mock, chưa có student_id thật
            camera_id=camera.id if camera else None,
            status=AttendanceStatus.PRESENT,
            similarity_score=similarity_score,
            image_path=image_path,
        )
        db.add(record)
        db.commit()

        return AttendanceCheckinResponse(
            success=True,
            status=AttendanceStatus.PRESENT,
            student_code=student["student_code"],
            full_name=student["full_name"],
            class_name=student["class_name"],
            similarity_score=similarity_score,
            checkin_time=now,
            message="Điểm danh thành công (dữ liệu mock).",
        )

    similarity_score = round(random.uniform(0.41, 0.7), 4)  # >= 0.4 => không đạt threshold

    record = Attendance(
        student_id=None,
        camera_id=camera.id if camera else None,
        status=AttendanceStatus.UNKNOWN,
        similarity_score=similarity_score,
        image_path=image_path,
    )
    db.add(record)
    db.commit()

    return AttendanceCheckinResponse(
        success=False,
        status=AttendanceStatus.UNKNOWN,
        similarity_score=similarity_score,
        checkin_time=now,
        message="Không nhận diện được sinh viên (Unknown, dữ liệu mock).",
    )


@router.get(
    "/history",
    response_model=list[AttendanceOut],
    summary="Xem lịch sử điểm danh đã ghi nhận",
)
def get_attendance_history(limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(Attendance)
        .order_by(Attendance.checkin_time.desc())
        .limit(limit)
        .all()
    )

