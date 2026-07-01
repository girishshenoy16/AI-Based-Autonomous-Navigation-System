"""Tests for the perception module (OpenCV)."""

import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()

from src.perception import PerceptionModule


@pytest.fixture
def perception():
    return PerceptionModule()


class TestPerceptionInit:
    def test_not_active_initially(self, perception):
        assert not perception.active

    def test_no_frame_initially(self, perception):
        assert perception.frame is None

    def test_no_detections_initially(self, perception):
        assert len(perception.detections) == 0


class TestPerceptionToggle:
    def test_toggle_on(self, perception):
        result = perception.toggle()
        assert result is True
        assert perception.active is True

    def test_toggle_off(self, perception):
        perception.toggle()
        result = perception.toggle()
        assert result is False
        assert perception.active is False


class TestFrameCapture:
    def test_capture_returns_array(self, perception):
        surface = pygame.Surface((800, 600))
        frame = perception.capture(surface)
        assert isinstance(frame, np.ndarray)
        assert frame.shape == (600, 800, 3)

    def test_capture_converts_to_bgr(self, perception):
        surface = pygame.Surface((100, 100))
        surface.fill((255, 0, 0))  # Red in RGB
        frame = perception.capture(surface)
        # In BGR, red should be (0, 0, 255)
        assert frame[50, 50, 2] > 200  # R channel high in BGR for red


class TestProcessing:
    def test_process_empty_frame(self, perception):
        result = perception.process()
        assert isinstance(result, np.ndarray)

    def test_process_with_frame(self, perception):
        surface = pygame.Surface((800, 600))
        surface.fill((255, 255, 255))
        perception.capture(surface)
        result = perception.process()
        assert isinstance(result, np.ndarray)
