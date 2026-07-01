# Algorithm Documentation

## A* Algorithm

### Description
A* is an informed search algorithm that finds the shortest path from a start node to a goal node. 
It uses a heuristic function to guide the search, making it significantly more efficient than Dijkstra's algorithm 
for single-pair pathfinding.

### Formula
```
f(n) = g(n) + h(n)
```
- **g(n)**: Actual cost from start to node n (cumulative step count)
- **h(n)**: Heuristic estimate from n to goal (admissible)
- **f(n)**: Total estimated cost through n

### Heuristics Implemented
1. **Manhattan Distance** (default): `|x1-x2| + |y1-y2|`
   - Optimal for 4-directional movement
   - Admissible (never overestimates)
   - Used by default in all simulations

2. **Euclidean Distance**: `sqrt((x1-x2)² + (y1-y2)²)`
   - Optimal for any-angle movement
   - Admissible and consistent
   - Slightly less tight bound on 8-connected grids

### Grid Connectivity
- **8-connected grid**: Agents can move in all 8 directions (horizontal, vertical, diagonal)
- Each move has uniform cost of 1.0
- Diagonal moves allowed without penalty

### Pseudocode
```
function A*(start, goal):
    open_set = PriorityQueue()
    open_set.add(start, 0)
    came_from = {}
    g_score = {start: 0}
    
    while open_set not empty:
        current = open_set.pop_lowest_f()
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_8_neighbors(current):
            tentative_g = g_score[current] + 1.0
            
            if tentative_g < g_score.get(neighbor, infinity):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                open_set.add(neighbor, f_score)
    
    return null  // No path found
```

### Complexity
- **Time**: O(V log V + E) with binary heap priority queue
- **Space**: O(V)
- **Best case**: O(d) where d is the depth of the solution

### Implementation Details
- Binary heap (Python `heapq`) for priority queue
- Tie-breaking counter to maintain FIFO order for equal f-scores
- Lazy deletion: duplicate entries allowed, stale entries skipped via `g_score` check
- Animated exploration via Python generator yielding `frontier`, `explored`, `current`, `path`, `done`

---

## Dijkstra's Algorithm

### Description
Dijkstra's algorithm finds the shortest path from a start node to all other nodes in a weighted graph. It explores all directions equally without using a heuristic, making it suitable when no goal is known in advance or when all-pairs shortest paths are needed.

### Formula
```
g(n) = cost from start to n
```
No heuristic estimate is used — exploration is purely cost-driven.

### Pseudocode
```
function Dijkstra(start, goal):
    open_set = PriorityQueue()
    open_set.add(start, 0)
    came_from = {}
    g_score = {start: 0}
    
    while open_set not empty:
        current = open_set.pop_lowest_g()
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        for neighbor in get_8_neighbors(current):
            tentative_g = g_score[current] + 1.0
            
            if tentative_g < g_score.get(neighbor, infinity):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                open_set.add(neighbor, tentative_g)
    
    return null  // No path found
```

### Complexity
- **Time**: O(V log V + E) with binary heap priority queue
- **Space**: O(V)

### Implementation Details
- Same binary heap structure as A* implementation
- Priority is solely `g_score` (cumulative cost)
- Explores uniformly in all directions, producing a circular frontier

---

## Comparison

| Aspect         | A*                         | Dijkstra                |
|----------------|----------------------------|-------------------------|
| Heuristic      | Yes (Manhattan/Euclidean)  | No                      |
| Optimal        | Yes (admissible heuristic) | Yes                     |
| Complete       | Yes                        | Yes                     |
| Nodes Explored | 87–97% fewer               | More                    |
| Speed          | Faster                     | Slower                  |
| Use Case       | Known goal position        | All-pairs shortest path |


### Benchmark Results (from simulation runs)

| Metric         | A*       | Dijkstra | Improvement  |
|----------------|----------|----------|--------------|
| Nodes Explored | ~36      | ~1,100   | 96.7% fewer  |
| Path Length    | 36 cells | 36 cells | Identical    |
| Planning Time  | ~1.0 ms  | ~30.4 ms | 96.7% faster |

### When to Use Each
- **A***: Robotics, navigation, game AI — any scenario where the goal is known
- **Dijkstra**: Network routing, map applications — scenarios requiring all-pairs shortest paths

---

## Animated Visualization

The A* algorithm supports animated visualization using Python generators:

### Exploration Overlay Colors
1. **Frontier nodes** (open list) — light blue `#ADE8F0`
2. **Explored nodes** (closed list) — pale lavender `#C8C8E6`
3. **Current node** being expanded — bright cyan `#00FFFF`
4. **Final path** — gold `#FFD700`

### Speed Modes

| Mode   | Delay per Frame | Description                          |
|--------|-----------------|--------------------------------------|
| Fast   | 0 ms            | Instant result, no animation         |
| Medium | 20 ms           | Visible exploration (~0.5s total)    |
| Slow   | 80 ms           | Educational step-by-step (~3s total) |

---

## State Machine

The navigation controller uses a 7-state machine for dynamic obstacle avoidance:

```
IDLE → PLANNING → MOVING → AVOIDING → REPLANNING → REACHED 
                                              → NO_PATH
```

| State      | Description                                         |
|------------|-----------------------------------------------------|
| IDLE       | Waiting for user to start navigation                |
| PLANNING   | Computing initial path (A* or Dijkstra)             |
| MOVING     | Agent following waypoints; monitoring for obstacles |
| AVOIDING   | Path blocked detected; waiting for cooldown         |
| REPLANNING | Computing new path around obstacles                 |
| REACHED    | Goal successfully reached                           |
| NO_PATH    | No feasible path exists (max replans exceeded)      |

### Replanning Parameters
- **Max replan count**: 15
- **Replan cooldown**: 500 ms
- Triggers: path blocked by dynamic obstacle, goal changed, wall added on path
