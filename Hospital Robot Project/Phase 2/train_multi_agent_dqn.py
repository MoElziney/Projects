# train_multi_agent_dqn.py

import argparse
import collections
import csv
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.tensorboard import SummaryWriter

# adjust this import if your filename differs
from env_multi_agent import MultiAgentEnv

# ---- hyperparams (قابلة للتعديل) ----------
GAMMA = 0.99
LR = 5e-4
BATCH_SIZE = 64
REPLAY_SIZE = 20000
MIN_REPLAY = 1000
TARGET_UPDATE_FREQ = 1000
EPS_START = 1.0
EPS_END = 0.05
EPS_DECAY_FRAMES = 100000
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Curriculum default (can be overridden via CLI)
DEFAULT_DYNAMIC_ENABLE_AT = 40000

Transition = collections.namedtuple("Transition", ("state","action","reward","next_state","done"))

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

# centralized DQN: returns n_agents*8 Q-values
class CentralDQN(nn.Module):
    def __init__(self, obs_dim, n_agents, n_actions_per_agent=8, hidden=512):
        super().__init__()
        self.n_agents = n_agents
        self.n_actions_per_agent = n_actions_per_agent
        # simple MLP
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_agents * n_actions_per_agent)
        )
    def forward(self, x):
        # x: (batch, obs_dim)
        return self.net(x)

def epsilon_by_frame(frame_idx):
    eps = EPS_END + (EPS_START - EPS_END) * max(0.0, (1.0 - frame_idx / EPS_DECAY_FRAMES))
    return eps

def compute_td_loss(batch, policy_net, target_net, optimizer, n_agents, n_actions):
    # batch: Transition of tuples; states and next_states are arrays (flattened)
    states = torch.from_numpy(np.vstack(batch.state)).float().to(DEVICE)             # (B, obs_dim)
    actions = torch.from_numpy(np.vstack(batch.action)).long().to(DEVICE)          # (B, n_agents)
    rewards = torch.from_numpy(np.vstack(batch.reward)).float().to(DEVICE)         # (B, n_agents)
    next_states = torch.from_numpy(np.vstack(batch.next_state)).float().to(DEVICE) # (B, obs_dim)
    dones = torch.from_numpy(np.array(batch.done).astype(np.uint8)).float().to(DEVICE) # (B,)

    # current Q: shape (B, n_agents * n_actions) -> reshape -> (B, n_agents, n_actions)
    q_vals = policy_net(states).view(-1, n_agents, n_actions)
    # gather the Q-values for the taken actions (actions shape B x n_agents)
    actions_unsq = actions.unsqueeze(-1)  # (B, n_agents, 1)
    q_value = q_vals.gather(2, actions_unsq).squeeze(2)  # (B, n_agents)

    with torch.no_grad():
        # Double DQN:
        # choose next actions by policy_net, evaluate with target_net
        next_q_policy = policy_net(next_states).view(-1, n_agents, n_actions)
        next_actions = next_q_policy.argmax(dim=2, keepdim=True)  # (B, n_agents, 1)
        next_q_target = target_net(next_states).view(-1, n_agents, n_actions)
        next_q_value = next_q_target.gather(2, next_actions).squeeze(2)  # (B, n_agents)
        # expected q per agent
        expected_q = rewards + GAMMA * next_q_value * (1.0 - dones.unsqueeze(1))

    # loss: MSE aggregated across agents and averaged over batch
    loss = nn.functional.mse_loss(q_value, expected_q)
    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(policy_net.parameters(), 10.0)
    optimizer.step()
    return loss.item()

def train(seed=0, render=False, max_frames=200000, out_dir="./ma_checkpoints", checkpoint_freq=5000, resume=None, dynamic_enable_at=DEFAULT_DYNAMIC_ENABLE_AT):
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "training_log.csv")
    tb_dir = os.path.join(out_dir, "tb")
    writer = SummaryWriter(log_dir=tb_dir)

    env = MultiAgentEnv(n_agents=3, render_mode=render)
    try:
        env.set_dynamic_moving(False)
    except Exception:
        pass
    env.reset()
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)

    obs = env.reset()
    obs_dim = obs.shape[0]
    n_agents = env.n_agents
    n_actions = 8

    policy = CentralDQN(obs_dim, n_agents, n_actions_per_agent=n_actions).to(DEVICE)
    target = CentralDQN(obs_dim, n_agents, n_actions_per_agent=n_actions).to(DEVICE)
    target.load_state_dict(policy.state_dict())

    optimizer = optim.Adam(policy.parameters(), lr=LR)
    replay = ReplayBuffer(REPLAY_SIZE)

    frame_idx = 0
    episode = 0
    episode_reward = np.zeros(n_agents)
    episode_length = 0
    best_episode_reward_sum = -1e9
    losses = []
    all_rewards = []

    # optionally resume
    if resume:
        ck = torch.load(resume, map_location=DEVICE)
        policy.load_state_dict(ck["policy_state_dict"])
        target.load_state_dict(policy.state_dict())
        optimizer.load_state_dict(ck.get("optimizer_state_dict", optimizer.state_dict()))
        frame_idx = ck.get("frame_idx", 0)
        best_episode_reward_sum = ck.get("best_episode_reward_sum", best_episode_reward_sum)
        print("Resumed from", resume)

    # prepare CSV header (include total_completed)
    if not os.path.exists(csv_path):
        with open(csv_path,"w",newline="") as f:
            w = csv.writer(f)
            w.writerow(["episode","frames","episode_reward_sum","episode_reward_per_agent","episode_length","avg_loss_recent","total_completed"])

    # warmup
    print("Warming up replay...")
    state = env.reset()
    while len(replay) < MIN_REPLAY and frame_idx < max_frames:
        actions = [random.randrange(n_actions) for _ in range(n_agents)]
        next_state, rewards, done, info = env.step(actions)
        replay.push(state, np.array(actions, dtype=np.int64), np.array(rewards, dtype=np.float32), next_state, done)
        state = next_state
        frame_idx += 1

        # Curriculum check during warmup (in case threshold is very small)
        if (not getattr(env, "dynamic_moving", True)) and frame_idx >= dynamic_enable_at:
            try:
                env.set_dynamic_moving(True)
                print(f"[CURRICULUM] enabled dynamic obstacles during warmup at frame {frame_idx}")
                ck_path = os.path.join(out_dir, f"checkpoint_before_dynamic_at_{frame_idx}.pth")
                torch.save({
                    "frame_idx": frame_idx,
                    "policy_state_dict": policy.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                }, ck_path)
                print(f"[CHECKPOINT] saved {ck_path} (before enabling dynamics)")
            except Exception:
                pass

        if done:
            state = env.reset()
    print("Warmup done; starting training loop")

    state = env.reset()
    q_mean_accum = []
    loss_accum = []

    try:
        while frame_idx < max_frames:
            eps = epsilon_by_frame(frame_idx)
            if random.random() < eps:
                actions = [random.randrange(n_actions) for _ in range(n_agents)]
                mean_q_val = 0.0
            else:
                with torch.no_grad():
                    st = torch.from_numpy(state[np.newaxis,:]).float().to(DEVICE)
                    qvals = policy(st).view(-1, n_agents, n_actions)
                    actions = [int(qvals[0,i].argmax().item()) for i in range(n_agents)]
                    mean_q_val = float(qvals.mean().item())

            next_state, rewards, done, info = env.step(actions)
            replay.push(state, np.array(actions, dtype=np.int64), np.array(rewards, dtype=np.float32), next_state, done)
            state = next_state
            episode_reward += np.array(rewards)
            episode_length += 1
            frame_idx += 1
            q_mean_accum.append(mean_q_val)

            # Curriculum: enable dynamic obstacles after threshold
            if (not getattr(env, "dynamic_moving", True)) and frame_idx >= dynamic_enable_at:
                try:
                    env.set_dynamic_moving(True)
                    print(f"[CURRICULUM] enabled dynamic obstacles at frame {frame_idx}")
                    ck_path = os.path.join(out_dir, f"checkpoint_before_dynamic_at_{frame_idx}.pth")
                    torch.save({
                        "frame_idx": frame_idx,
                        "policy_state_dict": policy.state_dict(),
                        "optimizer_state_dict": optimizer.state_dict(),
                    }, ck_path)
                    print(f"[CHECKPOINT] saved {ck_path} (before enabling dynamics)")
                except Exception as e:
                    print("[CURRICULUM] failed to enable dynamic obstacles:", e)

            if len(replay) >= BATCH_SIZE:
                batch = replay.sample(BATCH_SIZE)
                loss = compute_td_loss(batch, policy, target, optimizer, n_agents, n_actions)
                losses.append(loss)
                loss_accum.append(loss)

            if frame_idx % TARGET_UPDATE_FREQ == 0:
                target.load_state_dict(policy.state_dict())

            # periodic checkpoint
            if frame_idx % checkpoint_freq == 0:
                path = os.path.join(out_dir, f"checkpoint_frame_{frame_idx}.pth")
                torch.save({
                    "frame_idx": frame_idx,
                    "policy_state_dict": policy.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "best_episode_reward_sum": best_episode_reward_sum
                }, path)
                print("[CHECKPOINT] saved", path)

            if done:
                episode += 1
                sum_reward = float(episode_reward.sum())
                all_rewards.append(sum_reward)
                avg_loss_recent = float(np.mean(loss_accum[-100:])) if loss_accum else 0.0
                mean_q = float(np.mean(q_mean_accum)) if q_mean_accum else 0.0

                # total_completed from env (if available)
                total_completed = int(getattr(env, "total_completed", 0))

                with open(csv_path,"a",newline="") as f:
                    w = csv.writer(f)
                    w.writerow([episode, frame_idx, sum_reward, list(map(float, episode_reward.tolist())), episode_length, avg_loss_recent, total_completed])

                # TensorBoard logging (per episode)
                writer.add_scalar('episode/reward_sum', sum_reward, frame_idx)
                writer.add_scalar('episode/avg_loss', avg_loss_recent, frame_idx)
                writer.add_scalar('episode/total_completed', total_completed, frame_idx)
                writer.add_scalar('episode/mean_q', mean_q, frame_idx)
                writer.add_scalar('train/eps', eps, frame_idx)
                # per-agent rewards
                for i, r in enumerate(episode_reward):
                    writer.add_scalar(f'episode/agent_{i}_reward', float(r), frame_idx)

                # save best model (by sum of agent rewards)
                if sum_reward > best_episode_reward_sum:
                    best_episode_reward_sum = sum_reward
                    bestpath = os.path.join(out_dir, f"best_model_ep{episode}_r{sum_reward:.3f}.pth")
                    torch.save({
                        "frame_idx": frame_idx,
                        "episode": episode,
                        "episode_reward_sum": sum_reward,
                        "policy_state_dict": policy.state_dict(),
                        "optimizer_state_dict": optimizer.state_dict(),
                        "best_episode_reward_sum": best_episode_reward_sum
                    }, bestpath)
                    print("[BEST] new best episode", episode, "reward_sum", sum_reward, "saved to", bestpath)

                # reset episode bookkeeping
                episode_reward = np.zeros(n_agents)
                episode_length = 0
                q_mean_accum = []
                state = env.reset()

            if frame_idx % 1000 == 0:
                avg_reward20 = np.mean(all_rewards[-20:]) if all_rewards else 0.0
                avg_loss100 = np.mean(losses[-100:]) if losses else 0.0
                print(f"frame {frame_idx} | eps {eps:.3f} | episode {episode} | avg_reward(20) {avg_reward20:.3f} | avg_loss(100) {avg_loss100:.5f}")

    except KeyboardInterrupt:
        print("Training interrupted by user")

    # final checkpoint + close writer
    final_path = os.path.join(out_dir, f"final_model_frame_{frame_idx}.pth")
    torch.save({
        "frame_idx": frame_idx,
        "policy_state_dict": policy.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "best_episode_reward_sum": best_episode_reward_sum
    }, final_path)
    print("Training finished. final saved to", final_path)

    writer.close()
    return policy, all_rewards

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--max_frames", type=int, default=200000)
    parser.add_argument("--out_dir", type=str, default="./ma_checkpoints")
    parser.add_argument("--checkpoint_freq", type=int, default=5000)
    parser.add_argument("--resume", type=str, default=None)
    parser.add_argument("--dynamic_enable_at", type=int, default=DEFAULT_DYNAMIC_ENABLE_AT, help="Enable dynamic obstacles after this many frames")
    args = parser.parse_args()

    policy, rewards = train(seed=args.seed, render=args.render, max_frames=args.max_frames, out_dir=args.out_dir, checkpoint_freq=args.checkpoint_freq, resume=args.resume, dynamic_enable_at=args.dynamic_enable_at)
    print("Done. Last 10 episode reward sums:", rewards[-10:])
