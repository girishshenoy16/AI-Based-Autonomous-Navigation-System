"""A* and Dijkstra path planning algorithms with animated exploration."""

import heapq
import math
import time
from time import perf_counter
from typing import Callable, Dict, List, Optional, Set, Tuple

from . import config as cfg

# Speed presets: delay in seconds per animation frame
SPEED_DELAYS = {
    cfg.SPEED_FAST: 0.0,
    cfg.SPEED_MEDIUM: 0.02,
    cfg.SPEED_SLOW: 0.08,
}


class PathPlanner:
    """Path planner implementing A* and Dijkstra algorithms."""

    def __init__(self):
        self.last_nodes_explored = 0
        self.last_path_length = 0
        self.last_time_taken = 0.0
        self.last_algorithm = ""

    def astar(self, grid_world, start: Tuple[int, int], goal: Tuple[int, int],
              heuristic: str = cfg.HEURISTIC_MANHATTAN) -> Optional[List[Tuple[int, int]]]:
        """Find optimal path using A* algorithm.

        Returns list of (col, row) waypoints, or None if no path exists.
        """
        t0 = perf_counter()
        nodes_explored = 0

        open_set: List[Tuple[float, int, Tuple[int, int]]] = []
        counter = 0
        heapq.heappush(open_set, (0.0, counter, start))

        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}

        h = self._heuristic_fn(heuristic)

        while open_set:
            _, _, current = heapq.heappop(open_set)
            nodes_explored += 1

            if current == goal:
                path = self._reconstruct_path(came_from, current)
                self.last_nodes_explored = nodes_explored
                self.last_path_length = len(path)
                self.last_time_taken = perf_counter() - t0
                self.last_algorithm = "A*"
                return path

            for neighbor in self._get_neighbors(grid_world, current):
                tentative_g = g_score[current] + 1.0

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + h(neighbor, goal)
                    counter += 1
                    heapq.heappush(open_set, (f_score, counter, neighbor))
                    came_from[neighbor] = current

        self.last_nodes_explored = nodes_explored
        self.last_path_length = 0
        self.last_time_taken = perf_counter() - t0
        self.last_algorithm = "A*"
        return None

    def dijkstra(self, grid_world, start: Tuple[int, int],
                 goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Find optimal path using Dijkstra's algorithm.

        Returns list of (col, row) waypoints, or None if no path exists.
        """
        t0 = perf_counter()
        nodes_explored = 0

        open_set: List[Tuple[float, int, Tuple[int, int]]] = []
        counter = 0
        heapq.heappush(open_set, (0.0, counter, start))

        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}

        while open_set:
            _, _, current = heapq.heappop(open_set)
            nodes_explored += 1

            if current == goal:
                path = self._reconstruct_path(came_from, current)
                self.last_nodes_explored = nodes_explored
                self.last_path_length = len(path)
                self.last_time_taken = perf_counter() - t0
                self.last_algorithm = "Dijkstra"
                return path

            for neighbor in self._get_neighbors(grid_world, current):
                tentative_g = g_score[current] + 1.0

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    counter += 1
                    heapq.heappush(open_set, (tentative_g, counter, neighbor))
                    came_from[neighbor] = current

        self.last_nodes_explored = nodes_explored
        self.last_path_length = 0
        self.last_time_taken = perf_counter() - t0
        self.last_algorithm = "Dijkstra"
        return None

    # ──────────────────────────────────────────
    # Animated A* Exploration (Generator)
    # ──────────────────────────────────────────
    def astar_animated(self, grid_world, start: Tuple[int, int], goal: Tuple[int, int],
                       heuristic: str = cfg.HEURISTIC_MANHATTAN,
                       speed: str = None):
        """Generator that yields exploration states for animated A* visualization.

        Yields dicts with keys: frontier, explored, current, path, done.
        """
        if speed is None:
            speed = cfg.ANIMATION_SPEED
        delay = SPEED_DELAYS.get(speed, 0.0)
        open_set: List[Tuple[float, int, Tuple[int, int]]] = []
        counter = 0
        heapq.heappush(open_set, (0.0, counter, start))

        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}

        frontier: Set[Tuple[int, int]] = {start}
        explored: Set[Tuple[int, int]] = set()
        current = None

        h = self._heuristic_fn(heuristic)

        while open_set:
            _, _, current = heapq.heappop(open_set)
            frontier.discard(current)
            explored.add(current)

            if delay > 0:
                time.sleep(delay)

            if current == goal:
                path = self._reconstruct_path(came_from, current)
                yield {
                    "frontier": set(frontier),
                    "explored": set(explored),
                    "current": current,
                    "path": path,
                    "done": True,
                }
                return

            for neighbor in self._get_neighbors(grid_world, current):
                tentative_g = g_score[current] + 1.0

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    frontier.add(neighbor)
                    counter += 1
                    heapq.heappush(open_set,
                                   (tentative_g + h(neighbor, goal), counter, neighbor))
                    came_from[neighbor] = current

            yield {
                "frontier": set(frontier),
                "explored": set(explored),
                "current": current,
                "path": [],
                "done": False,
            }

        yield {
            "frontier": set(),
            "explored": set(explored),
            "current": None,
            "path": [],
            "done": True,
        }

    # ──────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────
    def _get_neighbors(self, grid_world, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid 8-connected neighbors."""
        neighbors = []
        for dc in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                if dc == 0 and dr == 0:
                    continue
                nc, nr = pos[0] + dc, pos[1] + dr
                if not grid_world.is_wall(nc, nr):
                    neighbors.append((nc, nr))
        return neighbors

    def _reconstruct_path(self, came_from: Dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Reconstruct path from came_from map."""
        path = [current]
        while came_from.get(current) is not None:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _heuristic_fn(self, heuristic: str) -> Callable:
        """Return the heuristic function."""
        if heuristic == cfg.HEURISTIC_EUCLIDEAN:
            return self._euclidean
        return self._manhattan

    @staticmethod
    def _manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def _euclidean(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def get_comparison_metrics(self) -> Dict:
        """Return metrics from the last planning call."""
        return {
            "algorithm": self.last_algorithm,
            "nodes_explored": self.last_nodes_explored,
            "path_length": self.last_path_length,
            "time_taken": self.last_time_taken,
        }
