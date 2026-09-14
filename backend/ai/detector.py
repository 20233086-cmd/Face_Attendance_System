import cv2
from detector import FaceDetector


def main():
    detector = FaceDetector()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Khong mo duoc webcam.")
        return

    print("Nhan Q de thoat.")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        results = detector.detect_frame(frame)
        display = detector.draw_detections(frame, results)

        cv2.putText(
            display,
            f"Faces: {len(results)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )

        cv2.imshow("Thanh vien 1 - AI Detect", display)

        if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
