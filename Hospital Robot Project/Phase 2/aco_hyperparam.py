
import argparse
import random
import time
import os
import multiprocessing as mp

# --- Search space (discrete choices) ---
SEARCH_SPACE = {
    "LR": [1e-4, 5e-4, 1e-3, 3e-3],
    "BATCH_SIZE": [32, 64, 128],
    "REPLAY_SIZE": [5000, 10000, 20000],
    "GAMMA": [0.95, 0.98, 0.99],
    "EPS_DECAY_FRAMES": [50000, 100000, 200000],
    "TARGET_UPDATE_FREQ": [500, 1000, 2000]
}

# --- ACO hyperparams ---
DEFAULT_ANTS = 6
DEFAULT_ITERS = 12
EVAPORATION = 0.25   # pheromone evaporation rate
Q_CONST = 1.0        # pheromone add scaling

# Helper: initialize pheromone matrix (dict of lists aligned to SEARCH_SPACE choices)
def init_pheromones(search_space, init_val=1.0):
    pher = {}
    for k, choices in search_space.items():
        pher[k] = [init_val for _ in choices]
    return pher

# Sample a candidate according to pheromones (probabilistic)
def sample_candidate(pheromones, search_space, rng):
    candidate = {}
    for k, choices in search_space.items():
        ph = pheromones[k]
        total = sum(ph) + 1e-12
        probs = [p / total for p in ph]
        idx = rng.choices(range(len(choices)), weights=probs, k=1)[0]
        candidate[k] = choices[idx]
    return candidate

# Evaluate a candidate by invoking train() from train_multi_agent_dqn
def evaluate_candidate(candidate, eval_frames, seed, out_dir_base):

    # import locally inside worker to avoid issues with pickling module-level state
    try:
        import train_multi_agent_dqn as trainer
    except Exception as e:
        print("Failed to import train_multi_agent_dqn in worker:", e)
        return -1e6, ""

    try:
        if hasattr(trainer, "LR"): trainer.LR = candidate["LR"]
        if hasattr(trainer, "BATCH_SIZE"): trainer.BATCH_SIZE = candidate["BATCH_SIZE"]
        if hasattr(trainer, "REPLAY_SIZE"): trainer.REPLAY_SIZE = candidate["REPLAY_SIZE"]
        if hasattr(trainer, "GAMMA"): trainer.GAMMA = candidate["GAMMA"]
        if hasattr(trainer, "EPS_DECAY_FRAMES"): trainer.EPS_DECAY_FRAMES = candidate["EPS_DECAY_FRAMES"]
        if hasattr(trainer, "TARGET_UPDATE_FREQ"): trainer.TARGET_UPDATE_FREQ = candidate["TARGET_UPDATE_FREQ"]
    except Exception as e:
        print("Warning: could not override trainer globals:", e)

    timestamp = int(time.time() * 1000) % 1000000
    out_dir = os.path.join(out_dir_base, f"aco_eval_s{seed}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    try:
        # Expect trainer.train to return (policy, rewards) or similar
        policy, rewards = trainer.train(seed=seed, render=False, max_frames=eval_frames, out_dir=out_dir, checkpoint_freq=eval_frames+1)
        if rewards:
            score = float(max(rewards))
        else:
            score = 0.0
        return score, out_dir
    except Exception as e:
        print("Evaluation failed (candidate):", e)
        return -1e6, out_dir

# Main ACO loop
def run_aco(search_space,
            ants=DEFAULT_ANTS,
            iters=DEFAULT_ITERS,
            eval_frames=20000,
            processes=1,
            out_dir_base="./aco_runs"):
    rng = random.Random(0)
    pher = init_pheromones(search_space, init_val=1.0)
    best_candidate = None
    best_score = -1e9

    os.makedirs(out_dir_base, exist_ok=True)

    for it in range(iters):
        print(f"[ACO] Iteration {it+1}/{iters}")
        candidates = []
        for a in range(ants):
            c = sample_candidate(pher, search_space, rng)
            candidates.append((c, it*ants + a))

        # Build job arguments for starmap: (candidate, eval_frames, seed, out_dir_base)
        job_args = [(cand, eval_frames, idx, out_dir_base) for cand, idx in candidates]

        # evaluate in parallel using starmap (clean argument matching)
        with mp.Pool(processes=processes) as pool:
            results = pool.starmap(evaluate_candidate, job_args)

        # process results and update pheromones
        scores = []
        for (cand, idx), (score, out_dir) in zip(candidates, results):
            scores.append(score)
            print(f"  Ant {idx % ants}: score={score:.3f} cand={cand} out:{out_dir}")
            if score > best_score:
                best_score = score
                best_candidate = (cand, score, out_dir)

        # Evaporate pheromones
        for k in pher:
            pher[k] = [p * (1.0 - EVAPORATION) for p in pher[k]]

        # Reinforce according to normalized quality
        if scores:
            min_s, max_s = min(scores), max(scores)
            score_range = max(1e-6, max_s - min_s)
            for (cand, _), (score, _) in zip(candidates, results):
                quality = (score - min_s) / score_range if score_range > 0 else 1.0
                for k, val in cand.items():
                    choices = search_space[k]
                    idx_choice = choices.index(val)
                    pher[k][idx_choice] += Q_CONST * (0.1 + quality)

        print(f"  Best so far: score={best_score:.3f} cand={best_candidate[0] if best_candidate else None}")
    return best_candidate, pher

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iters", type=int, default=DEFAULT_ITERS)
    parser.add_argument("--ants", type=int, default=DEFAULT_ANTS)
    parser.add_argument("--eval_frames", type=int, default=20000, help="Frames per eval run (smaller=quicker)")
    parser.add_argument("--processes", type=int, default=1, help="Parallel workers for evals")
    parser.add_argument("--out_dir", type=str, default="./aco_runs")
    return parser.parse_args()

if __name__ == "__main__":
    # Safe start for multiprocessing on Windows
    mp.set_start_method("spawn", force=False)
    args = parse_args()
    best, pheromones = run_aco(SEARCH_SPACE, ants=args.ants, iters=args.iters, eval_frames=args.eval_frames, processes=args.processes, out_dir_base=args.out_dir)
    print("DONE. Best candidate:", best)
