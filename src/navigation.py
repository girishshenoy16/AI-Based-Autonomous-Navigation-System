"""Navigation controller with state machine and dynamic obstacle avoidance."""

import time
from typing import Callable, Optional, Tuple

from . import config as cfg
from .agent import Agent
from .path_planning import PathPlanner


class NavigationController:
    """Manages agent navigation through a state machine."""

    def __init__(self, agent: Agent, planner: PathPlanner, grid_world):
        self.agent = agent
        self.planner = planner
        self.grid_world = grid_world

        self.state = cfg.STATE_IDLE
        self.algorithm = "astar"
        self.replan_count = 0
        self.last_replan_time = 0.0
        self.navigation_log: list = []

        # Callbacks for events
        self.on_state_change: Optional[Callable] = None
        self.on_goal_reached: Optional[Callable] = None

    def reset(self) -> None:
        """Reset navigation state."""
        self.state = cfg.STATE_IDLE
        self.replan_count = 0
        self.last_replan_time = 0.0
        self.navigation_log.clear()

    def set_algorithm(self, algo: str) -> None:
        """Set the path planning algorithm."""
        self.algorithm = algo

    def start_navigation(self) -> None:
        """Begin navigation from start to goal."""
        self.replan_count = 0
        self._log("Navigation started")
        self._set_state(cfg.STATE_PLANNING)
        self._plan_path()

    def update(self, dt: float) -> None:
        """Update navigation state machine."""
        if self.state == cfg.STATE_IDLE:
            pass

        elif self.state == cfg.STATE_PLANNING:
            pass  # Path already planned in start_navigation or replan

        elif self.state == cfg.STATE_MOVING:
            self.agent.update(dt)
            self.agent.sense()

            # Check if dynamic obstacle blocks current path
            if self.grid_world.is_path_blocked():
                self._log("Path blocked! Triggering replan")
                self._set_state(cfg.STATE_AVOIDING)

            # Check if agent reached goal
            if self.agent.reached_goal:
                self._log("Goal reached!")
                self._set_state(cfg.STATE_REACHED)
                if self.on_goal_reached:
                    self.on_goal_reached()

        elif self.state == cfg.STATE_AVOIDING:
            # Wait briefly then replan
            now = time.time() * 1000
            if now - self.last_replan_time > cfg.REPLAN_COOLDOWN_MS:
                self._set_state(cfg.STATE_REPLANNING)
                self._replan()

        elif self.state == cfg.STATE_REPLANNING:
            pass  # Replan completed, state changed to MOVING

        elif self.state == cfg.STATE_REACHED:
            pass

        elif self.state == cfg.STATE_NO_PATH:
            pass

    def _plan_path(self) -> None:
        """Plan a path from agent position to goal."""
        start = self.agent.get_grid_pos()
        goal = self.grid_world.goal

        if self.algorithm == "dijkstra":
            path = self.planner.dijkstra(self.grid_world, start, goal)
        else:
            path = self.planner.astar(self.grid_world, start, goal)

        if path:
            self.agent.set_path(path)
            self._log(f"Path planned: {len(path)} cells, "
                      f"{self.planner.last_nodes_explored} nodes explored")
            self._set_state(cfg.STATE_MOVING)
        else:
            self._log("No path found!")
            self._set_state(cfg.STATE_NO_PATH)

    def _replan(self) -> None:
        """Replan path around new obstacles."""
        self.replan_count += 1
        self.last_replan_time = time.time() * 1000

        if self.replan_count > cfg.MAX_REPLAN_COUNT:
            self._log("Max replan count reached!")
            self._set_state(cfg.STATE_NO_PATH)
            return

        self._log(f"Replan #{self.replan_count}")
        self._plan_path()

    def _set_state(self, new_state: str) -> None:
        """Transition to a new state."""
        old_state = self.state
        self.state = new_state
        if old_state != new_state:
            self._log(f"State: {old_state} -> {new_state}")
            if self.on_state_change:
                self.on_state_change(old_state, new_state)

    def _log(self, message: str) -> None:
        """Log a navigation event."""
        timestamp = time.strftime("%H:%M:%S")
        self.navigation_log.append(f"[{timestamp}] {message}")
        if len(self.navigation_log) > 50:
            self.navigation_log.pop(0)

    def get_status(self) -> dict:
        """Return current navigation status."""
        return {
            "state": self.state,
            "algorithm": self.algorithm,
            "replan_count": self.replan_count,
            "path_length": len(self.agent.path),
            "path_index": self.agent.path_index,
            "nodes_explored": self.planner.last_nodes_explored,
            "planner_time": self.planner.last_time_taken,
        }
