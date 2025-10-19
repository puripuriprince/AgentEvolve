# EVOLVE-BLOCK-START
"""Adaptive hexagonal/edge-relaxed circle packing for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Construct an improved hybrid-layered arrangement of 26 circles in a unit square.
    Uses a compact central hexagon, two staggered rings, and 3 edge/corner circles,
    followed by strong local relaxation.
    Returns:
        centers: np.array (26,2) of (x,y) circle centers
        radii:   np.array (26,) of circle radii
    """
    n = 26
    centers = np.zeros((n, 2))
    rng = np.random.default_rng(seed=42)  # deterministic

    # 1. Priority: Place circles exactly (or nearly) at the 4 corners and 4 edge midpoints for maximal use of square geometry.
    # Corners
    corner_inset = 0.023
    corner_jitter = 0.006
    corners = np.array([
        [corner_inset, corner_inset],
        [1-corner_inset, corner_inset],
        [1-corner_inset, 1-corner_inset],
        [corner_inset, 1-corner_inset],
    ])
    for i in range(4):
        centers[i] = np.clip(corners[i] + rng.uniform(-corner_jitter, corner_jitter, 2), 0.012, 0.988)
    # Edge midpoints
    edge_inset = 0.025
    edge_jitter = 0.009
    edges = np.array([
        [0.5, edge_inset],
        [1-edge_inset, 0.5],
        [0.5, 1-edge_inset],
        [edge_inset, 0.5],
    ])
    for i in range(4):
        centers[4+i] = np.clip(edges[i] + rng.uniform(-edge_jitter, edge_jitter, 2), 0.013, 0.987)

    # 2. Central hexagon: 7 circles (center + 6 around)
    core_r = 0.150
    centers[8] = [0.5, 0.5]
    for i in range(6):
        a = np.pi/6 + i * np.pi/3
        centers[9+i] = [0.5 + core_r * np.cos(a), 0.5 + core_r * np.sin(a)]

    # 3. First ring (7 circles), slightly inside mid-radius, angle offset for interlacing
    ring1_r = 0.272
    for i in range(7):
        a = (2*np.pi*i)/7 + np.pi/18
        centers[15+i] = [0.5 + ring1_r * np.cos(a), 0.5 + ring1_r * np.sin(a)]

    # 4. Second ring (8 circles), radius closer to edge, further angle offset
    ring2_r = 0.412
    for i in range(7):
        a = (2*np.pi*i)/7 + np.pi/7
        centers[22+i] = [0.5 + ring2_r * np.cos(a), 0.5 + ring2_r * np.sin(a)]

    # 5. Place one extra circle in the most open slot (bottom-right, not corner or edge)
    # This location tends to be available after two rings.
    centers[29-3] = [0.775, 0.225] + rng.uniform(-0.011, 0.011, 2)
    centers = np.clip(centers, 0.012, 0.988)

    # 6. Local repulsion & greedy radii maximization with annealing shake + more steps
    centers, radii = local_relax_and_grow(centers, steps=18, anneal_shake=True, rng=rng)

    return centers, radii

def local_relax_and_grow(centers, steps=8, anneal_shake=False, rng=None):
    """
    Given circle centers, iteratively relax positions to reduce overlaps and edge collisions,
    and greedily maximize radii.
    If anneal_shake is True, add decaying random noise to help escape local minima.
    Returns final (centers, radii)
    """
    n = centers.shape[0]
    # Slightly smaller initial radii for better initial movement
    radii = np.ones(n) * 0.067
    if rng is None:
        rng = np.random.default_rng(seed=12345)

    for step in range(steps):
        # 1. Compute repulsive forces (from overlaps and boundary)
        disp = np.zeros_like(centers)
        for i in range(n):
            xi, yi = centers[i]
            # Repel from boundaries if close
            margin = 0.012
            force = np.zeros(2)
            if xi < margin:
                force[0] += (margin - xi) * 2.2
            if xi > 1-margin:
                force[0] -= (xi - (1-margin)) * 2.2
            if yi < margin:
                force[1] += (margin - yi) * 2.2
            if yi > 1-margin:
                force[1] -= (yi - (1-margin)) * 2.2
            # Repel from other circles if overlap (using current radii)
            for j in range(n):
                if i == j: continue
                dx, dy = centers[i] - centers[j]
                dist = np.hypot(dx, dy)
                if dist < 1e-7:  # avoid divide by zero
                    force += rng.normal(0, 0.001, 2)
                    continue
                minsep = radii[i] + radii[j]
                if dist < minsep * 1.011:  # tighter slack, encourage compaction
                    push = ((minsep - dist) / dist) * np.array([dx, dy]) * 0.62
                    force += push
            disp[i] = force

        # 2. Move centers by small fraction of displacement
        move = np.clip(disp, -0.033, 0.033)

        # 3. Annealing random shake: add small decaying random jitter (except for first/last step)
        if anneal_shake and (step > 2) and (step < steps-2):
            temp = 0.012 * (1 - step/(steps-1))
            shake = rng.normal(0, temp, centers.shape)
            move += shake

        centers += move

        # 4. Clamp back inside unit square
        centers = np.clip(centers, 0.013, 0.987)

        # 5. Greedily maximize radii
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