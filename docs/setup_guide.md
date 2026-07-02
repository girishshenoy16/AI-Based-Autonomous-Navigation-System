# Setup Guide

## Prerequisites
- **Python 3.11** (3.9+ minimum, 3.11 recommended)
- **No GPU required** (YOLOv8-nano runs on CPU)
- ~500 MB disk space
- Windows, macOS, or Linux

## Installation (Windows)

### Step 1: Navigate to Project Directory
```powershell
cd "AI-Based Autonomous Navigation System"
```

### Step 2: Create Virtual Environment
```powershell
python -m venv venv
```

### Step 3: Activate Virtual Environment
```powershell
.\venv\Scripts\activate
```

### Step 4: Upgrade pip
```powershell
pip install --upgrade pip
```

### Step 5: Install Requirements
```powershell
pip install -r requirements.txt
```

### Step 6: Verify Installation
```powershell
python -c "import pygame, cv2, numpy, matplotlib, pandas; print('All OK')"
```

### Step 7 (Optional): Verify YOLO
```powershell
python -c "from ultralytics import YOLO; print('YOLO OK')"
```

## Installation (macOS/Linux)
```bash
cd "AI-Based Autonomous Navigation System"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python3 -c "import pygame, cv2, numpy, matplotlib, pandas; print('All OK')"
```

## Requirements

| Package       | Version | Purpose                             |
|---------------|---------|-------------------------------------|
| pygame        | ≥2.5.0  | 2D simulation engine                |
| opencv-python | ≥4.8.0  | Computer vision (contour detection) |
| numpy         | ≥1.24.0 | Numerical operations                |
| matplotlib    | ≥3.7.0  | Charts and analytics                |
| pandas        | ≥2.0.0  | Data analysis                       |
| ultralytics   | ≥8.4.84 | YOLOv8-nano ML detection            |
| pytest        | ≥7.0.0  | Unit testing                        |
| notebook      | ≥7.0.0  | Jupyter notebooks                   |

## Running the Simulation

### Default (Simple map, A* algorithm)
```bash
python main.py
```

### Command-Line Arguments
```bash
# Specific map
python main.py --map maze

# Specific algorithm
python main.py --algorithm dijkstra

# With OpenCV perception
python main.py --perception opencv

# With YOLO detection
python main.py --perception yolo

# Full options
python main.py --map warehouse --algorithm astar --perception opencv --save-metrics
```

### Available Maps
| Map         | Command             | Description                |
|-------------|---------------------|----------------------------|
| Simple      | `--map simple`      | Open area, minimal walls   |
| Maze        | `--map maze`        | Complex corridors          |
| Warehouse   | `--map warehouse`   | Industrial shelving layout |
| City Grid   | `--map city_grid`   | Urban street blocks        |
| Parking Lot | `--map parking_lot` | Parking spaces and lanes   |
| Hospital    | `--map hospital`    | Medical facility layout    |

### Quick Demo
```bash
python main.py
```

## Running Tests
```bash
# Run all 116 tests
python -m pytest 
python -m pytest -v
python -m pytest -q

# Run specific test file
python -m pytest tests/test_path_planning.py -v

# Run with coverage
python -m pytest -v --tb=short
```

## Keyboard Controls

| Key   | Action                                                                 |
|-------|------------------------------------------------------------------------|
| SPACE | Start navigation / Pause                                               |
| R     | Reset simulation                                                       |
| 1–6   | Switch map (Simple, Maze, Warehouse, City Grid, Parking Lot, Hospital) |
| A     | Switch to A* algorithm                                                 |
| D     | Switch to Dijkstra algorithm                                           |
| P     | Toggle OpenCV perception                                               |
| Y     | Toggle YOLO detection                                                  |
| S     | Save screenshot                                                        |
| N     | Spawn random dynamic obstacle                                          |
| ESC   | Quit                                                                   |

## Mouse Controls

| Action       | Effect                      |
|--------------|-----------------------------|
| Left-click   | Add wall at clicked cell    |
| Right-click  | Remove wall at clicked cell |
| Middle-click | Set goal at clicked cell    |

## Output Files

| Directory                                | Content                                              |
|------------------------------------------|------------------------------------------------------|
| `outputs/captures/`                      | Screenshots (PNG)                                    |
| `outputs/metrics/navigation_metrics.csv` | Navigation metrics CSV                               |
| `outputs/plots/`                         | Matplotlib charts (path comparison, sensor readings) |
| `outputs/models/`                        | YOLO model files                                     |


## Navigation Metrics CSV Columns

| Column            | Description                            |
|-------------------|----------------------------------------|
| timestamp         | Run timestamp                          |
| map               | Map name (Simple, Maze, etc.)          |
| algorithm         | astar or dijkstra                      |
| state             | Final state (REACHED, NO_PATH)         |
| path_length       | Number of cells in path                |
| path_index        | Final waypoint index                   |
| nodes_explored    | Nodes expanded during planning         |
| planner_time_ms   | Planning time in milliseconds          |
| total_time_s      | Total navigation time in seconds       |
| replan_count      | Number of replanning events            |
| dynamic_obstacles | Number of dynamic obstacles            |
| opencv_active     | OpenCV perception enabled (True/False) |
| yolo_active       | YOLO detection enabled (True/False)    |
| sensor_avg        | Average sensor reading distance        |


## Troubleshooting

### `ModuleNotFoundError: No module named 'pygame'`
Ensure virtual environment is activated. Look for `(venv)` in terminal prompt.

### Pygame window is black
Ensure `pygame.display.flip()` is called in the render loop. The simulation calls this in `GridWorld.tick()`.

### OpenCV crashes
Always call `cv2.waitKey(1)` after `cv2.imshow()`. The perception module handles this in `PerceptionModule.draw()`.

### YOLO model not found
The first run will download the YOLOv8-nano model (~6MB). Ensure internet connection for initial download.

### `No module named 'ultralytics'`
YOLO is optional. Run without `--perception yolo` if not needed. The system works fully without it.

### Performance issues
- Close other Pygame/OpenCV windows
- Use `--perception simulated` (default) for best performance
- Reduce FPS in `config.py` if needed (default: 60)
