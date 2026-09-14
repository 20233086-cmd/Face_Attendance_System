from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import verify_api_key
from backend.db.models import Camera
from backend.db.schemas import CameraCreate, CameraOut, CameraUpdateStatus

router = APIRouter(prefix="/api/v1/webcams", tags=["Webcams"])


@router.post("", response_model=CameraOut, dependencies=[Depends(verify_api_key)], summary="Đăng ký camera mới")
def register_camera(payload: CameraCreate, db: Session = Depends(get_db)):
    if db.query(Camera).filter(Camera.camera_code == payload.camera_code).first():
        raise HTTPException(status_code=400, detail="Mã camera đã tồn tại")
    camera = Camera(**payload.model_dump())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


@router.get("", response_model=list[CameraOut], summary="Danh sách camera")
def list_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()


@router.patch(
    "/{camera_code}/status",
    response_model=CameraOut,
    dependencies=[Depends(verify_api_key)],
    summary="Bật/tắt camera",
)
def update_camera_status(camera_code: str, payload: CameraUpdateStatus, db: Session = Depends(get_db)):
    camera = db.query(Camera).filter(Camera.camera_code == camera_code).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Không tìm thấy camera")
    camera.is_active = payload.is_active
    db.commit()
    db.refresh(camera)
    return camera
