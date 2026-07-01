"""Tests for the navigation controller state machine."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pygame
pygame.init()

from src.simulation import GridWorld
from src.agent import Agent
from src.path_planning import PathPlanner
from src.navigation import NavigationController
from src import config as cfg


@pytest.fixture
def nav_setup():
    sim = GridWorld()
    sim.load_map_by_index(0)
    agent = Agent(sim.start, sim)
    planner = PathPlanner()
    nav = NavigationController(agent, planner, sim)
    return nav, sim, agent


class TestInitialState:
    def test_idle_state(self, nav_setup):
        nav, _, _ = nav_setup
        assert nav.state == cfg.STATE_IDLE

    def test_default_algorithm(self, nav_setup):
        nav, _, _ = nav_setup
        assert nav.algorithm == "astar"

    def test_zero_replans(self, nav_setup):
        nav, _, _ = nav_setup
        assert nav.replan_count == 0


class TestStartNavigation:
    def test_plans_path(self, nav_setup):
        nav, _, agent = nav_setup
        nav.start_navigation()
        assert len(agent.path) > 0

    def test_state_becomes_moving(self, nav_setup):
        nav, _, _ = nav_setup
        nav.start_navigation()
        assert nav.state == cfg.STATE_MOVING

    def test_agent_is_moving(self, nav_setup):
        nav, _, agent = nav_setup
        nav.start_navigation()
        assert agent.moving


class TestUpdate:
    def test_agent_moves_during_update(self, nav_setup):
        nav, _, agent = nav_setup
        nav.start_navigation()
        
        initial_x = agent.x
        for _ in range(10):
            nav.update(0.016)
        
        assert agent.x != initial_x

    def test_state_stays_moving(self, nav_setup):
        nav, _, _ = nav_setup
        nav.start_navigation()
        
        for _ in range(50):
            nav.update(0.016)
        
        assert nav.state == cfg.STATE_MOVING or nav.state == cfg.STATE_REACHED


class TestReplan:
    def test_replan_increments_counter(self, nav_setup):
        nav, _, _ = nav_setup
        nav.start_navigation()
        initial_count = nav.replan_count
        nav._replan()
        assert nav.replan_count > initial_count

    def test_max_replan_limit(self, nav_setup):
        nav, _, _ = nav_setup
        nav.start_navigation()
        nav.replan_count = cfg.MAX_REPLAN_COUNT + 1
        nav._replan()
        assert nav.state == cfg.STATE_NO_PATH


class TestSetAlgorithm:
    def test_set_dijkstra(self, nav_setup):
        nav, _, _ = nav_setup
        nav.set_algorithm("dijkstra")
        assert nav.algorithm == "dijkstra"

    def test_set_astar(self, nav_setup):
        nav, _, _ = nav_setup
        nav.set_algorithm("astar")
        assert nav.algorithm == "astar"


class TestReset:
    def test_reset_to_idle(self, nav_setup):
        nav, _, _ = nav_setup
        nav.start_navigation()
        nav.reset()
        assert nav.state == cfg.STATE_IDLE

    def test_reset_replans(self, nav_setup):
        nav, _, _ = nav_setup
        nav.start_navigation()
        nav.replan_count = 5
        nav.reset()
        assert nav.replan_count == 0


class TestGetStatus:
    def test_status_keys(self, nav_setup):
        nav, _, _ = nav_setup
        nav.start_navigation()
        status = nav.get_status()
        
        assert "state" in status
        assert "algorithm" in status
        assert "replan_count" in status
        assert "path_length" in status
        assert "path_index" in status
