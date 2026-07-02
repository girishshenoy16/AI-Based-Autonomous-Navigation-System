# System Architecture

## Overview
The system follows a modular **sense-plan-act** architecture with clean interfaces between components. 
Each module is implemented as a standalone Python class with well-defined inputs and outputs.


## Architecture Diagram
```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          SIMULATION ENGINE                                   │
│                                                                              │
│                       GridWorld (Pygame 2D Grid)                             │
│                  40×30 Grid • 20 px Cells • 60 FPS                           │
│                                                                              │
│        ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                │
│        │ Map Loading  │   │  Rendering   │   │   Overlay    │                │
│        │ (JSON Maps)  │   │  (Pygame)    │   │  (A* Visual) │                │
│        └──────────────┘   └──────────────┘   └──────────────┘                │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────────────────┐
│                              AGENT MODULE                                    │
│                                                                              │
│                           Agent (agent.py)                                   │
│                                                                              │
│        ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                │
│        │  Movement    │   │  8-Direction │   │  Collision   │                │
│        │  Controller  │   │  Raycasting  │   │  Detection   │                │
│        │ (Waypoints)  │   │   Sensors    │   │              │                │
│        └──────────────┘   └──────────────┘   └──────────────┘                │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────────────────┐
│                           PERCEPTION MODULE                                  │
│                                                                              │
│                    PerceptionModule (perception.py)                          │
│                                                                              │
│      ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐            │
│      │   Level 1    │   │   Level 2    │   │      Level 3       │            │
│      │  Simulated   │   │    OpenCV    │   │    YOLOv8-nano     │            │
│      │  Raycasting  │   │   Contour    │   │   ML Detection     │            │
│      │   (8-dir)    │   │  Detection   │   │    (Optional)      │            │
│      └──────┬───────┘   └──────┬───────┘   └───────┬────────────┘            │
│             └──────────────────┼───────────────────┘                         │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────────┐
│                         PATH PLANNING MODULE                                 │
│                                                                              │
│                    PathPlanner (path_planning.py)                            │
│                                                                              │
│              ┌──────────────┐       ┌──────────────┐                         │
│              │      A*      │       │  Dijkstra    │                         │
│              │  Algorithm   │       │  Algorithm   │                         │
│              │   f = g + h  │       │    f = g     │                         │
│              └──────┬───────┘       └──────┬───────┘                         │
│                     └──────────────────────┘                                 │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────────┐
│                     NAVIGATION & CONTROL MODULE                              │
│                                                                              │
│                  NavigationController (navigation.py)                        │
│                                                                              │
│          ┌──────────────────┐      ┌──────────────────┐                      │
│          │  State Machine   │      │ Dynamic Obstacle │                      │
│          │    7 States      │      │    Avoidance     │                      │
│          │ (IDLE → REACHED) │      │   Replanning     │                      │
│          └──────────────────┘      └──────────────────┘                      │
└────────────────────────────────┬─────────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼─────────────────────────────────────────────┐
│                     VISUALIZATION & ANALYTICS                                │
│                                                                              │
│                    Dashboard (visualization.py)                              │
│                                                                              │
│        ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                │
│        │  HUD Panel   │   │ CSV Metrics  │   │ Matplotlib   │                │
│        │ (Real-time)  │   │    Export    │   │    Charts    │                │
│        └──────────────┘   └──────────────┘   └──────────────┘                │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Data Flow
```
1. Grid Map loaded from JSON (maps/map_*.json)
2. Agent senses environment (8-direction raycasting, range: 7 cells)
3. Path Planner computes optimal route (A* or Dijkstra) — 8-connected grid
4. Navigation Controller follows waypoints at 6 cells/second
5. Dynamic obstacle detected → AVOIDING → REPLANNING → new path
6. Agent reaches goal → REACHED state
7. Metrics recorded → CSV export → Matplotlib charts
```

## Module Files

| Module        | File                   | Class                  | Responsibilities                             |
|---------------|------------------------|------------------------|----------------------------------------------|
| Simulation    | `src/simulation.py`    | `GridWorld`            | Grid world, map loading, rendering, overlays |
| Agent         | `src/agent.py`         | `Agent`                | Movement, raycasting sensors, collision      |
| Perception    | `src/perception.py`    | `PerceptionModule`     | OpenCV contour detection                     |
| YOLO          | `src/yolo_detector.py` | `YOLODetector`         | YOLOv8-nano ML detection                     |
| Path Planning | `src/path_planning.py` | `PathPlanner`          | A* and Dijkstra algorithms                   |
| Navigation    | `src/navigation.py`    | `NavigationController` | State machine, replanning                    |
| Visualization | `src/visualization.py` | `Dashboard`            | HUD, CSV export, charts                      |
| Configuration | `src/config.py`        | —                      | All constants and settings                   |


## Module Interfaces

### GridWorld
```python
grid_world.load_map(map_path: str) -> None
grid_world.load_map_by_index(index: int) -> str
grid_world.is_wall(col: int, row: int) -> bool
grid_world.is_free(col: int, row: int) -> bool
grid_world.set_cell(col: int, row: int, value: int) -> None
grid_world.add_dynamic_obstacle(col: int, row: int) -> None
grid_world.remove_dynamic_obstacle(col: int, row: int) -> None
grid_world.spawn_random_obstacle() -> Optional[Tuple[int, int]]
grid_world.set_goal(col: int, row: int) -> None
grid_world.is_path_blocked() -> bool
grid_world.pixel_to_grid(px: int, py: int) -> Optional[Tuple[int, int]]
grid_world.render() -> None
grid_world.capture_frame() -> pygame.Surface
grid_world.tick() -> int
grid_world.quit() -> None
grid_world.clear_overlay() -> None
grid_world.set_overlay(frontier: set, explored: set, current: Tuple[int, int]) -> None
```

### Agent
```python
agent.reset(start: Tuple[int, int]) -> None
agent.set_path(path: List[Tuple[int, int]]) -> None
agent.update(dt: float) -> None
agent.get_grid_pos() -> Tuple[int, int]
agent.sense() -> List[SensorReading]
agent.check_collision() -> bool
agent.is_near_obstacle(threshold: float = 1.5) -> bool
agent.draw(surface: pygame.Surface) -> None
```

### PathPlanner
```python
planner.astar(grid_world, start, goal, heuristic="manhattan") -> Optional[List[Tuple[int, int]]]
planner.dijkstra(grid_world, start, goal) -> Optional[List[Tuple[int, int]]]
planner.astar_animated(grid_world, start, goal, heuristic, speed) -> Generator
planner.get_comparison_metrics() -> Dict
```

### NavigationController
```python
nav.start_navigation() -> None
nav.update(dt: float) -> None
nav.set_algorithm(algo: str) -> None
nav.reset() -> None
nav.get_status() -> dict
```

### PerceptionModule
```python
perception.toggle() -> bool
perception.capture(pygame_surface: pygame.Surface) -> np.ndarray
perception.process(frame: np.ndarray = None) -> np.ndarray
perception.get_detection_centers() -> List[Tuple[int, int]]
perception.draw(window_name: str = "Perception View") -> None
perception.save_screenshot(path: str) -> str
perception.close() -> None
```

### Dashboard
```python
dashboard.update_hud(surface, nav_status, sensor_readings, opencv_active, yolo_active) -> None
dashboard.record_metrics(run_data: Dict) -> None
dashboard.save_metrics_csv(filename: str = None) -> str
dashboard.generate_path_comparison_chart(astar_data, dijkstra_data) -> str
dashboard.generate_sensor_chart(sensor_history) -> str
dashboard.save_screenshot(surface, filename) -> str
```

## Project Structure
```
AI-Based Autonomous Navigation System/
├── main.py                    # Main entry point with CLI args
├── requirements.txt           # Python dependencies
│
├── src/                       # Source modules
│   ├── __init__.py
│   ├── config.py              # All constants
│   ├── simulation.py          # GridWorld engine
│   ├── agent.py               # Robot entity
│   ├── perception.py          # OpenCV detection
│   ├── yolo_detector.py       # YOLOv8 detection
│   ├── path_planning.py       # A* and Dijkstra
│   ├── navigation.py          # State machine
│   └── visualization.py       # Dashboard & charts
│
├── maps/                      # 6 JSON map files
│   ├── map_simple.json
│   ├── map_maze.json
│   ├── map_warehouse.json
│   ├── map_city_grid.json
│   ├── map_parking_lot.json
│   └── map_hospital.json
│
├── tests/                     # 116 unit tests
│   ├── __init__.py      # Empty File
│   ├── test_path_planning.py      # A*/Dijkstra tests (25 tests)
│   ├── test_agent.py              # Agent movement/sensors (14 tests)
│   ├── test_perception.py         # OpenCV module tests (9 tests)
│   ├── test_navigation.py         # State machine tests (15 tests)
│   ├── test_simulation.py         # Grid world tests (24 tests)
│   ├── test_visualization.py      # Dashboard tests (14 tests)
│   └── test_yolo_detector.py      # YOLO detector tests (12 tests)
│
├── docs/                      # Documentation
├── notebooks/                 # Jupyter notebooks
│
├── outputs/
│   ├── captures/              # Screenshots
│   ├── metrics/               # CSV navigation metrics
│   ├── models/                # YOLO model files
│   └── plots/                 # Matplotlib charts
│       ├── astar__exploration.png                                        
│       ├── algorithm_comparison.png                    
│       ├── sensor_readings.png                    
│       └── path_comparison.png 
│
└── screenshots/               # Demo screenshots
    ├── dijkstra_opencv.png                                        
    ├── astar_opencv.png 
    ├── dijkstra_yolo_opencv.png                                        
    ├── astar_yolo_opencv.png 
    ├── dijkstra_yolo.png                                        
    ├── astar_yolo.png                    
    ├── dijkstra_planning.png                    
    └── astar_planning.png 
```

## Technology Stack

| Component       | Technology                | Version |
|-----------------|---------------------------|---------|
| Language        | Python                    | 3.11    |
| Simulation      | Pygame                    | ≥2.5.0  |
| Computer Vision | OpenCV                    | ≥4.8.0  |
| ML Detection    | YOLOv8-nano (Ultralytics) | ≥8.4.84 |
| Numerical       | NumPy                     | ≥1.24.0 |
| Charts          | Matplotlib                | ≥3.7.0  |
| Data Analysis   | Pandas                    | ≥2.0.0  |
| Testing         | pytest                    | ≥7.0.0  |
| Notebooks       | Jupyter                   | ≥7.0.0  |
