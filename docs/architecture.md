# System Architecture

## Overview

The **AI-Based Autonomous Navigation System** is designed using a modular **Sense–Plan–Act** architecture, a widely adopted paradigm in autonomous robotics and intelligent systems. The architecture separates perception, planning, navigation, and visualization into independent modules, enabling clean communication between components while improving maintainability, scalability, and testability.

The system simulates how an autonomous robot perceives its environment, computes an optimal route, reacts to dynamic obstacles, and continuously updates its navigation strategy in real time.

The architecture emphasizes:

- Modular software design
- Clear separation of responsibilities
- Extensible AI pipeline
- Real-time autonomous decision making
- Performance monitoring and analytics
- Industry-oriented software engineering practices

---

# Design Principles

The project follows several core software engineering and robotics design principles.

## 1. Modular Architecture

Each subsystem is implemented independently and communicates through clearly defined interfaces. Individual modules can be developed, tested, and extended without affecting the rest of the application.

## 2. Separation of Concerns

Responsibilities are divided across dedicated modules.

- Simulation Engine
- Agent
- Perception
- Path Planning
- Navigation Controller
- Visualization
- Configuration

This minimizes coupling while maximizing maintainability.

## 3. Sense–Plan–Act Robotics Pipeline

The overall workflow follows the classical robotics pipeline:

```
Sense → Plan → Act
```

This architecture is widely used in autonomous robots, warehouse automation systems, and self-driving vehicles.

## 4. Extensibility

The architecture is intentionally designed so that future algorithms and perception models can be integrated with minimal modifications.

Examples include:

- RRT / RRT*
- D* Lite
- SLAM
- Reinforcement Learning
- ROS Integration
- Multi-Agent Navigation

## 5. Configuration Driven

System constants such as:

- Colors
- Grid dimensions
- Simulation speed
- Keyboard controls
- Sensor configuration

are centralized in `config.py`, reducing hardcoded values throughout the codebase.

## 6. Testability

Every major subsystem can be independently tested using unit tests.

This enables reliable validation of:

- Navigation
- Path Planning
- Perception
- Simulation
- Visualization
- Agent Behaviour

---

# High-Level System Architecture

The autonomous navigation pipeline follows the workflow shown below.

```
                           User Input
                                │
                                ▼
                  ┌──────────────────────────┐
                  │   Simulation Engine      │
                  │      (GridWorld)         │
                  └──────────────────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │    Agent Controller      │
                  └──────────────────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │   Perception Module      │
                  │ Raycasting • OpenCV      │
                  │     • YOLOv8-nano        │
                  └──────────────────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │      Path Planner        │
                  │   A* / Dijkstra Search   │
                  └──────────────────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ Navigation Controller    │
                  │ State Machine +          │
                  │ Dynamic Replanning       │
                  └──────────────────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ Visualization &          │
                  │ Analytics Layer          │
                  │ HUD • Charts • CSV       │
                  │ Reports • Screenshots    │
                  └──────────────────────────┘
```

Each component communicates only with the adjacent layer, resulting in a clean and maintainable architecture that is easy to extend for future robotics applications.

---

# Architecture Diagram

The system is organized into six primary layers. Each layer has a dedicated responsibility and communicates with adjacent layers through well-defined interfaces.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           SIMULATION ENGINE                                  │
│                                                                              │
│                       GridWorld (Pygame 2D Grid)                             │
│                  40 × 30 Grid • 20 px Cells • 60 FPS                         │
│                                                                              │
│       ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                 │
│       │ Map Loading  │   │  Rendering   │   │   Overlay    │                 │
│       │ (JSON Maps)  │   │  (Pygame)    │   │ Path Visuals │                 │
│       └──────────────┘   └──────────────┘   └──────────────┘                 │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              AGENT MODULE                                    │
│                                                                              │
│                           Agent (agent.py)                                   │
│                                                                              │
│       ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                 │
│       │  Movement    │   │ Raycasting   │   │  Collision   │                 │
│       │ Controller   │   │   Sensors    │   │  Detection   │                 │
│       └──────────────┘   └──────────────┘   └──────────────┘                 │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                           PERCEPTION MODULE                                  │
│                                                                              │
│                  PerceptionModule (perception.py)                            │
│                                                                              │
│      Level 1        Level 2                Level 3                           │
│   Raycasting  ───►  OpenCV  ───►  YOLOv8-nano (Optional)                     │
│                                                                              │
│          Sensor Fusion & Obstacle Detection Pipeline                         │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         PATH PLANNING MODULE                                 │
│                                                                              │
│                    PathPlanner (path_planning.py)                            │
│                                                                              │
│         A* Search          Dijkstra Search          Animated Search          │
│                                                                              │
│        Heuristic Search      Uniform Search      Exploration Visualizer      │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     NAVIGATION & CONTROL MODULE                              │
│                                                                              │
│                NavigationController (navigation.py)                          │
│                                                                              │
│      State Machine      Dynamic Obstacle      Automatic Replanning           │
│                                                                              │
│   IDLE → PLAN → MOVE → AVOID → REPLAN → REACHED / NO_PATH                    │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     VISUALIZATION & ANALYTICS                                │
│                                                                              │
│                    Dashboard (visualization.py)                              │
│                                                                              │
│      HUD          CSV Export        Charts         Screenshots               │
│                                                                              │
│        Real-Time Monitoring & Performance Analytics                          │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

# Runtime Execution Flow

The application executes continuously at **60 FPS**, allowing the autonomous agent to react to environmental changes in real time.

```
                           Load Selected Map
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │ Initialize Simulation│
                      └──────────────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │   Initialize Agent   │
                      └──────────────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │ Capture Sensor Data  │
                      │    (Raycasting)      │
                      └──────────────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │  OpenCV Processing   │
                      │     (Optional)       │
                      └──────────────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │   YOLO Detection     │
                      │     (Optional)       │
                      └──────────────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │ Generate Obstacle Map│
                      └──────────────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │ Compute Optimal Path │
                      │   (A* / Dijkstra)    │
                      └──────────────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │ Navigation Controller│
                      └──────────────────────┘
                                   │
                                   ▼
                      ┌──────────────────────┐
                      │      Move Agent      │
                      └──────────────────────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │ Obstacle Found?│
                          └───────┬────────┘
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                    No                        Yes
                     │                         │
                     ▼                         ▼
            Continue Navigation        Replan Path
                     │                         │
                     └────────────┬────────────┘
                                  │
                                  ▼
                      ┌──────────────────────┐
                      │   Update Dashboard   │
                      └──────────────────────┘
                                  │
                                  ▼
                      ┌──────────────────────┐
                      │  Render Next Frame   │
                      └──────────────────────┘
                                  │
                                  ▼
                      ┌──────────────────────┐
                      │   Repeat @ 60 FPS    │
                      └──────────────────────┘
```

---

# Component Dependency Graph

The dependency graph illustrates how different software modules interact while maintaining a layered architecture.

```
                              main.py
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
      ┌────────────┐      ┌──────────────┐      ┌─────────────────┐
      │ config.py  │      │ simulation.py│      │ visualization.py│
      └────────────┘      └──────┬───────┘      └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    agent.py     │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ perception.py   │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │path_planning.py │
                        └────────┬────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │ navigation.py   │
                        └─────────────────┘
```

Only higher-level modules interact directly with lower-level modules, reducing unnecessary coupling and improving maintainability.

---

# System Data Flow

Unlike the previous architecture diagram, the following illustrates how **information** moves through the system.

```
                             ┌──────────────┐
                             │   JSON Map   │
                             └──────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │     GridWorld      │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │   Agent Position   │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │  Sensor Readings   │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │ Obstacle Detection │
                          │   & Information    │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │    Path Planner    │
                          │ (A* / Dijkstra)    │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │ Optimal Waypoints  │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │ Navigation Control │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │   Agent Movement   │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │ Performance Metrics│
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │     Dashboard      │
                          └────────────────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │ CSV Export • Charts│
                          │   • Screenshots    │
                          └────────────────────┘
```

This continuous feedback loop enables the agent to adapt its navigation strategy whenever the environment changes during execution.

---

# Module Responsibilities

The autonomous navigation system is divided into independent modules, each responsible for a specific stage of the navigation pipeline.

| Module                    | File                   | Primary Class          | Primary Responsibility                                                                              |
|---------------------------|------------------------|------------------------|-----------------------------------------------------------------------------------------------------|
| **Simulation Engine**     | `src/simulation.py`    | `GridWorld`            | Creates and manages the grid environment, rendering pipeline, map loading, and obstacle management. |
| **Agent System**          | `src/agent.py`         | `Agent`                | Controls robot movement, maintains navigation state, performs raycasting, and collision detection.  |
| **Perception Engine**     | `src/perception.py`    | `PerceptionModule`     | Processes simulated sensor data and OpenCV-based obstacle detection.                                |
| **Object Detection**      | `src/yolo_detector.py` | `YOLODetector`         | Performs optional AI-powered object detection using YOLOv8 Nano.                                    |
| **Path Planner**          | `src/path_planning.py` | `PathPlanner`          | Computes optimal navigation paths using A* and Dijkstra algorithms.                                 |
| **Navigation Controller** | `src/navigation.py`    | `NavigationController` | Coordinates planning, movement, replanning, and state transitions.                                  |
| **Visualization**         | `src/visualization.py` | `Dashboard`            | Displays real-time metrics, HUD, analytics, charts, and exports reports.                            |
| **Configuration**         | `src/config.py`        | —                      | Stores centralized configuration values used throughout the project.                                |

---

# Module Interfaces

Each module exposes a small public API while hiding its internal implementation details. This improves maintainability and allows components to evolve independently.

---

## Simulation Engine (GridWorld)

### Map Management

```python
load_map()
load_map_by_index()
set_goal()
```

### Environment Queries

```python
is_wall()
is_free()
is_path_blocked()
```

### Obstacle Management

```python
add_dynamic_obstacle()
remove_dynamic_obstacle()
spawn_random_obstacle()
```

### Coordinate Utilities

```python
pixel_to_grid()
set_cell()
```

### Rendering

```python
render()
capture_frame()
set_overlay()
clear_overlay()
```

### Simulation Lifecycle

```python
tick()
quit()
```

---

## Agent

### Navigation

```python
reset()
set_path()
update()
```

### Position

```python
get_grid_pos()
```

### Environment Awareness

```python
sense()
check_collision()
is_near_obstacle()
```

### Visualization

```python
draw()
```

---

## Path Planner

### Search Algorithms

```python
astar()
dijkstra()
```

### Visualization

```python
astar_animated()
```

### Analytics

```python
get_comparison_metrics()
```

---

## Navigation Controller

### Navigation

```python
start_navigation()
update()
reset()
```

### Configuration

```python
set_algorithm()
```

### Monitoring

```python
get_status()
```

---

## Perception Module

### Processing

```python
capture()
process()
```

### Detection

```python
get_detection_centers()
```

### Display

```python
draw()
```

### Utilities

```python
toggle()
save_screenshot()
close()
```

---

## Dashboard

### HUD

```python
update_hud()
```

### Metrics

```python
record_metrics()
save_metrics_csv()
```

### Analytics

```python
generate_path_comparison_chart()
generate_sensor_chart()
```

### Screenshots

```python
save_screenshot()
```

---

# Performance Characteristics

| Metric                         | Value        |
|--------------------------------|--------------|
| Grid Resolution                | 40 × 30      |
| Cell Size                      | 20 px        |
| Total Grid Cells               | 1,200        |
| Rendering Speed                | 60 FPS       |
| Agent Speed                    | 6 Cells/sec  |
| Sensor Range                   | 7 Cells      |
| Grid Connectivity              | 8 Directions |
| Average A* Planning Time       | < 5 ms       |
| Average Dijkstra Planning Time | < 50 ms      |
| Dynamic Replanning Delay       | < 500 ms     |
| Supported Maps                 | 6            |
| Unit Tests                     | 116          |
| Navigation Success Rate        | 100%         |

---

# Failure Handling & Recovery

The navigation system is designed to gracefully recover from runtime failures and unexpected environmental changes.

```
                                        ┌────────────────────┐
                           │ Start Navigation   │
                           └────────────────────┘
                                      │
                                      ▼
                           ┌────────────────────┐
                           │    Compute Path    │
                           └─────────┬──────────┘
                                     │
                  ┌──────────────────┴──────────────────┐
                  │                                     │
                  ▼                                     ▼
        ┌────────────────────┐              ┌────────────────────┐
        │     Path Found     │              │      No Path       │
        └─────────┬──────────┘              └─────────┬──────────┘
                  │                                   │
                  ▼                                   ▼
        ┌────────────────────┐              ┌────────────────────┐
        │ Begin Navigation   │              │   NO_PATH State    │
        └─────────┬──────────┘              └────────────────────┘
                  │
                  ▼
        ┌────────────────────┐
        │ Obstacle Detected? │
        └─────────┬──────────┘
                  │
         ┌────────┴────────┐
         │                 │
        No                Yes
         │                 │
         ▼                 ▼
┌────────────────────┐  ┌────────────────────┐
│ Continue Movement  │  │ Enter AVOIDING     │
└────────────────────┘  └─────────┬──────────┘
                                  │
                                  ▼
                       ┌────────────────────┐
                       │ REPLANNING State   │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ New Path Computed  │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │ Resume Navigation  │
                       └────────────────────┘
```

This recovery mechanism allows the agent to continue navigating even when dynamic obstacles block the previously planned route.

---

# Architectural Decisions

Several important design decisions were made during development to balance performance, maintainability, and extensibility.

| Decision                     | Rationale                                                          |
|------------------------------|--------------------------------------------------------------------|
| Grid-Based Environment       | Simplifies visualization and deterministic path planning.          |
| Sense–Plan–Act Pipeline      | Industry-standard robotics architecture.                           |
| Modular Python Classes       | Improves maintainability, testing, and future scalability.         |
| 8-Connected Navigation       | Produces more natural movement than 4-direction grids.             |
| A* as Default Planner        | Significantly faster while preserving optimality.                  |
| Optional YOLO Detection      | Allows execution on systems without machine learning dependencies. |
| Configuration-Driven Design  | Centralizes application settings and simplifies maintenance.       |
| Separate Visualization Layer | Keeps analytics independent from navigation logic.                 |

---

# Extensibility

The architecture has been intentionally designed for future enhancements.

| Current Component     | Possible Future Upgrade    |
|-----------------------|----------------------------|
| A*                    | RRT / RRT*                 |
| Dijkstra              | D* Lite                    |
| Raycasting            | LiDAR Simulation           |
| OpenCV                | Detectron2                 |
| YOLOv8 Nano           | YOLOv11 / RT-DETR          |
| Pygame                | ROS + Gazebo               |
| Static Maps           | SLAM                       |
| Single Agent          | Multi-Agent Navigation     |
| Rule-Based Navigation | Reinforcement Learning     |
| CSV Analytics         | Real-Time Database Logging |

---

# Project Structure

The repository is organized using a modular directory structure to separate source code, documentation, datasets, generated outputs, and test suites.

```text
AI-Based-Autonomous-Navigation-System/
│
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
├── README.md                   # Project overview
│
├── src/                        # Core source code
│   ├── __init__.py
│   ├── config.py               # Global configuration
│   ├── simulation.py           # GridWorld simulation engine
│   ├── agent.py                # Robot agent
│   ├── perception.py           # OpenCV perception
│   ├── yolo_detector.py        # YOLO object detection
│   ├── path_planning.py        # A* & Dijkstra algorithms
│   ├── navigation.py           # Navigation controller
│   └── visualization.py        # Dashboard & analytics
│
├── maps/                       # Navigation environments
│   ├── map_simple.json
│   ├── map_maze.json
│   ├── map_warehouse.json
│   ├── map_city_grid.json
│   ├── map_parking_lot.json
│   └── map_hospital.json
│
├── tests/                      # 116 Unit test suite
│   ├── __init__.py
│   ├── test_path_planning.py
│   ├── test_agent.py
│   ├── test_navigation.py
│   ├── test_simulation.py
│   ├── test_perception.py
│   ├── test_visualization.py
│   └── test_yolo_detector.py
│
├── docs/                       # Project documentation
│   ├── architecture.md
│   ├── project_report.md
│   ├── executive_summary.md
│   ├── algorithms.md
│   └── setup_guide.md
│
├── notebooks/                  # Experimental notebooks
│   └── algorithm_comparison.ipynb
│
├── outputs/
│   ├── captures/               # Screenshots
│   ├── metrics/                # CSV metrics
│   ├── plots/                  # Generated charts
│   └── models/                 # YOLO model weights
│
└── screenshots/                # README assets
    ├── dijkstra_opencv.png
    ├── astar_opencv.png
    ├── dijkstra_yolo_opencv.png
    ├── astar_yolo_opencv.png
    ├── dijkstra_yolo.png
    ├── astar_yolo.png
    ├── dijkstra_planning.png
    └── astar_planning.png 
```

---

# Technology Stack

The project combines Artificial Intelligence, Robotics, Computer Vision, Data Analytics, and Software Engineering technologies.

| Category             | Technology   | Purpose                                |
|----------------------|--------------|----------------------------------------|
| Programming Language | Python 3.11  | Core application development           |
| Simulation Engine    | Pygame       | Real-time 2D simulation                |
| Computer Vision      | OpenCV       | Image processing and contour detection |
| Object Detection     | YOLOv8 Nano  | AI-based obstacle detection            |
| Numerical Computing  | NumPy        | Matrix and array operations            |
| Data Processing      | Pandas       | Metrics processing and reporting       |
| Data Visualization   | Matplotlib   | Charts and analytics                   |
| Testing Framework    | pytest       | Automated testing                      |
| Documentation        | Markdown     | Technical documentation                |
| Version Control      | Git & GitHub | Source code management                 |

---

# Quality Attributes

The architecture was designed with several software quality attributes in mind.

| Attribute           | Implementation                                               |
|---------------------|--------------------------------------------------------------|
| **Modularity**      | Independent components with clearly defined responsibilities |
| **Maintainability** | Layered architecture and centralized configuration           |
| **Scalability**     | Easy integration of new algorithms and perception models     |
| **Extensibility**   | Plugin-style perception and planning modules                 |
| **Testability**     | Independent unit tests for every major subsystem             |
| **Reliability**     | State-based navigation and recovery mechanisms               |
| **Reusability**     | Modular classes reusable across robotics projects            |
| **Readability**     | Consistent naming conventions and documentation              |

---

# Future Architecture Roadmap

The current architecture provides a strong foundation for future research and industrial applications.

```
                          ┌──────────────────────┐
                          │   Current System     │
                          └──────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │ Grid-Based Navigation│
                          └──────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │   SLAM Integration   │
                          └──────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │    ROS / Gazebo      │
                          └──────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │ Real Robot Deployment│
                          └──────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │ Multi-Agent Systems  │
                          │   & Coordination     │
                          └──────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │    Cloud Robotics    │
                          └──────────────────────┘
```

Potential future enhancements include:

- Simultaneous Localization and Mapping (SLAM)
- Reinforcement Learning based navigation
- Multi-Agent path planning
- ROS 2 integration
- Gazebo simulation
- CARLA autonomous driving simulation
- LiDAR sensor simulation
- Cloud-based fleet management

---

# Key Takeaways

This project demonstrates the implementation of a complete autonomous navigation pipeline by combining concepts from multiple domains.

### Artificial Intelligence

- Intelligent path planning
- Search algorithms
- Decision making
- Real-time replanning

### Robotics

- Sense–Plan–Act architecture
- State-machine based navigation
- Dynamic obstacle avoidance
- Autonomous movement

### Computer Vision

- OpenCV perception
- Image processing
- Object detection using YOLO

### Software Engineering

- Modular architecture
- Layered system design
- Unit testing
- Configuration-driven development
- Technical documentation

---

# Conclusion

The **AI-Based Autonomous Navigation System** demonstrates how modern autonomous systems integrate perception, planning, navigation, and visualization into a cohesive software architecture.

Rather than focusing on a single algorithm, the project emphasizes the interaction between multiple intelligent components working together in real time. This modular design not only improves maintainability and scalability but also provides a strong foundation for future enhancements such as SLAM, reinforcement learning, ROS integration, and multi-agent coordination.

The architecture reflects industry-oriented software engineering practices and illustrates the complete lifecycle of an autonomous navigation system—from environmental perception and optimal path computation to intelligent decision-making, dynamic replanning, and performance analytics.

---

# References

1. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). *A Formal Basis for the Heuristic Determination of Minimum Cost Paths.*

2. Dijkstra, E. W. (1959). *A Note on Two Problems in Connection with Graphs.*

3. Brooks, R. A. (1986). *A Robust Layered Control System for a Mobile Robot.*

4. LaValle, S. M. (2006). *Planning Algorithms.*

5. Russell, S., & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach (4th Edition).*

---

<div align="center">

### AI-Based Autonomous Navigation System

**Designed using Modular Software Engineering Principles and the Sense–Plan–Act Robotics Architecture**

**Built using Python, Pygame, OpenCV, YOLOv8, and Artificial Intelligence**

</div>