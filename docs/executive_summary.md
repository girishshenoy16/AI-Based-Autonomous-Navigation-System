# Executive Summary — AI-Based Autonomous Navigation System

## Overview
A complete AI-powered autonomous navigation system that enables a virtual robot to navigate from start to goal in 
2D grid environments with dynamic obstacle avoidance. Built with Python, Pygame, OpenCV, and optional YOLOv8 
machine learning detection.

## Problem
Autonomous navigation requires integrating perception, planning, and control — critical capabilities for 
self-driving cars, warehouse robots, and delivery drones. This project demonstrates a complete implementation 
of these systems in a real-time 2D simulation.

## Solution
Complete sense-plan-act pipeline:
- **Perception**: 3-level system (simulated raycasting sensors, OpenCV contour detection, YOLOv8-nano ML detection)
- **Planning**: A* and Dijkstra algorithms with animated visualization and performance comparison
- **Control**: 7-state machine (IDLE→PLANNING→MOVING→AVOIDING→REPLANNING→REACHED/NO_PATH) with dynamic obstacle avoidance and automatic replanning

## Key Features

| Feature              | Description                                                         |
|----------------------|---------------------------------------------------------------------|
| 6 Map Environments   | Simple, Maze, Warehouse, City Grid, Parking Lot, Hospital           |
| Dual Algorithms      | A* vs Dijkstra with real-time performance comparison                |
| 3-Level Perception   | Simulated raycasting, OpenCV contour detection, YOLOv8-nano ML      |
| Dynamic Obstacles    | Real-time obstacle spawning, path blocking, automatic replanning    |
| Interactive Controls | Click-to-place walls, keyboard shortcuts, mouse goal placement      |
| Real-time Dashboard  | HUD with state, metrics, sensor visualization                       |
| Analytics            | CSV export, Matplotlib comparison charts, sensor readings over time |
| Animated A*          | Visual exploration of frontier, explored nodes, and final path      |


## Algorithm Performance

| Metric         | A*       | Dijkstra | Improvement         |
|----------------|----------|----------|---------------------|
| Nodes Explored | ~36      | ~1,100   | 96.7% fewer         |
| Planning Time  | ~1.0 ms  | ~30.4 ms | 96.7% faster        |
| Path Length    | 36 cells | 36 cells | Identical (optimal) |


## Technologies
Python 3.11, Pygame ≥2.5, OpenCV ≥4.8, NumPy, Matplotlib, Pandas, YOLOv8-nano (Ultralytics ≥8.4), pytest


## Testing
- **87 unit tests** with 100% pass rate
- Coverage of simulation, agent, path planning, navigation, and perception modules

## Project Structure
```
src/          — 8 Python modules (simulation, agent, perception, yolo_detector, path_planning, navigation, visualization, config)
maps/         — 6 JSON map environments
tests/        — 87 unit tests across 5 test files
docs/         — 6 documentation files
notebooks/    — Jupyter analysis notebooks
outputs/      — captures/, metrics/, models/, plots/
```

## Industry Applications

| Industry             | Use Case                         |
|----------------------|----------------------------------|
| Autonomous Vehicles  | Self-driving cars (Tesla, Waymo) |
| Warehouse Automation | Pick-and-place robots (Amazon)   |
| Drone Navigation     | Delivery/inspection drones       |
| Healthcare           | Hospital delivery robots         |

## Author
AI-Based Autonomous Navigation System — Diploma Project
