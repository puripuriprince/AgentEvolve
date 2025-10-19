# EVOLVE-BLOCK-START
"""LP-based iterative maximization circle packing for n=26 circles"""

import numpy as np
from scipy.optimize import linprog

def construct_packing():
    """
    Pack 26 circles in a unit square by iteratively maximizing radii with LP,
    and updating centers by centroidal relaxation.
    
    Returns:
        centers: np.array (26,2) of (x,y) circle centers
        radii:   np.array (26,) of circle radii
    """
    n = 26
    rng = np.random.default_rng(seed=6789)

    # Initial centers: variable-size core/edge/corner hybrid
    centers = np.zeros((n, 2))
    # Center
    centers[0] = [0.5, 0.5]
    # 6 surrounding (hexagon)
    for k in range(6):
        a = np.pi/6 + k * np.pi/3
        centers[1+k] = [0.5 + 0.15*np.cos(a), 0.5 + 0.15*np.sin(a)]
    # 8 mid ring
    for k in range(8):
        a = np.pi/8 + k*2*np.pi/8
        centers[7+k] = [0.5 + 0.29*np.cos(a), 0.5 + 0.29*np.sin(a)]
    # 8 edge/corner
    preset = [
        [0.04, 0.04], [0.96, 0.04], [0.96, 0.96], [0.04, 0.96],
        [0.5, 0.04], [0.96, 0.5], [0.5, 0.96], [0.04, 0.5]
    ]
    for k in range(8):
        centers[15+k] = np.array(preset[k]) + rng.normal(0, 0.012, 2)
        centers[15+k] = np.clip(centers[15+k], 0.02, 0.98)
    # 3 outer (filling sparse regions)
    for k in range(3):
        a = np.pi/7 + k*2*np.pi/3
        centers[23+k] = [0.5 + 0.44*np.cos(a), 0.5 + 0.44*np.sin(a)]
    centers[26-1] = [0.83, 0.19]  # fill a gap near a corner
    # Small jitter to break symmetry, except for corners/edge
    centers[:15] += rng.normal(0, 0.012, (15,2))
    centers = np.clip(centers, 0.02, 0.98)

    # Iterative LP radii maximization & centroidal relaxation
    radii = np.full(n, 0.065)
    for iter in range(16):
        # Step 1: Maximize radii via LP
        radii = maximize_radii_lp(centers)

        # Step 2: Move each center towards centroid of available space
        centers = centroidal_update(centers, radii, steps=2, rng=rng)

        # Step 3: Small random jitter to escape local minima
        if iter < 12:
            centers += rng.normal(0, 0.004*(1-iter/18), centers.shape)
            centers = np.clip(centers, 0.015, 0.985)

    # Final pass for tightest radii
    radii = maximize_radii_lp(centers)
    return centers, radii

def maximize_radii_lp(centers):
    """
    For given centers, maximize sum(r) subject to:
      - r_i >= 0
      - r_i + r_j <= ||c_i - c_j||  (no overlap)
      - r_i <= distance to boundary (within square)
    """
    n = centers.shape[0]
    A_ub = []
    b_ub = []
    # Non-overlap: r_i + r_j <= dist(c_i, c_j)
    for i in range(n):
        for j in range(i+1, n):
            d = np.linalg.norm(centers[i] - centers[j])
            if d < 1e-5:
                d = 1e-5
            row = np.zeros(n)
            row[i] = 1
            row[j] = 1
            A_ub.append(row)
            b_ub.append(d-1e-6)
    # Boundary: r_i <= min(x, y, 1-x, 1-y)
    for i in range(n):
        x, y = centers[i]
        for bound in [x, y, 1-x, 1-y]:
            row = np.zeros(n)
            row[i] = 1
            A_ub.append(row)
            b_ub.append(bound-1e-6)
    A_ub = np.stack(A_ub)
    b_ub = np.array(b_ub)
    # r_i >= 0
    bounds = [(0, None)] * n
    # Objective: maximize sum(r)
    c = -np.ones(n)
    res = linprog(c, A_ub, b_ub, bounds=bounds, method='highs')
    if res.success:
        radii = res.x
        # Clamp just in case
        radii = np.clip(radii, 0, 0.5)
    else:
        # fallback: safe greedy radii
        radii = greedy_radii(centers)
    return radii

def greedy_radii(centers):
    n = centers.shape[0]
    radii = np.ones(n)
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1-x, 1-y)
    for i in range(n):
        for j in range(i+1, n):
            d = np.linalg.norm(centers[i] - centers[j])
            if d < 1e-7:
                radii[i] *= 0.93
                radii[j] *= 0.93
                continue
            max_ij = d / 2.0
            if radii[i] > max_ij:
                radii[i] = max_ij
            if radii[j] > max_ij:
                radii[j] = max_ij
    return radii

def centroidal_update(centers, radii, steps=2, rng=None):
    """Move each center towards centroid of its local free space (gradient-free relaxation)."""
    n = centers.shape[0]
    newcenters = centers.copy()
    gridres = 17
    # For each circle, sample a grid around its position, weight by distance from other circles
    for i in range(n):
        x0, y0 = centers[i]
        # Local grid window size
        win = max(0.15, 2.2*radii[i])
        xs = np.linspace(max(0.01, x0-win), min(0.99, x0+win), gridres)
        ys = np.linspace(max(0.01, y0-win), min(0.99, y0+win), gridres)
        grid = np.stack(np.meshgrid(xs, ys), -1).reshape(-1,2)
        # Exclude points inside any other circle, or too near boundary
        mask = np.ones(len(grid), dtype=bool)
        for j in range(n):
            if i==j: continue
            d = np.linalg.norm(grid - centers[j], axis=1)
            mask &= (d > radii[j]*1.08)
        mask &= (grid[:,0]>radii[i]*1.01)
        mask &= (grid[:,0]<1-radii[i]*1.01)
        mask &= (grid[:,1]>radii[i]*1.01)
        mask &= (grid[:,1]<1-radii[i]*1.01)
        pts = grid[mask]
        if len(pts)>0:
            # Move toward centroid, but only a small step to avoid instability
            centroid = np.mean(pts, axis=0)
            delta = centroid - centers[i]
            step = 0.25 * delta
            # Optionally add a mild random kick
            if rng is not None:
                step += rng.normal(0, 0.001, 2)
            newcenters[i] = centers[i] + step
            newcenters[i] = np.clip(newcenters[i], 0.01, 0.99)
        else:
            # No space: small random move
            if rng is not None:
                newcenters[i] = centers[i] + rng.normal(0, 0.003, 2)
                newcenters[i] = np.clip(newcenters[i], 0.01, 0.99)
    return newcenters

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii