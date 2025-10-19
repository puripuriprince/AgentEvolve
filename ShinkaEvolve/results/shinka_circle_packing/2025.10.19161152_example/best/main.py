# EVOLVE-BLOCK-START
"""Genetic + CMA-ES evolutionary circle packing for n=26 in a unit square."""

import numpy as np

def construct_packing():
    """
    Use genetic algorithm with CMA-ES local refinement to arrange 26 circles
    in a unit square, maximizing the sum of radii.
    Returns:
        centers: np.array (26,2)
        radii: np.array (26,)
    """
    n = 26
    popsize = 33
    generations = 22
    elite = 7
    cmaes_iters = 6

    rng = np.random.default_rng(seed=20240613)
    
    # Helper: generate random arrangement (centered, rings + jitter)
    def random_candidate():
        arr = np.zeros((n,2))
        idx = 0
        # Center
        arr[idx] = [0.5,0.5]; idx += 1
        # Corners
        for d in [(0.03,0.03),(0.97,0.03),(0.97,0.97),(0.03,0.97)]:
            arr[idx] = np.clip(np.array(d) + rng.uniform(-0.012,0.012,2), 0.01, 0.99)
            idx += 1
        # Edges
        for d in [(0.5,0.03),(0.97,0.5),(0.5,0.97),(0.03,0.5)]:
            arr[idx] = np.clip(np.array(d) + rng.uniform(-0.012,0.012,2), 0.01, 0.99)
            idx += 1
        # Hex ring 1
        base_r = 0.205
        for i in range(8):
            a = np.pi/8 + 2*np.pi*i/8 + rng.uniform(-0.11,0.11)
            r = base_r + rng.uniform(-0.015, 0.015)
            pos = [0.5 + r*np.cos(a), 0.5 + r*np.sin(a)]
            arr[idx] = np.clip(pos, 0.01, 0.99)
            idx += 1
        # Outer ring
        outer = n-idx
        outer_r = 0.44
        for i in range(outer):
            a = 2*np.pi*i/outer + rng.uniform(-0.12,0.12)
            r = outer_r + rng.uniform(-0.017,0.017)
            pos = [0.5+r*np.cos(a),0.5+r*np.sin(a)]
            arr[idx] = np.clip(pos, 0.01, 0.99)
            idx += 1
        assert idx==n
        return arr

    # Helper: flatten/unflatten
    def flatten(arr):
        return arr.reshape(-1)
    def unflatten(vec):
        return vec.reshape((n,2))

    # Helper: fitness function
    def fitness(vec):
        centers = unflatten(vec)
        radii = calc_max_radii(centers)
        # Soft penalty for out-of-square
        if np.any((centers<0.0) | (centers>1.0)):
            return -1.0
        return np.sum(radii)

    # Helper: greedy radii maximization
    def calc_max_radii(centers):
        n = centers.shape[0]
        radii = np.ones(n)
        # Border limit
        for i in range(n):
            x,y = centers[i]
            radii[i] = min(x, y, 1-x, 1-y)
        # Pairwise limit
        for t in range(3):  # multiple passes for fairness
            for i in range(n):
                for j in range(i+1,n):
                    d = np.linalg.norm(centers[i]-centers[j])
                    if d < 1e-8:
                        radii[i] *= 0.88
                        radii[j] *= 0.88
                        continue
                    max_ij = d/2.0
                    if radii[i]>max_ij:
                        radii[i]=max_ij
                    if radii[j]>max_ij:
                        radii[j]=max_ij
        return radii

    # --- Genetic Algorithm Main Loop ---
    pop = np.array([flatten(random_candidate()) for _ in range(popsize)])
    pop_fitness = np.array([fitness(ind) for ind in pop])

    for gen in range(generations):
        # Elitism: select best
        elite_idx = np.argsort(-pop_fitness)[:elite]
        newpop = [pop[i].copy() for i in elite_idx]

        # Variation: crossover + mutation
        while len(newpop) < popsize:
            # Tournament selection
            p1, p2 = rng.choice(popsize, 2, replace=False)
            if pop_fitness[p1]>pop_fitness[p2]:
                parent = pop[p1]
            else:
                parent = pop[p2]
            child = parent.copy()
            # Occasional (blend) crossover with another elite
            if rng.uniform()<0.45:
                mate = pop[rng.choice(elite_idx)]
                alpha = rng.uniform(0.18,0.82)
                child = alpha*child + (1-alpha)*mate
            # Mutate: gaussian jitter (decaying with gen)
            noise = rng.normal(0, 0.045*(1-gen/generations), child.shape)
            child += noise
            # Clamp
            child = np.clip(child, 0.01, 0.99)
            newpop.append(child)
        pop = np.array(newpop)
        # Evaluate
        pop_fitness = np.array([fitness(ind) for ind in pop])
        # CMA-ES refinement on best (every 3rd gen)
        if gen%3==0:
            best = pop[elite_idx[0]].copy()
            best_score = pop_fitness[elite_idx[0]]
            x = best.copy()
            sigma = 0.09*(1-gen/generations)
            for it in range(cmaes_iters):
                mutants = []
                mutant_scores = []
                for _ in range(8):
                    step = rng.normal(0,sigma,x.shape)
                    trial = np.clip(x+step,0.01,0.99)
                    score = fitness(trial)
                    mutants.append(trial)
                    mutant_scores.append(score)
                mutant_scores = np.array(mutant_scores)
                best_idx = np.argmax(mutant_scores)
                if mutant_scores[best_idx] > best_score:
                    x = mutants[best_idx]
                    best_score = mutant_scores[best_idx]
            pop[elite_idx[0]] = x
            pop_fitness[elite_idx[0]] = best_score

    # Select best
    best_idx = np.argmax(pop_fitness)
    best_vec = pop[best_idx]
    centers = unflatten(best_vec)
    radii = calc_max_radii(centers)
    return centers, radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii