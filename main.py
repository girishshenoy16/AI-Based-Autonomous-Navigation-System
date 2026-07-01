"""Main entry point — orchestrates all modules for the full simulation."""

import argparse
import sys
import os
import time

import cv2
import numpy as np
import pygame

sys.path.insert(0, os.path.dirname(__file__))

from src.simulation import GridWorld
from src.agent import Agent
from src.perception import PerceptionModule
from src.yolo_detector import YOLODetector
from src.path_planning import PathPlanner
from src.navigation import NavigationController
from src.visualization import Dashboard
from src import config as cfg


def parse_args():
    parser = argparse.ArgumentParser(description="AI-Based Autonomous Navigation System")
    parser.add_argument("--map", type=str, default="simple",
                        choices=["simple", "maze", "warehouse", "city_grid",
                                 "parking_lot", "hospital"],
                        help="Map environment to load")
    parser.add_argument("--algorithm", type=str, default="astar",
                        choices=["astar", "dijkstra"],
                        help="Path planning algorithm")
    parser.add_argument("--perception", type=str, default="simulated",
                        choices=["simulated", "opencv", "yolo"],
                        help="Perception mode")
    parser.add_argument("--interactive", action="store_true",
                        help="Enable interactive mode (click/keyboard)")
    parser.add_argument("--save-metrics", action="store_true",
                        help="Save run metrics to CSV")
    return parser.parse_args()


def get_map_index(map_name: str) -> int:
    name_map = {
        "simple": 0, "maze": 1, "warehouse": 2,
        "city_grid": 3, "parking_lot": 4, "hospital": 5,
    }
    return name_map.get(map_name, 0)


def main():
    args = parse_args()

    print("=" * 50)
    print(" AI-Based Autonomous Navigation System")
    print("=" * 50)

    # Initialize modules
    sim = GridWorld()
    map_idx = get_map_index(args.map)
    map_name = sim.load_map_by_index(map_idx)
    print(f"[INFO] Loaded map: {map_name}")

    agent = Agent(sim.start, sim)
    planner = PathPlanner()
    nav = NavigationController(agent, planner, sim)
    nav.set_algorithm(args.algorithm)

    perception = PerceptionModule()
    yolo = YOLODetector()
    dashboard = Dashboard()

    # Set up perception mode
    if args.perception == cfg.PERCEPTION_OPENCV:
        perception.active = True
    elif args.perception == cfg.PERCEPTION_YOLO:
        yolo.active = True

    # State
    paused = False
    running = True
    navigation_started = False
    navigation_start_time = 0.0
    sensor_history = []

    print(f"[INFO] Algorithm: {args.algorithm.upper()}")
    print(f"[INFO] Perception: {args.perception}")
    print("[INFO] Press SPACE to start navigation, ESC to quit")
    print("=" * 50)

    while running:
        dt = sim.tick() / 1000.0  # delta time in seconds
        if dt > 0.1:
            dt = 0.016  # cap at ~60fps equivalent

        # ── Event Handling ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    if not navigation_started:
                        nav.start_navigation()
                        navigation_started = True
                        navigation_start_time = time.time()
                        print(f"[INFO] Navigation started, path: {len(agent.path)} cells")
                    else:
                        paused = not paused

                elif event.key == pygame.K_r:
                    if navigation_started:
                        status = nav.get_status()
                        status["map"] = map_name
                        status["planner_time_ms"] = round(status.pop("planner_time", 0) * 1000, 2)
                        status["total_time_s"] = round(time.time() - navigation_start_time, 2)
                        status["dynamic_obstacles"] = len(sim.dynamic_obstacles)
                        status["opencv_active"] = perception.active
                        status["yolo_active"] = yolo.active
                        avg_sensor = 0
                        if sensor_history:
                            avg_sensor = round(sum(sum(r) for r in sensor_history) / len(sensor_history) / cfg.NUM_SENSORS, 2)
                        status["sensor_avg"] = avg_sensor
                        dashboard.record_metrics(status)
                        dashboard.save_metrics_csv()
                    agent.reset(sim.start)
                    nav.reset()
                    sim.clear_overlay()
                    sim.path = []
                    navigation_started = False
                    sensor_history.clear()
                    print("[INFO] Simulation reset")

                elif event.key == pygame.K_s:
                    path = dashboard.save_screenshot(sim.screen)
                    print(f"[INFO] Screenshot saved: {path}")
                    if perception.active and perception.processed_frame is not None:
                        cv_path = path.replace("screenshot_", "opencv_")
                        cv2.imwrite(cv_path, perception.processed_frame)
                        print(f"[INFO] OpenCV frame saved: {cv_path}")

                elif event.key == pygame.K_p:
                    active = perception.toggle()
                    print(f"[INFO] OpenCV perception: {'ON' if active else 'OFF'}")

                elif event.key == pygame.K_y:
                    active = yolo.toggle()
                    print(f"[INFO] YOLO detection: {'ON' if active else 'OFF'}")

                elif event.key == pygame.K_n:
                    pos = sim.spawn_random_obstacle()
                    if pos:
                        print(f"[INFO] Spawned obstacle at {pos}")

                elif event.key in cfg.KEYBINDINGS["map_switch"]:
                    idx = cfg.KEYBINDINGS["map_switch"][event.key]
                    name = sim.load_map_by_index(idx)
                    agent.reset(sim.start)
                    nav.reset()
                    sim.clear_overlay()
                    sim.path = []
                    navigation_started = False
                    sensor_history.clear()
                    print(f"[INFO] Switched to map: {name}")

                elif event.key in cfg.KEYBINDINGS["algorithm"]:
                    algo = cfg.KEYBINDINGS["algorithm"][event.key]
                    nav.set_algorithm(algo)
                    print(f"[INFO] Algorithm: {algo.upper()}")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                grid_pos = sim.pixel_to_grid(event.pos[0], event.pos[1])
                if grid_pos:
                    col, row = grid_pos
                    if event.button == 1:  # Left click — add obstacle
                        sim.set_cell(col, row, 1)
                        if navigation_started and sim.is_path_blocked():
                            nav._set_state(cfg.STATE_AVOIDING)
                    elif event.button == 3:  # Right click — remove obstacle
                        sim.set_cell(col, row, 0)
                    elif event.button == 2:  # Middle click — set goal
                        sim.set_goal(col, row)
                        if navigation_started:
                            nav._replan()

        # ── Update ──
        if not paused and navigation_started:
            nav.update(dt)
            agent.sense()

            if agent.sensor_readings:
                sensor_history.append([r.distance for r in agent.sensor_readings])

            if nav.state in (cfg.STATE_REACHED, cfg.STATE_NO_PATH):
                status = nav.get_status()
                status["map"] = map_name
                status["planner_time_ms"] = round(status.pop("planner_time", 0) * 1000, 2)
                status["total_time_s"] = round(time.time() - navigation_start_time, 2)
                status["dynamic_obstacles"] = len(sim.dynamic_obstacles)
                status["opencv_active"] = perception.active
                status["yolo_active"] = yolo.active
                avg_sensor = 0
                if sensor_history:
                    avg_sensor = round(sum(sum(r) for r in sensor_history) / len(sensor_history) / cfg.NUM_SENSORS, 2)
                status["sensor_avg"] = avg_sensor
                dashboard.record_metrics(status)
                dashboard.save_metrics_csv()

                algo_data = {
                    "nodes_explored": status.get("nodes_explored", 0),
                    "path_length": status.get("path_length", len(sim.path)),
                    "time_taken": status.get("planner_time_ms", 0.0)
                }
                if status.get("algorithm") == "astar":
                    dashboard.last_astar_data = algo_data
                else:
                    dashboard.last_dijkstra_data = algo_data

                navigation_started = False

        # ── Sync path for rendering (AFTER update, BEFORE render) ──
        # Must reference agent.path directly since it may change on replan
        sim.path = agent.path

        # ── Render ──
        sim.render()
        agent.draw(sim.screen)
        dashboard.update_hud(sim.screen, nav.get_status(), agent.sensor_readings,
                             perception.active, yolo.active)

        # ── Perception windows ──
        if perception.active:
            frame = sim.capture_frame()
            img = np.transpose(np.array(pygame.surfarray.pixels3d(frame)), (1, 0, 2))
            perception.process(img)
            perception.draw()

        if yolo.active and yolo.is_available():
            frame = sim.capture_frame()
            img = np.transpose(np.array(pygame.surfarray.pixels3d(frame)), (1, 0, 2))
            yolo.detect(img)

    # ── Final chart generation ──
    if dashboard.last_astar_data or dashboard.last_dijkstra_data:
        a = dashboard.last_astar_data if dashboard.last_astar_data else {"nodes_explored": 0, "path_length": 0, "time_taken": 0}
        d = dashboard.last_dijkstra_data if dashboard.last_dijkstra_data else {"nodes_explored": 0, "path_length": 0, "time_taken": 0}
        chart_path = dashboard.generate_path_comparison_chart(a, d)
        print(f"[INFO] Path comparison chart saved: {chart_path}")

    sensor_chart = dashboard.generate_sensor_chart(sensor_history)
    if sensor_chart:
        print(f"[INFO] Sensor chart saved: {sensor_chart}")

    perception.close()
    sim.quit()
    print("[INFO] Simulation ended")


if __name__ == "__main__":
    main()
