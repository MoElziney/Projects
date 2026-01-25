# env_no_a_star.py
import pygame
import numpy as np
import random
import time
from collections import deque

# Attempt to import user modules (Robot, PriorityQueue, dynamic obstacles).
try:
    from Robot import Robot
except Exception as e:
    Robot = None
    print("Warning: Robot.py import failed:", e)

try:
    from PriorityQueue import PriorityQueue
except Exception as e:
    # simple fallback
    import heapq
    class PriorityQueue:
        def __init__(self):
            self.elements = []
        def push(self, item, priority):
            heapq.heappush(self.elements, (priority, item))
        def pop_lowest_f(self):
            return heapq.heappop(self.elements)[1]
        def empty(self):
            return len(self.elements) == 0
        def push_or_update(self, item, priority):
            heapq.heappush(self.elements, (priority, item))
    print("Warning: PriorityQueue.py import failed, using fallback.")

try:
    import dynamic_obstacle as dyn_mod
    HAS_DYNAMIC = True
except Exception as e:
    HAS_DYNAMIC = False
    print("Warning: dynamic_obstacle import failed:", e)

# Grid / cell utilities
def grid_coords_from_px(px_x, px_y, cell_size):
    return int(px_x // cell_size), int(px_y // cell_size)

def px_from_grid(gx, gy, cell_size):
    return gx * cell_size, gy * cell_size

class SimpleEnv:
    
    def __init__(self, width=800, height=600, scaled_robot_size=(32,32), render_mode=True, seed=None,
                 # reward shaping params (you can tune via trainer CLI env_params)
                 goal_reward=50.0, completion_bonus=500.0, step_penalty=-0.002, shaping_alpha=0.4,
                 dynamic_moving_initial=True, return_to_start=True):
        self.width = width
        self.height = height
        self.cell_size = scaled_robot_size[0]  # assume square cells
        self.grid_w = width // self.cell_size
        self.grid_h = height // self.cell_size
        self.render_mode = render_mode
        self.screen = None
        self.clock = None
        self.font = None

        self.action_space_n = 8
        # actions: (dx, dy) in grid coords
        self.actions = [
            (0, -1),  # up
            (0, 1),   # down
            (-1, 0),  # left
            (1, 0),   # right
            (1, -1),  # up-right
            (-1, -1), # up-left
            (1, 1),   # down-right
            (-1, 1),  # down-left
        ]

        # seed
        self._rng = random.Random(seed)

        # reward / behavior params
        self.GOAL_REWARD = goal_reward
        self.COMPLETION_BONUS = completion_bonus
        self.STEP_PENALTY = step_penalty
        self.SHAPING_ALPHA = shaping_alpha
        self.RETURN_TO_START = return_to_start

        # map arrays
        # 0 = free, 1 = wall, 2 = bed/room obstacle, 3 = door(open) (treated as free but marked), 4 = dynamic obstacle (doctors)
        self.grid = np.zeros((self.grid_h, self.grid_w), dtype=np.uint8)

        # create layout: walls + 6 isolation rooms with doors + beds
        self._create_layout()

        # robot start (grid coords)
        self.start_pos = (2, self.grid_h // 2)
        self.robot_pos = self.start_pos

        # build goals (one goal per bed: adjacent cell)
        self.goals = self._compute_bed_goals()
        self.goal_queue = deque(self.goals)  # simple FIFO
        self.current_goal = None
        if self.goal_queue:
            self.current_goal = self.goal_queue[0]

        # dynamic obstacles (doctors)
        self.dynamic_obstacles = []
        self.dynamic_moving = dynamic_moving_initial
        self._init_dynamic_obstacles()

        # episode bookkeeping
        self.max_steps = 1000
        self.step_count = 0
        self.visited_goals = set()
        self.returning_to_start = False

        # new: pending goal marker to prevent repeated collection while waiting to return
        self._pending_goal = None

        # pygame init (for rendering)
        if self.render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Hospital Grid Env")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 14)

        # observation size: grid_flat + 4 coords
        self.obs_dim = self.grid_w * self.grid_h + 4

        # store previous robot pos for shaping and fallbacks
        self._prev_robot_pos = self.robot_pos

    # ---------------- layout ----------------
    def _create_layout(self):
        # outer walls
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1
        self.grid[0, :] = 1
        self.grid[-1, :] = 1

        # create 6 small rooms on the right side stacked vertically (like isolation rooms)
        room_w = 6  # in cells
        room_h = max(4, self.grid_h // 6)  # make sure rooms fit
        right_start = self.grid_w - room_w - 1

        bed_positions = []
        door_cells = []

        y = 1
        for i in range(6):
            top = y
            bottom = min(self.grid_h - 2, y + room_h - 1)
            # draw room walls
            for gx in range(right_start, right_start + room_w):
                self.grid[top, gx] = 1
                self.grid[bottom, gx] = 1
            for gy in range(top, bottom + 1):
                self.grid[gy, right_start] = 1
                self.grid[gy, right_start + room_w - 1] = 1

            # place bed inside (as obstacle)
            bed_x = right_start + 2
            bed_y = top + (bottom - top) // 2
            self.grid[bed_y, bed_x] = 2
            bed_positions.append((bed_x, bed_y))

            # door: leave an opening in left wall of room (door cell)
            door_x = right_start
            door_y = bed_y
            # mark door as 3 (open) but not obstacle
            self.grid[door_y, door_x] = 3
            door_cells.append((door_x, door_y))

            # next room start
            y = bottom + 1

        # also scatter some additional beds in left area (optional) — keep some obstacles
        for gx in range(3, 8):
            for gy in range(2, 4):
                if self.grid[gy, gx] == 0:
                    self.grid[gy, gx] = 2

        self._bed_positions = bed_positions
        self._door_cells = door_cells

    def _compute_bed_goals(self):
        # For each bed, choose an adjacent free cell as the goal (prefers left side of bed)
        goals = []
        for (bx, by) in self._bed_positions:
            candidates = [
                (bx - 1, by), (bx + 1, by),
                (bx, by - 1), (bx, by + 1)
            ]
            for cand in candidates:
                x, y = cand
                if 0 <= x < self.grid_w and 0 <= y < self.grid_h and self.grid[y, x] == 0:
                    goals.append(cand)
                    break
        return goals

    def _init_dynamic_obstacles(self):
        """
        Initialize dynamic obstacles for RANDOM walk behavior.
        """
        self.dynamic_obstacles = []
        # control master switch (True => obstacles move)
        self.dynamic_moving = self.dynamic_moving if hasattr(self, "dynamic_moving") else True

        base_speed = 1  # move every step; increase to >1 to slow them down
        # For each bed, build a small set of candidate cells near the bed (left corridor)
        for i, (bx, by) in enumerate(self._bed_positions):
            candidates = []
            # collect cells in a rectangular neighborhood left of the bed (width 4)
            for gx in range(max(1, bx - 4), min(self.grid_w - 1, bx + 1)):
                for gy in range(max(1, by - 1), min(self.grid_h - 1, by + 2)):
                    # allow cells that are walkable (grid == 0) or door (3)
                    if self.grid[gy, gx] == 0 or self.grid[gy, gx] == 3:
                        candidates.append((gx, gy))
            # if no candidates found (rare), fallback to a single adjacent free cell
            if not candidates:
                cand = (max(1, bx - 2), by)
                candidates = [cand]
            # seed starting pos (choose middle candidate if possible)
            start_pos = candidates[len(candidates)//2]
            obj = {
                "pos": start_pos,
                "candidates": candidates,
                "move_every": base_speed,
                "last_moved_step": 0,
                "mode": "random",
                "type": "doctor"
            }
            self.dynamic_obstacles.append(obj)

    def set_dynamic_moving(self, active: bool):
        """Enable or disable movement of dynamic obstacles (for curriculum training)."""
        self.dynamic_moving = active

    # ---------------- environment API ----------------
    def seed(self, s=None):
        self._rng.seed(s)

    def reset(self):
        # reset robot location and episode bookkeeping
        self.robot_pos = self.start_pos
        self._prev_robot_pos = self.robot_pos
        self.step_count = 0
        self.visited_goals = set()
        self.goal_queue = deque(self.goals)
        self.current_goal = self.goal_queue[0] if self.goal_queue else None
        self.returning_to_start = False

        # reset pending marker so visiting works per-episode
        self._pending_goal = None

        # optionally randomize dynamic obstacles starting positions
        for d in self.dynamic_obstacles:
            if "candidates" in d and d["candidates"]:
                d["pos"] = d["candidates"][len(d["candidates"])//2]
            else:
                d["pos"] = (1,1)
            d["last_moved_step"] = 0

        return self._get_obs()

    def _get_obs(self):
        # flat grid with: 0 free, 1 wall/obstacle (we collapse bed->1), 2 doctor (dynamic)
        grid_flat = np.array(self.grid.flatten(), dtype=np.float32)
        # mark dynamic obstacles on a copy
        dynamic_map = np.zeros_like(grid_flat)
        for d in self.dynamic_obstacles:
            gx, gy = d["pos"]
            idx = gy * self.grid_w + gx
            if 0 <= idx < dynamic_map.size:
                dynamic_map[idx] = 1.0
        # overlay dynamic: we'll add as +2 to indicate dynamic presence
        # (we'll add dynamic_map * 2 to the grid_flat to keep numeric encoding)
        grid_obs = grid_flat.copy()
        grid_obs[dynamic_map.astype(bool)] = 4.0

        rx, ry = self.robot_pos
        
        # --- FIXED OBSERVATION LOGIC ---
        if self.current_goal:
            gx, gy = self.current_goal
        elif self.returning_to_start:
            # If returning, tell the robot the goal is the Start Position
            gx, gy = self.start_pos 
        else:
            gx, gy = (-1, -1)

        obs = np.concatenate([
            grid_obs.astype(np.float32),
            np.array([rx, ry, gx, gy], dtype=np.float32)
        ])
        return obs

    def step(self, action):
        info = {}
        done = False
        reward = self.STEP_PENALTY  # small step penalty to encourage speed
        self.step_count += 1

        # store prev pos for shaping
        prev_x, prev_y = self.robot_pos
        self._prev_robot_pos = (prev_x, prev_y)

        # apply action
        if action < 0 or action >= self.action_space_n:
            action = 0
        dx, dy = self.actions[action]
        new_x = self.robot_pos[0] + dx
        new_y = self.robot_pos[1] + dy

        # bounds check
        if not (0 <= new_x < self.grid_w and 0 <= new_y < self.grid_h):
            # hitting wall
            new_x, new_y = self.robot_pos

        # check collision with static obstacles (treat 1 and 2 as blocking; 3 door is passable)
        cell_value = self.grid[new_y, new_x]
        if cell_value == 1 or cell_value == 2:
            # blocked: stay in place and penalize a bit
            reward += -0.5
            new_x, new_y = self.robot_pos
        else:
            # move
            self.robot_pos = (new_x, new_y)

        # update dynamic obstacles (simple random-walk)
        self._update_dynamic_obstacles()

        # check collision with dynamic obstacle
        for d in self.dynamic_obstacles:
            if d["pos"] == self.robot_pos:
                # penalize and push back one cell (avoid teleport reset)
                reward += -1.0
                self.robot_pos = (prev_x, prev_y)
                break

        # ---------------- goal logic (one-time reward + pending-return) ----------------
        # If agent has an active goal and stands on it
        if self.current_goal and self._is_at_goal(self.robot_pos, self.current_goal):
            # only give reward once per visit: use _pending_goal to block repeats
            if self._pending_goal is None:
                # first time hitting this goal in this visit
                if self.current_goal not in self.visited_goals:
                    reward += self.GOAL_REWARD
                else:
                    # smaller one-time credit if previously visited earlier in same training
                    reward += (self.GOAL_REWARD * 0.3)
                self.visited_goals.add(self.current_goal)
                info['reached_goal'] = True

                # mark pending and require returning to start before finalizing
                self._pending_goal = self.current_goal
                if self.RETURN_TO_START:
                    self.returning_to_start = True
                    # hide current_goal so agent can't keep collecting it while pending
                    self.current_goal = None
                else:
                    # immediate finalize (no return requirement)
                    try:
                        self.goal_queue.popleft()
                    except Exception:
                        pass
                    self.current_goal = self.goal_queue[0] if self.goal_queue else None
                    if self.current_goal is None:
                        reward += self.COMPLETION_BONUS
                        done = True

        # If agent is returning to start and reached start -> finalize pending goal
        if self.returning_to_start and self.robot_pos == self.start_pos:
            if self._pending_goal is not None:
                try:
                    self.goal_queue.popleft()
                except Exception:
                    pass
            # clear pending and return flag
            self._pending_goal = None
            self.returning_to_start = False
            # set next goal or finish
            if len(self.goal_queue) > 0:
                self.current_goal = self.goal_queue[0]
            else:
                self.current_goal = None
                reward += self.COMPLETION_BONUS
                done = True

        # --- FIXED REWARD SHAPING LOGIC ---
        # Determine the target for shaping (either the current goal OR the start position if returning)
        target_pos = None
        if self.current_goal is not None:
            target_pos = self.current_goal
        elif self.returning_to_start:
            target_pos = self.start_pos

        # Apply shaping if we have a valid target
        if target_pos is not None:
            goal_x, goal_y = target_pos
            old_dist = abs(prev_x - goal_x) + abs(prev_y - goal_y)
            new_dist = abs(self.robot_pos[0] - goal_x) + abs(self.robot_pos[1] - goal_y)
            reward += self.SHAPING_ALPHA * (old_dist - new_dist)

        # termination: if all goals visited or max_steps
        if (not self.current_goal) and (not self.returning_to_start) and (len(self.goal_queue) == 0):
            done = True
        if self.step_count >= self.max_steps:
            done = True

        return self._get_obs(), reward, done, info

    def _is_at_goal(self, pos, goal):
        return pos == goal

    def _update_dynamic_obstacles(self):
        """
        Random-walk update
        """
        if not self.dynamic_moving:
            return

        for d in self.dynamic_obstacles:
            # obey speed throttle
            if (self.step_count - d.get("last_moved_step", 0)) < d.get("move_every", 1):
                continue

            mode = d.get("mode", "random")
            if mode == "random":
                candidates = d.get("candidates", [])
                if not candidates:
                    continue
                cur = d.get("pos", candidates[0])

                # build neighbor subset: prefer nearby candidates (Manhattan distance <=1)
                nearby = [c for c in candidates if abs(c[0] - cur[0]) + abs(c[1] - cur[1]) <= 1]
                # if none within distance 1 (unlikely), use full candidates
                pool = nearby if nearby else candidates

                # choose a next position randomly; allow staying in place with small prob
                # probability to stay = 0.2
                stay_prob = 0.20
                if random.random() < stay_prob:
                    nxt = cur
                else:
                    # choose uniformly a different or same cell from pool
                    nxt = random.choice(pool)

                d["pos"] = nxt
                d["last_moved_step"] = self.step_count

            else:
                d["last_moved_step"] = self.step_count


    # ---------------- rendering ----------------
    def render(self, mode='human'):
        if not self.render_mode:
            return
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()

        self.screen.fill((230, 230, 230))

        # draw grid cells
        for gy in range(self.grid_h):
            for gx in range(self.grid_w):
                val = self.grid[gy, gx]
                rect = pygame.Rect(gx * self.cell_size, gy * self.cell_size, self.cell_size, self.cell_size)
                if val == 1:
                    pygame.draw.rect(self.screen, (100, 100, 100), rect)  # wall
                elif val == 2:
                    pygame.draw.rect(self.screen, (160, 120, 120), rect)  # bed
                elif val == 3:
                    pygame.draw.rect(self.screen, (200, 200, 200), rect)  # door (looks like wall but passable)
                else:
                    pygame.draw.rect(self.screen, (245, 245, 245), rect)

                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)  # cell border (thin)

        # draw dynamic obstacles (doctors)
        for d in self.dynamic_obstacles:
            gx, gy = d["pos"]
            rect = pygame.Rect(gx * self.cell_size + 4, gy * self.cell_size + 4, self.cell_size - 8, self.cell_size - 8)
            pygame.draw.ellipse(self.screen, (200, 0, 0), rect)

        # draw goals
        # Draw only the current_goal; pending goals are hidden until finalized
        if self.current_goal:
            gx, gy = self.current_goal
            rect = pygame.Rect(gx * self.cell_size + 6, gy * self.cell_size + 6, self.cell_size - 12, self.cell_size - 12)
            pygame.draw.rect(self.screen, (0, 200, 0), rect)

        # draw robot
        rx, ry = self.robot_pos
        rrect = pygame.Rect(rx * self.cell_size + 2, ry * self.cell_size + 2, self.cell_size - 4, self.cell_size - 4)
        pygame.draw.rect(self.screen, (50, 120, 250), rrect)

        # HUD
        pending = 1 if self._pending_goal is not None else 0
        txt = self.font.render(f"Steps: {self.step_count} | Goals left: {len(self.goal_queue)} | Visited: {len(self.visited_goals)} | Pending: {pending}", True, (0,0,0))
        self.screen.blit(txt, (8, 8))

        pygame.display.flip()
        self.clock.tick(30)

    def close(self):
        if self.render_mode:
            pygame.quit()

    # convenience for manual control (not used by trainer)
    def manual_control_step(self, key):
        # map arrow keys to actions
        keymap = {
            pygame.K_UP: 0,
            pygame.K_DOWN: 1,
            pygame.K_LEFT: 2,
            pygame.K_RIGHT: 3,
            pygame.K_w: 0,
            pygame.K_s: 1,
            pygame.K_a: 2,
            pygame.K_d: 3,
        }
        return self.step(keymap.get(key, 0))

if __name__ == "__main__":
    # quick visual test window
    env = SimpleEnv(render_mode=True)
    obs = env.reset()
    done = False
    while not done:
        # random agent for test
        action = random.randrange(env.action_space_n)
        obs, r, done, info = env.step(action)
        env.render()
    print("Episode finished")
    time.sleep(1)
    env.close()