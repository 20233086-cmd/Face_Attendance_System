import os
from pathlib import Path
from dotenv import load_dotenv

# backend/core/config.py -> parent (core) -> parent (backend) -> parent (project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    # --- App ---
    APP_NAME: str = os.getenv("APP_NAME", "Face Attendance System")
    APP_VERSION: str = "0.1.0"

    # --- Database (MySQL) ---
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "attendance_db")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # --- Chế độ Mock (Tuần 1: chưa có AI thật -> luôn True) ---
    MOCK_MODE: bool = os.getenv("MOCK_MODE", "true").lower() == "true"

    # --- Bảo mật: API Key dùng cho thiết bị Camera / endpoint quản trị ---
    API_KEY: str = os.getenv("API_KEY", "dev-secret-key-change-me")

    # --- AI / Nhận diện ---
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.4"))
    VECTOR_DIM: int = int(os.getenv("VECTOR_DIM", "512"))  # ArcFace embedding 512 chiều

    # --- Upload ảnh ---
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "uploads")

    # --- CORS (Frontend gọi API) ---
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
