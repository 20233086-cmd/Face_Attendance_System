#!/usr/bin/env python3
"""
Script test nhận diện khuôn mặt với ArcFace
Tích hợp với API Next.js để lưu trữ và nhận diện
"""

import cv2
import numpy as np
import requests
import json
from pathlib import Path
import argparse

try:
    from insightface.app import FaceAnalysis
except ImportError:
    print("Cần cài đặt insightface: pip install insightface onnxruntime")
    print("Hoặc: pip install insightface onnxruntime-gpu (nếu có GPU)")
    exit(1)

# Cấu hình API
API_BASE_URL = "http://localhost:3000/api"

class FaceRecognitionSystem:
    def __init__(self):
        """Khởi tạo hệ thống nhận diện khuôn mặt với ArcFace"""
        print("Đang khởi tạo mô hình ArcFace...")
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        print("Khởi tạo thành công!")
    
    def extract_face_embedding(self, image_path):
        """
        Trích xuất vector ArcFace từ ảnh
        
        Args:
            image_path: Đường dẫn đến ảnh
            
        Returns:
            embedding: Vector ArcFace (512 chiều)
            face_info: Thông tin khuôn mặt
        """
        # Đọc ảnh
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Không thể đọc ảnh: {image_path}")
        
        # Phát hiện khuôn mặt và trích xuất đặc trưng
        faces = self.app.get(img)
        
        if len(faces) == 0:
            raise ValueError("Không phát hiện khuôn mặt trong ảnh")
        
        if len(faces) > 1:
            print(f"Cảnh báo: Phát hiện {len(faces)} khuôn mặt. Chỉ sử dụng khuôn mặt đầu tiên.")
        
        # Lấy khuôn mặt đầu tiên
        face = faces[0]
        
        # Vector ArcFace embedding (512 chiều)
        embedding = face.embedding
        
        # Thông tin khuôn mặt
        face_info = {
            "bbox": face.bbox.tolist(),  # Bounding box
            "det_score": float(face.det_score),  # Độ tin cậy phát hiện
            "age": int(face.age) if hasattr(face, 'age') else None,
            "gender": int(face.gender) if hasattr(face, 'gender') else None,
        }
        
        return embedding, face_info
    
    def compare_faces(self, embedding1, embedding2):
        """
        So sánh 2 vector embedding (Cosine Similarity)
        
        Args:
            embedding1, embedding2: Các vector ArcFace
            
        Returns:
            similarity: Độ tương đồng (0-1)
        """
        # Chuẩn hóa vector
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def register_user(self, name, image_path, email=None, student_id=None, 
                     department=None, role="student"):
        """
        Đăng ký người dùng mới với ảnh khuôn mặt
        
        Args:
            name: Tên người dùng
            image_path: Đường dẫn ảnh
            email: Email
            student_id: Mã sinh viên
            department: Khoa/Phòng ban
            role: Vai trò (student/teacher/admin)
        """
        print(f"\n=== Đăng ký người dùng: {name} ===")
        
        # Trích xuất embedding
        embedding, face_info = self.extract_face_embedding(image_path)
        print(f"✓ Trích xuất thành công vector ArcFace (512 chiều)")
        print(f"  - Độ tin cậy phát hiện: {face_info['det_score']:.2%}")
        print(f"  - Bounding box: {face_info['bbox']}")
        
        # Gửi đến API
        data = {
            "name": name,
            "email": email,
            "studentId": student_id,
            "department": department,
            "role": role,
            "faceEmbedding": embedding.tolist(),
            "imageUrl": str(image_path)
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/users", json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✓ Đăng ký thành công! User ID: {result['data']['id']}")
                    return result['data']
                else:
                    print(f"✗ Lỗi: {result.get('error')}")
            else:
                print(f"✗ Lỗi API: {response.status_code}")
                if response.text:
                    print(f"  Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Lỗi kết nối API: {e}")
            print("  Đảm bảo server đang chạy tại http://localhost:3000")
        
        return None
    
    def recognize_face(self, image_path, threshold=0.6):
        """
        Nhận diện khuôn mặt từ ảnh
        
        Args:
            image_path: Đường dẫn ảnh
            threshold: Ngưỡng nhận diện (mặc định 0.6)
            
        Returns:
            Thông tin người dùng nếu nhận diện thành công
        """
        print(f"\n=== Nhận diện khuôn mặt ===")
        
        # Trích xuất embedding
        embedding, face_info = self.extract_face_embedding(image_path)
        print(f"✓ Trích xuất vector ArcFace")
        print(f"  - Độ tin cậy phát hiện: {face_info['det_score']:.2%}")
        
        # Gửi đến API để nhận diện
        data = {
            "faceEmbedding": embedding.tolist(),
            "imageUrl": str(image_path),
            "threshold": threshold
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/recognize", json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    if result.get('recognized'):
                        user = result['user']
                        confidence = result['confidence']
                        print(f"\n✓ NHẬN DIỆN THÀNH CÔNG!")
                        print(f"  - Tên: {user['name']}")
                        print(f"  - Email: {user.get('email', 'N/A')}")
                        print(f"  - MSSV: {user.get('studentId', 'N/A')}")
                        print(f"  - Khoa: {user.get('department', 'N/A')}")
                        print(f"  - Độ tin cậy: {confidence}%")
                        return user
                    else:
                        print(f"\n✗ Không tìm thấy khuôn mặt khớp")
                        print(f"  - Độ tương đồng cao nhất: {result.get('confidence')}%")
                        print(f"  - Ngưỡng yêu cầu: {threshold * 100}%")
                else:
                    print(f"✗ Lỗi: {result.get('error')}")
            else:
                print(f"✗ Lỗi API: {response.status_code}")
                if response.text:
                    print(f"  Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Lỗi kết nối API: {e}")
            print("  Đảm bảo server đang chạy tại http://localhost:3000")
        
        return None
    
    def mark_attendance(self, user_id, location="Classroom", notes=None):
        """
        Đánh dấu điểm danh cho người dùng
        
        Args:
            user_id: ID người dùng
            location: Vị trí điểm danh
            notes: Ghi chú
        """
        data = {
            "userId": user_id,
            "status": "present",
            "location": location,
            "notes": notes
        }
        
        try:
            response = requests.post(f"{API_BASE_URL}/attendance", json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✓ Điểm danh thành công!")
                    return result['data']
                else:
                    print(f"✗ Lỗi điểm danh: {result.get('error')}")
            else:
                print(f"✗ Lỗi API điểm danh: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Lỗi kết nối khi điểm danh: {e}")
        
        return None
    
    def test_recognition_pipeline(self, image_path, location="Test Room"):
        """
        Test toàn bộ quy trình: nhận diện -> điểm danh
        
        Args:
            image_path: Đường dẫn ảnh
            location: Vị trí
        """
        # Nhận diện
        user = self.recognize_face(image_path)
        
        if user:
            # Điểm danh
            self.mark_attendance(user['id'], location=location)


def main():
    parser = argparse.ArgumentParser(description='Hệ thống nhận diện khuôn mặt ArcFace')
    parser.add_argument('--mode', choices=['register', 'recognize', 'test'], 
                       required=True, help='Chế độ hoạt động')
    parser.add_argument('--image', required=True, help='Đường dẫn ảnh')
    parser.add_argument('--name', help='Tên người dùng (dùng cho register)')
    parser.add_argument('--email', help='Email')
    parser.add_argument('--student-id', help='Mã sinh viên')
    parser.add_argument('--department', help='Khoa/Phòng ban')
    parser.add_argument('--threshold', type=float, default=0.6, 
                       help='Ngưỡng nhận diện (mặc định 0.6)')
    
    args = parser.parse_args()
    
    # Khởi tạo hệ thống
    system = FaceRecognitionSystem()
    
    if args.mode == 'register':
        if not args.name:
            print("Lỗi: Cần cung cấp --name cho chế độ register")
            return
        
        system.register_user(
            name=args.name,
            image_path=args.image,
            email=args.email,
            student_id=args.student_id,
            department=args.department
        )
    
    elif args.mode == 'recognize':
        system.recognize_face(args.image, threshold=args.threshold)
    
    elif args.mode == 'test':
        system.test_recognition_pipeline(args.image)


if __name__ == "__main__":
    # Example usage:
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     HỆ THỐNG ĐIỂM DANH KHUÔN MẶT - ARCFACE                  ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Ví dụ sử dụng:
    
    1. Đăng ký người dùng:
       python test_recognition.py --mode register --image person1.jpg \\
           --name "Nguyễn Văn A" --student-id "SV001" --email "a@example.com"
    
    2. Nhận diện khuôn mặt:
       python test_recognition.py --mode recognize --image test.jpg
    
    3. Test toàn bộ quy trình:
       python test_recognition.py --mode test --image test.jpg
    
    ══════════════════════════════════════════════════════════════
    """)
    
    main()
