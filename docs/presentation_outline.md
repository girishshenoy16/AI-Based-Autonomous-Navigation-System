# Presentation Outline — 15 Minute Slide Deck

---

## Slide 1: Title (1 min)
**AI-Based Autonomous Navigation System**
- Your Name
- Diploma Project
- Date

---

## Slide 2: Problem Statement (1 min)
- Autonomous navigation is critical for robotics and AI
- Challenges: real-time perception, optimal planning, dynamic obstacle avoidance
- Goal: Build a complete sense-plan-act navigation pipeline
- Applications: self-driving cars, warehouse robots, delivery drones

---

## Slide 3: Solution Overview (1 min)
- Sense-Plan-Act architecture (classical robotics paradigm)
- 2D simulation with Pygame (40×30 grid, 20px cells, 60 FPS)
- A* and Dijkstra path planning with comparison analytics
- Dynamic obstacle avoidance with 7-state machine

---

## Slide 4: System Architecture (2 min)
- Show architecture diagram (6 modules)
- Module responsibilities:
  - Simulation Engine (GridWorld) — map loading, rendering
  - Agent — movement, 8-direction raycasting sensors
  - Perception — OpenCV contour detection, YOLOv8-nano
  - Path Planning — A* and Dijkstra algorithms
  - Navigation — state machine, replanning
  - Visualization — HUD, CSV export, Matplotlib charts
- Data flow: Grid Map → Sensors → Path Planner → Waypoints → Controller → Movement

---

## Slide 5: Perception Module (2 min)
- Level 1: Simulated raycasting (8 sensors, range 7 cells, color-coded beams)
  - Green (safe) → Yellow (caution) → Red (danger)
- Level 2: OpenCV contour detection (HSV color filtering, wall/obstacle identification)
- Level 3: YOLOv8-nano ML detection (optional, real-time object detection)
- Show sensor visualization in HUD

---

## Slide 6: Path Planning (2 min)
- A* algorithm: f(n) = g(n) + h(n)
  - Manhattan and Euclidean heuristics
  - 8-connected grid, uniform cost
- Dijkstra: f(n) = g(n) — no heuristic, uniform exploration
- Animated A* visualization: frontier (blue), explored (lavender), current (cyan), path (gold)
- Speed modes: Fast (instant), Medium (0.5s), Slow (3s)

---

## Slide 7: Navigation & Control (1 min)
- 7-state machine:
  ```
  IDLE → PLANNING → MOVING → AVOIDING → REPLANNING → REACHED
                                                → NO_PATH
  ```
- Dynamic obstacle detection (path blocked check)
- Automatic replanning (max 15 replans, 500ms cooldown)
- Interactive controls: click-to-place obstacles, keyboard shortcuts

---

## Slide 8: Live Demo (3 min)
- Start with Simple map, A* algorithm
- Press SPACE to start navigation
- Show agent following path with sensor beams
- Press N to spawn dynamic obstacle
- Show replanning in action (AVOIDING → REPLANNING → MOVING)
- Switch to Maze map (press 2) for complex navigation
- Open OpenCV perception (press P) — show detection window
- Switch to Dijkstra (press D) — compare exploration visually

---

## Slide 9: Results (1 min)
- 100% navigation success across all 6 environments
- Algorithm comparison chart (A* vs Dijkstra)
  - A* explores 87–97% fewer nodes
  - Planning time: ~1ms vs ~30ms
- Real-time dynamic obstacle avoidance
- Interactive analytics dashboard

---

## Slide 10: Testing (0.5 min)
- 87 unit tests, 100% pass rate
- Test files: test_simulation.py, test_agent.py, test_path_planning.py, test_navigation.py, test_perception.py
- Coverage of all core modules
- pytest framework

---

## Slide 11: Tech Stack & Project Structure (0.5 min)
- Python 3.11, Pygame ≥2.5, OpenCV ≥4.8, NumPy, Matplotlib, Pandas, YOLOv8-nano, pytest
- Clean modular architecture: 8 source modules, 6 map files, 87 tests
- Outputs: screenshots, CSV metrics, Matplotlib charts

---

## Slide 12: Future Work (0.5 min)
- ROS integration for real robot hardware (TurtleBot)
- 3D simulation (CARLA or Webots)
- Reinforcement learning (DQN/PPO)
- Multi-agent coordination
- SLAM (Simultaneous Localization and Mapping)
- Real camera input (webcam feed)

---

## Slide 13: Q&A (1 min)
- Open for questions

---

## Key Points to Emphasize
1. **Complete Pipeline**: Perception → Planning → Control — end-to-end autonomous navigation
2. **Industry Relevance**: Self-driving cars, warehouse robots, delivery drones
3. **Technical Depth**: A*, Dijkstra, OpenCV, YOLOv8, state machines
4. **Engineering Quality**: 87 tests, clean architecture, modular design
5. **Portfolio Value**: Impressive for recruiters — real-time simulation with analytics

---

## Demo Script
1. Start with Simple map, A* algorithm (`python main.py --map simple --algorithm astar`)
2. Press SPACE to start navigation
3. Show agent following path with color-coded sensor beams
4. Press N to spawn dynamic obstacle
5. Show replanning in action (state transitions visible in HUD)
6. Switch to Maze map (press 2)
7. Show more complex navigation with longer path
8. Open OpenCV perception (press P)
9. Show detection window with contour detection
10. Press S to save screenshot
11. Press R to reset, switch to Dijkstra (press D)
12. Run same navigation — show larger frontier, more nodes explored
13. Exit (ESC) — show generated comparison chart and sensor readings plot
