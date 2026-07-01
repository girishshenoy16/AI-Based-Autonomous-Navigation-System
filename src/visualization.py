"""Visualization dashboard with HUD, charts, screenshots, and metrics export."""

import csv
import os
import time
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pygame

from . import config as cfg


# ── Chart style constants ──
plt.rcParams.update({
    "figure.facecolor": "#1e1e1e",
    "axes.facecolor": "#2d2d2d",
    "axes.edgecolor": "#555555",
    "axes.labelcolor": "#cccccc",
    "text.color": "#ffffff",
    "xtick.color": "#aaaaaa",
    "ytick.color": "#aaaaaa",
    "grid.color": "#444444",
    "grid.alpha": 0.4,
    "font.size": 10,
})

COLOR_ASTAR = "#00DCEC"
COLOR_DIJKSTRA = "#FFD700"
SENSOR_COLORS = ["#00DCEC", "#00CC00", "#FFD700", "#FF6600",
                 "#FF0000", "#CC00FF", "#0066FF", "#FF00CC"]


class Dashboard:
    """Real-time HUD overlay and analytics dashboard."""

    def __init__(self):
        self.font = pygame.font.SysFont("consolas", 11)
        self.font_bold = pygame.font.SysFont("consolas", 11, bold=True)
        self.metrics_history: List[Dict] = []
        self.current_run_data: Dict = {}
        self.last_astar_data: Dict = {}
        self.last_dijkstra_data: Dict = {}
        self._last_saved_count = 0

    def update_hud(self, surface: pygame.Surface, nav_status: dict,
                   sensor_readings: list, opencv_active: bool = False,
                   yolo_active: bool = False) -> None:
        """Draw real-time HUD information on the info panel."""
        panel_x = cfg.GRID_COLS * cfg.CELL_SIZE + 10
        panel_w = cfg.INFO_PANEL_WIDTH - 20
        y = 8

        bg_rect = pygame.Rect(cfg.GRID_COLS * cfg.CELL_SIZE, 0,
                              cfg.INFO_PANEL_WIDTH, cfg.WINDOW_HEIGHT)
        pygame.draw.rect(surface, cfg.COLOR_PANEL_BG, bg_rect)

        def text(txt, yy, color=cfg.COLOR_HUD_LABEL, bold=False):
            f = self.font_bold if bold else self.font
            surf = f.render(txt, True, color)
            surface.blit(surf, (panel_x, yy))

        def colored_bar(ratio, yy, width=80):
            if ratio > 0.7:
                c = cfg.COLOR_BEAM_SAFE
            elif ratio > 0.3:
                c = cfg.COLOR_BEAM_CAUTION
            else:
                c = cfg.COLOR_BEAM_DANGER
            bw = int(ratio * width)
            pygame.draw.rect(surface, c, (panel_x, yy, bw, 7))
            pygame.draw.rect(surface, (60, 60, 60), (panel_x, yy, width, 7), 1)

        # ── Section: Status ──
        text("STATUS", y, cfg.COLOR_AGENT, bold=True)
        y += 16

        state = nav_status.get("state", "N/A")
        state_colors = {
            cfg.STATE_IDLE: cfg.COLOR_HUD_LABEL,
            cfg.STATE_PLANNING: cfg.COLOR_BEAM_CAUTION,
            cfg.STATE_MOVING: cfg.COLOR_BEAM_SAFE,
            cfg.STATE_AVOIDING: cfg.COLOR_BEAM_DANGER,
            cfg.STATE_REPLANNING: cfg.COLOR_BEAM_CAUTION,
            cfg.STATE_REACHED: cfg.COLOR_AGENT,
            cfg.STATE_NO_PATH: cfg.COLOR_BEAM_DANGER,
        }
        sc = state_colors.get(state, cfg.COLOR_HUD_VALUE)

        text(f"State:  {state}", y, sc)
        y += 15
        text(f"Algo:   {nav_status.get('algorithm', '').upper()}", y)
        y += 15
        text(f"Path:   {nav_status.get('path_length', 0)} cells", y)
        y += 15
        text(f"Step:   {nav_status.get('path_index', 0)}/{nav_status.get('path_length', 0)}", y)
        y += 15
        text(f"Replans:{nav_status.get('replan_count', 0)}", y)
        y += 15
        text(f"Nodes:  {nav_status.get('nodes_explored', 0)}", y)
        y += 15
        ms = nav_status.get('planner_time', 0) * 1000
        text(f"Time:   {ms:.1f}ms", y)
        y += 15

        cv_color = cfg.COLOR_BEAM_SAFE if opencv_active else cfg.COLOR_HUD_LABEL
        cv_status = "ON" if opencv_active else "OFF"
        text(f"OpenCV: {cv_status}", y, cv_color)
        y += 15

        yolo_color = cfg.COLOR_BEAM_SAFE if yolo_active else cfg.COLOR_HUD_LABEL
        yolo_status = "ON" if yolo_active else "OFF"
        text(f"YOLO:   {yolo_status}", y, yolo_color)
        y += 20

        # ── Section: Sensors ──
        pygame.draw.line(surface, (60, 60, 60), (panel_x, y), (panel_x + panel_w, y), 1)
        y += 4
        text("SENSORS", y, cfg.COLOR_BEAM_CAUTION, bold=True)
        y += 16

        for i, reading in enumerate(sensor_readings):
            colored_bar(reading.distance / cfg.SENSOR_RANGE, y)
            y += 10

        y += 6

        # ── Section: Controls ──
        pygame.draw.line(surface, (60, 60, 60), (panel_x, y), (panel_x + panel_w, y), 1)
        y += 4
        text("CONTROLS", y, cfg.COLOR_BEAM_CAUTION, bold=True)
        y += 16

        controls = [
            "SPACE  Start/Pause",
            "R      Reset",
            "1-6    Switch map",
            "A/D    A*/Dijkstra",
            "P      OpenCV",
            "Y      YOLO detect",
            "S      Screenshot",
            "N      Spawn obstacle",
            "ESC    Quit",
        ]
        for ctrl in controls:
            text(ctrl, y, (130, 130, 130))
            y += 13

        y += 4
        pygame.draw.line(surface, (60, 60, 60), (panel_x, y), (panel_x + panel_w, y), 1)
        y += 4
        text("MOUSE", y, cfg.COLOR_BEAM_CAUTION, bold=True)
        y += 16

        mouse = [
            "Left-click   Add wall",
            "Right-click  Remove",
            "Middle-click Set goal",
        ]
        for m in mouse:
            text(m, y, (130, 130, 130))
            y += 13

    # ──────────────────────────────────────────
    # Metrics & Charts
    # ──────────────────────────────────────────
    def record_metrics(self, run_data: Dict) -> None:
        run_data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.metrics_history.append(run_data)
        self.current_run_data = run_data

    def save_metrics_csv(self, filename: str = None) -> str:
        os.makedirs(cfg.METRICS_DIR, exist_ok=True)
        filepath = os.path.join(cfg.METRICS_DIR, "navigation_metrics.csv")

        new_rows = self.metrics_history[self._last_saved_count:]
        if not new_rows:
            return filepath

        file_exists = os.path.isfile(filepath) and os.path.getsize(filepath) > 0
        ordered_keys = [
            "timestamp", "map", "algorithm", "state",
            "path_length", "path_index", "nodes_explored",
            "planner_time_ms", "total_time_s", "replan_count",
            "dynamic_obstacles", "opencv_active", "yolo_active",
            "sensor_avg"
        ]
        with open(filepath, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=ordered_keys)
            if not file_exists:
                writer.writeheader()
            for row in new_rows:
                writer.writerow(row)

        self._last_saved_count = len(self.metrics_history)
        return filepath

    def generate_path_comparison_chart(self, astar_data: Dict,
                                       dijkstra_data: Dict) -> str:
        os.makedirs(cfg.PLOTS_DIR, exist_ok=True)

        fig, axes = plt.subplots(1, 3, figsize=(14, 5))
        fig.suptitle("A* vs Dijkstra — Performance Comparison",
                     fontsize=14, fontweight="bold", color="#ffffff")

        metrics = ["nodes_explored", "path_length", "time_taken"]
        labels = ["Nodes Explored", "Path Length", "Time (s)"]

        for ax, metric, label in zip(axes, metrics, labels):
            v1 = astar_data.get(metric, 0)
            v2 = dijkstra_data.get(metric, 0)
            bars = ax.bar(["A*", "Dijkstra"], [v1, v2],
                          color=[COLOR_ASTAR, COLOR_DIJKSTRA], width=0.5,
                          edgecolor="#555555", linewidth=0.8)
            ax.set_title(label, fontsize=11, fontweight="bold")
            ax.set_ylabel("Value")
            for bar, val in zip(bars, [v1, v2]):
                txt = f"{val:.3f}" if isinstance(val, float) else str(val)
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                        txt, ha="center", va="bottom", fontsize=10,
                        color="#ffffff", fontweight="bold")
            ax.grid(True, axis="y", alpha=0.3)

        plt.tight_layout(rect=[0, 0, 1, 0.93])
        filepath = os.path.join(cfg.PLOTS_DIR, "path_comparison.png")
        plt.savefig(filepath, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        return filepath

    def generate_sensor_chart(self, sensor_history: List[List[float]]) -> str:
        os.makedirs(cfg.PLOTS_DIR, exist_ok=True)
        if not sensor_history:
            return ""

        fig, ax = plt.subplots(figsize=(12, 5))
        fig.suptitle("Sensor Readings Over Time", fontsize=14,
                     fontweight="bold", color="#ffffff")

        x = np.arange(len(sensor_history))
        for i in range(min(cfg.NUM_SENSORS, len(SENSOR_COLORS))):
            values = [r[i] if i < len(r) else 0 for r in sensor_history]
            ax.plot(x, values, label=f"Sensor {i}", color=SENSOR_COLORS[i],
                    linewidth=1.5, alpha=0.85)

        ax.set_xlabel("Time Step")
        ax.set_ylabel("Distance (cells)")
        ax.set_ylim(0, cfg.SENSOR_RANGE + 1)
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.legend(fontsize=9, loc="upper right", framealpha=0.7,
                  facecolor="#2d2d2d", edgecolor="#555555")
        ax.grid(True, alpha=0.3)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        filepath = os.path.join(cfg.PLOTS_DIR, "sensor_readings.png")
        plt.savefig(filepath, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        return filepath

    def save_screenshot(self, surface: pygame.Surface,
                        filename: str = None) -> str:
        os.makedirs(cfg.SCREENSHOTS_DIR, exist_ok=True)
        if filename is None:
            filename = f"screenshot_{time.strftime('%Y-%m-%d_%H-%M-%S')}.png"
        filepath = os.path.join(cfg.SCREENSHOTS_DIR, filename)
        pygame.image.save(surface, filepath)
        return filepath
