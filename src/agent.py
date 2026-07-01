"""Robot/car agent with sensors, smooth movement, and collision detection."""

import math
from typing import List, Optional, Tuple

import pygame

from . import config as cfg


class SensorReading:
    """Single sensor beam reading."""

    def __init__(self, angle_deg: float, distance: float, hit: bool,
                 hit_pos: Optional[Tuple[float, float]] = None):
        self.angle_deg = angle_deg
        self.distance = distance
        self.hit = hit
        self.hit_pos = hit_pos


class Agent:
    """Autonomous robot/car entity with 8-direction raycasting sensors."""

    def __init__(self, start: Tuple[int, int], grid_world):
        self.grid_world = grid_world
        self.x = float(start[0]) + 0.5
        self.y = float(start[1]) + 0.5
        self.heading = 0.0  # degrees, 0 = right
        self.speed = cfg.AGENT_SPEED
        self.radius = cfg.AGENT_RADIUS

        # Path following
        self.path: List[Tuple[int, int]] = []
        self.path_index = 0
        self.target_x = self.x
        self.target_y = self.y

        # Trail history
        self.trail: List[Tuple[float, float]] = []
        self.max_trail_length = 200

        # Sensor data
        self.sensor_readings: List[SensorReading] = []

        # State
        self.moving = False
        self.reached_goal = False

    def reset(self, start: Tuple[int, int]) -> None:
        """Reset agent to a starting position."""
        self.x = float(start[0]) + 0.5
        self.y = float(start[1]) + 0.5
        self.heading = 0.0
        self.path.clear()
        self.path_index = 0
        self.trail.clear()
        self.sensor_readings.clear()
        self.moving = False
        self.reached_goal = False

    def set_path(self, path: List[Tuple[int, int]]) -> None:
        """Set the path for the agent to follow."""
        self.path = list(path)
        self.path_index = 0
        self.moving = True
        self.reached_goal = False
        if self.path:
            self._set_next_target()

    def _set_next_target(self) -> None:
        """Set the next waypoint target."""
        if self.path_index < len(self.path):
            cell = self.path[self.path_index]
            self.target_x = float(cell[0]) + 0.5
            self.target_y = float(cell[1]) + 0.5

    def update(self, dt: float) -> None:
        """Update agent position with smooth interpolation.

        Args:
            dt: Delta time in seconds.
        """
        if not self.moving or self.reached_goal:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)

        if dist < 0.05:
            # Reached current waypoint
            self.x = self.target_x
            self.y = self.target_y
            self.trail.append((self.x, self.y))
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)

            self.path_index += 1
            if self.path_index >= len(self.path):
                self.moving = False
                self.reached_goal = True
                return
            self._set_next_target()
        else:
            # Move toward target
            move_dist = self.speed * dt
            if move_dist > dist:
                move_dist = dist
            ratio = move_dist / dist
            self.x += dx * ratio
            self.y += dy * ratio

            # Update heading
            self.heading = math.degrees(math.atan2(dy, dx))

    def get_grid_pos(self) -> Tuple[int, int]:
        """Get the current grid cell position."""
        return (int(self.x), int(self.y))

    # ──────────────────────────────────────────
    # Sensor / Raycasting
    # ──────────────────────────────────────────
    def sense(self) -> List[SensorReading]:
        """Cast 8 sensor rays and return readings."""
        self.sensor_readings.clear()
        grid = self.grid_world

        for angle_deg in cfg.SENSOR_ANGLES:
            angle_rad = math.radians(angle_deg)
            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)

            hit = False
            hit_pos = None
            dist = cfg.SENSOR_RANGE

            for step in range(1, cfg.SENSOR_RANGE + 1):
                check_x = int(self.x + dx * step - 0.5)
                check_y = int(self.y + dy * step - 0.5)

                if grid.is_wall(check_x, check_y):
                    dist = step
                    hit = True
                    hit_pos = (self.x + dx * step, self.y + dy * step)
                    break

            reading = SensorReading(
                angle_deg=angle_deg,
                distance=float(dist),
                hit=hit,
                hit_pos=hit_pos,
            )
            self.sensor_readings.append(reading)

        return self.sensor_readings

    # ──────────────────────────────────────────
    # Collision Detection
    # ──────────────────────────────────────────
    def check_collision(self) -> bool:
        """Check if agent collides with any obstacle."""
        gx, gy = self.get_grid_pos()
        return self.grid_world.is_wall(gx, gy)

    def is_near_obstacle(self, threshold: float = 1.5) -> bool:
        """Check if any sensor detects an obstacle within threshold."""
        for reading in self.sensor_readings:
            if reading.hit and reading.distance <= threshold:
                return True
        return False

    # ──────────────────────────────────────────
    # Rendering
    # ──────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the agent, sensor beams, and trail."""
        self._draw_trail(surface)
        self._draw_sensors(surface)
        self._draw_body(surface)

    def _draw_trail(self, surface: pygame.Surface) -> None:
        """Draw fading trail behind the agent."""
        if len(self.trail) < 2:
            return
        for i in range(1, len(self.trail)):
            brightness = int(128 + 127 * (i / len(self.trail)))
            color = (brightness, brightness, brightness)
            p1 = (int(self.trail[i - 1][0] * cfg.CELL_SIZE),
                   int(self.trail[i - 1][1] * cfg.CELL_SIZE))
            p2 = (int(self.trail[i][0] * cfg.CELL_SIZE),
                   int(self.trail[i][1] * cfg.CELL_SIZE))
            pygame.draw.line(surface, color, p1, p2, 2)

    def _draw_sensors(self, surface: pygame.Surface) -> None:
        """Draw color-coded sensor beams (green/yellow/red)."""
        agent_px = int(self.x * cfg.CELL_SIZE)
        agent_py = int(self.y * cfg.CELL_SIZE)

        for reading in self.sensor_readings:
            ratio = reading.distance / cfg.SENSOR_RANGE

            if ratio > 0.7:
                color = cfg.COLOR_BEAM_SAFE
            elif ratio > 0.3:
                color = cfg.COLOR_BEAM_CAUTION
            else:
                color = cfg.COLOR_BEAM_DANGER

            # Beam thickness: thicker when closer danger
            thickness = max(1, int((1 - ratio) * 3) + 1)

            angle_rad = math.radians(reading.angle_deg)
            end_x = agent_px + math.cos(angle_rad) * reading.distance * cfg.CELL_SIZE
            end_y = agent_py + math.sin(angle_rad) * reading.distance * cfg.CELL_SIZE

            pygame.draw.line(surface, color, (agent_px, agent_py),
                             (int(end_x), int(end_y)), thickness)

    def _draw_body(self, surface: pygame.Surface) -> None:
        """Draw the agent body as a circle with heading indicator."""
        center = (int(self.x * cfg.CELL_SIZE), int(self.y * cfg.CELL_SIZE))

        # Main body
        pygame.draw.circle(surface, cfg.COLOR_AGENT, center, self.radius)

        # Heading indicator (small line showing direction)
        heading_rad = math.radians(self.heading)
        end_x = center[0] + math.cos(heading_rad) * self.radius
        end_y = center[1] + math.sin(heading_rad) * self.radius
        pygame.draw.line(surface, cfg.COLOR_BG, center, (int(end_x), int(end_y)), 2)
