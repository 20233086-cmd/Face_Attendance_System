"""
============================================================
MODULE: test_recognition.py
MÔ TẢ: File test độc lập cho AI nhận diện khuôn mặt.
       Có thể chạy trực tiếp để kiểm tra engine hoạt động.

CÁCH CHẠY:
       cd attendance_system/backend
       python test_recognition.py

       # Hoặc test với webcam:
       python test_recognition.py --mode webcam

       # Test với ảnh:
       python test_recognition.py --mode image --path path/to/image.jpg
============================================================
"""

import argparse
import sys
import os
import logging
import time
from pathlib import Path

# Thêm project root vào Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("test_recognition")


def test_imports():
    """Kiểm tra các thư viện cần thiết đã được cài đặt."""
    print("\n" + "="*60)
    print("🔍 Kiểm tra thư viện...")
    print("="*60)

    libs = {
        "cv2 (OpenCV)": "cv2",
        "face_recognition": "face_recognition",
        "numpy": "numpy",
        "PIL (Pillow)": "PIL",
    }

    all_ok = True
    for name, module in libs.items():
        try:
            __import__(module)
            print(f"  ✅ {name} - OK")
        except ImportError:
            print(f"  ❌ {name} - CHƯA CÀI ĐẶT")
            all_ok = False

    return all_ok


def test_encode_face(image_path: str) -> bool:
    """
    Test encode khuôn mặt từ ảnh.

    Args:
        image_path: Đường dẫn file ảnh

    Returns:
        True nếu test thành công
    """
    print("\n" + "="*60)
    print(f"🖼️  Test encode khuôn mặt: {image_path}")
    print("="*60)

    try:
        import cv2
        import face_recognition
        import numpy as np

        # Đọc ảnh
        image = cv2.imread(image_path)
        if image is None:
            print(f"  ❌ Không thể đọc ảnh: {image_path}")
            return False

        print(f"  ✅ Đọc ảnh: {image.shape[1]}x{image.shape[0]}px")

        # Chuyển BGR → RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Phát hiện khuôn mặt
        t_start = time.time()
        face_locations = face_recognition.face_locations(rgb, model="hog")
        t_detect = time.time() - t_start

        print(f"  ✅ Phát hiện {len(face_locations)} khuôn mặt (thời gian: {t_detect:.3f}s)")

        if not face_locations:
            print("  ⚠️  Không tìm thấy khuôn mặt trong ảnh")
            return False

        # Mã hóa khuôn mặt
        t_start = time.time()
        encodings = face_recognition.face_encodings(rgb, face_locations)
        t_encode = time.time() - t_start

        print(f"  ✅ Mã hóa {len(encodings)} khuôn mặt (thời gian: {t_encode:.3f}s)")
        print(f"  📊 Kích thước encoding vector: {len(encodings[0])} chiều")

        # Vẽ kết quả
        annotated = image.copy()
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(annotated, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(annotated, "DETECTED", (left, top-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Lưu ảnh kết quả
        output_path = "test_output_detection.jpg"
        cv2.imwrite(output_path, annotated)
        print(f"  💾 Đã lưu ảnh kết quả: {output_path}")

        return True

    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        return False


def test_webcam_recognition():
    """
    Test nhận diện khuôn mặt realtime từ webcam.
    Nhấn 'Q' để thoát, 'S' để lưu ảnh, 'R' để đăng ký khuôn mặt.
    """
    print("\n" + "="*60)
    print("📷 Test nhận diện khuôn mặt qua Webcam")
    print("  Phím điều khiển:")
    print("  [Q] - Thoát")
    print("  [S] - Chụp ảnh màn hình")
    print("="*60)

    try:
        import cv2
        import face_recognition
        import numpy as np

        # Khởi động webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("  ❌ Không thể mở webcam (kiểm tra kết nối camera)")
            return False

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        print(f"  ✅ Webcam khởi động: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")

        # Load encodings đã biết (nếu có)
        from ai.face_recognition_engine import FaceRecognitionEngine
        engine = FaceRecognitionEngine()
        print(f"  ✅ Đã nạp {len(engine.known_encodings)} khuôn mặt đã đăng ký")

        frame_count = 0
        fps_start = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                print("  ❌ Không nhận được frame từ camera")
                break

            frame_count += 1

            # Nhận diện mỗi 2 frame
            if frame_count % 2 == 0:
                results = engine.recognize_from_frame(frame)
                student_map = {r["student_id"]: f"SV_{r['student_id']}" for r in results if r.get("student_id")}
                if results:
                    frame = engine.draw_recognition_result(frame, results, student_map)

            # Tính FPS
            if frame_count % 30 == 0:
                fps = 30 / (time.time() - fps_start)
                fps_start = time.time()
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Hiển thị hướng dẫn
            cv2.putText(frame, "Q: Thoat | S: Chup anh", (10, frame.shape[0] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Hiển thị
            cv2.imshow("FaceAttend - Test Nhan Dien", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("  🛑 Đã thoát")
                break
            elif key == ord('s'):
                save_path = f"test_capture_{int(time.time())}.jpg"
                cv2.imwrite(save_path, frame)
                print(f"  💾 Đã lưu: {save_path}")

        cap.release()
        cv2.destroyAllWindows()
        return True

    except ImportError as e:
        print(f"  ❌ Thiếu thư viện: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        return False


def test_similarity_comparison():
    """Test so sánh độ tương đồng giữa 2 khuôn mặt."""
    print("\n" + "="*60)
    print("🔬 Test so sánh độ tương đồng khuôn mặt")
    print("="*60)

    try:
        import face_recognition
        import numpy as np

        # Tạo 2 encoding giả để demo
        enc1 = np.random.rand(128)
        enc2 = enc1 + np.random.rand(128) * 0.1  # Rất giống

        distance = face_recognition.face_distance([enc1], enc2)[0]
        similarity = 1.0 - distance

        print(f"  📊 Face distance: {distance:.4f}")
        print(f"  📊 Similarity score: {similarity:.4f} ({similarity*100:.1f}%)")
        print(f"  📊 Ngưỡng (tolerance): 0.5")
        print(f"  📊 Kết quả: {'✅ NHẬN DIỆN ĐƯỢC' if distance <= 0.5 else '❌ KHÔNG NHẬN DIỆN'}")

        return True

    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        return False


def main():
    """Hàm chính của test script."""
    parser = argparse.ArgumentParser(
        description="Test AI nhận diện khuôn mặt - FaceAttend System"
    )
    parser.add_argument(
        "--mode",
        choices=["all", "imports", "webcam", "image", "similarity"],
        default="all",
        help="Chế độ test"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Đường dẫn ảnh (dùng với --mode image)"
    )

    args = parser.parse_args()

    print("\n" + "🤖 FACEATTEND - HỆ THỐNG ĐIỂM DANH AI 🤖".center(60))
    print("=" * 60)
    print(f"Thời gian: {time.strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

    results = {}

    if args.mode in ("all", "imports"):
        results["imports"] = test_imports()

    if args.mode in ("all", "similarity"):
        results["similarity"] = test_similarity_comparison()

    if args.mode == "image" and args.path:
        results["image"] = test_encode_face(args.path)
    elif args.mode == "all":
        # Test với ảnh mẫu nếu có
        sample_images = list(Path("data/faces").glob("*.jpg"))
        if sample_images:
            results["image"] = test_encode_face(str(sample_images[0]))
        else:
            print("\n⚠️  Chưa có ảnh mẫu trong data/faces/")

    if args.mode == "webcam":
        results["webcam"] = test_webcam_recognition()

    # Tổng kết
    print("\n" + "="*60)
    print("📋 KẾT QUẢ TỔNG KẾT")
    print("="*60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")

    all_passed = all(results.values())
    print("\n" + ("🎉 TẤT CẢ TEST ĐỀU PASS!" if all_passed else "⚠️  MỘT SỐ TEST THẤT BẠI"))
    print("="*60 + "\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
