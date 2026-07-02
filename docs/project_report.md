# AI-Based Autonomous Navigation System — Project Report

## Abstract

This project presents an AI-based autonomous navigation system that enables a virtual agent to navigate from a start point to a goal point in a 2D grid environment. 

The system implements a complete sense-plan-act pipeline with three-level perception (simulated 8-direction raycasting sensors, OpenCV contour detection, and optional YOLOv8-nano ML detection), 
dual path planning algorithms (A* and Dijkstra) on an 8-connected grid, and dynamic obstacle avoidance with real-time replanning via a 7-state machine.

The simulation runs in Pygame at 60 FPS with interactive controls, a real-time HUD dashboard, CSV metrics export, and Matplotlib comparison charts. Testing across 6 different map environments 
(Simple, Maze, Warehouse, City Grid, Parking Lot, Hospital) demonstrates 100% navigation success rate. 

Algorithm comparison shows A* explores 87–97% fewer nodes than Dijkstra while producing identical optimal paths.

---

## 1. Introduction

### 1.1 Problem Statement
Autonomous navigation is a fundamental challenge in robotics and artificial intelligence. 
The ability for a robot or vehicle to navigate from point A to point B without human intervention requires 
integrating perception, planning, and control systems — capabilities critical for self-driving cars, warehouse 
robots, and delivery drones.

### 1.2 Motivation
- Eliminates need for human operators in navigation tasks
- Reduces accidents caused by human error
- Enables 24/7 autonomous operation in warehouses, roads, and hazardous environments
- Provides a testing framework for comparing navigation algorithms

### 1.3 Objectives
1. Build a real-time 2D simulation of autonomous navigation
2. Implement A* and Dijkstra path planning algorithms with animated visualization
3. Create a multi-level perception system (simulated sensors, OpenCV, YOLOv8)
4. Design dynamic obstacle avoidance with a 7-state machine
5. Provide interactive controls, real-time HUD, and analytics dashboard
6. Achieve 100% navigation success across 6 different environments
7. Export metrics to CSV and generate comparison charts

---

## 2. Literature Review

### 2.1 Path Planning Algorithms
- **A*** **Algorithm**: Optimal pathfinding using heuristic search (Hart et al., 1968). Uses f(n) = g(n) + h(n) with admissible heuristics to guarantee optimal paths.
- **Dijkstra's Algorithm**: Shortest path in weighted graphs (Dijkstra, 1959). Explores uniformly without heuristics, suitable for all-pairs shortest path problems.
- **RRT**: Rapidly-exploring Random Trees for high-dimensional spaces (LaValle, 1998).

### 2.2 Computer Vision in Navigation
- **OpenCV**: Open-source computer vision library for real-time image processing. Used for HSV color filtering and contour detection.
- **YOLO**: You Only Look Once for real-time object detection (Redmon et al., 2016). YOLOv8-nano variant provides lightweight ML-based detection.
- **Contour Detection**: Edge-based obstacle identification using `cv2.findContours()`.

### 2.3 Autonomous Systems
- **Sense-Plan-Act**: Classical robotics architecture (Arkin, 1998)
- **Reactive Architecture**: Brooks' subsumption architecture (1986)
- **ROS**: Robot Operating System for real-world deployment

---

## 3. Methodology

### 3.1 System Architecture
The system follows a modular sense-plan-act architecture with 8 source modules:

```
GridWorld → Agent → Perception → PathPlanner → NavigationController → Dashboard
```

### 3.2 Technology Stack

| Component     | Technology                | Version |
|---------------|---------------------------|---------|
| Language      | Python                    | 3.11    |
| Simulation    | Pygame                    | ≥2.5.0  |
| Perception    | OpenCV                    | ≥4.8.0  |
| ML Detection  | YOLOv8-nano (Ultralytics) | ≥8.4.84 |
| Numerical     | NumPy                     | ≥1.24.0 |
| Charts        | Matplotlib                | ≥3.7.0  |
| Data Analysis | Pandas                    | ≥2.0.0  |
| Testing       | pytest                    | ≥7.0.0  |
| Notebooks     | Jupyter                   | ≥7.0.0  |


### 3.3 Development Approach
- Agile iterative development
- Test-driven development with 116 unit tests
- Modular design with clean class interfaces
- Centralized configuration in `config.py`

---

## 4. System Design

### 4.1 Modules
1. **Simulation Engine** (`simulation.py`) — `GridWorld` class: 40×30 grid, 20px cells, 60 FPS rendering, JSON map loading, overlay management, frame capture
2. **Agent** (`agent.py`) — `Agent` class: smooth continuous movement at 6 cells/sec, 8-direction raycasting sensors (range 7 cells), trail history, collision detection
3. **Perception** (`perception.py`) — `PerceptionModule` class: OpenCV HSV color filtering, contour detection for walls and dynamic obstacles
4. **YOLO Detector** (`yolo_detector.py`) — `YOLODetector` class: YOLOv8-nano ML-based object detection (optional)
5. **Path Planning** (`path_planning.py`) — `PathPlanner` class: A* and Dijkstra algorithms, animated exploration generator, Manhattan/Euclidean heuristics
6. **Navigation** (`navigation.py`) — `NavigationController` class: 7-state machine, dynamic obstacle avoidance, replanning logic
7. **Visualization** (`visualization.py`) — `Dashboard` class: real-time HUD, CSV metrics export, Matplotlib comparison charts
8. **Configuration** (`config.py`) — All centralized constants and keybindings


### 4.2 Data Flow
```
1. Grid Map loaded from JSON (maps/map_*.json)
2. Agent senses environment via 8-direction raycasting (range: 7 cells)
3. Path Planner computes optimal route (A* with Manhattan heuristic or Dijkstra) on 8-connected grid
4. Navigation Controller follows waypoints at 6 cells/second
5. Dynamic obstacle detected → AVOIDING → REPLANNING → new path computed
6. Agent reaches goal → REACHED state
7. Metrics recorded → CSV export → Matplotlib charts generated
```

### 4.3 Navigation State Machine
```
IDLE → PLANNING → MOVING → AVOIDING → REPLANNING → REACHED
                                              → NO_PATH
```

| State      | Description                                         |
|------------|-----------------------------------------------------|
| IDLE       | Waiting for user to start navigation                |
| PLANNING   | Computing initial path                              |
| MOVING     | Agent following waypoints, monitoring for obstacles |
| AVOIDING   | Path blocked, waiting for 500ms cooldown            |
| REPLANNING | Computing new path around obstacles                 |
| REACHED    | Goal successfully reached                           |
| NO_PATH    | No feasible path (max 15 replans exceeded)          |

---

## 5. Algorithm Analysis

### 5.1 A* Algorithm
- **Heuristic**: Manhattan distance (default) or Euclidean distance
- **Grid**: 8-connected, uniform cost of 1.0 per move
- **Time Complexity**: O(V log V + E) with binary heap
- **Space Complexity**: O(V)
- **Optimal**: Yes, with admissible heuristic
- **Animated exploration**: Python generator yielding frontier, explored, current, path states

### 5.2 Dijkstra's Algorithm
- **Approach**: Uniform cost search, no heuristic
- **Time Complexity**: O(V log V + E) with binary heap
- **Space Complexity**: O(V)
- **Optimal**: Yes
- **Exploration**: Uniform circular expansion

### 5.3 Comparison

| Metric         | A*       | Dijkstra | Improvement         |
|----------------|----------|----------|---------------------|
| Nodes Explored | ~36      | ~1,100   | 96.7% fewer         |
| Path Length    | 36 cells | 36 cells | Identical (optimal) |
| Planning Time  | ~1.0 ms  | ~30.4 ms | 96.7% faster        |

### 5.4 Key Insight
A* with Manhattan heuristic explores 87–97% fewer nodes than Dijkstra on the same map. 
Both algorithms produce identical optimal paths (same path length), but A* achieves this with dramatically 
less computation by using heuristic guidance.

---

## 6. Implementation

### 6.1 Simulation Engine
- 40×30 grid with 20px cells (total 1,200 cells)
- 6 map environments loaded from JSON files
- Real-time rendering at 60 FPS
- A* exploration overlay (frontier, explored, current node visualization)
- Frame capture for OpenCV/YOLO processing

### 6.2 Agent System
- Smooth continuous movement between waypoints at 6 cells/second
- 8-direction raycasting sensors with 7-cell range
- Color-coded beams: green (safe), yellow (caution), red (danger)
- Trail history visualization (up to 200 points)
- Heading indicator showing movement direction

### 6.3 Perception System
- **Level 1 (Simulated)**: Raycasting in 8 directions (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°)
- **Level 2 (OpenCV)**: HSV color filtering for dark gray walls and red dynamic obstacles, contour detection with area > 50 filtering
- **Level 3 (YOLOv8-nano)**: Optional ML-based real-time object detection

### 6.4 Interactive Controls

| Key   | Action                                                                 |
|-------|------------------------------------------------------------------------|
| SPACE | Start navigation / Pause                                               |
| R     | Reset simulation                                                       |
| 1–6   | Switch map (Simple, Maze, Warehouse, City Grid, Parking Lot, Hospital) |
| A / D | Switch algorithm (A* / Dijkstra)                                       |
| P     | Toggle OpenCV perception                                               |
| Y     | Toggle YOLO detection                                                  |
| S     | Save screenshot                                                        |
| N     | Spawn random dynamic obstacle                                          |
| ESC   | Quit                                                                   |


### Mouse Controls

| Mouse        | Action      |
|--------------|-------------|
| Left-click   | Add wall    |
| Right-click  | Remove wall |
| Middle-click | Set goal    |

### 6.5 Analytics Dashboard
- Real-time HUD panel: state, algorithm, path length, step progress, replan count, nodes explored, planner time, OpenCV/YOLO status, sensor readings
- CSV export: `outputs/metrics/navigation_metrics.csv`
- Matplotlib charts: path comparison (A* vs Dijkstra), sensor readings over time

---

## 7. Results

### 7.1 Navigation Success Rate

| Map         | Algorithm | Success Rate |
|-------------|-----------|--------------|
| Simple      | A*        | 100%         |
| Maze        | A*        | 100%         |
| Warehouse   | A*        | 100%         |
| City Grid   | A*        | 100%         |
| Parking Lot | A*        | 100%         |
| Hospital    | A*        | 100%         |

### 7.2 Performance Metrics
- Average path planning time: < 5ms (A*), < 50ms (Dijkstra)
- Agent speed: 6 cells/second
- Dynamic obstacle replanning: < 500ms cooldown
- Rendering: 60 FPS with full HUD

### 7.3 Algorithm Comparison
- A* explores 87–97% fewer nodes than Dijkstra
- Both produce identical optimal paths
- A* with Manhattan heuristic is the recommended default

### 7.4 Interactive Features
- Click-to-place obstacles with real-time replanning
- Keyboard controls for map/algorithm/perception switching
- Screenshot capture and metrics export
- Animated A* exploration visualization

---

## 8. Testing

### 8.1 Test Coverage
- **116 unit tests** across 7 test files
- **100% pass rate**

| Test File               | Module Covered                          |
|-------------------------|-----------------------------------------|
| `test_simulation.py`    | GridWorld, map loading, cell management |
| `test_agent.py`         | Agent movement, sensors, collision      |
| `test_path_planning.py` | A* and Dijkstra algorithms              |
| `test_navigation.py`    | State machine, replanning logic         |
| `test_perception.py`    | OpenCV detection pipeline               |

### 8.2 Test Framework
- pytest ≥7.0.0
- Run with: `python -m pytest`
- Run with: `python -m pytest -v`
- Run with: `python -m pytest -q`

---

## 9. Limitations

1. **2D Simulation**: Limited to grid-based environments; no 3D or continuous space
2. **Perfect Information**: Agent has complete map knowledge (walls known)
3. **Synthetic Perception**: Simulated raycasting, not real sensor data
4. **No Real Hardware**: Simulation only, not deployed on physical robot
5. **Single Agent**: No multi-agent coordination or collision avoidance

---

## 10. Future Work

1. **ROS Integration**: Deploy on real robot hardware (TurtleBot, Arduino)
2. **3D Simulation**: Upgrade to CARLA, Webots, or Gazebo
3. **Reinforcement Learning**: Train agent with DQN/PPO for adaptive navigation
4. **Multi-Agent**: Multiple robots navigating simultaneously with inter-agent collision avoidance
5. **SLAM**: Simultaneous Localization and Mapping for unknown environments
6. **Real Camera Input**: Replace simulation with webcam feed for real-world testing

---

## 11. Conclusion

This project successfully implements a complete autonomous navigation pipeline with:
- A* and Dijkstra path planning with animated visualization and performance comparison
- Multi-level perception (simulated raycasting, OpenCV contour detection, YOLOv8-nano ML)
- Dynamic obstacle avoidance with a 7-state machine and automatic replanning
- Interactive simulation with 6 map environments and real-time controls
- 116 unit tests with 100% pass rate
- Comprehensive documentation, analytics dashboard, and presentation materials

The system demonstrates industry-relevant skills in AI, robotics, computer vision, and software engineering.

---

## References

1. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics*.
2. Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik*.
3. Redmon, J., et al. (2016). You Only Look Once: Unified, Real-Time Object Detection. *CVPR*.
4. LaValle, S. M. (1998). Rapidly-Exploring Random Trees: A New Tool for Path Planning.
5. Arkin, R. C. (1998). *Behavior-Based Robotics*. MIT Press.
6. Brooks, R. A. (1986). A Robust Layered Control System for a Mobile Robot. *IEEE Journal of Robotics and Automation*.
7. Pygame Community. Pygame Documentation. https://www.pygame.org/docs/
8. OpenCV Team. OpenCV Documentation. https://docs.opencv.org/
9. Ultralytics. YOLOv8 Documentation. https://docs.ultralytics.com/
