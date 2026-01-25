
import pygame, time, random
import numpy as np
from collections import deque

class MultiAgentEnv:
    def __init__(self,
                 n_agents=3,
                 width=1152, height=768,
                 cell_size=32,
                 render_mode=True,
                 seed=None,
                 goal_reward=100.0,      # INCREASED: Stronger motivation
                 completion_bonus=1000.0, # INCREASED: Big finish bonus
                 step_penalty=-0.01,      # ADJUSTED: Small cost to exist
                 shaping_alpha=1.0,       # INCREASED: Strong "Hot/Cold" hint
                 dynamic_moving_initial=True,
                 return_to_start=True,
                 rooms_per_col=4,
                 extra_rooms=2):
        self.n_agents = n_agents
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_w = width // cell_size
        self.grid_h = height // cell_size
        self.render_mode = render_mode
        self._rng = random.Random(seed)

        # rewards/params
        self.GOAL_REWARD = goal_reward
        self.COMPLETION_BONUS = completion_bonus
        self.STEP_PENALTY = step_penalty
        self.SHAPING_ALPHA = shaping_alpha
        self.RETURN_TO_START = return_to_start

        # build grid
        self.grid = np.zeros((self.grid_h, self.grid_w), dtype=np.uint8)
        self._create_layout(rooms_per_col=rooms_per_col, extra_rooms=extra_rooms)

        # dynamic obstacles
        self.dynamic_obstacles = []
        self.dynamic_moving = dynamic_moving_initial
        self._init_dynamic_obstacles()

        # agents
        self.start_positions = []
        left_x = 2
        spacing = max(2, self.grid_h // (self.n_agents + 1))
        for i in range(self.n_agents):
            sy = spacing * (i + 1)
            self.start_positions.append((left_x, sy))

        self.agent_pos = [pos for pos in self.start_positions]
        self._pending = [None] * self.n_agents
        self.visited_by_agent = [set() for _ in range(self.n_agents)]

        self.goals = self._compute_bed_goals()
        self.goal_queue = deque(self.goals)
        self.claimed_by = {}

        # new: hidden goals set (hide immediately on pickup)
        self.hidden_goals = set()

        # total completed counter (finalized goals)
        self.total_completed = 0

        self.max_steps = 2500
        self.step_count = 0
        self.returning_flags = [False] * self.n_agents

        if self.render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Hospital Multi-Agent Env")
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 14)

        # --- CHANGED: Observation Space Calculation ---
        self.obs_dim = self.n_agents * 6
        self.agent_colors = [(50,120,250), (20,200,120), (200,120,20), (120,20,200), (200,50,50)]

    def _create_layout(self, rooms_per_col=4, extra_rooms=2):
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        room_w = 6
        room_h = max(4, (self.grid_h - 2) // (rooms_per_col + extra_rooms))
        right_start = self.grid_w - room_w - 1
        bed_positions = []
        y = 1
        for i in range(rooms_per_col + extra_rooms):
            top = y
            bottom = min(self.grid_h - 2, y + room_h - 1)
            for gx in range(right_start, right_start + room_w):
                self.grid[top, gx] = 1
                self.grid[bottom, gx] = 1
            for gy in range(top, bottom + 1):
                self.grid[gy, right_start] = 1
                self.grid[gy, right_start + room_w - 1] = 1
            bed_x = right_start + 2
            bed_y = top + (bottom - top) // 2
            self.grid[bed_y, bed_x] = 2
            bed_positions.append((bed_x, bed_y))
            door_x = right_start
            door_y = bed_y
            self.grid[door_y, door_x] = 3
            y = bottom + 1
        for gx in range(4, min(12, self.grid_w//2)):
            for gy in range(2, min(6, self.grid_h-2)):
                if self.grid[gy,gx] == 0 and self._rng.random() < 0.15:
                    self.grid[gy,gx] = 2
        self._bed_positions = bed_positions

    def _compute_bed_goals(self):
        goals = []
        for (bx, by) in self._bed_positions:
            for cand in [(bx-1,by),(bx,by-1),(bx,by+1),(bx+1,by)]:
                x,y = cand
                if 0 <= x < self.grid_w and 0 <= y < self.grid_h and self.grid[y,x] == 0:
                    goals.append(cand)
                    break
        return goals

    def _init_dynamic_obstacles(self):
        self.dynamic_obstacles = []
        self.dynamic_moving = getattr(self, "dynamic_moving", True)
        base_min = 2
        base_max = 6
        for i, (bx, by) in enumerate(self._bed_positions):
            candidates = []
            for gx in range(max(1, bx - 6), min(self.grid_w - 1, bx + 2)):
                for gy in range(max(1, by - 2), min(self.grid_h - 1, by + 3)):
                    if self.grid[gy, gx] == 0 or self.grid[gy, gx] == 3:
                        candidates.append((gx, gy))
            if not candidates: candidates = [(max(1, bx - 2), by)]
            start = candidates[len(candidates)//2]
            move_every = self._rng.randint(base_min, base_max)
            obj = {"pos": start, "candidates": candidates, "move_every": move_every, "last_moved_step": 0}
            self.dynamic_obstacles.append(obj)

    def set_dynamic_moving(self, enabled: bool):
        self.dynamic_moving = bool(enabled)

    def reset(self):
        self.agent_pos = [pos for pos in self.start_positions]
        self._pending = [None] * self.n_agents
        self.visited_by_agent = [set() for _ in range(self.n_agents)]
        self.claimed_by = {}
        self.goal_queue = deque(self.goals)
        self.returning_flags = [False]*self.n_agents
        self.step_count = 0
        self.hidden_goals = set()       # reset hidden goals
        self.total_completed = 0        # reset completed counter
        for d in self.dynamic_obstacles:
            if "candidates" in d and d["candidates"]: d["pos"] = self._rng.choice(d["candidates"])
            else: d["pos"] = (1, 1)
            d["last_moved_step"] = 0
        return self._get_obs()

    # SENSOR BASED OBSERVATION
    def _get_obs(self, centralized=True):
        all_agent_obs = []
        for i in range(self.n_agents):
            ax, ay = self.agent_pos[i]
            target = None
            if self.returning_flags[i]:
                target = self.start_positions[i]
            else:
                for g, owner in self.claimed_by.items():
                    if owner == i:
                        target = g
                        break
                if target is None:
                    for g in self.goal_queue:
                        if g not in self.claimed_by:
                            target = g
                            break
            if target is None:
                dx, dy = 0.0, 0.0
            else:
                tx, ty = target
                dx = (tx - ax) / self.grid_w
                dy = (ty - ay) / self.grid_h
            def is_blocked(nx, ny):
                if not (0 <= nx < self.grid_w and 0 <= ny < self.grid_h): return 1.0
                if self.grid[ny, nx] in (1, 2): return 1.0
                for d in self.dynamic_obstacles:
                    if d["pos"] == (nx, ny): return 1.0
                return 0.0
            wall_u = is_blocked(ax, ay-1)
            wall_d = is_blocked(ax, ay+1)
            wall_l = is_blocked(ax-1, ay)
            wall_r = is_blocked(ax+1, ay)
            all_agent_obs.extend([dx, dy, wall_u, wall_d, wall_l, wall_r])
        return np.array(all_agent_obs, dtype=np.float32)

    def step(self, actions):
        rewards = [self.STEP_PENALTY for _ in range(self.n_agents)]
        infos = [{} for _ in range(self.n_agents)]
        dones = False
        self.step_count += 1
        prev_positions = [pos for pos in self.agent_pos]

        # Moves
        deltas = [(0,-1),(0,1),(-1,0),(1,0),(1,-1),(-1,-1),(1,1),(-1,1)]
        new_positions = []
        for i, a in enumerate(actions):
            dx,dy = deltas[a] if 0 <= a < 8 else (0,0)
            ax,ay = self.agent_pos[i]
            nx,ny = ax+dx, ay+dy
            if not (0 <= nx < self.grid_w and 0 <= ny < self.grid_h): nx,ny = ax,ay
            if self.grid[ny,nx] in (1,2):
                nx,ny = ax,ay
                rewards[i] += -0.2
            new_positions.append((nx,ny))

        # Collisions between agents
        occupied = {}
        for i,pos in enumerate(new_positions):
            if pos in occupied:
                j = occupied[pos]
                new_positions[i] = prev_positions[i]
                new_positions[j] = prev_positions[j]
                rewards[i] += -0.5
                rewards[j] += -0.5
            else:
                occupied[pos] = i
        self.agent_pos = list(new_positions)
        self._update_dynamic_obstacles()

        # Doctor Collisions
        for i,pos in enumerate(self.agent_pos):
            for d in self.dynamic_obstacles:
                if d["pos"] == pos:
                    self.agent_pos[i] = prev_positions[i]
                    rewards[i] += -1.0

        # Goal Logic
        for i in range(self.n_agents):
            pos = self.agent_pos[i]
            # Claim
            if self._pending[i] is None and not self.returning_flags[i]:
                already_claimed = any(c == i for c in self.claimed_by.values())
                if not already_claimed:
                    self.claim_goal_for_agent(i)

            # Identify my target
            my_goal = None
            if self.returning_flags[i]:
                my_goal = self.start_positions[i]
            else:
                for g,c in self.claimed_by.items():
                    if c == i:
                        my_goal = g
                        break

            # Reached Goal (Pick up)
            if my_goal is not None and not self.returning_flags[i] and pos == my_goal:
                rewards[i] += self.GOAL_REWARD
                self._pending[i] = my_goal
                self.returning_flags[i] = True
                # HIDE the goal from rendering immediately
                self.hidden_goals.add(my_goal)
                # print pickup event
                picked_count = sum(len(s) for s in self.visited_by_agent) + len(self.hidden_goals) - self.total_completed
                print(f"[PICKUP] Agent {i} picked goal {my_goal}. Hidden goals: {len(self.hidden_goals)}. (picked_count approx {picked_count})")

            # Reached Start (Drop off / finalize)
            elif self.returning_flags[i] and pos == self.start_positions[i]:
                if self._pending[i] is not None:
                    try:
                        # remove from goal_queue if still present
                        self.goal_queue.remove(self._pending[i])
                    except ValueError:
                        pass
                    # remove claim mapping
                    if self._pending[i] in self.claimed_by:
                        del self.claimed_by[self._pending[i]]
                    # ensure it's no longer in hidden_goals
                    if self._pending[i] in self.hidden_goals:
                        self.hidden_goals.discard(self._pending[i])
                    self.visited_by_agent[i].add(self._pending[i])
                    # increment total completed counter
                    self.total_completed += 1
                    finalized_goal = self._pending[i]
                    self._pending[i] = None
                    self.returning_flags[i] = False
                    rewards[i] += self.GOAL_REWARD  # reward for drop-off
                    # print finalize event
                    print(f"[FINALIZE] Agent {i} finalized goal {finalized_goal}. Total completed: {self.total_completed}")
                    if len(self.goal_queue) == 0:
                        rewards[i] += self.COMPLETION_BONUS
                        dones = True

            # Shaping Reward
            target = self.start_positions[i] if self.returning_flags[i] else my_goal
            if target is not None:
                ax, ay = prev_positions[i]
                old_dist = abs(ax - target[0]) + abs(ay - target[1])
                nx, ny = self.agent_pos[i]
                new_dist = abs(nx - target[0]) + abs(ny - target[1])
                rewards[i] += self.SHAPING_ALPHA * (old_dist - new_dist)

        if self.step_count >= self.max_steps:
            dones = True
        return self._get_obs(), np.array(rewards, dtype=np.float32), dones, {}

    def claim_goal_for_agent(self, agent_idx):
        for g in self.goal_queue:
            if g not in self.claimed_by:
                self.claimed_by[g] = agent_idx
                return g
        return None

    def _update_dynamic_obstacles(self):
        if not getattr(self, "dynamic_moving", True): return
        for d in self.dynamic_obstacles:
            if (self.step_count - d.get("last_moved_step", 0)) < d.get("move_every", 1): continue
            candidates = d.get("candidates", [])
            if not candidates: continue
            cur = d.get("pos", candidates[0])
            nearby = [c for c in candidates if abs(c[0]-cur[0])+abs(c[1]-cur[1])<=1]
            pool = nearby if nearby else candidates
            if self._rng.random() < 0.20: nxt = cur
            else: nxt = self._rng.choice(pool)
            d["pos"] = nxt
            d["last_moved_step"] = self.step_count

    def render(self):
        if not self.render_mode: return
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                pygame.quit()
        self.screen.fill((230,230,230))
        for gy in range(self.grid_h):
            for gx in range(self.grid_w):
                val = self.grid[gy,gx]
                rect = pygame.Rect(gx*self.cell_size, gy*self.cell_size, self.cell_size, self.cell_size)
                if val==1: pygame.draw.rect(self.screen, (100,100,100), rect)
                elif val==2: pygame.draw.rect(self.screen, (160,120,120), rect)
                elif val==3: pygame.draw.rect(self.screen, (200,200,200), rect)
                else: pygame.draw.rect(self.screen, (245,245,245), rect)
                pygame.draw.rect(self.screen, (200,200,200), rect, 1)

        # dynamic obstacles (doctors)
        for d in self.dynamic_obstacles:
            gx,gy = d["pos"]
            rect = pygame.Rect(gx*self.cell_size+4, gy*self.cell_size+4, self.cell_size-8, self.cell_size-8)
            pygame.draw.ellipse(self.screen, (200,0,0), rect)

        # goals (unvisited AND not hidden)
        for g in list(self.goal_queue):
            if g in self.hidden_goals:
                continue  # hide immediately after pickup
            gx,gy = g
            rect = pygame.Rect(gx*self.cell_size+6, gy*self.cell_size+6, self.cell_size-12, self.cell_size-12)
            pygame.draw.rect(self.screen, (0,200,0), rect)

        # agents + pending marker
        for i,(ax,ay) in enumerate(self.agent_pos):
            color = self.agent_colors[i % len(self.agent_colors)]
            rect = pygame.Rect(ax*self.cell_size+2, ay*self.cell_size+2, self.cell_size-4, self.cell_size-4)
            pygame.draw.rect(self.screen, color, rect)
            if self._pending[i] is not None:
                px,py = self._pending[i]
                pygame.draw.circle(self.screen, color, (px*self.cell_size + self.cell_size//2, py*self.cell_size + self.cell_size//2), 4)

        # HUD: show steps, goals left, hidden, completed
        txt = self.font.render(f"Steps:{self.step_count} | Goals left:{len(self.goal_queue)} | Hidden:{len(self.hidden_goals)} | Completed:{self.total_completed}", True, (0,0,0))
        self.screen.blit(txt, (8,8))
        pygame.display.flip()
        self.clock.tick(30)

    def close(self):
        if self.render_mode: pygame.quit()
