import os
import cv2
from detector import FaceDetector


IMAGE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "data", "test.jpg"
)
RESULT_DIR = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "results"
)


def main():
    os.makedirs(RESULT_DIR, exist_ok=True)

    if not os.path.exists(IMAGE_PATH):
        print("Chua co file data/test.jpg")
        print("Hay dat mot anh co 1 hoac nhieu khuon mat vao data/test.jpg")
        return

    detector = FaceDetector()
    results = detector.detect(IMAGE_PATH)

    image = cv2.imread(IMAGE_PATH)
    drawn = detector.draw_detections(image, results)

    detection_path = os.path.join(RESULT_DIR, "detection_result.jpg")
    cv2.imwrite(detection_path, drawn)

    print("So khuon mat:", len(results))
    print("Anh detection:", detection_path)

    for i, result in enumerate(results, start=1):
        aligned_path = os.path.join(
            RESULT_DIR, f"aligned_face_{i}.jpg"
        )
        cv2.imwrite(aligned_path, result["face"])

        print(f"\nKhuon mat {i}")
        print("Bounding Box:", result["bbox"])
        print("5 Landmarks:", result["landmarks"])
        print("Aligned:", aligned_path)


if __name__ == "__main__":
    main()
