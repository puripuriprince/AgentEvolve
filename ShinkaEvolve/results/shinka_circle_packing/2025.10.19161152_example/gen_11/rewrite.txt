# EVOLVE-BLOCK-START
"""Hybrid adaptive ring + LP-annealed circle packing for n=26 in a unit square."""

import numpy as np
from scipy.optimize import linprog

def construct_packing():
    """
    Pack 26 circles in a unit square using adaptive hybrid placement and 
    simulated annealing with global LP-based radii maximization.
    Returns:
        centers: np.array (26,2) of (x,y) circle centers
        radii:   np.array (26,) of circle radii
    """
    rng = np.random.default_rng(seed=112358)
    n = 26
    centers = np.zeros((n, 2))
    idx = 0

    # Step 1: Place central core (center + 6 around, slightly non-uniform radius)
    centers[idx] = [0.5, 0.5]; idx += 1
    core_r = 0.144 + rng.uniform(-0.008, 0.008)
    for i in range(6):
        angle = np.pi/7 + i * np.pi/3 + rng.uniform(-0.09,0.09)
        r = core_r + rng.uniform(-0.012,0.012)
        centers[idx] = [0.5 + r*np.cos(angle), 0.5 + r*np.sin(angle)]
        idx += 1

    # Step 2: Place inner ring (7) with staggered angle, variable radius
    ring1_count = 7
    ring1_r_mean = 0.268
    ring1_r_jitter = 0.021
    base_ang1 = rng.uniform(0, 2*np.pi)
    for k in range(ring1_count):
        theta = (base_ang1 + 2*np.pi*k/ring1_count + rng.uniform(-0.10,0.10))
        ring_r = ring1_r_mean + rng.uniform(-ring1_r_jitter, ring1_r_jitter)
        centers[idx] = [0.5 + ring_r*np.cos(theta), 0.5 + ring_r*np.sin(theta)]
        idx += 1

    # Step 3: Place outer ring (8) with staggered angle and adaptive radius
    ring2_count = 8
    ring2_r_mean = 0.425
    ring2_r_jitter = 0.025
    base_ang2 = rng.uniform(0, 2*np.pi)
    for k in range(ring2_count):
        theta = (base_ang2 + 2*np.pi*k/ring2_count + rng.uniform(-0.08,0.08))
        ring_r = ring2_r_mean + rng.uniform(-ring2_r_jitter, ring2_r_jitter)
        pos = np.array([0.5 + ring_r*np.cos(theta), 0.5 + ring_r*np.sin(theta)])
        centers[idx] = np.clip(pos, 0.012, 0.988)
        idx += 1

    # Step 4: Place corners (4), tight insets with random jitter
    corner_inset = 0.021
    for d in [(corner_inset, corner_inset), (1-corner_inset, corner_inset),
              (1-corner_inset, 1-corner_inset), (corner_inset, 1-corner_inset)]:
        offset = rng.uniform(-0.007, +0.007, 2)
        centers[idx] = np.clip(np.array(d) + offset, 0.01, 0.99)
        idx += 1

    # Step 5: Place edge-mid circles (final 4), with tight insets and jitter
    edge_inset = 0.021
    for d in [(0.5, edge_inset), (1-edge_inset, 0.5),
              (0.5, 1-edge_inset), (edge_inset, 0.5)]:
        offset = rng.uniform(-0.011, +0.011, 2)
        centers[idx] = np.clip(np.array(d) + offset, 0.01, 0.99)
        idx += 1

    assert idx == n

    # Annealing with LP-based radii maximization
    anneal_steps = 18
    centers, radii = lp_anneal_relax_and_grow(centers, anneal_steps=anneal_steps, move_scale=0.08, rng=rng)

    return centers, radii

def lp_anneal_relax_and_grow(centers, anneal_steps=18, move_scale=0.08, rng=None):
    """
    Given circle centers, iteratively relax positions to reduce overlaps and edge collisions,
    while maximizing radii globally using LP at every step.
    """
    n = centers.shape[0]
    if rng is None:
        rng = np.random.default_rng()
    radii = np.ones(n) * 0.07  # Start with small radii

    for step in range(anneal_steps):
        disp = np.zeros_like(centers)
        # Compute soft forces: boundary, circle overlap, random annealing
        for i in range(n):
            xi, yi = centers[i]
            force = np.zeros(2)
            # Boundary repulsion
            margin = 0.013
            steep = 2.3
            if xi < margin:
                force[0] += (margin - xi) * steep
            if xi > 1-margin:
                force[0] -= (xi - (1-margin)) * steep
            if yi < margin:
                force[1] += (margin - yi) * steep
            if yi > 1-margin:
                force[1] -= (yi - (1-margin)) * steep
            # Circle repulsion
            for j in range(n):
                if i == j: continue
                dx, dy = centers[i] - centers[j]
                dist = np.hypot(dx, dy)
                if dist < 1e-8:
                    force += rng.normal(0, 0.002, 2)
                    continue
                minsep = radii[i] + radii[j]
                slack = 0.99
                if dist < minsep * slack:
                    push = ((minsep*slack - dist)/dist) * np.array([dx, dy]) * 0.65
                    force += push
            # Add random annealing noise (decays with step)
            noise_scale = 0.014 * (1 - step / (1.1*anneal_steps))
            force += rng.normal(0, noise_scale, 2)
            disp[i] = force
        # Decaying step size
        s = move_scale * (0.68 + 0.32*(1 - step/(anneal_steps-1)))
        centers += np.clip(disp, -s, s)
        centers = np.clip(centers, 0.013, 0.987)
        # Global LP radii maximization at every step
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
            b_ub.append(d-1e-7)
    # Boundary: r_i <= min(x, y, 1-x, 1-y)
    for i in range(n):
        x, y = centers[i]
        for bound in [x, y, 1-x, 1-y]:
            row = np.zeros(n)
            row[i] = 1
            A_ub.append(row)
            b_ub.append(bound-1e-7)
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

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii