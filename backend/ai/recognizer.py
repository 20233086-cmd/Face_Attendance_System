"""
Face Detection + Alignment module
Thanh vien 1 - AI Detect

Input : image path / OpenCV frame
Output: detected faces with bounding boxes, 5 landmarks and aligned crops.
"""

from typing import Any, Dict, List, Optional
import cv2
from insightface.app import FaceAnalysis
from insightface.utils import face_align


class FaceDetector:
    """Detect faces with RetinaFace (via InsightFace) and align them."""

    def __init__(
        self,
        model_name: str = "buffalo_l",
        det_size: tuple = (640, 640),
        providers: Optional[list] = None,
    ):
        if providers is None:
            providers = ["CPUExecutionProvider"]

        self.app = FaceAnalysis(
            name=model_name,
            providers=providers
        )
        # -1: CPU. Change to 0 when using a supported GPU provider.
        self.app.prepare(ctx_id=-1, det_size=det_size)

    @staticmethod
    def _process(img, faces) -> List[Dict[str, Any]]:
        results = []

        for face in faces:
            bbox = face.bbox.astype(int).tolist()
            landmarks = face.kps.tolist()

            aligned = face_align.norm_crop(
                img,
                landmark=face.kps,
                image_size=112
            )

            results.append({
                "bbox": bbox,
                "landmarks": landmarks,
                "face": aligned
            })

        return results

    def detect(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect faces from an image file.

        Returns a list. Each item contains:
        - bbox: [x1, y1, x2, y2]
        - landmarks: 5 facial landmarks
        - face: aligned 112x112 BGR image
        """
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Khong the doc anh: {image_path}")

        faces = self.app.get(img)
        return self._process(img, faces)

    def detect_frame(self, frame) -> List[Dict[str, Any]]:
        """Detect faces directly from an OpenCV BGR frame."""
        if frame is None or frame.size == 0:
            raise ValueError("Frame rong hoac khong hop le.")

        faces = self.app.get(frame)
        return self._process(frame, faces)

    @staticmethod
    def draw_detections(frame, results):
        """Draw bounding boxes and 5 landmarks for demonstration."""
        output = frame.copy()

        for idx, result in enumerate(results, start=1):
            x1, y1, x2, y2 = result["bbox"]

            cv2.rectangle(
                output, (x1, y1), (x2, y2),
                (0, 255, 0), 2
            )

            for x, y in result["landmarks"]:
                cv2.circle(
                    output, (int(x), int(y)),
                    3, (0, 0, 255), -1
                )

            cv2.putText(
                output,
                f"Face {idx}",
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 0),
                2
            )

        return output
