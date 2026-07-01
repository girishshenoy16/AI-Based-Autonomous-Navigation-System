"""Tests for the Agent class with sensors and movement."""

import sys
import os
import pytest
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()

from src.simulation import GridWorld
from src.agent import Agent


@pytest.fixture
def agent_with_grid():
    sim = GridWorld()
    sim.load_map_by_index(0)
    agent = Agent(sim.start, sim)
    return agent, sim


class TestAgentInitialization:
    def test_correct_start_position(self, agent_with_grid):
        agent, sim = agent_with_grid
        assert agent.x == float(sim.start[0]) + 0.5
        assert agent.y == float(sim.start[1]) + 0.5

    def test_not_moving_initially(self, agent_with_grid):
        agent, _ = agent_with_grid
        assert not agent.moving
        assert not agent.reached_goal

    def test_empty_path_initially(self, agent_with_grid):
        agent, _ = agent_with_grid
        assert len(agent.path) == 0

    def test_empty_trail_initially(self, agent_with_grid):
        agent, _ = agent_with_grid
        assert len(agent.trail) == 0


class TestAgentMovement:
    def test_set_path_starts_moving(self, agent_with_grid):
        agent, sim = agent_with_grid
        path = [(2, 2), (3, 3), (4, 4)]
        agent.set_path(path)
        assert agent.moving
        assert agent.path_index == 0

    def test_update_moves_agent(self, agent_with_grid):
        agent, sim = agent_with_grid
        path = [(2, 2), (3, 2), (4, 2)]
        agent.set_path(path)
        
        initial_x = agent.x
        for _ in range(10):
            agent.update(0.016)
        
        assert agent.x != initial_x

    def test_agent_reaches_waypoint(self, agent_with_grid):
        agent, sim = agent_with_grid
        agent.set_path([(2, 2)])
        
        # Agent starts at (2.5, 2.5), target is (2.5, 2.5)
        agent.update(0.016)
        assert agent.path_index == 1  # Should advance past first waypoint

    def test_get_grid_pos(self, agent_with_grid):
        agent, _ = agent_with_grid
        pos = agent.get_grid_pos()
        assert pos == (int(agent.x), int(agent.y))

    def test_heading_updates(self, agent_with_grid):
        agent, sim = agent_with_grid
        agent.set_path([(10, 2), (15, 2)])
        
        # Force agent to first waypoint
        agent.update(0.1)
        
        # Now set path to different direction
        agent.set_path([(10, 10)])
        initial_heading = agent.heading
        
        for _ in range(20):
            agent.update(0.016)
        
        assert agent.heading != initial_heading


class TestSensors:
    def test_sense_returns_readings(self, agent_with_grid):
        agent, _ = agent_with_grid
        readings = agent.sense()
        assert len(readings) == 8

    def test_sensor_reading_has_distance(self, agent_with_grid):
        agent, _ = agent_with_grid
        readings = agent.sense()
        for reading in readings:
            assert reading.distance > 0
            assert reading.distance <= 7  # SENSOR_RANGE

    def test_sensor_detects_wall(self, agent_with_grid):
        agent, sim = agent_with_grid
        # Place wall nearby
        sim.set_cell(4, 2, 1)
        readings = agent.sense()
        
        # At least one sensor should detect the wall at shorter distance
        distances = [r.distance for r in readings]
        assert min(distances) < 7

    def test_collision_detection(self, agent_with_grid):
        agent, sim = agent_with_grid
        # Place wall at agent position
        sim.set_cell(int(agent.x), int(agent.y), 1)
        assert agent.check_collision()


class TestTrail:
    def test_trail_grows(self, agent_with_grid):
        agent, sim = agent_with_grid
        agent.set_path([(3, 2), (4, 2), (5, 2)])
        
        for _ in range(50):
            agent.update(0.016)
        
        assert len(agent.trail) > 0
