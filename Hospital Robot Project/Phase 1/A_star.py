
# A_star.py
# Uses the Simulation's pygame loop + sprites, but paths with grid-based Dijkstra.
# The robot sequentially visits "Goal" positions using a priority queue.
# Left-click still sets a temporary ad-hoc goal (optional).

import pygame
import math
import time
from Robot import Robot
from Room_data import Room_data
from PriorityQueue import PriorityQueue
from dynamic_obstacle import Dynamic_obstacle

# ---------------------------- Config ----------------------------
WIDTH, HEIGHT = 700, 700
ROBOT_SIZE = 40
SPEED = 3.5
GOAL_THRESHOLD = 16
CELL_SIZE = 10  # Grid cell size for Dijkstra (smaller = more precise but slower)
CLEARANCE = 18
NUM_OF_ACHEIVEMENTS=0
# ---------------------------- Init ------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hospital robot simulation (Dijkstra grid-based)")
clock = pygame.time.Clock()

BORDER_THICKNESS = 10
DOOR = 60
WALL_THICKNESS = 15

robot_imgs = Robot.robot_imgs
for i in range(len(robot_imgs)):
    robot_imgs[i] = pygame.transform.scale(robot_imgs[i], (ROBOT_SIZE, ROBOT_SIZE))

def draw_robot(surface, x, y, angle):
    if 22.5 < angle <= 67.5:
        surface.blit(robot_imgs[6], (x, y))
    elif 67.5 < angle <= 112.5:
        surface.blit(robot_imgs[1], (x, y))
    elif 112.5 < angle <= 157.5:
        surface.blit(robot_imgs[7], (x, y))
    elif 157.5 < angle <= 202.5:
        surface.blit(robot_imgs[2], (x, y))
    elif 202.5 < angle <= 247.5:
        surface.blit(robot_imgs[5], (x, y))
    elif 247.5 < angle <= 292.5:
        surface.blit(robot_imgs[0], (x, y))
    elif 292.5 < angle <= 337.5:
        surface.blit(robot_imgs[4], (x, y))
    else:
        surface.blit(robot_imgs[3], (x, y))
def draw_dynamic_obstacles(surface, x, y, animation_id=None):
    """
    Draw animated dynamic obstacle and return a list of pygame.Rect for current frame(s).
    """
    current_dyn_rects = []

    if not dynamic_obstacles:
        return current_dyn_rects

    key = animation_id if animation_id is not None else "_default_dynamic_obstacle"
    state = dynamic_animation_states.setdefault(key, {"frame": 0, "last_time": 0})
    current_time = pygame.time.get_ticks()

    if current_time - state["last_time"] >= DYNAMIC_FRAME_DELAY_MS:
        state["frame"] = (state["frame"] + 1) % len(dynamic_obstacles)
        state["last_time"] = current_time

    frame_surface = dynamic_obstacles[state["frame"]]
    frame_rect = frame_surface.get_rect(topleft=(x, y))

    # store rect for collision / detection use
    dynamic_obstacle_rects[key] = frame_rect
    current_dyn_rects.append(frame_rect)

    surface.blit(frame_surface, frame_rect.topleft)
    pygame.draw.rect(surface, (0, 0, 0), frame_rect, 2)

    return current_dyn_rects

def draw_target(surface, x, y):
    pygame.draw.circle(surface, (255, 0, 0), (int(x), int(y)), 8)

# ------------------------- Environment --------------------------
r1 = Room_data(WIDTH, BORDER_THICKNESS, HEIGHT, DOOR)
obstacles = r1.first_floor_struct[:]  # list[pygame.Rect]
obj_obstacles = r1.obj_obstacles_first_floor[:]
dynamic_obstacles = Dynamic_obstacle.Frames
DYNAMIC_FRAME_DELAY_MS = 120  # delay between animation frames in milliseconds
DEFAULT_DYNAMIC_ANIMATION_ID = "_dynamic_obstacle_default"
dynamic_animation_states = {}
dynamic_obstacle_rects = {}
# --------------------------- Grid-based Dijkstra ---------------------------

def inflate_rect_for_clearance(rect: pygame.Rect, clearance: int) -> pygame.Rect:
    return rect.inflate(clearance * 2, clearance * 2)

def point_blocked(x: float, y: float, rects, clearance: int) -> bool:
    """Check if a point is blocked by obstacles."""
    for r in rects:
        if inflate_rect_for_clearance(r, clearance).collidepoint(x, y):
            return True
    return False

def build_grid(rects, clearance):
    """Build a grid representation of the environment."""
    cols = WIDTH // CELL_SIZE
    rows = HEIGHT // CELL_SIZE
    grid = [[False for _ in range(cols)] for _ in range(rows)]
    
    # Mark obstacles in the grid
    for y in range(rows):
        for x in range(cols):
            # Get center of cell
            cell_x = x * CELL_SIZE + CELL_SIZE // 2
            cell_y = y * CELL_SIZE + CELL_SIZE // 2
            if point_blocked(cell_x, cell_y, rects, clearance):
                grid[y][x] = True  # Blocked
    return grid

def pixel_to_cell(x, y):
    """Convert pixel coordinates to grid cell coordinates."""
    col = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)
    return (col, row)

def cell_to_pixel(col, row):
    """Convert grid cell coordinates to pixel coordinates (center of cell)."""
    x = col * CELL_SIZE + CELL_SIZE // 2
    y = row * CELL_SIZE + CELL_SIZE // 2
    return (x, y)

def get_neighbors(col, row, cols, rows):
    """Get 8-connected neighbors of a cell."""
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nc = col + dx
            nr = row + dy
            if 0 <= nc < cols and 0 <= nr < rows:
                neighbors.append((nc, nr))
    return neighbors

def dist_cells(cell1, cell2):
    """Calculate distance between two cells."""
    c1, r1 = cell1
    c2, r2 = cell2
    # Use Euclidean distance for diagonal movement
    return math.hypot((c2 - c1) * CELL_SIZE, (r2 - r1) * CELL_SIZE)

def A_star_grid(grid, start_cell, goal_cell):
    """A* algorithm on a grid (Dijkstra + heuristic)."""
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    sc, sr = start_cell
    gc, gr = goal_cell
    
    # Check if start or goal is blocked
    if not (0 <= sc < cols and 0 <= sr < rows) or grid[sr][sc]:
        return []
    if not (0 <= gc < cols and 0 <= gr < rows) or grid[gr][gc]:
        return []

    def heuristic(cell, goal_cell):
        c1, r1 = cell
        c2, r2 = goal_cell
        # (Euclidean distance)
        return math.hypot((c2 - c1) * CELL_SIZE, (r2 - r1) * CELL_SIZE)
    
    pq = PriorityQueue()
    pq.push(start_cell, 0.0)
    g = {start_cell: 0.0}
    parent = {start_cell: None}
    
    while not pq.empty():
        current = pq.pop_lowest_f()
        cost = g.get(current, float('inf'))
        
        if current == goal_cell:
            # Reconstruct path
            path = []
            v = goal_cell
            while v is not None:
                path.append(v)
                v = parent[v]
            path.reverse()
            return path
        
        col, row = current
        neighbors = get_neighbors(col, row, cols, rows)
        
        for neighbor in neighbors:
            nc, nr = neighbor
            if grid[nr][nc]:
                continue
            
            # Movement cost
            if abs(nc - col) + abs(nr - row) == 2:  # Diagonal
                edge_cost = math.sqrt(2) * CELL_SIZE
            else:
                edge_cost = CELL_SIZE
            
            new_cost = cost + edge_cost
            
            if new_cost < g.get(neighbor, float('inf')):
                g[neighbor] = new_cost
                parent[neighbor] = current
                #  f = g + h
                f_cost = new_cost + heuristic(neighbor, goal_cell)
                pq.push(neighbor, f_cost)
    
    return []  # No path found

def plan_path(start, goal, rects):
    """Plan a path from start to goal using grid-based Dijkstra."""
    # Build grid
    grid = build_grid(rects, CLEARANCE)
    
    # Convert pixel coordinates to grid cells
    start_cell = pixel_to_cell(start[0], start[1])
    goal_cell = pixel_to_cell(goal[0], goal[1])
    
    # Run Dijkstra on grid
    path_cells = A_star_grid(grid, start_cell, goal_cell)
    
    if not path_cells:
        return []
    
    # Convert grid cells back to pixel coordinates
    path = [cell_to_pixel(c, r) for c, r in path_cells]
    
    return path

# ------------------------ Goals (priority) ----------------------
# (priority, (x, y)) -> smallest priority first
Goal = [[4, (580, 70)], [3, (58, 310)], [1, (580, 316)], [5, (58, 60)], [0, (58, 550)], [2, (580, 550)]]

open_set = PriorityQueue()
for pr, pos in Goal:
    open_set.push(pos, pr)  # PriorityQueue.push(item, priority)

# ----------------------- Simulation state ----------------------
STATIC_START = (370, 50)  # Static start point
robot_x, robot_y = STATIC_START[0], STATIC_START[1]  # Initialize at static start
angle = 0.0
current_path = []
current_goal = None
adhoc_goal = None   # if user left-clicks
returning_to_start = False  # Flag to track if robot is returning to start
return_path_retry_count = 0  # Counter for retrying return path
MAX_RETRY_ATTEMPTS = 3  # Maximum retry attempts for return path

def advance_along_path(x, y, path, speed):
    if not path:
        return (x, y), path
    tx, ty = path[0]
    dx, dy = tx - x, ty - y
    d = math.hypot(dx, dy)
    if d < max(1.0, speed):
        # consume this waypoint
        path.pop(0)
        return (tx, ty), path
    nx = x + (dx / d) * speed
    ny = y + (dy / d) * speed
    return (nx, ny), path

def face_angle(from_xy, to_xy):
    dx, dy = to_xy[0]-from_xy[0], to_xy[1]-from_xy[1]
    if dx == 0 and dy == 0:
        return 0.0
    return (math.degrees(math.atan2(dy, dx)) + 360) % 360
# -------------------- timing --------------------
start_time = time.time()
# ----------------------------- Loop ----------------------------
running = True
increase = -1
dynamic_x = 400
dynamic_y = 400

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            adhoc_goal = (mx, my)
            # Plan path from current robot position to the clicked goal
            current_goal = adhoc_goal
            current_path = plan_path((robot_x, robot_y), current_goal, obstacles)
            # If no path found, clear the goal
            if not current_path:
                print(f"No path found to clicked goal {current_goal}")
                current_goal = None
                adhoc_goal = None
            returning_to_start = False

    # If no path and not returning to start, and robot is at start, fetch next queued goal
    at_start = math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1]) <= GOAL_THRESHOLD
    if not current_path and current_goal is None and not returning_to_start and at_start and not open_set.empty():
        current_goal = open_set.pop_lowest_f()
        # Plan path from static start point to the goal
        current_path = plan_path(STATIC_START, current_goal, obstacles)
        # If no path found, skip this goal and try next one
        if not current_path:
            print(f"No path found to goal {current_goal}, skipping...")
            current_goal = None

    # If we have a path, move
    if current_path:
        (robot_x, robot_y), current_path = advance_along_path(robot_x, robot_y, current_path, SPEED)
        angle = face_angle((robot_x, robot_y), current_path[0] if current_path else current_goal)
    # If we have a goal but no path (path planning failed), clear the goal to try next one
    elif current_goal is not None and not returning_to_start:
        print(f"Stuck with no path to goal {current_goal}, clearing goal...")
        current_goal = None
        adhoc_goal = None

    # If goal reached
    if current_goal and math.hypot(robot_x - current_goal[0], robot_y - current_goal[1]) <= GOAL_THRESHOLD:
        # After reaching goal, return to static start point
        NUM_OF_ACHEIVEMENTS+=1
        total_time = time.time() - start_time
        print(f"\n⏱️ run time: {total_time:.2f} second")
        print(f"\nnum of the goals has been reached: {NUM_OF_ACHEIVEMENTS} goal")
        current_goal = None
        adhoc_goal = None
        returning_to_start = True
        return_path_retry_count = 0  # Reset retry counter for new return journey
        current_path = plan_path((robot_x, robot_y), STATIC_START, obstacles)
        # If no path found back to start, try to snap to start or handle gracefully
        if not current_path:
            print(f"Warning: No path found back to start from goal position {(robot_x, robot_y)}")
            # Try direct path or snap if close enough
            if math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1]) <= GOAL_THRESHOLD * 2:
                # Close enough, just snap to start
                robot_x, robot_y = STATIC_START[0], STATIC_START[1]
                returning_to_start = False
                current_path = []
            else:
                # Try a few more times with different parameters or give up
                print("Attempting to find alternative path to start...")
                # Could retry with more samples or different clearance, but for now, snap if very close
                if math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1]) <= GOAL_THRESHOLD * 3:
                    robot_x, robot_y = STATIC_START[0], STATIC_START[1]
                    returning_to_start = False
                    current_path = []
    
    # If returning to start and reached it
    if returning_to_start and math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1]) <= GOAL_THRESHOLD:
        returning_to_start = False
        current_path = []
        robot_x, robot_y = STATIC_START[0], STATIC_START[1]  # Snap to exact start position
        return_path_retry_count = 0  # Reset retry counter
    
    # If returning to start but no path (stuck), try to recover
    if returning_to_start and not current_path:
        # Check if we're already close to start
        dist_to_start = math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1])
        if dist_to_start <= GOAL_THRESHOLD * 2:
            # Close enough, snap to start
            robot_x, robot_y = STATIC_START[0], STATIC_START[1]
            returning_to_start = False
            current_path = []
            return_path_retry_count = 0
            print("Recovered: Snapped to start position")
        elif return_path_retry_count < MAX_RETRY_ATTEMPTS:
            # Try to replan the path to start (limit retries)
            return_path_retry_count += 1
            print(f"Retrying path to start (attempt {return_path_retry_count}/{MAX_RETRY_ATTEMPTS})...")
            current_path = plan_path((robot_x, robot_y), STATIC_START, obstacles)
            if current_path:
                # Path found, reset retry counter
                return_path_retry_count = 0
            elif return_path_retry_count >= MAX_RETRY_ATTEMPTS:
                # Last resort: try moving directly towards start (only if very close)
                if dist_to_start <= GOAL_THRESHOLD * 5:
                    print("Using direct approach to start as last resort...")
                    dx = STATIC_START[0] - robot_x
                    dy = STATIC_START[1] - robot_y
                    if dist_to_start > 0:
                        # Move a small step towards start
                        step_size = min(SPEED, dist_to_start)
                        robot_x += (dx / dist_to_start) * step_size
                        robot_y += (dy / dist_to_start) * step_size
                else:
                    # Too far, reset and try again next frame
                    return_path_retry_count = 0

    # ------------- DRAW -------------
    screen.fill((255, 255, 255))

    # Map
    for rect in obstacles:
        pygame.draw.rect(screen, (0, 0, 0), rect)

    # Object obstacles (beds, etc.)
    drawn_rects = []
    for img, size, pos in obj_obstacles:
        scaled = pygame.transform.scale(img.convert_alpha(), size)
        screen.blit(scaled, pos)
        r = pygame.Rect(pos, scaled.get_size())
        r = pygame.Rect(r.left, r.top, r.width-20, r.height)  # mimic original code's -20 width
        drawn_rects.append(r)

    # overlay rects for collision clarity (optional)
    # for r in drawn_rects: pygame.draw.rect(screen, (0, 0, 255), r, 1)

    # Static start point visual (green circle)

    pygame.draw.circle(screen, (0, 255, 0), STATIC_START, 10)
     # Dynamic obstacle animation and collect current dynamic rects
    current_dynamic_rects = []
    if dynamic_x >= 150:
        dynamic_x += increase
        current_dynamic_rects = draw_dynamic_obstacles(screen, dynamic_x, dynamic_y, animation_id="doctor")

    # Goals visual
    for pr, pos in Goal:
        draw_target(screen, pos[0], pos[1])

    # Current path
    if len(current_path) > 1:
        pygame.draw.lines(screen, (255,165,0), False, current_path, 3)

    # Robot
    draw_robot(screen, int(robot_x - ROBOT_SIZE/2), int(robot_y - ROBOT_SIZE/2), angle)

    pygame.display.update()
    clock.tick(30)

pygame.quit()
