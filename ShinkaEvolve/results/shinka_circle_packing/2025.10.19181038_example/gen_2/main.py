# EVOLVE-BLOCK-START
"""Adaptive force relaxation algorithm for packing 26 circles in a unit square."""

import numpy as np

def construct_packing():
    """
    Force-based adaptive arrangement of 26 circles in a unit square to maximize the sum of radii.
    Returns:
        Tuple of (centers, radii)
    """
    n = 26
    np.random.seed(42)
    centers = np.zeros((n, 2))

    # Hybrid initial placement
    # Corners
    centers[0] = [0.08, 0.08]
    centers[1] = [0.08, 0.92]
    centers[2] = [0.92, 0.08]
    centers[3] = [0.92, 0.92]
    # Edges (not corners)
    centers[4] = [0.5, 0.08]
    centers[5] = [0.5, 0.92]
    centers[6] = [0.08, 0.5]
    centers[7] = [0.92, 0.5]
    # Interior: loose hex grid, points in a 3x3 grid, centered
    grid = []
    for i in range(3):
        for j in range(3):
            grid.append([0.26 + 0.24*i, 0.26 + 0.24*j])
    grid = np.array(grid)
    centers[8:17] = grid
    # Remaining 9: random points in [0.20,0.80]^2
    centers[17:] = np.random.uniform(0.20, 0.80, (n-17,2))

    # Initial radii - small
    radii = np.full(n, 0.03)

    # Hyperparameters
    learning_rate = 0.12
    min_learning_rate = 0.001
    repulse_weight = 1.0
    attract_weight = 0.12
    border_weight = 0.28
    growth_step = 0.008
    n_iter = 340

    for t in range(n_iter):
        # --- Force computation ---
        disp = np.zeros((n, 2))

        # Pairwise repulsion
        for i in range(n):
            for j in range(i+1, n):
                v = centers[i] - centers[j]
                dist = np.linalg.norm(v)
                min_dist = radii[i] + radii[j] + 1e-6
                if dist < 1e-7:  # perfect overlap, random direction
                    direction = np.random.uniform(-1,1,2)
                    direction /= np.linalg.norm(direction)
                    v = direction * 1e-2
                    dist = 1e-2
                if dist < min_dist:
                    # Overlap => strong repulsion
                    force = repulse_weight * (min_dist - dist + 1e-6) / (dist+1e-7)
                    disp[i] += force * v
                    disp[j] -= force * v
                else:
                    # Gentle repulsion when close
                    force = 0.08 * repulse_weight * (min_dist/dist)**2
                    disp[i] += force * v
                    disp[j] -= force * v

        # Border soft force: keep in [r,1-r]
        for i in range(n):
            x, y = centers[i]
            r = radii[i]
            # Push inward if too near boundary
            if x < r+0.006:
                disp[i][0] += border_weight * (r+0.006-x)
            if x > 1 - (r+0.006):
                disp[i][0] -= border_weight * (x-(1-r-0.006))
            if y < r+0.006:
                disp[i][1] += border_weight * (r+0.006-y)
            if y > 1 - (r+0.006):
                disp[i][1] -= border_weight * (y-(1-r-0.006))

        # Gentle attraction to center to prevent edge sticking
        for i in range(n):
            v = np.array([0.5,0.5]) - centers[i]
            dist = np.linalg.norm(v)
            if dist > 0.01:
                disp[i] += attract_weight * v

        # Move
        scale = learning_rate * (1 - t/n_iter)
        scale = max(scale, min_learning_rate)
        centers += scale * disp

        # Clamp within [r+eps, 1-r-eps] (soft, will readjust later)
        centers = np.clip(centers, radii+0.002, 1-(radii+0.002))

        # --- Radius growth ---
        # Try to expand all radii by growth_step, then shrink any that cause overlap or boundary violation
        radii += growth_step * (0.98 - t/n_iter)
        for i in range(n):
            # Boundary
            x, y = centers[i]
            r = radii[i]
            if x - r < 0: radii[i] = x
            if x + r > 1: radii[i] = 1-x
            if y - r < 0: radii[i] = y
            if y + r > 1: radii[i] = 1-y
        # Overlap
        for i in range(n):
            for j in range(i+1, n):
                v = centers[i] - centers[j]
                dist = np.linalg.norm(v)
                if dist < radii[i] + radii[j]:
                    # Shrink both equally just enough to resolve overlap
                    excess = radii[i] + radii[j] - dist
                    cut = excess/2.0 + 1e-6
                    radii[i] -= cut
                    radii[j] -= cut
                    if radii[i] < 0.001: radii[i] = 0.001
                    if radii[j] < 0.001: radii[j] = 0.001

    return centers, radii
# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii
