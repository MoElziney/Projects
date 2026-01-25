# train_dqn_no_a_star.py (patched with curriculum & logging)
import argparse
import collections
import random
import time
import os
import csv
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from custom_env import SimpleEnv

# -------- hyperparams (default; some overridden by CLI args) ----------
GAMMA = 0.99
LR = 1e-3
BATCH_SIZE = 64
REPLAY_SIZE = 20000
MIN_REPLAY = 1000
TARGET_UPDATE_FREQ = 1000  # steps

# default epsilon schedule (can be overridden via CLI)
EPS_START = 1.0
EPS_END = 0.10
EPS_DECAY_FRAMES = 80000

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# -------- replay buffer ----------
Transition = collections.namedtuple('Transition', ('state', 'action', 'reward', 'next_state', 'done'))

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = collections.deque(maxlen=capacity)

    def push(self, *args):
        self.buffer.append(Transition(*args))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        return Transition(*zip(*batch))

    def __len__(self):
        return len(self.buffer)

# -------- model ----------
class DQN(nn.Module):
    def __init__(self, obs_dim, n_actions, hidden=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_actions)
        )

    def forward(self, x):
        return self.net(x)

# -------- utilities ----------
def epsilon_by_frame(frame_idx: int):
    eps = EPS_END + (EPS_START - EPS_END) * max(0.0, (1.0 - frame_idx / EPS_DECAY_FRAMES))
    return eps

def compute_td_loss(batch, policy_net, target_net, optimizer):
    """
    Double DQN update:
      - actions for next_states are chosen by policy_net
      - their Q-values are evaluated by target_net
    """
    states = torch.from_numpy(np.vstack(batch.state)).float().to(DEVICE)
    actions = torch.from_numpy(np.array(batch.action)).long().to(DEVICE)
    rewards = torch.from_numpy(np.array(batch.reward)).float().to(DEVICE)
    next_states = torch.from_numpy(np.vstack(batch.next_state)).float().to(DEVICE)
    dones = torch.from_numpy(np.array(batch.done).astype(np.uint8)).float().to(DEVICE)

    # Current Q-values for taken actions
    q_values = policy_net(states)
    q_value = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

    with torch.no_grad():
        # Double DQN:
        # 1) use policy_net to choose next actions
        next_q_values_policy = policy_net(next_states)
        next_actions = next_q_values_policy.max(1)[1].unsqueeze(1)  # indices shape (batch,1)

        # 2) evaluate those actions using target_net
        next_q_values_target = target_net(next_states)
        next_q_value = next_q_values_target.gather(1, next_actions).squeeze(1)

        expected_q_value = rewards + GAMMA * next_q_value * (1 - dones)

    # MSE loss
    loss = nn.functional.mse_loss(q_value, expected_q_value)

    optimizer.zero_grad()
    loss.backward()
    # optional gradient clipping for stability
    torch.nn.utils.clip_grad_norm_(policy_net.parameters(), 10)
    optimizer.step()
    return loss.item()


# -------- training loop (with logging & checkpointing) ----------
def train(seed=0, render=False, max_frames=250000, out_dir="./checkpoints",
          checkpoint_freq=5000, resume_path=None,
          eps_end=None, eps_decay_frames=None,
          curriculum_frames=0,
          env_params=None):
    global EPS_END, EPS_DECAY_FRAMES
    if eps_end is not None:
        EPS_END = eps_end
    if eps_decay_frames is not None:
        EPS_DECAY_FRAMES = eps_decay_frames

    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "training_log.csv")

    # environment (pass env_params dict to customize rewards & curriculum)
    env_kwargs = env_params or {}
    env = SimpleEnv(width=800, height=600, scaled_robot_size=(32,32),
                    render_mode=render, seed=seed,
                    **env_kwargs)
    env.seed(seed)
    state = env.reset()

    obs_dim = state.shape[0]
    n_actions = env.action_space_n

    policy_net = DQN(obs_dim, n_actions).to(DEVICE)
    target_net = DQN(obs_dim, n_actions).to(DEVICE)
    target_net.load_state_dict(policy_net.state_dict())

    optimizer = optim.Adam(policy_net.parameters(), lr=LR)
    replay = ReplayBuffer(REPLAY_SIZE)

    start_frame = 0
    best_episode_reward = -1e9
    frame_idx = 0
    losses = []
    all_rewards = []
    episode_reward = 0.0
    episode = 0
    episode_length = 0

    # resume if requested
    if resume_path:
        ck = torch.load(resume_path, map_location=DEVICE)
        policy_net.load_state_dict(ck.get("policy_state_dict", ck))
        target_net.load_state_dict(policy_net.state_dict())
        optimizer.load_state_dict(ck.get("optimizer_state_dict", optimizer.state_dict()))
        start_frame = ck.get("frame_idx", 0)
        best_episode_reward = ck.get("best_episode_reward", best_episode_reward)
        print(f"[RESUME] loaded checkpoint from {resume_path}, starting at frame {start_frame}")
        frame_idx = start_frame

    # CSV header if new
    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["episode","frames","episode_reward","episode_length","mean_q","avg_loss_recent","goals_completed"])

    # warm-up: fill replay with random transitions
    print("Warming up replay buffer...")
    while len(replay) < MIN_REPLAY and frame_idx < max_frames:
        action = random.randrange(n_actions)
        next_state, reward, done, info = env.step(action)
        replay.push(state, action, reward, next_state, done)
        state = next_state
        episode_reward += reward
        episode_length += 1
        frame_idx += 1
        if done:
            goals_done = len(env.visited_goals)
            all_rewards.append(episode_reward)
            with open(csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([episode, frame_idx, episode_reward, episode_length, 0.0, 0.0, goals_done])
            episode_reward = 0.0
            episode += 1
            episode_length = 0
            state = env.reset()
    print("Warmup done, starting training loop")

    state = env.reset()
    qvals_accum = []
    loss_accum = []

    # ensure dynamic_moving matches curriculum initial condition
    if curriculum_frames > 0:
        env.set_dynamic_moving(False)

    while frame_idx < max_frames:
        # enable dynamic obstacles if curriculum cutoff passed
        if curriculum_frames > 0 and frame_idx >= curriculum_frames and not env.dynamic_moving:
            env.set_dynamic_moving(True)
            print(f"[CURRICULUM] enabled dynamic obstacles at frame {frame_idx}")

        eps = epsilon_by_frame(frame_idx)
        if random.random() < eps:
            action = random.randrange(n_actions)
            mean_q_val = 0.0
        else:
            with torch.no_grad():
                st = torch.from_numpy(state[np.newaxis, :]).float().to(DEVICE)
                qvals = policy_net(st)
                action = int(qvals.max(1)[1].item())
                mean_q_val = float(qvals.mean().item())

        next_state, reward, done, info = env.step(action)
        replay.push(state, action, reward, next_state, done)
        state = next_state
        episode_reward += reward
        episode_length += 1
        frame_idx += 1

        qvals_accum.append(mean_q_val)

        if len(replay) >= BATCH_SIZE:
            batch = replay.sample(BATCH_SIZE)
            loss = compute_td_loss(batch, policy_net, target_net, optimizer)
            losses.append(loss)
            loss_accum.append(loss)

        if frame_idx % TARGET_UPDATE_FREQ == 0:
            target_net.load_state_dict(policy_net.state_dict())

        if frame_idx % checkpoint_freq == 0:
            ck_path = os.path.join(out_dir, f"checkpoint_frame_{frame_idx}.pth")
            torch.save({
                "frame_idx": frame_idx,
                "policy_state_dict": policy_net.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "best_episode_reward": best_episode_reward
            }, ck_path)
            print(f"[CHECKPOINT] saved {ck_path}")

        if done:
            episode += 1
            all_rewards.append(episode_reward)
            avg_loss_recent = float(np.mean(loss_accum[-100:])) if loss_accum else 0.0
            mean_q_episode = float(np.mean(qvals_accum)) if qvals_accum else 0.0
            goals_done = len(env.visited_goals)

            with open(csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([episode, frame_idx, episode_reward, episode_length, mean_q_episode, avg_loss_recent, goals_done])

            if episode_reward > best_episode_reward:
                best_episode_reward = episode_reward
                best_path = os.path.join(out_dir, f"best_model_ep{episode}_r{episode_reward:.3f}.pth")
                torch.save({
                    "frame_idx": frame_idx,
                    "episode": episode,
                    "episode_reward": episode_reward,
                    "policy_state_dict": policy_net.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "best_episode_reward": best_episode_reward
                }, best_path)
                print(f"[BEST] new best episode {episode} reward {episode_reward:.3f} saved to {best_path}")

            episode_reward = 0.0
            episode_length = 0
            qvals_accum = []
            state = env.reset()

        if frame_idx % 1000 == 0:
            avg_reward20 = np.mean(all_rewards[-20:]) if all_rewards else 0.0
            avg_loss100 = np.mean(losses[-100:]) if losses else 0.0
            print(f"frame {frame_idx} | eps {eps:.3f} | episode {episode} | avg_reward(20) {avg_reward20:.3f} | avg_loss(100) {avg_loss100:.5f}")

    final_path = os.path.join(out_dir, f"final_model_frame_{frame_idx}.pth")
    torch.save({
        "frame_idx": frame_idx,
        "policy_state_dict": policy_net.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "best_episode_reward": best_episode_reward
    }, final_path)
    print(f"Training finished. final model saved to {final_path}")

    return policy_net, all_rewards

# -------- run when called directly ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--render", action="store_true", help="Enable pygame render (slow)")
    parser.add_argument("--max_frames", type=int, default=250000)
    parser.add_argument("--out_dir", type=str, default="./checkpoints")
    parser.add_argument("--checkpoint_freq", type=int, default=5000, help="Save checkpoint every N frames")
    parser.add_argument("--resume", type=str, default=None, help="Path to checkpoint to resume from")
    parser.add_argument("--eps_end", type=float, default=None, help="Final epsilon (overrides default)")
    parser.add_argument("--eps_decay_frames", type=int, default=None, help="Frames over which epsilon decays")
    parser.add_argument("--curriculum_frames", type=int, default=0, help="Number of frames to keep doctors static (0 = no curriculum)")
    # env reward params (optional override)
    parser.add_argument("--goal_reward", type=float, default=None)
    parser.add_argument("--completion_bonus", type=float, default=None)
    parser.add_argument("--step_penalty", type=float, default=None)
    parser.add_argument("--shaping_alpha", type=float, default=None)
    parser.add_argument("--return_to_start", type=int, default=1, help="1=robot must return to start after each goal; 0 = immediate next goal")

    args = parser.parse_args()

    # build env params dict
    env_params = {}
    if args.goal_reward is not None:
        env_params["goal_reward"] = args.goal_reward
    if args.completion_bonus is not None:
        env_params["completion_bonus"] = args.completion_bonus
    if args.step_penalty is not None:
        env_params["step_penalty"] = args.step_penalty
    if args.shaping_alpha is not None:
        env_params["shaping_alpha"] = args.shaping_alpha
    env_params["dynamic_moving_initial"] = False if args.curriculum_frames > 0 else True
    env_params["return_to_start"] = bool(args.return_to_start)

    policy, rewards = train(seed=args.seed,
                            render=args.render,
                            max_frames=args.max_frames,
                            out_dir=args.out_dir,
                            checkpoint_freq=args.checkpoint_freq,
                            resume_path=args.resume,
                            eps_end=args.eps_end,
                            eps_decay_frames=args.eps_decay_frames,
                            curriculum_frames=args.curriculum_frames,
                            env_params=env_params)
    print("Done. Last 10 episode rewards:", rewards[-10:])
