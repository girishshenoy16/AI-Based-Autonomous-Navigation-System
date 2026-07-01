"""Tests for the visualization dashboard module."""

import sys
import os
import pytest
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()

from src.visualization import Dashboard
from src import config as cfg


@pytest.fixture
def dashboard():
    return Dashboard()


class TestDashboardInit:
    def test_empty_metrics_history(self, dashboard):
        assert len(dashboard.metrics_history) == 0

    def test_empty_current_run_data(self, dashboard):
        assert dashboard.current_run_data == {}

    def test_empty_last_astar_data(self, dashboard):
        assert dashboard.last_astar_data == {}

    def test_empty_last_dijkstra_data(self, dashboard):
        assert dashboard.last_dijkstra_data == {}


class TestRecordMetrics:
    def test_records_single_run(self, dashboard):
        data = {"algorithm": "astar", "path_length": 42, "state": "REACHED"}
        dashboard.record_metrics(data)
        assert len(dashboard.metrics_history) == 1
        assert dashboard.metrics_history[0]["algorithm"] == "astar"
        assert "timestamp" in dashboard.metrics_history[0]

    def test_records_multiple_runs(self, dashboard):
        for i in range(3):
            data = {"algorithm": "astar", "path_length": i}
            dashboard.record_metrics(data)
        assert len(dashboard.metrics_history) == 3

    def test_current_run_data_updated(self, dashboard):
        data = {"algorithm": "dijkstra", "path_length": 10}
        dashboard.record_metrics(data)
        assert dashboard.current_run_data == data


class TestSaveMetricsCSV:
    def test_save_creates_file(self, dashboard, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg, "METRICS_DIR", str(tmp_path))
        data = {"algorithm": "astar", "path_length": 42, "state": "REACHED",
                "planner_time_ms": 1.5, "total_time_s": 10.0, "replan_count": 0,
                "dynamic_obstacles": 0, "opencv_active": False, "yolo_active": False,
                "sensor_avg": 5.0, "path_index": 42, "nodes_explored": 36}
        dashboard.record_metrics(data)
        filepath = dashboard.save_metrics_csv()
        assert os.path.exists(filepath)

    def test_save_writes_header(self, dashboard, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg, "METRICS_DIR", str(tmp_path))
        data = {"algorithm": "astar", "path_length": 42, "state": "REACHED",
                "planner_time_ms": 1.5, "total_time_s": 10.0, "replan_count": 0,
                "dynamic_obstacles": 0, "opencv_active": False, "yolo_active": False,
                "sensor_avg": 5.0, "path_index": 42, "nodes_explored": 36}
        dashboard.record_metrics(data)
        filepath = dashboard.save_metrics_csv()
        with open(filepath, "r") as f:
            reader = csv.reader(f)
            header = next(reader)
            assert "algorithm" in header
            assert "planner_time_ms" in header

    def test_no_duplicates_on_resave(self, dashboard, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg, "METRICS_DIR", str(tmp_path))
        data = {"algorithm": "astar", "path_length": 42, "state": "REACHED",
                "planner_time_ms": 1.5, "total_time_s": 10.0, "replan_count": 0,
                "dynamic_obstacles": 0, "opencv_active": False, "yolo_active": False,
                "sensor_avg": 5.0, "path_index": 42, "nodes_explored": 36}
        dashboard.record_metrics(data)
        dashboard.save_metrics_csv()
        dashboard.save_metrics_csv()
        filepath = os.path.join(str(tmp_path), "navigation_metrics.csv")
        with open(filepath, "r") as f:
            lines = f.readlines()
            assert len(lines) == 2  # header + 1 data row


class TestChartGeneration:
    def test_generate_path_comparison_chart(self, dashboard, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg, "PLOTS_DIR", str(tmp_path))
        a_data = {"nodes_explored": 36, "path_length": 42, "time_taken": 0.001}
        d_data = {"nodes_explored": 1100, "path_length": 42, "time_taken": 0.005}
        filepath = dashboard.generate_path_comparison_chart(a_data, d_data)
        assert os.path.exists(filepath)

    def test_generate_sensor_chart_empty(self, dashboard, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg, "PLOTS_DIR", str(tmp_path))
        filepath = dashboard.generate_sensor_chart([])
        assert filepath == ""

    def test_generate_sensor_chart_with_data(self, dashboard, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg, "PLOTS_DIR", str(tmp_path))
        history = [[7.0] * 8 for _ in range(10)]
        filepath = dashboard.generate_sensor_chart(history)
        assert os.path.exists(filepath)


class TestScreenshot:
    def test_save_screenshot(self, dashboard, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg, "SCREENSHOTS_DIR", str(tmp_path))
        surface = pygame.Surface((800, 600))
        filepath = dashboard.save_screenshot(surface)
        assert os.path.exists(filepath)
