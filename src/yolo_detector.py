"""Optional YOLOv8-nano object detection module."""

from typing import List, Tuple, Optional

import numpy as np

from . import config as cfg

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class YOLODetector:
    """YOLOv8-nano based object detection (optional)."""

    def __init__(self, model_name: str = "outputs/models/yolov8n.pt"):
        self.active = False
        self.model = None
        self.model_name = model_name
        self.detections: List[dict] = []

        if YOLO_AVAILABLE:
            try:
                self.model = YOLO(model_name)
                print(f"[INFO] YOLO model loaded: {model_name}")
            except Exception:
                print(f"[WARN] YOLO model not found: {model_name}")
                print("[WARN] Download it or press Y to disable YOLO")
                self.model = None

    def is_available(self) -> bool:
        """Check if YOLO is installed and model is loaded."""
        return YOLO_AVAILABLE and self.model is not None

    def toggle(self) -> bool:
        """Toggle detection on/off."""
        if self.is_available():
            self.active = not self.active
        return self.active

    def detect(self, frame: np.ndarray) -> List[dict]:
        """Run YOLO inference on a frame.

        Returns list of dicts with keys: class, confidence, bbox (x1,y1,x2,y2).
        """
        if not self.active or not self.is_available() or frame is None:
            return []

        self.detections.clear()
        results = self.model(frame, verbose=False)

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    self.detections.append({
                        "class": cls,
                        "confidence": conf,
                        "bbox": (int(x1), int(y1), int(x2), int(y2)),
                        "label": self.model.names.get(cls, "unknown"),
                    })

        return self.detections

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """Draw bounding boxes and labels on the frame."""
        if frame is None:
            return frame

        img = frame.copy()
        for det in self.detections:
            x1, y1, x2, y2 = det["bbox"]
            label = f"{det['label']} {det['confidence']:.2f}"

            try:
                import cv2
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(img, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            except ImportError:
                pass

        return img

    def get_obstacle_positions(self, frame_width: int, frame_height: int,
                               grid_cols: int, grid_rows: int) -> List[Tuple[int, int]]:
        """Convert YOLO detections to grid cell positions."""
        grid_positions = []
        for det in self.detections:
            x1, y1, x2, y2 = det["bbox"]
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Map pixel coords to grid coords
            col = int(cx * grid_cols / frame_width)
            row = int(cy * grid_rows / frame_height)

            col = max(0, min(col, grid_cols - 1))
            row = max(0, min(row, grid_rows - 1))
            grid_positions.append((col, row))

        return grid_positions
