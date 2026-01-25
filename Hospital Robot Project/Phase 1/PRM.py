# dijkstra_path_planning_with_dynamic_avoidance_reviewed.py
import pygame
import math
import random
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
SAMPLE_COUNT = 280
K_NEIGHBORS = 12
CLEARANCE = 18
NUM_OF_ACHEIVEMENTS=0
# local avoidance params
DETECTION_RANGE = 60      # how far robot "looks" ahead
SENSOR_BOX_SIZE = 30      # size of sensor square
AVOID_STEP_FACTOR = 0.5   # step size factor when sidestepping (fraction of SPEED)
REPLAN_AFTER_FAIL = True  # attempt replanning if local avoidance fails

# ---------------------------- Init ------------------------------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hospital robot simulation (PRM + dynamic avoidance)")
clock = pygame.time.Clock()

BORDER_THICKNESS = 10
DOOR = 60
WALL_THICKNESS = 15

# ---------------- Dynamic obstacle frames (define before functions) -----------
Dynamic_obstacles_frames = Dynamic_obstacle.Frames  # list of surfaces (may be empty)

# ---------------- Robot sprites ----------------
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

def draw_target(surface, x, y):
    pygame.draw.circle(surface, (255, 0, 0), (int(x), int(y)), 8)

# ---------------- Dynamic obstacle drawing (returns rects) -----------
DYNAMIC_FRAME_DELAY_MS = 120  # delay between animation frames in milliseconds
dynamic_animation_states = {}
dynamic_obstacle_rects = {}  # keyed by animation id -> pygame.Rect

def draw_dynamic_obstacles(surface, x, y, animation_id=None):
    """
    Draw animated dynamic obstacle and return a list of pygame.Rect for current frame(s).
    """
    current_dyn_rects = []

    if not Dynamic_obstacles_frames:
        return current_dyn_rects

    key = animation_id if animation_id is not None else "_default_dynamic_obstacle"
    state = dynamic_animation_states.setdefault(key, {"frame": 0, "last_time": 0})
    current_time = pygame.time.get_ticks()

    if current_time - state["last_time"] >= DYNAMIC_FRAME_DELAY_MS:
        state["frame"] = (state["frame"] + 1) % len(Dynamic_obstacles_frames)
        state["last_time"] = current_time

    frame_surface = Dynamic_obstacles_frames[state["frame"]]
    frame_rect = frame_surface.get_rect(topleft=(x, y))

    # store rect for collision / detection use
    dynamic_obstacle_rects[key] = frame_rect
    current_dyn_rects.append(frame_rect)

    surface.blit(frame_surface, frame_rect.topleft)
    pygame.draw.rect(surface, (0, 0, 0), frame_rect, 2)

    return current_dyn_rects

# ------------------------- Environment --------------------------
r1 = Room_data(WIDTH, BORDER_THICKNESS, HEIGHT, DOOR)
obstacles = r1.first_floor_struct[:]  # list[pygame.Rect]
obj_obstacles = r1.obj_obstacles_first_floor[:]  # list of (img, size, pos)

# --------------------------- PRM core ---------------------------
def inflate_rect_for_clearance(rect: pygame.Rect, clearance: int) -> pygame.Rect:
    return rect.inflate(clearance * 2, clearance * 2)

def point_blocked(x: float, y: float, rects, clearance: int) -> bool:
    for r in rects:
        if inflate_rect_for_clearance(r, clearance).collidepoint(x, y):
            return True
    return False

def segment_blocked(p1, p2, rects, clearance: int) -> bool:
    x1, y1 = int(p1[0]), int(p1[1])
    x2, y2 = int(p2[0]), int(p2[1])
    for r in rects:
        rr = inflate_rect_for_clearance(r, clearance)
        if rr.clipline(x1, y1, x2, y2):
            return True
    return False

def dist(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def sample_free_space(n, rects, clearance):
    pts = []
    attempts = 0
    while len(pts) < n and attempts < n * 50:
        attempts += 1
        x = random.randint(20, WIDTH-20)
        y = random.randint(20, HEIGHT-20)
        if not point_blocked(x, y, rects, clearance):
            pts.append((x, y))
    return pts

def k_nearest(k, p, pts):
    return sorted(pts, key=lambda q: dist(p, q))[:k]

def build_graph(samples, rects, clearance):
    graph = {p: [] for p in samples}
    for p in samples:
        for q in k_nearest(K_NEIGHBORS, p, samples):
            if q == p:
                continue
            if not segment_blocked(p, q, rects, clearance):
                graph[p].append(q)
                graph[q].append(p)
    return graph

def connect_point(point, samples, graph, rects, clearance):
    if point not in graph:
        graph[point] = []
    for q in k_nearest(K_NEIGHBORS, point, samples + [point]):
        if q == point:
            continue
        if not segment_blocked(point, q, rects, clearance):
            graph[point].append(q)
            graph[q].append(point)

def dijkstra(graph, start, goal):
    pq = PriorityQueue()
    pq.push(start, 0.0)
    g = {start: 0.0}
    parent = {start: None}

    while not pq.empty():
        u = pq.pop_lowest_f()
        cost = g.get(u, float('inf'))
        if u == goal:
            path = []
            v = goal
            while v is not None:
                path.append(v)
                v = parent[v]
            path.reverse()
            return path
        for v in graph[u]:
            nc = cost + dist(u, v)
            if nc < g.get(v, float('inf')):
                g[v] = nc
                parent[v] = u
                pq.push(v, nc)
    return []

def plan_path(start, goal, rects):
    samples = sample_free_space(SAMPLE_COUNT, rects, CLEARANCE)
    graph = build_graph(samples, rects, CLEARANCE)
    connect_point(start, samples, graph, rects, CLEARANCE)
    connect_point(goal, samples, graph, rects, CLEARANCE)
    return dijkstra(graph, start, goal)

# ---------------- Motion helpers (avoid dynamic obstacles) ----------------
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

# ------------------------ Goals (priority) ----------------------
Goal = [[4, (580, 70)], [3, (58, 310)], [1, (580, 316)], [5, (58, 60)], [0, (58, 550)], [2, (580, 550)]]

open_set = PriorityQueue()
for pr, pos in Goal:
    open_set.push(pos, pr)

# ----------------------- Simulation state ----------------------
STATIC_START = (370, 50)
robot_x, robot_y = STATIC_START[0], STATIC_START[1]
angle = 0.0
current_path = []
current_goal = None
adhoc_goal = None
returning_to_start = False
return_path_retry_count = 0
MAX_RETRY_ATTEMPTS = 3

# ---------------- Local avoidance helpers -----------------------
def detect_dynamic_obstacle_ahead(robot_pos, robot_angle, dyn_rects, detection_range=DETECTION_RANGE, box_size=SENSOR_BOX_SIZE):
    """Return True if any dynamic rect is inside the sensor box ahead of the robot."""
    look_ahead_x = robot_pos[0] + math.cos(math.radians(robot_angle)) * detection_range
    look_ahead_y = robot_pos[1] + math.sin(math.radians(robot_angle)) * detection_range
    sensor_rect = pygame.Rect(int(look_ahead_x - box_size/2), int(look_ahead_y - box_size/2), box_size, box_size)
    for r in dyn_rects:
        if sensor_rect.colliderect(r):
            return True
    return False

def find_alternative_direction(robot_pos, robot_angle, dyn_rects):
    """Try several angle offsets and return first safe angle (or original if none)."""
    offsets = [-45, 45, -30, 30, -90, 90]
    for off in offsets:
        new_angle = (robot_angle + off) % 360
        if not detect_dynamic_obstacle_ahead(robot_pos, new_angle, dyn_rects, detection_range=40, box_size=24):
            return new_angle
    return robot_angle

def step_in_direction(x, y, angle_deg, step):
    nx = x + math.cos(math.radians(angle_deg)) * step
    ny = y + math.sin(math.radians(angle_deg)) * step
    return nx, ny
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
            current_goal = adhoc_goal
            current_path = plan_path((robot_x, robot_y), current_goal, obstacles)
            if not current_path:
                print(f"No path found to clicked goal {current_goal}")
                current_goal = None
                adhoc_goal = None
            returning_to_start = False

    # If no path and not returning to start, and robot is at start, fetch next queued goal
    at_start = math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1]) <= GOAL_THRESHOLD
    if not current_path and current_goal is None and not returning_to_start and at_start and not open_set.empty():
        current_goal = open_set.pop_lowest_f()
        current_path = plan_path(STATIC_START, current_goal, obstacles)
        if not current_path:
            print(f"No path found to goal {current_goal}, skipping...")
            current_goal = None

    # ------------- DRAW -------------
    screen.fill((255, 255, 255))

    # Map (walls)
    for rect in obstacles:
        pygame.draw.rect(screen, (0, 0, 0), rect)

    # Object obstacles (beds, etc.)
    drawn_rects = []
    for img, size, pos in obj_obstacles:
        scaled = pygame.transform.scale(img.convert_alpha(), size)
        screen.blit(scaled, pos)
        r = pygame.Rect(pos, scaled.get_size())
        r = pygame.Rect(r.left, r.top, r.width-20, r.height)
        drawn_rects.append(r)

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

    # ---------- Movement & Local Avoidance ----------
    static_rects_for_planning = obstacles + drawn_rects

    if current_path:
        # Determine next target point (waypoint) to head to
        target_point = current_path[0] if current_path else current_goal
        # Compute desired angle toward next waypoint
        desired_angle = face_angle((robot_x, robot_y), target_point)

        # Check dynamic obstacle ahead in that direction
        blocked = detect_dynamic_obstacle_ahead((robot_x, robot_y), desired_angle, current_dynamic_rects)

        if blocked:
            # Try simple sidestep (local avoidance)
            alt_angle = find_alternative_direction((robot_x, robot_y), desired_angle, current_dynamic_rects)
            if alt_angle != desired_angle:
                # perform a small sidestep toward alt_angle
                step = SPEED * AVOID_STEP_FACTOR
                robot_x, robot_y = step_in_direction(robot_x, robot_y, alt_angle, step)
                angle = alt_angle
                # do NOT pop the waypoint yet; we sidestepped around obstacle
            else:
                # No immediate sidestep possible -> try replanning (avoid dynamic rects)
                if REPLAN_AFTER_FAIL and current_goal is not None:
                    combined_rects = static_rects_for_planning + current_dynamic_rects
                    new_path = plan_path((robot_x, robot_y), current_goal, combined_rects)
                    if new_path:
                        current_path = new_path
                        (robot_x, robot_y), current_path = advance_along_path(robot_x, robot_y, current_path, SPEED)
                        angle = face_angle((robot_x, robot_y), current_path[0] if current_path else current_goal)
                    else:
                        # can't replan now: wait a frame
                        pass
                else:
                    # just wait a frame
                    pass
        else:
            # Path clear -> follow it normally
            (robot_x, robot_y), current_path = advance_along_path(robot_x, robot_y, current_path, SPEED)
            angle = face_angle((robot_x, robot_y), current_path[0] if current_path else current_goal)
    elif current_goal is not None and not returning_to_start:
        # we have a goal but no path (path planning failed), clear the goal to try next one
        print(f"Stuck with no path to goal {current_goal}, clearing goal...")
        current_goal = None
        adhoc_goal = None

    # If goal reached
    if current_goal and math.hypot(robot_x - current_goal[0], robot_y - current_goal[1]) <= GOAL_THRESHOLD:
        NUM_OF_ACHEIVEMENTS+=1
        total_time = time.time() - start_time
        print(f"\n⏱️ run time: {total_time:.2f} second")
        print(f"\nnum of the goals has been reached: {NUM_OF_ACHEIVEMENTS} goal")
        current_goal = None
        adhoc_goal = None
        returning_to_start = True
        return_path_retry_count = 0
        current_path = plan_path((robot_x, robot_y), STATIC_START, obstacles)
        if not current_path:
            print(f"Warning: No path found back to start from goal position {(robot_x, robot_y)}")
            if math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1]) <= GOAL_THRESHOLD * 2:
                robot_x, robot_y = STATIC_START[0], STATIC_START[1]
                returning_to_start = False
                current_path = []
            else:
                print("Attempting to find alternative path to start...")
                if math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1]) <= GOAL_THRESHOLD * 3:
                    robot_x, robot_y = STATIC_START[0], STATIC_START[1]
                    returning_to_start = False
                    current_path = []

    # If returning to start and reached it
    if returning_to_start and math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1]) <= GOAL_THRESHOLD:
        returning_to_start = False
        current_path = []
        robot_x, robot_y = STATIC_START[0], STATIC_START[1]
        return_path_retry_count = 0

    # If returning to start but no path (stuck), try to recover
    if returning_to_start and not current_path:
        dist_to_start = math.hypot(robot_x - STATIC_START[0], robot_y - STATIC_START[1])
        if dist_to_start <= GOAL_THRESHOLD * 2:
            robot_x, robot_y = STATIC_START[0], STATIC_START[1]
            returning_to_start = False
            current_path = []
            return_path_retry_count = 0
            print("Recovered: Snapped to start position")
        elif return_path_retry_count < MAX_RETRY_ATTEMPTS:
            return_path_retry_count += 1
            print(f"Retrying path to start (attempt {return_path_retry_count}/{MAX_RETRY_ATTEMPTS})...")
            current_path = plan_path((robot_x, robot_y), STATIC_START, obstacles)
            if current_path:
                return_path_retry_count = 0
            elif return_path_retry_count >= MAX_RETRY_ATTEMPTS:
                if dist_to_start <= GOAL_THRESHOLD * 5:
                    print("Using direct approach to start as last resort...")
                    dx = STATIC_START[0] - robot_x
                    dy = STATIC_START[1] - robot_y
                    if dist_to_start > 0:
                        step_size = min(SPEED, dist_to_start)
                        robot_x += (dx / dist_to_start) * step_size
                        robot_y += (dy / dist_to_start) * step_size
                else:
                    return_path_retry_count = 0

    # Current path (visual)
    if len(current_path) > 1:
        pygame.draw.lines(screen, (255,165,0), False, current_path, 3)

    # Robot
    draw_robot(screen, int(robot_x - ROBOT_SIZE/2), int(robot_y - ROBOT_SIZE/2), angle)

    pygame.display.update()
    clock.tick(30)

pygame.quit()
