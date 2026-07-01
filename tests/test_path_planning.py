"""Tests for A* and Dijkstra path planning algorithms."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()

from src.simulation import GridWorld
from src.path_planning import PathPlanner
from src import config as cfg


@pytest.fixture
def simple_grid():
    sim = GridWorld()
    sim.load_map_by_index(0)
    return sim


@pytest.fixture
def planner():
    return PathPlanner()


class TestAStar:
    def test_finds_path_on_simple_grid(self, simple_grid, planner):
        path = planner.astar(simple_grid, (2, 2), (37, 27))
        assert path is not None
        assert len(path) > 0

    def test_path_starts_at_start(self, simple_grid, planner):
        path = planner.astar(simple_grid, (2, 2), (37, 27))
        assert path[0] == (2, 2)

    def test_path_ends_at_goal(self, simple_grid, planner):
        path = planner.astar(simple_grid, (2, 2), (37, 27))
        assert path[-1] == (37, 27)

    def test_path_avoids_walls(self, simple_grid, planner):
        path = planner.astar(simple_grid, (2, 2), (37, 27))
        for cell in path:
            assert not simple_grid.is_wall(cell[0], cell[1])

    def test_manhattan_heuristic(self, simple_grid, planner):
        path = planner.astar(simple_grid, (2, 2), (37, 27), heuristic='manhattan')
        assert path is not None

    def test_euclidean_heuristic(self, simple_grid, planner):
        path = planner.astar(simple_grid, (2, 2), (37, 27), heuristic='euclidean')
        assert path is not None

    def test_same_path_length_both_heuristics(self, simple_grid, planner):
        path_m = planner.astar(simple_grid, (2, 2), (37, 27), heuristic='manhattan')
        path_e = planner.astar(simple_grid, (2, 2), (37, 27), heuristic='euclidean')
        assert len(path_m) == len(path_e)


class TestDijkstra:
    def test_finds_path_on_simple_grid(self, simple_grid, planner):
        path = planner.dijkstra(simple_grid, (2, 2), (37, 27))
        assert path is not None
        assert len(path) > 0

    def test_path_starts_at_start(self, simple_grid, planner):
        path = planner.dijkstra(simple_grid, (2, 2), (37, 27))
        assert path[0] == (2, 2)

    def test_path_ends_at_goal(self, simple_grid, planner):
        path = planner.dijkstra(simple_grid, (2, 2), (37, 27))
        assert path[-1] == (37, 27)

    def test_path_avoids_walls(self, simple_grid, planner):
        path = planner.dijkstra(simple_grid, (2, 2), (37, 27))
        for cell in path:
            assert not simple_grid.is_wall(cell[0], cell[1])


class TestComparison:
    def test_both_find_same_optimal_length(self, simple_grid, planner):
        path_astar = planner.astar(simple_grid, (2, 2), (37, 27))
        path_dijkstra = planner.dijkstra(simple_grid, (2, 2), (37, 27))
        assert len(path_astar) == len(path_dijkstra)

    def test_astar_explores_fewer_nodes(self, simple_grid, planner):
        planner.astar(simple_grid, (2, 2), (37, 27))
        astar_nodes = planner.last_nodes_explored

        planner.dijkstra(simple_grid, (2, 2), (37, 27))
        dijkstra_nodes = planner.last_nodes_explored

        assert astar_nodes <= dijkstra_nodes


class TestNoPath:
    def test_no_path_when_fully_blocked(self, simple_grid, planner):
        start = (2, 2)
        goal = (37, 27)
        for c in range(cfg.GRID_COLS):
            for r in range(cfg.GRID_ROWS):
                if (c, r) != start and (c, r) != goal:
                    simple_grid.set_cell(c, r, 1)
        path = planner.astar(simple_grid, start, goal)
        assert path is None

    def test_no_path_when_completely_surrounded(self, simple_grid, planner):
        start = (2, 2)
        for dc in range(-1, 2):
            for dr in range(-1, 2):
                if dc == 0 and dr == 0:
                    continue
                simple_grid.set_cell(start[0] + dc, start[1] + dr, 1)
        path = planner.astar(simple_grid, start, (37, 27))
        assert path is None


class TestAllMaps:
    @pytest.mark.parametrize("map_index", [0, 1, 2, 3, 4])
    def test_astar_on_all_maps(self, map_index, planner):
        sim = GridWorld()
        sim.load_map_by_index(map_index)
        path = planner.astar(sim, sim.start, sim.goal)
        assert path is not None
        assert len(path) > 0

    @pytest.mark.parametrize("map_index", [0, 1, 2, 3, 4])
    def test_dijkstra_on_all_maps(self, map_index, planner):
        sim = GridWorld()
        sim.load_map_by_index(map_index)
        path = planner.dijkstra(sim, sim.start, sim.goal)
        assert path is not None
        assert len(path) > 0

    def test_hospital_map_has_path(self, planner):
        sim = GridWorld()
        sim.load_map_by_index(5)
        path = planner.astar(sim, (1, 1), (38, 28))
        assert path is not None
        assert len(path) > 0
        assert path[0] == (1, 1)
        assert path[-1] == (38, 28)
