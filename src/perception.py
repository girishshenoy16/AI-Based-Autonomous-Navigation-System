"""OpenCV-based perception module for visual obstacle detection."""

from typing import List, Tuple

import cv2
import numpy as np
import pygame

from . import config as cfg


class PerceptionModule:
    """Captures Pygame frames and detects obstacles using OpenCV."""

    def __init__(self):
        self.active = False
        self.frame = None
        self.processed_frame = None
        self.detections: List[Tuple[int, int, int, int]] = []  # x, y, w, h

    def toggle(self) -> bool:
        """Toggle perception on/off and return new state."""
        self.active = not self.active
        return self.active

    def capture(self, pygame_surface: pygame.Surface) -> np.ndarray:
        """Capture Pygame surface and convert to OpenCV BGR format."""
        w = pygame_surface.get_width()
        h = pygame_surface.get_height()
        raw = pygame.image.tostring(pygame_surface, "RGB")
        img = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 3))

        # Pygame uses RGB, OpenCV uses BGR
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        self.frame = img_bgr
        return img_bgr

    def process(self, frame: np.ndarray = None) -> np.ndarray:
        """Detect obstacles using contour detection and color filtering."""
        if frame is not None:
            self.frame = frame
        if self.frame is None:
            return np.zeros((cfg.WINDOW_HEIGHT, cfg.WINDOW_WIDTH, 3), dtype=np.uint8)

        img = self.frame.copy()
        self.detections.clear()

        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Detect dark gray walls (HSV ranges for dark gray)
        lower_wall = np.array([0, 0, 30])
        upper_wall = np.array([180, 50, 100])
        mask_wall = cv2.inRange(hsv, lower_wall, upper_wall)

        # Detect red dynamic obstacles
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask_red = cv2.bitwise_or(
            cv2.inRange(hsv, lower_red1, upper_red1),
            cv2.inRange(hsv, lower_red2, upper_red2),
        )

        # Combine masks
        combined = cv2.bitwise_or(mask_wall, mask_red)

        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 50:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                self.detections.append((x, y, w, h))
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        self.processed_frame = img
        return img

    def get_detection_centers(self) -> List[Tuple[int, int]]:
        """Return center positions of all detected obstacles."""
        centers = []
        for x, y, w, h in self.detections:
            centers.append((x + w // 2, y + h // 2))
        return centers

    def draw(self, window_name: str = "Perception View") -> None:
        """Show the processed frame in an OpenCV window."""
        if self.processed_frame is not None:
            display = cv2.resize(self.processed_frame,
                                 (cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
            cv2.imshow(window_name, display)
            cv2.waitKey(1)
        else:
            blank = np.zeros((cfg.WINDOW_HEIGHT, cfg.WINDOW_WIDTH, 3),
                             dtype=np.uint8)
            cv2.putText(blank, "No Frame", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow(window_name, blank)
            cv2.waitKey(1)

    def save_screenshot(self, path: str) -> str:
        """Save current processed frame to file."""
        if self.processed_frame is not None:
            cv2.imwrite(path, self.processed_frame)
            return path
        return ""

    def close(self) -> None:
        """Close OpenCV windows."""
        cv2.destroyAllWindows()
