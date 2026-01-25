import pygame                                    # import pygame for graphics and window handling
import sys                                       # import sys to call sys.exit() at the end
import math                                      # import math for trig and other math functions
import numpy as np                               # import NumPy for arrays and numeric ops
import random                                    # import random for stochastic choices
import time                                      # import time to measure runtime / timestamps
from Robot import Robot                           # import Robot (assumed to provide robot images/data)
from Room_data import Room_data                   # import Room_data (provides obstacles / room structure)
from ekf_mapper import EKFMapper                  # import EKFMapper helper for grid conversions & saving map

# ---------------------------- Config ----------------------------
WIDTH, HEIGHT = 700, 700                          # window width and height in pixels
WHITE, BLACK = (255, 255, 255), (0, 0, 0)        # basic color definitions (RGB)
BORDER_THICKNESS = 10                             # border thickness parameter used by Room_data
DOOR = 60                                         # door width used by Room_data
WALL_THICKNESS = 15                               # wall thickness (unused here but defined)
GRID_SIZE = 20                                    # grid cell size for mapping (pixels per cell)

pygame.init()                                     # initialize pygame modules
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)  # create resizable display surface
pygame.display.set_caption("Hospital robot simulation")  # set window title
clock = pygame.time.Clock()                       # create Clock to manage FPS
fullscreen = False                                # fullscreen flag
robot_imgs = Robot.robot_imgs                     # load robot images from Robot class
r1 = Room_data(WIDTH, BORDER_THICKNESS, HEIGHT, DOOR)  # instantiate Room_data with room parameters
obstacles = list(r1.first_floor_struct)           # copy list of structural obstacles (Rects or similar)
obj_obstacles = r1.obj_obstacles_first_floor      # objects with images/sizes/positions (like beds)

# scale robot images once
for i in range(len(robot_imgs)):                  # iterate indices of robot images
    robot_imgs[i] = pygame.transform.scale(robot_imgs[i], (40, 40))  # scale each robot image to 40x40

# Precompute scaled bed images and rects once
scaled_beds = []                                  # list to hold scaled (image, rect) tuples
for item in obj_obstacles:                        # each item is expected like (image, size, topleft)
    img = item[0].convert_alpha()                 # ensure image has an alpha channel
    img = pygame.transform.scale(img, item[1])    # scale image to the given size
    rect = img.get_rect(topleft=item[2])          # create rect positioned at the specified top-left
    scaled_beds.append((img, rect))               # save the scaled image and its rect
    obstacles.append(rect)                        # add the rect to the obstacles list for collision checks

# -------------------- helpers --------------------

def draw_robot(surface, x, y, angle):             # draw the robot on given surface at x,y with angle (degrees)
    # choose image based on angle (degrees)
    # angle expected in degrees [0,360)
    if 22.5 < angle <= 67.5:                      # angle sector 22.5..67.5 deg
        img = robot_imgs[6]                       # select image index 6
    elif 67.5 < angle <= 112.5:                   # angle sector 67.5..112.5 deg
        img = robot_imgs[1]                       # select image index 1
    elif 112.5 < angle <= 157.5:                  # angle sector 112.5..157.5 deg
        img = robot_imgs[7]                       # select image index 7
    elif 157.5 < angle <= 202.5:                  # angle sector 157.5..202.5 deg
        img = robot_imgs[2]                       # select image index 2
    elif 202.5 < angle <= 247.5:                  # angle sector 202.5..247.5 deg
        img = robot_imgs[5]                       # select image index 5
    elif 247.5 < angle <= 292.5:                  # angle sector 247.5..292.5 deg
        img = robot_imgs[0]                       # select image index 0
    elif 292.5 < angle <= 337.5:                  # angle sector 292.5..337.5 deg
        img = robot_imgs[4]                       # select image index 4
    else:                                         # remaining angles (including near 0/360)
        img = robot_imgs[3]                       # select default image index 3

    w, h = img.get_size()                         # get image width and height
    surface.blit(img, (int(x - w/2), int(y - h/2)))  # blit image centered at (x,y)

# -------------------- simulation state --------------------
robot_x = robot_y = WIDTH // 2                    # initial robot display coordinates (center of screen)
angle = 0.0                                       # initial angle in degrees

# Initialize map utils (EKFMapper handles grid conversions)
map_utils = EKFMapper(WIDTH, HEIGHT, grid_size=GRID_SIZE)  # create EKFMapper for grid/world conversions and saving

# EKF and motion parameters
robot_radius = 20                                 # robot radius approximation for collision (pixels)
robot_velocity = 30                               # robot linear speed (units per second)
mu = np.array([robot_x, robot_y, math.radians(angle)], dtype=float)  # EKF state vector [x, y, theta(rad)]
Sigma = np.eye(3) * 0.1                           # initial covariance matrix Sigma (3x3)
# Use matching names for noise (consistent with EKFMapper)
process_noise = np.diag([0.1, 0.1, 0.05])         # process noise covariance Q (3x3 diagonal)
meas_noise = np.diag([0.5, 0.5])                  # measurement noise covariance R (2x2 diagonal for range,bearing)

# landmarks and visited map
landmarks = []                                    # list to store landmark positions as numpy arrays [x,y]
# visited shape: (height, width) and index as visited[y,x]
visited = np.full((HEIGHT, WIDTH), False, dtype=bool)  # boolean array of visited pixels (False = unvisited)
light_radius = 50                                 # radius around robot considered "seen" (pixels)

# -------------------- collision & control --------------------

def will_collide(next_x, next_y):                 # returns True if robot at (next_x,next_y) collides with any obstacle
    """Check collision for robot center at (next_x, next_y).
    Uses rectangle approximation with robot_radius. Assumes obstacles contain pygame.Rect.
    """
    r = int(robot_radius)                          # integer radius for rectangle approximation
    robot_rect = pygame.Rect(int(next_x - r), int(next_y - r), r * 2, r * 2)  # rectangle approximating robot footprint

    for obs in obstacles:                          # iterate obstacles
        if isinstance(obs, pygame.Rect):           # if obstacle is a pygame.Rect
            if robot_rect.colliderect(obs):       # check rectangle-rectangle collision
                return True                        # collision detected
        else:
            # Try to build rect if possible
            try:
                if robot_rect.colliderect(pygame.Rect(obs)):  # try to coerce obs to Rect and test
                    return True                    # collision detected
            except Exception:
                pass                               # ignore if obs can't be converted to Rect
    return False                                   # no collision with any obstacle

def normalize_angle(angle):                        # normalize an angle (radians) to range [-pi, pi]
    """Normalize angle to [-pi, pi]."""
    return (angle + np.pi) % (2 * np.pi) - np.pi   # modular arithmetic to wrap angle

def ekf_step(state, Sigma, u, landmarks_list, dt, process_noise_local, meas_noise_local):
    """Combined EKF predict+update for this simple robot model.
    - state: [x,y,theta]
    - u: [forward_dist, steering_delta] where forward_dist is in units (already multiplied by speed*dt)
    - dt: time step (seconds)
    - landmarks_list: list of np.array([x,y]) measurements available this step
    - process_noise_local / meas_noise_local: covariance matrices
    Returns new_state, new_Sigma
    """                                           # docstring: describes inputs and outputs
    theta = state[2]                              # current heading theta (radians)
    # Jacobian of motion
    G = np.array([[1, 0, -u[0] * math.sin(theta)],  # motion Jacobian G (partial derivatives wrt state)
                  [0, 1,  u[0] * math.cos(theta)],
                  [0, 0, 1]], dtype=float)

    # Prediction
    state_bar = state + np.array([u[0] * math.cos(theta), u[0] * math.sin(theta), u[1]], dtype=float)  # predicted state after motion
    state_bar[2] = normalize_angle(state_bar[2])  # normalize predicted heading
    Sigma_bar = G @ Sigma @ G.T + process_noise_local  # predicted covariance: P_bar = G P G^T + Q

    # Measurement updates (for each observed landmark)
    for lm in landmarks_list:                     # iterate each observed landmark position
        delta = lm - state_bar[:2]                # vector from predicted robot pos to landmark (dx,dy)
        q = max(1e-8, float(np.dot(delta, delta)))  # squared distance with small epsilon guard
        r = math.sqrt(q)                          # range (distance) to landmark
        z = np.array([r, math.atan2(delta[1], delta[0]) - state_bar[2]], dtype=float)  # expected measurement (range, bearing)

        H = np.array([[-delta[0]/r, -delta[1]/r, 0.0],  # measurement Jacobian H (2x3)
                      [ delta[1]/q, -delta[0]/q, -1.0]], dtype=float)

        S = H @ Sigma_bar @ H.T + meas_noise_local  # innovation covariance S = H P_bar H^T + R
        # simulate a noisy measurement
        noise = np.random.randn(2) * np.sqrt([meas_noise_local[0,0], meas_noise_local[1,1]])  # sample measurement noise
        z_meas = z + noise                        # simulated noisy measurement z_meas
        y = z_meas - z                            # innovation (measurement residual)
        y[1] = normalize_angle(y[1])              # normalize angular component of residual

        # Kalman gain
        try:
            K = Sigma_bar @ H.T @ np.linalg.inv(S)  # compute Kalman gain K = P_bar H^T S^-1
        except np.linalg.LinAlgError:
            K = Sigma_bar @ H.T @ np.linalg.pinv(S)  # fallback to pseudo-inverse if S is singular

        state_bar = state_bar + K @ y              # correct predicted state with Kalman gain * innovation
        state_bar[2] = normalize_angle(state_bar[2])  # normalize heading after correction
        Sigma_bar = (np.eye(3) - K @ H) @ Sigma_bar  # update covariance (simplified form)

    return state_bar, Sigma_bar                     # return updated state and covariance

def add_new_landmark(state, landmarks_list, obstacles_list, min_distance=20):
    """Add a random nearby landmark if it is not too close to existing ones and not inside obstacle."""
    new_landmark = state[:2] + np.random.randn(2) * 20.0  # propose a new landmark near current robot position
    for lm in landmarks_list:                         # check distance to existing landmarks
        if np.linalg.norm(new_landmark - lm) < min_distance:
            return landmarks_list                      # too close to existing landmark -> do nothing
    for obs in obstacles_list:                         # ensure proposed point is not inside an obstacle
        try:
            # ensure we pass ints to collidepoint
            if obs.collidepoint(int(new_landmark[0]), int(new_landmark[1])):  # if point inside obstacle rect
                return landmarks_list                  # inside obstacle -> do not add
        except Exception:
            pass                                       # ignore obstacles that don't support collidepoint
    landmarks_list.append(new_landmark)                # append new landmark to list
    return landmarks_list                               # return updated landmarks list

def avoid_collision(state, u, obstacles_list):
    """Modify commanded control u=[forward,turn] to avoid collisions.
    Returns adjusted u.
    """
    theta = state[2]                                    # robot heading
    potential_x = state[0] + u[0] * math.cos(theta)     # predicted x after executing forward u[0]
    potential_y = state[1] + u[0] * math.sin(theta)     # predicted y after executing forward u[0]

    future_rect = pygame.Rect(int(potential_x - robot_radius), int(potential_y - robot_radius), robot_radius * 2, robot_radius * 2)  # future footprint rect

    # check collisions with expanded obstacles; if near boundary also react
    for obs in obstacles_list:                          # iterate obstacles
        if isinstance(obs, pygame.Rect):                # if the obstacle is a Rect
            expanded = obs.inflate(30, 30)              # inflate obstacle rect by safety margin
            if future_rect.colliderect(expanded):      # if future robot rect intersects the inflated obstacle
                return [u[0] * 0.1, 0.3]                # reduce forward speed and return small turning command
    if not (15 <= potential_x <= WIDTH - 15 and 15 <= potential_y <= HEIGHT - 15):  # if predicted position near window border
        return [u[0] * 0.1, 0.3]                        # slow down and turn slightly to avoid border
    return u                                           # otherwise return the original control command

# -------------------- timing --------------------
start_time = time.time()                               # record start time for runtime measurements

# ---- Mapping helpers (local duplicates can be removed in favor of map_utils) ----

def world_to_grid_local(x, y):
    return map_utils.world_to_grid(x, y)               # wrapper: convert world coords to grid indices via EKFMapper

def grid_to_world_local(row, col):
    return map_utils.grid_to_world(row, col)           # wrapper: convert grid indices to world coords via EKFMapper

# Path finding helper (lightweight heuristic used previously)
def get_path(x, y, dx, dy, step_angle=30, step_distance=40):
    base = math.atan2(dy, dx)                          # base heading angle toward target delta (dx,dy)
    offsets = []                                       # list to hold angular offsets (degrees)
    k = 0
    while k * step_angle <= 180:                       # generate offsets symmetric around base up to 180 degrees
        if k == 0:
            offsets.append(0)                          # first try straight toward base
        else:
            offsets.append(k * step_angle)             # try +k*step_angle
            offsets.append(-k * step_angle)            # and -k*step_angle
        k += 1

    for offset_deg in offsets:                          # try spatial candidates in offset order
        angle = base + math.radians(offset_deg)         # candidate angle in radians
        candidate_x = x + math.cos(angle) * step_distance  # candidate x at step_distance along candidate angle
        candidate_y = y + math.sin(angle) * step_distance  # candidate y at step_distance
        if not will_collide(candidate_x, candidate_y):  # if candidate position is collision-free
            return candidate_x, candidate_y             # return it as a valid path point

    for _ in range(20):                                 # fallback: try several random nearby points
        rand_angle = random.uniform(0, 2 * math.pi)     # random heading
        candidate_x = x + math.cos(rand_angle) * (step_distance // 2)  # shorter random step
        candidate_y = y + math.sin(rand_angle) * (step_distance // 2)
        if not will_collide(candidate_x, candidate_y):  # if random candidate is free
            return candidate_x, candidate_y             # return it

    return x + 1.0, y                                   # final fallback: return a small step forward

# -------------------- Main loop --------------------
running = True                                       # main loop control flag
time_List=[]                                         # list to collect runtime stamps for printing
percentage_List=[]                                   # list to collect exploration percentages for printing
while running:
    dt_ms = clock.tick(30)                           # cap framerate to 30 FPS; returns ms since last tick
    dt = max(1e-3, dt_ms / 1000.0)                   # convert ms to seconds, with a small lower bound
    total_time = time.time() - start_time            # compute elapsed runtime
    if int(total_time) % 10 == 0:                    # every ~10 seconds (when integer seconds divisible by 10)
        explored_pixels = np.sum(visited)            # number of visited pixels (True count)
        total_pixels = WIDTH * HEIGHT                # total pixels in the map
        exploration_ratio = (explored_pixels / total_pixels) * 100  # exploration percentage
        print(f"\n⏱️ run time: {total_time:.2f} second")  # print runtime
        print(f"🗺️ discovered: {exploration_ratio:.2f}%")  # print discovered percentage
        time_List.append(f"{total_time} s")          # append runtime to list
        percentage_List.append(f"{exploration_ratio}%")  # append percentage to list

    for event in pygame.event.get():                 # process pygame events
        if event.type == pygame.QUIT:                 # window close event
            print(time_List)                         # print collected runtimes
            print(percentage_List)                    # print collected percentages
            map_utils.save_map(visited, out_dir='.') # save map and visited overlay before exit
            running = False                          # break main loop
           
        elif event.type == pygame.KEYDOWN:            # key press event
            if event.key in (pygame.K_F11, pygame.K_m):  # toggle fullscreen on F11 or 'm'
                fullscreen = not fullscreen
                if fullscreen:
                    info = pygame.display.Info()
                    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)  # set fullscreen mode
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)  # revert to resizable window
            elif event.key == pygame.K_s:             # save map on 's' key
                map_utils.save_map(visited, out_dir='.')
                print("Map saved")

    # draw background & static objects
    screen.fill(WHITE)                                # clear screen with white background
    pygame.draw.circle(screen, (0, 255, 0), (356, 640), 20)  # draw a static green circle (reference or marker)

    # Draw static obstacles and update map grid
    for obs in obstacles:                             # draw each obstacle and mark grid cells as obstacles
        if isinstance(obs, pygame.Rect):
            pygame.draw.rect(screen, BLACK, obs)     # draw rectangle obstacle in black
            rect = obs
            # mark obstacle area in grid (iterate by grid cells)
            for x in range(rect.left, rect.right, GRID_SIZE):  # iterate cell x positions inside rect
                for y in range(rect.top, rect.bottom, GRID_SIZE):  # iterate cell y positions inside rect
                    row, col = world_to_grid_local(x, y)  # convert world point to grid cell indices
                    if map_utils.grid[row, col] != 1:    # if cell isn't already marked as obstacle
                        map_utils.grid[row, col] = 1    # set grid cell to obstacle
                        map_utils.update_map(x, y, True)  # call map_utils to record obstacle landmark if needed

    # draw precomputed bed images
    for img, rect in scaled_beds:                     # blit each precomputed image (beds etc.) to the screen
        screen.blit(img, rect)

    # decide control command: forward velocity scaled by dt, small rotation
    forward = robot_velocity * dt                     # compute forward distance for this timestep
    u_cmd = [forward, 0.0]                            # control command: [forward_distance, steering_delta]

    # collision avoidance may modify u_cmd
    u_cmd = avoid_collision(mu, u_cmd, obstacles)     # adjust command to avoid imminent collisions

    # perform EKF step with current landmarks
    mu, Sigma = ekf_step(mu, Sigma, u_cmd, landmarks, dt, process_noise, meas_noise)  # run EKF predict+update

    # mark visited pixels in visited[y,x]
    rx, ry = int(mu[0]), int(mu[1])                   # robot integer pixel coordinates from EKF state
    y_min = max(0, ry - light_radius)                  # clamp top of light region
    y_max = min(HEIGHT, ry + light_radius)             # clamp bottom of light region
    x_min = max(0, rx - light_radius)                  # clamp left of light region
    x_max = min(WIDTH, rx + light_radius)              # clamp right of light region

    for yy in range(y_min, y_max):                      # iterate over rows in the light region
        # vectorized inner loop would be faster, but keep readable
        for xx in range(x_min, x_max):                  # iterate over columns in the light region
            if (xx - rx) ** 2 + (yy - ry) ** 2 <= light_radius ** 2:  # if pixel inside circular light
                visited[yy, xx] = True                  # mark pixel as visited

    # draw visited overlay efficiently in steps
    visited_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # create transparent surface for overlay
    visited_surface.fill((0, 0, 0, 0))             # fill fully transparent
    step = 4                                       # subsampling step for drawing visited overlay
    for i in range(0, WIDTH, step):                # iterate over x in increments of step
        for j in range(0, HEIGHT, step):           # iterate over y in increments of step
            if visited[j, i]:                      # if this subsampled pixel was visited
                visited_surface.fill((255, 255, 255, 30), rect=pygame.Rect(i, j, step, step))  # draw faint white block
    screen.blit(visited_surface, (0, 0))           # blit visited overlay onto screen

    # occasionally add a random new landmark
    if random.random() < 0.01:                     # with small probability, attempt to add a new landmark
        landmarks = add_new_landmark(mu, landmarks, obstacles)  # add landmark if valid

    # update robot display coords and angle
    robot_x, robot_y = float(mu[0]), float(mu[1])  # set display coords from EKF state
    angle = (math.degrees(mu[2]) + 360) % 360      # convert theta to degrees in [0,360)

    # draw landmarks
    for lm in landmarks:                            # draw each landmark as a red circle
        pygame.draw.circle(screen, (255, 0, 0), lm.astype(int), 5)

    # draw robot
    draw_robot(screen, int(robot_x), int(robot_y), angle)  # draw robot at computed position and angle

    pygame.display.update()                         # update the display to show this frame

pygame.quit()                                       # quit pygame when loop ends
sys.exit()                                          # exit the Python process
