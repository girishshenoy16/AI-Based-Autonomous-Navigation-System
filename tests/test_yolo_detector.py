"""Tests for the YOLO detector module."""

import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()

from src.yolo_detector import YOLODetector


@pytest.fixture
def detector():
    return YOLODetector(model_name="nonexistent_model.pt")


class TestYOLOInit:
    def test_not_active_initially(self, detector):
        assert detector.active is False

    def test_no_detections_initially(self, detector):
        assert len(detector.detections) == 0

    def test_model_not_loaded_with_bad_path(self, detector):
        assert detector.model is None


class TestYOLOToggle:
    def test_toggle_off_when_unavailable(self, detector):
        result = detector.toggle()
        assert result is False
        assert detector.active is False


class TestYOLOAvailability:
    def test_not_available_without_model(self, detector):
        assert detector.is_available() is False


class TestYOLOResults:
    def test_detect_returns_empty_when_inactive(self, detector):
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        result = detector.detect(frame)
        assert result == []

    def test_detect_returns_empty_when_no_model(self, detector):
        detector.active = True
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        result = detector.detect(frame)
        assert result == []

    def test_detect_returns_empty_on_none_frame(self, detector):
        detector.active = True
        result = detector.detect(None)
        assert result == []


class TestYOLORender:
    def test_draw_returns_none_for_none_frame(self, detector):
        result = detector.draw(None)
        assert result is None

    def test_draw_returns_same_shape(self, detector):
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        result = detector.draw(frame)
        assert result.shape == frame.shape

    def test_draw_with_detections(self, detector):
        detector.detections = [
            {"class": 0, "confidence": 0.9, "bbox": (10, 10, 50, 50), "label": "person"}
        ]
        frame = np.zeros((600, 800, 3), dtype=np.uint8)
        result = detector.draw(frame)
        assert result.shape == frame.shape


class TestYOLOObstaclePositions:
    def test_get_obstacle_positions_empty(self, detector):
        positions = detector.get_obstacle_positions(800, 600, 40, 30)
        assert positions == []

    def test_get_obstacle_positions_with_detection(self, detector):
        detector.detections = [
            {"class": 0, "confidence": 0.9, "bbox": (400, 300, 500, 400), "label": "person"}
        ]
        positions = detector.get_obstacle_positions(800, 600, 40, 30)
        assert len(positions) == 1
        col, row = positions[0]
        assert 0 <= col < 40
        assert 0 <= row < 30

    def test_positions_clamped_to_grid(self, detector):
        detector.detections = [
            {"class": 0, "confidence": 0.9, "bbox": (799, 599, 800, 600), "label": "person"}
        ]
        positions = detector.get_obstacle_positions(800, 600, 40, 30)
        col, row = positions[0]
        assert col == 39
        assert row == 29
