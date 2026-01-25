# run_best_model.py
import os
import glob
import time
import torch
import numpy as np

# import environment and model definition (from train script)
from custom_env import SimpleEnv
from train_dpq import DQN, DEVICE

import pygame

def find_latest_best_checkpoint(checkpoint_dir="./checkpoints"):
    pattern = os.path.join(checkpoint_dir, "best_model_ep231_r850.648.pth")
    files = glob.glob(pattern)
    if not files:
        return None
    # choose the newest by modified time
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[0]

def load_policy_from_ckpt(path, obs_dim, n_actions):
    ck = torch.load(path, map_location=DEVICE)
    policy = DQN(obs_dim, n_actions).to(DEVICE)
    # checkpoint may contain 'policy_state_dict' or be the state_dict itself
    if isinstance(ck, dict) and "policy_state_dict" in ck:
        policy.load_state_dict(ck["policy_state_dict"])
    elif isinstance(ck, dict) and any(k.startswith("module.") or k in policy.state_dict() for k in ck.keys()):
        # assume ck is a direct state dict
        try:
            policy.load_state_dict(ck)
        except Exception:
            # fallback: try key 'state_dict' or similar
            if "state_dict" in ck:
                policy.load_state_dict(ck["state_dict"])
            else:
                raise
    else:
        raise RuntimeError("Unrecognized checkpoint format.")
    policy.eval()
    return policy

def run_visualization(ckpt_path=None, episodes=10, render_delay=0.08):
    env = SimpleEnv(width=800, height=600, scaled_robot_size=(32,32), render_mode=True)
    obs = env.reset()

    obs_dim = obs.shape[0]
    n_actions = env.action_space_n

    if ckpt_path is None:
        ckpt_path = find_latest_best_checkpoint()
    if ckpt_path is None:
        raise FileNotFoundError("No best_model_*.pth found in ./checkpoints. Run training first.")

    print(f"Loading checkpoint: {ckpt_path}")
    policy = load_policy_from_ckpt(ckpt_path, obs_dim, n_actions)

    # initialize pygame (env already does inside SimpleEnv when render_mode=True)
    running = True
    episode = 0

    try:
        while running and episode < episodes:
            obs = env.reset()
            done = False
            total_r = 0.0
            step = 0
            while not done and running:
                # handle pygame events so window stays responsive
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        running = False
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        running = False

                # choose greedy action from policy
                with torch.no_grad():
                    st = torch.from_numpy(obs[np.newaxis, :]).float().to(DEVICE)
                    q = policy(st)
                    action = int(q.max(1)[1].item())

                next_obs, reward, done, info = env.step(action)
                total_r += reward
                step += 1
                obs = next_obs

                # render the environment
                env.render()
                time.sleep(render_delay)  # small delay so we can watch

            print(f"Episode {episode} finished. steps={step} reward={total_r:.3f} info={info}")
            episode += 1

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        env.close()
        print("Visualizer closed.")

if __name__ == "__main__":
    ck = find_latest_best_checkpoint("./checkpoints")
    if ck:
        print("Found checkpoint:", ck)
    else:
        print("No 'best_model_*.pth' found in ./checkpoints. Exiting.")
    run_visualization(ckpt_path=ck, episodes=100, render_delay=0.06)
