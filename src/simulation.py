"""Pygame 2D Grid World simulation engine."""

import json
import math
import random
import sys
from typing import List, Optional, Tuple

import pygame

from . import config as cfg


class GridWorld:
    """2D grid-based simulation environment with obstacles, start, and goal."""

    def __init__(self, map_path: Optional[str] = None):
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.WINDOW_WIDTH, cfg.WINDOW_HEIGHT))
        pygame.display.set_caption("AI-Based Autonomous Navigation System")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 14)
        self.font_small = pygame.font.SysFont("consolas", 11)

        self.grid: List[List[int]] = []
        self.obstacles: set = set()
        self.dynamic_obstacles: set = set()
        self.start: Tuple[int, int] = cfg.DEFAULT_START
        self.goal: Tuple[int, int] = cfg.DEFAULT_GOAL
        self.path: List[Tuple[int, int]] = []
        self.current_map_index = 0

        # A* exploration overlay data
        self.frontier_nodes: set = set()
        self.explored_nodes: set = set()
        self.current_node: Optional[Tuple[int, int]] = None
        self.overlay_active = False

        if map_path:
            self.load_map(map_path)

    # ──────────────────────────────────────────
    # Map Management
    # ──────────────────────────────────────────
    def load_map(self, map_path: str) -> None:
        """Load a JSON map file and populate the grid."""
        with open(map_path, "r") as f:
            data = json.load(f)

        self.grid = []
        self.obstacles.clear()
        self.dynamic_obstacles.clear()

        rows = data.get("rows", cfg.GRID_ROWS)
        cols = data.get("cols", cfg.GRID_COLS)
        if not isinstance(rows, int) or rows <= 0:
            rows = cfg.GRID_ROWS
        if not isinstance(cols, int) or cols <= 0:
            cols = cfg.GRID_COLS

        raw_walls = data.get("walls", [])
        if not isinstance(raw_walls, list):
            raw_walls = []

        wall_set = set()
        for w in raw_walls:
            if isinstance(w, list) and len(w) == 2:
                wr, wc = w
                if isinstance(wr, int) and isinstance(wc, int):
                    wall_set.add((wr, wc))

        for r in range(rows):
            row = []
            for c in range(cols):
                if (r, c) in wall_set:
                    row.append(1)
                    self.obstacles.add((c, r))
                else:
                    row.append(0)
            self.grid.append(row)

        start = data.get("start", list(cfg.DEFAULT_START))
        goal = data.get("goal", list(cfg.DEFAULT_GOAL))
        if (isinstance(start, list) and len(start) == 2 and
                isinstance(start[0], int) and isinstance(start[1], int)):
            self.start = tuple(start)
        else:
            self.start = cfg.DEFAULT_START
        if (isinstance(goal, list) and len(goal) == 2 and
                isinstance(goal[0], int) and isinstance(goal[1], int)):
            self.goal = tuple(goal)
        else:
            self.goal = cfg.DEFAULT_GOAL

        self.path.clear()
        self.clear_overlay()

    def load_map_by_index(self, index: int) -> str:
        """Load map by index and return its name."""
        index = max(0, min(index, len(cfg.MAP_FILES) - 1))
        self.current_map_index = index
        self.load_map(cfg.MAP_FILES[index])
        return cfg.MAP_NAMES[index]

    def is_wall(self, col: int, row: int) -> bool:
        """Check if a cell is a wall or out of bounds."""
        if col < 0 or col >= cfg.GRID_COLS or row < 0 or row >= cfg.GRID_ROWS:
            return True
        if self.grid[row][col] == 1:
            return True
        if (col, row) in self.dynamic_obstacles:
            return True
        return False

    def is_free(self, col: int, row: int) -> bool:
        """Check if a cell is free (not wall, not out of bounds)."""
        return not self.is_wall(col, row)

    def set_cell(self, col: int, row: int, value: int) -> None:
        """Set a cell value and update the obstacles set."""
        if 0 <= col < cfg.GRID_COLS and 0 <= row < cfg.GRID_ROWS:
            self.grid[row][col] = value
            if value == 1:
                self.obstacles.add((col, row))
            else:
                self.obstacles.discard((col, row))

    def add_dynamic_obstacle(self, col: int, row: int) -> None:
        """Add a dynamic obstacle at runtime."""
        if self.is_free(col, row) and (col, row) != self.start and (col, row) != self.goal:
            self.dynamic_obstacles.add((col, row))

    def remove_dynamic_obstacle(self, col: int, row: int) -> None:
        """Remove a dynamic obstacle."""
        self.dynamic_obstacles.discard((col, row))

    def spawn_random_obstacle(self) -> Optional[Tuple[int, int]]:
        """Spawn a random dynamic obstacle on a free cell."""
        attempts = 0
        while attempts < 100:
            c = random.randint(0, cfg.GRID_COLS - 1)
            r = random.randint(0, cfg.GRID_ROWS - 1)
            if self.is_free(c, r) and (c, r) != self.start and (c, r) != self.goal:
                self.add_dynamic_obstacle(c, r)
                return (c, r)
            attempts += 1
        return None

    def set_goal(self, col: int, row: int) -> None:
        """Set a new goal position."""
        if self.is_free(col, row) and (col, row) != self.start:
            self.goal = (col, row)
            self.path.clear()

    def is_path_blocked(self) -> bool:
        """Check if any cell on the current path is blocked."""
        for cell in self.path:
            if self.is_wall(cell[0], cell[1]):
                return True
        return False

    # ──────────────────────────────────────────
    # Rendering
    # ──────────────────────────────────────────
    def pixel_to_grid(self, px: int, py: int) -> Optional[Tuple[int, int]]:
        """Convert pixel coordinates to grid cell (col, row)."""
        if px >= cfg.GRID_COLS * cfg.CELL_SIZE or py >= cfg.GRID_ROWS * cfg.CELL_SIZE:
            return None
        col = px // cfg.CELL_SIZE
        row = py // cfg.CELL_SIZE
        return (col, row)

    def render(self) -> None:
        """Render the entire grid world to the screen."""
        self.screen.fill(cfg.COLOR_BG)
        self._draw_grid()
        self._draw_path()
        self._draw_overlay()
        self._draw_start_goal()
        self._draw_dynamic_obstacles()

    def _draw_grid(self) -> None:
        """Draw the grid cells (walls and free spaces)."""
        for r in range(cfg.GRID_ROWS):
            for c in range(cfg.GRID_COLS):
                rect = pygame.Rect(c * cfg.CELL_SIZE, r * cfg.CELL_SIZE,
                                   cfg.CELL_SIZE, cfg.CELL_SIZE)
                if self.grid[r][c] == 1:
                    pygame.draw.rect(self.screen, cfg.COLOR_WALL, rect)
                else:
                    pygame.draw.rect(self.screen, cfg.COLOR_FREE, rect)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def _draw_path(self) -> None:
        """Draw the computed path as gold cells."""
        for cell in self.path:
            rect = pygame.Rect(cell[0] * cfg.CELL_SIZE, cell[1] * cfg.CELL_SIZE,
                               cfg.CELL_SIZE, cfg.CELL_SIZE)
            pygame.draw.rect(self.screen, cfg.COLOR_FINAL_PATH, rect)

    def _draw_start_goal(self) -> None:
        """Draw start (green) and goal (blue) markers."""
        for pos, color in [(self.start, cfg.COLOR_START), (self.goal, cfg.COLOR_GOAL)]:
            center = (pos[0] * cfg.CELL_SIZE + cfg.CELL_SIZE // 2,
                      pos[1] * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
            pygame.draw.circle(self.screen, color, center, cfg.CELL_SIZE // 2 - 2)

    def _draw_dynamic_obstacles(self) -> None:
        """Draw dynamic obstacles in red."""
        for obs in self.dynamic_obstacles:
            rect = pygame.Rect(obs[0] * cfg.CELL_SIZE + 2, obs[1] * cfg.CELL_SIZE + 2,
                               cfg.CELL_SIZE - 4, cfg.CELL_SIZE - 4)
            pygame.draw.rect(self.screen, cfg.COLOR_DYNAMIC_OBSTACLE, rect)

    def _draw_overlay(self) -> None:
        """Draw A* exploration overlay (frontier, explored, current, final path)."""
        if not self.overlay_active:
            return
        for node in self.explored_nodes:
            rect = pygame.Rect(node[0] * cfg.CELL_SIZE + 4, node[1] * cfg.CELL_SIZE + 4,
                               cfg.CELL_SIZE - 8, cfg.CELL_SIZE - 8)
            pygame.draw.rect(self.screen, cfg.COLOR_EXPLORED, rect)
        for node in self.frontier_nodes:
            rect = pygame.Rect(node[0] * cfg.CELL_SIZE + 4, node[1] * cfg.CELL_SIZE + 4,
                               cfg.CELL_SIZE - 8, cfg.CELL_SIZE - 8)
            pygame.draw.rect(self.screen, cfg.COLOR_FRONTIER, rect)
        if self.current_node:
            center = (self.current_node[0] * cfg.CELL_SIZE + cfg.CELL_SIZE // 2,
                      self.current_node[1] * cfg.CELL_SIZE + cfg.CELL_SIZE // 2)
            pygame.draw.circle(self.screen, cfg.COLOR_CURRENT_NODE, center, cfg.CELL_SIZE // 3)

    def _draw_info_panel(self) -> None:
        """Draw the right-side information panel."""
        panel_x = cfg.GRID_COLS * cfg.CELL_SIZE
        panel_rect = pygame.Rect(panel_x, 0, cfg.INFO_PANEL_WIDTH, cfg.WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, cfg.COLOR_PANEL_BG, panel_rect)

        lines = [
            f"Map: {cfg.MAP_NAMES[self.current_map_index]}",
            f"Grid: {cfg.GRID_COLS}x{cfg.GRID_ROWS}",
            f"Walls: {len(self.obstacles)}",
            f"Dynamic: {len(self.dynamic_obstacles)}",
            f"Start: {self.start}",
            f"Goal: {self.goal}",
            f"Path len: {len(self.path)}",
            f"",
            f"--- Controls ---",
            f"1-6: Switch map",
            f"A/D: Algorithm",
            f"P: Perception",
            f"Y: YOLO detect",
            f"S: Screenshot",
            f"R: Reset",
            f"SPACE: Pause",
            f"N: Spawn obstacle",
            f"ESC: Quit",
            f"",
            f"Click: Add obstacle",
            f"Right-click: Remove",
            f"Middle-click: Set goal",
        ]

        y = 10
        for line in lines:
            if line.startswith("---"):
                text = self.font_small.render(line, True, cfg.COLOR_BEAM_CAUTION)
            else:
                text = self.font_small.render(line, True, cfg.COLOR_TEXT)
            self.screen.blit(text, (panel_x + 8, y))
            y += 16

    # ──────────────────────────────────────────
    # Overlay Management
    # ──────────────────────────────────────────
    def clear_overlay(self) -> None:
        """Clear the A* exploration overlay data."""
        self.frontier_nodes.clear()
        self.explored_nodes.clear()
        self.current_node = None
        self.overlay_active = False

    def set_overlay(self, frontier: set, explored: set,
                    current: Optional[Tuple[int, int]]) -> None:
        """Update the A* exploration overlay data."""
        self.frontier_nodes = frontier
        self.explored_nodes = explored
        self.current_node = current
        self.overlay_active = True

    # ──────────────────────────────────────────
    # Frame Capture
    # ──────────────────────────────────────────
    def capture_frame(self):
        """Capture the current Pygame surface as a raw surface for OpenCV/YOLO."""
        return self.screen.copy()

    # ──────────────────────────────────────────
    # Main Loop Helper
    # ──────────────────────────────────────────
    def tick(self) -> int:
        """Advance one frame; returns delta time in milliseconds."""
        pygame.display.flip()
        return self.clock.tick(cfg.FPS)

    def quit(self) -> None:
        """Clean up Pygame."""
        pygame.quit()
