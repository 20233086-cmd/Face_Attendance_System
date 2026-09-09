# SQL thuần, backup cho ai không dùng ORM
CREATE DATABASE IF NOT EXISTS attendance_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE attendance_db;

-- Bảng Lớp học
CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_code VARCHAR(50) NOT NULL UNIQUE,
    class_name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Sinh viên
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_code VARCHAR(50) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    class_id INT NOT NULL,
    face_registered BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Bảng Camera
CREATE TABLE IF NOT EXISTS cameras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    camera_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Bảng Điểm danh
CREATE TABLE IF NOT EXISTS attendances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NULL,
    camera_id INT NULL,
    status ENUM('present', 'unknown') NOT NULL DEFAULT 'present',
    similarity_score FLOAT NULL,
    image_path VARCHAR(500) NULL,
    checkin_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (camera_id) REFERENCES cameras(id) ON DELETE SET NULL
);

-- Dữ liệu mẫu
INSERT IGNORE INTO classes (class_code, class_name) VALUES
    ('CNTT-K17', 'Công nghệ thông tin K17');

INSERT IGNORE INTO students (student_code, full_name, class_id) VALUES
    ('SV001', 'Nguyễn Văn An', (SELECT id FROM classes WHERE class_code = 'CNTT-K17')),
    ('SV002', 'Trần Thị Bình', (SELECT id FROM classes WHERE class_code = 'CNTT-K17')),
    ('SV003', 'Lê Hoàng Nam', (SELECT id FROM classes WHERE class_code = 'CNTT-K17'));

INSERT IGNORE INTO cameras (camera_code, name, location) VALUES
    ('CAM-01', 'Camera cổng chính', 'Phòng A101'),
    ('CAM-02', 'Camera hành lang', 'Phòng A102');
