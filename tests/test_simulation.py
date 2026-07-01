"""Tests for the simulation engine (GridWorld)."""

import sys
import os
import pytest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()

from src.simulation import GridWorld
from src import config as cfg


@pytest.fixture
def sim():
    s = GridWorld()
    s.load_map_by_index(0)
    return s


class TestGridWorldInit:
    def test_grid_dimensions(self, sim):
        assert len(sim.grid) == cfg.GRID_ROWS
        assert len(sim.grid[0]) == cfg.GRID_COLS

    def test_has_start(self, sim):
        assert sim.start is not None

    def test_has_goal(self, sim):
        assert sim.goal is not None

    def test_has_obstacles(self, sim):
        assert len(sim.obstacles) > 0


class TestMapLoading:
    def test_load_simple_map(self, sim):
        sim.load_map_by_index(0)
        assert cfg.MAP_NAMES[0] == "Simple"

    def test_load_maze_map(self, sim):
        sim.load_map_by_index(1)
        assert len(sim.obstacles) > 50

    def test_load_warehouse_map(self, sim):
        sim.load_map_by_index(2)
        assert len(sim.obstacles) > 50

    def test_load_all_maps(self, sim):
        for i in range(6):
            sim.load_map_by_index(i)
            assert len(sim.grid) == cfg.GRID_ROWS

    def test_load_map_sets_start_goal(self, sim):
        sim.load_map_by_index(0)
        assert sim.start == (2, 2)
        assert sim.goal == (37, 27)


class TestCellOperations:
    def test_is_wall(self, sim):
        # Place a wall
        sim.set_cell(5, 5, 1)
        assert sim.is_wall(5, 5)

    def test_is_free(self, sim):
        assert sim.is_free(2, 2)  # Start position

    def test_set_cell_wall(self, sim):
        sim.set_cell(10, 10, 1)
        assert sim.grid[10][10] == 1
        assert (10, 10) in sim.obstacles

    def test_set_cell_free(self, sim):
        sim.set_cell(10, 10, 1)
        sim.set_cell(10, 10, 0)
        assert sim.grid[10][10] == 0
        assert (10, 10) not in sim.obstacles

    def test_out_of_bounds_is_wall(self, sim):
        assert sim.is_wall(-1, 0)
        assert sim.is_wall(0, -1)
        assert sim.is_wall(cfg.GRID_COLS, 0)
        assert sim.is_wall(0, cfg.GRID_ROWS)


class TestDynamicObstacles:
    def test_add_dynamic_obstacle(self, sim):
        sim.add_dynamic_obstacle(15, 15)
        assert (15, 15) in sim.dynamic_obstacles

    def test_remove_dynamic_obstacle(self, sim):
        sim.add_dynamic_obstacle(15, 15)
        sim.remove_dynamic_obstacle(15, 15)
        assert (15, 15) not in sim.dynamic_obstacles

    def test_dynamic_obstacle_blocks_path(self, sim):
        sim.path = [(5, 5), (5, 6)]
        sim.add_dynamic_obstacle(5, 5)
        assert sim.is_path_blocked()

    def test_spawn_random_obstacle(self, sim):
        pos = sim.spawn_random_obstacle()
        assert pos is not None
        assert pos in sim.dynamic_obstacles


class TestGoalSetting:
    def test_set_goal(self, sim):
        sim.set_goal(20, 20)
        assert sim.goal == (20, 20)

    def test_set_goal_on_wall_fails(self, sim):
        original_goal = sim.goal
        # Find a wall position
        for wall in sim.obstacles:
            sim.set_goal(wall[0], wall[1])
            break
        assert sim.goal == original_goal


class TestPathBlocked:
    def test_clear_path_not_blocked(self, sim):
        sim.path = [(2, 2), (3, 3)]
        assert not sim.is_path_blocked()

    def test_wall_on_path_blocked(self, sim):
        sim.path = [(5, 5)]
        sim.set_cell(5, 5, 1)
        assert sim.is_path_blocked()


class TestPixelConversion:
    def test_pixel_to_grid(self, sim):
        result = sim.pixel_to_grid(100, 100)
        assert result is not None
        assert result == (5, 5)

    def test_pixel_out_of_bounds(self, sim):
        result = sim.pixel_to_grid(10000, 10000)
        assert result is None
