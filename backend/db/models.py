import enum

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.core.database import Base


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    class_code = Column(String(50), unique=True, index=True, nullable=False)   # VD: CNTT-K17
    class_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    students = relationship("Student", back_populates="class_", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_code = Column(String(50), unique=True, index=True, nullable=False)  # VD: SV001
    full_name = Column(String(255), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    # Vector khuôn mặt (ArcFace 512-d) không lưu ở MySQL -> lưu ở ChromaDB (backend/ai/vector_store.py)
    face_registered = Column(Boolean, default=False)  # đã có embedding trong ChromaDB chưa
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    class_ = relationship("Class", back_populates="students")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_code = Column(String(50), unique=True, index=True, nullable=False)  # VD: CAM-01
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)          # VD: Phòng A101
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    attendances = relationship("Attendance", back_populates="camera")


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"    # Có mặt - nhận diện thành công (similarity < threshold)
    UNKNOWN = "unknown"    # Người lạ / không nhận diện được (similarity >= threshold)


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=True)
    camera_id = Column(Integer, ForeignKey("cameras.id", ondelete="SET NULL"), nullable=True)
    status = Column(Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    similarity_score = Column(Float, nullable=True)   # Khoảng cách cosine trả về từ ChromaDB
    image_path = Column(String(500), nullable=True)   # Đường dẫn ảnh đã lưu trong uploads/
    checkin_time = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="attendances")
    camera = relationship("Camera", back_populates="attendances")
