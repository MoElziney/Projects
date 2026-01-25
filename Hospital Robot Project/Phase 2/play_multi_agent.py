# play_multi_agent.py (callable API version)

import time
import numpy as np
import torch
import torch.nn as nn
import random

from env_multi_agent import MultiAgentEnv

class CentralDQN(nn.Module):
    def __init__(self, obs_dim, n_agents, n_actions_per_agent=8, hidden=512):
        super().__init__()
        self.n_agents = n_agents
        self.n_actions_per_agent = n_actions_per_agent
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_agents * n_actions_per_agent)
        )
    def forward(self, x):
        return self.net(x)

KEY_TO_ACTION = {
    "UP": 0, "DOWN": 1, "LEFT": 2, "RIGHT": 3,
    "UP_RIGHT": 4, "UP_LEFT": 5, "DOWN_RIGHT": 6, "DOWN_LEFT": 7
}

def load_policy(ckpt_path, obs_dim, n_agents, device):
    net = CentralDQN(obs_dim, n_agents).to(device)
    ck = torch.load(ckpt_path, map_location=device)
    if isinstance(ck, dict) and "policy_state_dict" in ck:
        net.load_state_dict(ck["policy_state_dict"])
    elif isinstance(ck, dict) and "state_dict" in ck:
        net.load_state_dict(ck["state_dict"])
    else:
        try:
            net.load_state_dict(ck)
        except Exception as e:
            print("Failed to load checkpoint keys directly:", e)
            raise
    net.eval()
    return net

def get_actions_from_policy(policy_net, obs, n_agents, n_actions, device):
    with torch.no_grad():
        t = torch.from_numpy(obs[None,:]).float().to(device)
        q = policy_net(t).view(-1, n_agents, n_actions)
        actions = [int(q[0,i].argmax().item()) for i in range(n_agents)]
        return actions

def manual_key_to_action(pressed_keys):
    up = 'UP' in pressed_keys
    down = 'DOWN' in pressed_keys
    left = 'LEFT' in pressed_keys
    right = 'RIGHT' in pressed_keys
    if up and right: return KEY_TO_ACTION["UP_RIGHT"]
    if up and left: return KEY_TO_ACTION["UP_LEFT"]
    if down and right: return KEY_TO_ACTION["DOWN_RIGHT"]
    if down and left: return KEY_TO_ACTION["DOWN_LEFT"]
    if up: return KEY_TO_ACTION["UP"]
    if down: return KEY_TO_ACTION["DOWN"]
    if left: return KEY_TO_ACTION["LEFT"]
    if right: return KEY_TO_ACTION["RIGHT"]
    return None

def run_episode(env, mode, policy_net, device, delay, seed):
    obs = env.reset()
    done = False
    total_rewards = np.zeros(env.n_agents, dtype=float)

    try:
        import pygame
    except Exception:
        pygame = None

    pressed = set()

    while not done:
        if mode == "random":
            actions = [random.randrange(8) for _ in range(env.n_agents)]
        elif mode == "greedy":
            if policy_net is None:
                actions = [random.randrange(8) for _ in range(env.n_agents)]
            else:
                actions = get_actions_from_policy(policy_net, obs, env.n_agents, 8, device)
        elif mode == "manual":
            if pygame is None:
                raise RuntimeError("pygame required for manual mode")
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    return total_rewards, True
                elif ev.type == pygame.KEYDOWN:
                    if ev.key in (pygame.K_UP, pygame.K_w): pressed.add('UP')
                    if ev.key in (pygame.K_DOWN, pygame.K_s): pressed.add('DOWN')
                    if ev.key in (pygame.K_LEFT, pygame.K_a): pressed.add('LEFT')
                    if ev.key in (pygame.K_RIGHT, pygame.K_d): pressed.add('RIGHT')
                elif ev.type == pygame.KEYUP:
                    if ev.key in (pygame.K_UP, pygame.K_w): pressed.discard('UP')
                    if ev.key in (pygame.K_DOWN, pygame.K_s): pressed.discard('DOWN')
                    if ev.key in (pygame.K_LEFT, pygame.K_a): pressed.discard('LEFT')
                    if ev.key in (pygame.K_RIGHT, pygame.K_d): pressed.discard('RIGHT')

            my0 = manual_key_to_action(pressed)
            a0 = my0 if my0 is not None else 0
            other_actions = []
            for i in range(1, env.n_agents):
                if policy_net:
                    other_actions.append(get_actions_from_policy(policy_net, obs, env.n_agents, 8, device)[i])
                else:
                    other_actions.append(random.randrange(8))
            actions = [a0] + other_actions
        else:
            raise ValueError("Unknown mode: " + str(mode))

        obs, rewards, done, info = env.step(actions)
        total_rewards += np.array(rewards, dtype=float)

        if env.render_mode:
            env.render()
        time.sleep(delay)

    return total_rewards, done

def play(mode="random",
         ckpt=None,
         n_episodes=5,
         delay=0.06,
         seed=0,
         n_agents=3,
         render=True,
         device=None):

    random.seed(seed); np.random.seed(seed); 
    device = torch.device(device) if device is not None else (torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu"))

    env = MultiAgentEnv(n_agents=n_agents, render_mode=render)
    obs = env.reset()
    obs_dim = obs.shape[0]
    policy_net = None
    if ckpt:
        try:
            policy_net = load_policy(ckpt, obs_dim, n_agents, device)
            print("Loaded policy from", ckpt)
        except Exception as e:
            print("Failed to load policy:", e)
            policy_net = None

    results = []
    for ep in range(n_episodes):
        rewards, _ = run_episode(env, mode, policy_net, device, delay, seed + ep)
        print(f"Episode {ep+1}/{n_episodes} total_rewards per_agent: {rewards}")
        results.append(rewards)
        time.sleep(0.2)

    env.close()
    return results

# Convenience when running file directly
if __name__ == "__main__":
    # example: run 3 random episodes
    play(mode="random", ckpt='aco_runs/best_model_ep2_r-356.150.pth', n_episodes=3, delay=0.06, seed=0, n_agents=3, render=True)
