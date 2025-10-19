# EVOLVE-BLOCK-START
"""Adaptive hexagonal/edge-relaxed circle packing for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Construct an arrangement of 26 circles in a unit square
    that attempts to maximize the sum of their radii using
    a central hexagonal core, adaptive edge/corner circles,
    and local repulsion-based relaxation.
    Returns:
        centers: np.array (26,2) of (x,y) circle centers
        radii:   np.array (26,) of circle radii
    """
    n = 26
    centers = np.zeros((n, 2))
    rng = np.random.default_rng(seed=42)  # deterministic

    # 1. 7-circle compact hexagonal core (center + 6 around)
    hex_r = 0.15
    centers[0] = [0.5, 0.5]
    for i in range(6):
        a = np.pi/6 + i * np.pi/3  # rotate to avoid edge alignment
        centers[1+i] = [0.5 + hex_r * np.cos(a), 0.5 + hex_r * np.sin(a)]

    # 2. 12 "middle ring" circles, relaxed radius, angle offset to avoid core/edges
    ring_r = 0.33
    ring_jitter = 0.03
    for i in range(12):
        a = (2*np.pi*i)/12 + np.pi/12
        r = ring_r + rng.uniform(-ring_jitter, ring_jitter)
        centers[7+i] = [0.5 + r*np.cos(a), 0.5 + r*np.sin(a)]

    # 3. 7 edge/corner circles, slightly inset and jittered to break symmetry
    edge_idx = 19
    edge_inset = 0.03
    jitter = 0.015
    # corners
    corners = np.array([
        [edge_inset, edge_inset],
        [1-edge_inset, edge_inset],
        [1-edge_inset, 1-edge_inset],
        [edge_inset, 1-edge_inset],
    ])
    for k in range(4):
        offset = rng.uniform(-jitter, jitter, 2)
        centers[edge_idx] = np.clip(corners[k] + offset, 0.01, 0.99)
        edge_idx += 1
    # edge midpoints
    mids = np.array([
        [0.5, edge_inset],
        [1-edge_inset, 0.5],
        [0.5, 1-edge_inset],
    ])
    for k in range(3):
        offset = rng.uniform(-jitter, jitter, 2)
        centers[edge_idx] = np.clip(mids[k] + offset, 0.01, 0.99)
        edge_idx += 1

    # 4. Local repulsion & greedy radii maximization
    centers, radii = local_relax_and_grow(centers, steps=8)

    return centers, radii

def local_relax_and_grow(centers, steps=8):
    """
    Given circle centers, iteratively relax positions to reduce overlaps and edge collisions,
    and greedily maximize radii.
    Returns final (centers, radii)
    """
    n = centers.shape[0]
    radii = np.ones(n) * 0.075  # initialize with small radii

    for step in range(steps):
        # 1. Compute repulsive forces (from overlaps and boundary)
        disp = np.zeros_like(centers)
        for i in range(n):
            xi, yi = centers[i]
            # Repel from boundaries if close
            margin = 0.01
            force = np.zeros(2)
            if xi < margin:
                force[0] += (margin - xi) * 1.8
            if xi > 1-margin:
                force[0] -= (xi - (1-margin)) * 1.8
            if yi < margin:
                force[1] += (margin - yi) * 1.8
            if yi > 1-margin:
                force[1] -= (yi - (1-margin)) * 1.8
            # Repel from other circles if overlap (using current radii)
            for j in range(n):
                if i == j: continue
                dx, dy = centers[i] - centers[j]
                dist = np.hypot(dx, dy)
                if dist < 1e-7:  # avoid divide by zero
                    force += rng.normal(0, 0.001, 2)
                    continue
                minsep = radii[i] + radii[j]
                if dist < minsep * 0.98:  # allow a little slack
                    push = ((minsep - dist) / dist) * np.array([dx, dy]) * 0.5
                    force += push
            disp[i] = force

        # 2. Move centers by small fraction of displacement
        centers += np.clip(disp, -0.04, 0.04)

        # 3. Clamp back inside unit square
        centers = np.clip(centers, 0.01, 0.99)

        # 4. Greedily maximize radii
        radii = maximize_radii(centers)

    return centers, radii

def maximize_radii(centers):
    """
    Given centers, compute maximal radii for each circle that fit in square and do not overlap.
    """
    n = centers.shape[0]
    radii = np.ones(n)
    # Limit by distance to boundary
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1-x, 1-y)
    # Limit by distance to neighbors
    for i in range(n):
        for j in range(i+1, n):
            d = np.linalg.norm(centers[i] - centers[j])
            if d < 1e-7:  # overlap, avoid zero division
                radii[i] *= 0.9
                radii[j] *= 0.9
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