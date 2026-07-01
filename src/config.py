"""Centralized configuration constants for the AI-Based Autonomous Navigation System."""

import pygame

# ──────────────────────────────────────────────
# Window & Grid
# ──────────────────────────────────────────────
GRID_COLS = 40
GRID_ROWS = 30
CELL_SIZE = 20
INFO_PANEL_WIDTH = 220
WINDOW_WIDTH = GRID_COLS * CELL_SIZE + INFO_PANEL_WIDTH  # 1020
WINDOW_HEIGHT = GRID_ROWS * CELL_SIZE  # 600
FPS = 60

# ──────────────────────────────────────────────
# Colors (R, G, B)
# ──────────────────────────────────────────────
COLOR_FREE = (255, 255, 255)
COLOR_WALL = (64, 64, 64)
COLOR_DYNAMIC_OBSTACLE = (220, 50, 50)
COLOR_START = (0, 200, 0)
COLOR_GOAL = (0, 100, 255)
COLOR_PATH = (255, 220, 0)
COLOR_AGENT = (0, 220, 220)
COLOR_TRAIL = (180, 220, 220)
COLOR_BG = (40, 40, 40)
COLOR_TEXT = (255, 255, 255)
COLOR_PANEL_BG = (30, 30, 30)

# Sensor beam colors
COLOR_BEAM_SAFE = (0, 220, 0)
COLOR_BEAM_CAUTION = (220, 220, 0)
COLOR_BEAM_DANGER = (220, 0, 0)

# A* exploration colors
COLOR_FRONTIER = (173, 216, 230)
COLOR_EXPLORED = (200, 200, 230)
COLOR_CURRENT_NODE = (0, 255, 255)
COLOR_FINAL_PATH = (255, 215, 0)

# Info panel
COLOR_HUD_LABEL = (180, 180, 180)
COLOR_HUD_VALUE = (255, 255, 255)

# ──────────────────────────────────────────────
# Agent Settings
# ──────────────────────────────────────────────
AGENT_SPEED = 6.0  # cells per second
AGENT_RADIUS = 8
SENSOR_RANGE = 7  # max cells the sensor can reach
NUM_SENSORS = 8
SENSOR_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]  # degrees

# ──────────────────────────────────────────────
# Perception Modes
# ──────────────────────────────────────────────
PERCEPTION_SIMULATED = "simulated"
PERCEPTION_OPENCV = "opencv"
PERCEPTION_YOLO = "yolo"

# ──────────────────────────────────────────────
# Path Planning
# ──────────────────────────────────────────────
HEURISTIC_MANHATTAN = "manhattan"
HEURISTIC_EUCLIDEAN = "euclidean"

# Animation speed modes
SPEED_FAST = "fast"
SPEED_MEDIUM = "medium"
SPEED_SLOW = "slow"

ANIMATION_SPEED = SPEED_MEDIUM

# ──────────────────────────────────────────────
# Navigation State Machine
# ──────────────────────────────────────────────
STATE_IDLE = "IDLE"
STATE_PLANNING = "PLANNING"
STATE_MOVING = "MOVING"
STATE_AVOIDING = "AVOIDING"
STATE_REPLANNING = "REPLANNING"
STATE_REACHED = "REACHED"
STATE_NO_PATH = "NO_PATH"

MAX_REPLAN_COUNT = 15
REPLAN_COOLDOWN_MS = 500

# ──────────────────────────────────────────────
# Interactive Controls
# ──────────────────────────────────────────────
KEYBINDINGS = {
    "map_switch": {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
                   pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5},
    "algorithm": {pygame.K_a: "astar", pygame.K_d: "dijkstra"},
    "perception": pygame.K_p,
    "yolo": pygame.K_y,
    "screenshot": pygame.K_s,
    "reset": pygame.K_r,
    "pause": pygame.K_SPACE,
    "quit": pygame.K_ESCAPE,
    "spawn_obstacle": pygame.K_n,
}

# ──────────────────────────────────────────────
# Map Files
# ──────────────────────────────────────────────
MAP_FILES = [
    "maps/map_simple.json",
    "maps/map_maze.json",
    "maps/map_warehouse.json",
    "maps/map_city_grid.json",
    "maps/map_parking_lot.json",
    "maps/map_hospital.json",
]

MAP_NAMES = ["Simple", "Maze", "Warehouse", "City Grid", "Parking Lot", "Hospital"]

DEFAULT_START = (2, 2)
DEFAULT_GOAL = (37, 27)

# ──────────────────────────────────────────────
# Output Paths
# ──────────────────────────────────────────────
SCREENSHOTS_DIR = "outputs/captures"
METRICS_DIR = "outputs/metrics"
PLOTS_DIR = "outputs/plots"
