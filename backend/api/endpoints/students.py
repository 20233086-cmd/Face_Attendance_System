from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import verify_api_key
from backend.db.models import Class, Student
from backend.db.schemas import ClassCreate, ClassOut, StudentCreate, StudentOut

router = APIRouter(prefix="/api/v1", tags=["Students & Classes"])


# ---------- Classes ----------
@router.post("/classes", response_model=ClassOut, dependencies=[Depends(verify_api_key)], summary="Tạo lớp học")
def create_class(payload: ClassCreate, db: Session = Depends(get_db)):
    if db.query(Class).filter(Class.class_code == payload.class_code).first():
        raise HTTPException(status_code=400, detail="Mã lớp đã tồn tại")
    new_class = Class(**payload.model_dump())
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class


@router.get("/classes", response_model=list[ClassOut], summary="Danh sách lớp học")
def list_classes(db: Session = Depends(get_db)):
    return db.query(Class).all()


# ---------- Students ----------
@router.post("/students", response_model=StudentOut, dependencies=[Depends(verify_api_key)], summary="Thêm sinh viên")
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    if not db.query(Class).filter(Class.id == payload.class_id).first():
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    if db.query(Student).filter(Student.student_code == payload.student_code).first():
        raise HTTPException(status_code=400, detail="Mã sinh viên đã tồn tại")

    new_student = Student(**payload.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.get("/students", response_model=list[StudentOut], summary="Danh sách sinh viên")
def list_students(class_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Student)
    if class_id is not None:
        query = query.filter(Student.class_id == class_id)
    return query.all()


@router.get("/students/{student_code}", response_model=StudentOut, summary="Xem chi tiết 1 sinh viên")
def get_student(student_code: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.student_code == student_code).first()
    if not student:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return student
