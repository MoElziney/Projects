import numpy as np                                # import NumPy for arrays and numerical ops, aliased as np
import math                                      # import math module for trig and sqrt, pi, etc.
import pygame                                    # import pygame for drawing and saving images
import os                                        # import os for filesystem operations (mkdir, path joins)


class EKFMapper:                                  # define class EKFMapper that encapsulates mapping + EKF logic
    """Improved EKF-based mapper utility.
    Changes / fixes applied:
    - Clear naming for process vs measurement noise (process_noise, meas_noise).
    - Fixed save_map visited handling (visited expected shape: (height, width) and indexed as [y,x]).
    - More robust landmark saving (JSON + Python list) and safer file IO.
    - update_ekf uses numerically-stable Kalman gain expression and clearer innovation handling.
    - Helpful docstrings and consistent grid coordinate conversions: grid[row, col] with row = y//grid_size.
    - Defensive checks for small ranges.
    """                                           # class-level docstring describing purpose and improvements

    def __init__(self, width, height, grid_size=20):  # constructor: initialize sizes, grid, EKF state, noise, landmarks
        # Map parameters
        self.grid_size = int(grid_size)           # store grid cell size as integer
        self.width = int(width)                   # store world width as integer
        self.height = int(height)                 # store world height as integer
        self.grid_w = max(1, self.width // self.grid_size)  # compute number of grid columns, at least 1
        self.grid_h = max(1, self.height // self.grid_size) # compute number of grid rows, at least 1
        # grid indexed as grid[row, col] where row = y//grid_size
        self.grid = np.full((self.grid_h, self.grid_w), -1, dtype=int)  # occupancy grid initialized to -1 (unknown)

        # EKF state and covariance: state = [x, y, theta]
        self.state = np.zeros(3, dtype=float)     # initialize EKF state vector [x, y, theta] to zeros
        self.covariance = np.eye(3, dtype=float) * 0.1  # initial covariance (small uncertainty)

        # Use descriptive names for noise covariances
        # process_noise: affects state propagation
        # meas_noise: affects measurement (range,bearing)
        self.process_noise = np.diag([0.1, 0.1, 0.05])  # process noise covariance Q (3x3 diagonal)
        self.meas_noise = np.diag([0.5, 0.5])          # measurement noise covariance R (2x2 diagonal for range,bearing)

        # landmarks: mapping (row,col) -> {x,y,type}
        # we store landmark positions at cell centers to keep consistency
        self.landmarks = {}                        # dictionary to store detected landmarks keyed by grid cell (row,col)

    # -------------------- coordinate helpers --------------------
    def world_to_grid(self, x, y):                 # convert world coordinates (x,y) to grid indices (row,col)
        """Convert world (x,y) to grid indices (row, col) and clamp inside grid."""  # docstring
        col = int(x) // self.grid_size            # column index from x coordinate
        row = int(y) // self.grid_size            # row index from y coordinate
        col = min(max(0, col), self.grid_w - 1)  # clamp column to valid range [0, grid_w-1]
        row = min(max(0, row), self.grid_h - 1)  # clamp row to valid range [0, grid_h-1]
        return row, col                          # return tuple (row, col)

    def grid_to_world(self, row, col):            # convert grid indices (row,col) to world coordinates (cell center)
        """Convert grid indices (row,col) to world coordinates (cell center)."""  # docstring
        cx = (col * self.grid_size) + (self.grid_size // 2)  # center x of the cell
        cy = (row * self.grid_size) + (self.grid_size // 2)  # center y of the cell
        return float(cx), float(cy)               # return center coordinates as floats

    # -------------------- motion / EKF prediction --------------------
    def predict(self, velocity, steering_angle, dt=1.0):  # EKF prediction step using a simple motion model
        """EKF prediction step for a simple differential motion model.

        Args:
            velocity: forward displacement (units per dt)
            steering_angle: change in heading (radians per dt)
            dt: time step multiplier (default 1.0)
        Returns:
            copy of predicted state
        """                                       # docstring describing arguments and return
        th = float(self.state[2])                 # current heading theta from state
        # state update
        dx = velocity * math.cos(th) * dt        # compute x displacement using cos(theta)
        dy = velocity * math.sin(th) * dt        # compute y displacement using sin(theta)
        dth = steering_angle * dt                # compute heading change

        self.state += np.array([dx, dy, dth], dtype=float)  # apply motion increment to state
        # normalize heading
        self.state[2] = (self.state[2] + math.pi) % (2 * math.pi) - math.pi  # normalize theta to (-pi, pi]

        # Jacobian of motion wrt state (approx for small dth)
        G = np.array([                             # construct motion Jacobian matrix G (3x3)
            [1.0, 0.0, -velocity * math.sin(th) * dt],  # d(x')/d(x,y,theta)
            [0.0, 1.0,  velocity * math.cos(th) * dt],  # d(y')/d(x,y,theta)
            [0.0, 0.0, 1.0]                             # d(theta')/d(theta)
        ], dtype=float)

        # covariance propagation
        self.covariance = G @ self.covariance @ G.T + self.process_noise  # P = G P G^T + Q
        return self.state.copy()                  # return a copy of the predicted state

    # -------------------- map updates --------------------
    def update_map(self, x, y, is_obstacle):       # update occupancy grid with observation at world (x,y)
        """Mark a cell as obstacle or free from a measurement at (x,y).

        (x,y) are world coordinates. We update the grid and optionally add a landmark
        when an obstacle is observed.
        """                                       # docstring
        row, col = self.world_to_grid(x, y)      # convert world point to grid indices
        self.grid[row, col] = 1 if is_obstacle else 0  # set grid cell: 1 for obstacle, 0 for free
        # create landmark at cell center for obstacles (if not exists)
        if is_obstacle and (row, col) not in self.landmarks:  # if it's an obstacle and not yet stored
            cx, cy = self.grid_to_world(row, col)  # get world center of that grid cell
            self.landmarks[(row, col)] = {"x": float(cx), "y": float(cy), "type": "obstacle"}  # store landmark dict

    def get_unexplored_direction(self, current_x, current_y, max_radius_cells=6):  # find heading to nearest unknown cell
        """Return heading (radians) to nearest unexplored grid cell, or None if none.

        Searches outward in increasing Chebyshev radius (square rings) up to
        max_radius_cells.
        """                                       # docstring
        row, col = self.world_to_grid(current_x, current_y)  # get current robot grid cell

        for r in range(1, max_radius_cells + 1):  # expand rings from 1 to max_radius_cells
            # iterate square ring at radius r (all edges)
            for dr in range(-r, r + 1):         # iterate rows along vertical edges
                for dc in (-r, r):              # check left and right columns of the ring
                    nr, nc = row + dr, col + dc  # candidate cell indices
                    if 0 <= nr < self.grid_h and 0 <= nc < self.grid_w and self.grid[nr, nc] == -1:  # if in bounds and unknown
                        wx, wy = self.grid_to_world(nr, nc)  # convert that cell to world coords
                        dy = wy - current_y
                        dx = wx - current_x
                        return math.atan2(dy, dx)  # return heading angle toward the unknown cell
            for dc in range(-r + 1, r):       # iterate columns along horizontal edges (excluding corners already checked)
                for dr in (-r, r):            # check top and bottom rows of the ring
                    nr, nc = row + dr, col + dc  # candidate cell indices
                    if 0 <= nr < self.grid_h and 0 <= nc < self.grid_w and self.grid[nr, nc] == -1:  # if unknown and valid
                        wx, wy = self.grid_to_world(nr, nc)  # get world center
                        dy = wy - current_y
                        dx = wx - current_x
                        return math.atan2(dy, dx)  # return heading for exploration
        return None                                # return None if no unexplored cell found within radius

    # -------------------- persistence / visualization --------------------
    def save_map(self, visited=None, out_dir='.'):  # save grid, images, and landmarks to out_dir; optionally save visited overlay
        """Save the internal grid map and landmarks.

        Produces:
            - <out_dir>/robot_map.npy (numpy grid)
            - <out_dir>/robot_map.png (visualization, one pixel per cell scaled up by grid size)
            - <out_dir>/robot_map_landmarks.json and _landmarks.py
            - If `visited` supplied (shape: height,width boolean), produces
              robot_explored.npy and robot_explored.png (visited overlay, obstacles in red).

        Notes:
            visited is expected with shape (height, width) and is indexed visited[y,x].
        """                                       # docstring describing outputs and visited shape expectation
        try:                                       # start try block to avoid crashing on save errors
            os.makedirs(out_dir, exist_ok=True)   # ensure output directory exists

            # save raw grid
            map_npy = os.path.join(out_dir, 'robot_map.npy')  # path for numpy file
            np.save(map_npy, self.grid)           # save grid array to .npy file

            # create a small surface (one pixel per grid cell) then scale up
            surf = pygame.Surface((self.grid_w, self.grid_h))  # create a tiny surface where each pixel = one grid cell
            colors = {
                -1: (160, 160, 160),  # unknown: gray
                0:  (255, 255, 255),   # free: white
                1:  (0, 0, 0),         # obstacle: black
            }                                     # define colors for cell values
            for r in range(self.grid_h):         # iterate over grid rows
                for c in range(self.grid_w):     # iterate over grid columns
                    val = int(self.grid[r, c])  # read cell value
                    surf.fill(colors.get(val, (255, 255, 255)), (c, r, 1, 1))  # draw 1x1 pixel at (c,r) with mapped color

            scaled = pygame.transform.scale(surf, (self.grid_w * self.grid_size, self.grid_h * self.grid_size))  # upscale image
            map_png = os.path.join(out_dir, 'robot_map.png')  # path for png image
            pygame.image.save(scaled, map_png)    # save the upscaled map image as PNG

            # Save landmarks as JSON (human/tool friendly)
            try:
                import json                    # import json module locally for saving
                data = list(self.landmarks.values())  # get list of landmark dicts
                with open(os.path.join(out_dir, 'robot_map_landmarks.json'), 'w') as f:  # open file for writing
                    json.dump(data, f, indent=2)  # write JSON with indentation for readability
            except Exception:
                # non-fatal
                pass                             # ignore JSON save errors and continue

            # Also save landmarks as Python file with a plain list
            try:
                py_path = os.path.join(out_dir, 'robot_map_landmarks.py')  # path for python landmarks file
                with open(py_path, 'w') as f:    # open python file for writing
                    f.write('# Auto-generated landmarks: LANDMARKS = [(x,y,type), ...]\n')  # header comment
                    f.write('LANDMARKS = [\n')  # start list
                    for v in self.landmarks.values():  # iterate stored landmark dicts
                        f.write(f"    ({float(v['x'])!r}, {float(v['y'])!r}, {v.get('type','')!r}),\n")  # write tuple line
                    f.write(']\n')              # close list
            except Exception:
                pass                             # ignore errors writing python landmarks file

            # If a visited pixel map is provided, save it with obstacle information
            if visited is not None:               # if visited overlay was passed
                try:
                    # expect visited shape = (height, width) and bool / 0-1
                    visited_arr = np.asarray(visited, dtype=bool)  # convert visited to boolean numpy array
                    if visited_arr.ndim != 2:    # check that visited is 2D
                        raise ValueError('visited must be 2D array (height, width)')  # raise error if wrong shape

                    explored_npy = os.path.join(out_dir, 'robot_explored.npy')  # path for visited npy
                    np.save(explored_npy, visited_arr)  # save visited array

                    h, w = visited_arr.shape     # height and width of visited pixels
                    surf2 = pygame.Surface((w, h))  # surface one pixel per visited pixel
                    surf2.fill((128, 128, 128))  # unexplored gray background

                    for y in range(h):           # iterate over visited pixel rows
                        for x in range(w):       # iterate over visited pixel columns
                            if visited_arr[y, x]:  # if this pixel was visited
                                grid_row = y // self.grid_size  # map pixel y to grid row
                                grid_col = x // self.grid_size  # map pixel x to grid col
                                if 0 <= grid_row < self.grid_h and 0 <= grid_col < self.grid_w:  # ensure grid indices valid
                                    if self.grid[grid_row, grid_col] == 1:  # if that grid cell is an obstacle
                                        surf2.fill((255, 0, 0), (x, y, 1, 1))  # mark visited obstacle red
                                    else:
                                        surf2.fill((255, 255, 255), (x, y, 1, 1))  # mark visited free space white

                    explored_png = os.path.join(out_dir, 'robot_explored.png')  # path for explored image
                    # upscale for visibility
                    pygame.image.save(pygame.transform.scale(surf2, (w * 2, h * 2)), explored_png)  # save scaled visited image
                except Exception:
                    # don't break the overall save if visited fails
                    pass                             # ignore visited saving errors

            print(f"Map saved to {map_npy} and {map_png} (landmarks in {out_dir})")  # print success message
        except Exception as e:                    # outer exception catcher for save_map
            print('Failed to save map:', e)       # print failure message with exception info

    # -------------------- EKF measurement update --------------------
    def update_ekf(self, measurement, landmark_pos):  # EKF update step using a measurement to a known landmark
        """EKF state update given a measurement (range,bearing) to a known landmark_pos (x,y).

        Args:
            measurement: np.array([range, bearing]) where bearing is in radians (robot frame)
            landmark_pos: (x_land, y_land) in world coords
        Returns:
            copy of updated state
        """                                       # docstring describing args and return
        x, y, th = float(self.state[0]), float(self.state[1]), float(self.state[2])  # unpack state into x,y,theta
        dx = float(landmark_pos[0]) - x         # delta x from robot to landmark
        dy = float(landmark_pos[1]) - y         # delta y from robot to landmark
        q = max(1e-8, dx * dx + dy * dy)        # squared distance q with guard against zero
        r = math.sqrt(q)                        # range = sqrt(q)

        # predicted measurement (range, bearing relative to robot heading)
        z_hat = np.array([r, math.atan2(dy, dx) - th], dtype=float)  # predicted [range, bearing] to landmark
        # Normalize bearing
        z_hat[1] = (z_hat[1] + math.pi) % (2 * math.pi) - math.pi  # wrap predicted bearing to (-pi, pi]

        # measurement Jacobian H (2x3)
        H = np.array([                            # construct measurement Jacobian matrix H
            [-dx / r, -dy / r, 0.0],              # partials of range wrt [x,y,theta]
            [ dy / q, -dx / q, -1.0]              # partials of bearing wrt [x,y,theta] (note -1 for d(bearing)/d(theta))
        ], dtype=float)

        # innovation: measurement minus prediction, normalized angle
        z = np.asarray(measurement, dtype=float)  # convert measurement to numpy array
        y_res = z - z_hat                         # innovation (residual) = z - z_hat
        y_res[1] = (y_res[1] + math.pi) % (2 * math.pi) - math.pi  # normalize bearing residual

        S = H @ self.covariance @ H.T + self.meas_noise  # innovation covariance S = H P H^T + R
        # Kalman gain: use stable solve where possible
        try:
            K = self.covariance @ H.T @ np.linalg.inv(S)  # compute Kalman gain K = P H^T S^-1
        except np.linalg.LinAlgError:
            # fallback to pseudo-inverse
            K = self.covariance @ H.T @ np.linalg.pinv(S)  # use pseudo-inverse of S if inversion fails

        # state update
        self.state = self.state + K @ y_res          # update state: x = x + K * innovation
        self.state[2] = (self.state[2] + math.pi) % (2 * math.pi) - math.pi  # normalize theta after update

        I = np.eye(3)                                # identity matrix for covariance update
        # Joseph form for numerical stability
        self.covariance = (I - K @ H) @ self.covariance @ (I - K @ H).T + K @ self.meas_noise @ K.T  # stable covariance update

        return self.state.copy()                     # return a copy of the updated state
