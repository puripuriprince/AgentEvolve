# EVOLVE-BLOCK-START
"""Simulated annealing-based circle packing for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Simulated annealing-based arrangement of 26 circles in a unit square.
    Returns:
        centers: np.array of shape (26,2)
        radii:   np.array of shape (26,)
    """
    n = 26
    # 1) Initialize centers randomly in [0.1,0.9]^2
    centers = np.random.rand(n,2) * 0.8 + 0.1
    radii = compute_max_radii(centers)
    current_sum = np.sum(radii)

    # 2) Simulated annealing parameters
    max_iter = 10000
    step_start = 0.1
    step_end   = 0.005

    for k in range(max_iter):
        t = k / (max_iter - 1)
        step = step_start*(1 - t) + step_end*t
        T = step  # temperature

        # pick one circle to move
        i = np.random.randint(n)
        cand = centers.copy()
        cand[i] += np.random.randn(2) * step
        cand[i] = np.clip(cand[i], 0.0, 1.0)

        # recompute radii and objective
        rad_cand = compute_max_radii(cand)
        sum_cand = np.sum(rad_cand)

        # acceptance
        Δ = sum_cand - current_sum
        if Δ >= 0 or np.random.rand() < np.exp(Δ / T):
            centers = cand
            radii = rad_cand
            current_sum = sum_cand

    # 3) Final local refinement (greedy)
    refine_iters = 2000
    for _ in range(refine_iters):
        i = np.random.randint(n)
        cand = centers.copy()
        cand[i] += np.random.randn(2) * step_end
        cand[i] = np.clip(cand[i], 0.0, 1.0)
        rad_cand = compute_max_radii(cand)
        sum_cand = np.sum(rad_cand)
        if sum_cand > current_sum:
            centers = cand
            radii = rad_cand
            current_sum = sum_cand

    # final radii
    radii = compute_max_radii(centers)
    return centers, radii

def compute_max_radii(centers):
    """
    Given circle centers, compute the maximum non-overlapping radii
    that keep all circles inside the unit square.
    """
    n = centers.shape[0]
    radii = np.zeros(n)
    # boundary-limited radii
    for i in range(n):
        x,y = centers[i]
        radii[i] = min(x, y, 1-x, 1-y)

    # pairwise overlap constraints
    for i in range(n):
        for j in range(i+1, n):
            d = np.linalg.norm(centers[i] - centers[j])
            if d <= 0: 
                continue
            # if sum of current radii > d, scale both
            if radii[i] + radii[j] > d:
                scale = d / (radii[i] + radii[j])
                radii[i] *= scale
                radii[j] *= scale
    return radii
# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii