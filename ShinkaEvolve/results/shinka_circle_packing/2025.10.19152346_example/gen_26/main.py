# EVOLVE-BLOCK-START
"""Adaptive edge-center hybrid circle packing for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Construct an adaptive arrangement of 26 circles in a unit square
    that attempts to maximize the sum of their radii.
    Returns:
        Tuple of (centers, radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26) with radius of each circle
    """
    n = 26
    centers = np.zeros((n, 2))
    radii = np.zeros(n)

    # Parameters
    edge_weight = 8
    corner_weight = 4
    center_weight = 6
    inner_ring_weight = 8
    perturb_scale = 0.012
    adaptive_iters = 18
    shrink_factor = 0.98

    # 1. Place 4 large circles near corners
    corner_pos = [
        [0.08, 0.08],
        [0.92, 0.08],
        [0.92, 0.92],
        [0.08, 0.92]
    ]
    for i in range(corner_weight):
        centers[i] = corner_pos[i]
        radii[i] = 0.08

    # 2. Place 8 circles along edges (not at corners)
    edge_offsets = np.linspace(0.22, 0.78, edge_weight//2)
    idx = corner_weight
    for x in edge_offsets:
        centers[idx] = [x, 0.04]
        centers[idx+1] = [x, 0.96]
        radii[idx] = radii[idx+1] = 0.06
        idx += 2

    # 3. Place 6 circles in the center region (hex pattern)
    center_hex = [
        [0.5, 0.5],
        [0.5+0.14, 0.5],
        [0.5-0.14, 0.5],
        [0.5, 0.5+0.14],
        [0.5, 0.5-0.14],
        [0.5+0.095, 0.5+0.095]
    ]
    for i in range(center_weight):
        centers[idx] = center_hex[i]
        radii[idx] = 0.10
        idx += 1

    # 4. Place 8 circles in an inner ring
    ring_r = 0.33
    for i in range(inner_ring_weight):
        angle = 2 * np.pi * i / inner_ring_weight
        centers[idx] = [0.5 + ring_r * np.cos(angle), 0.5 + ring_r * np.sin(angle)]
        radii[idx] = 0.07
        idx += 1

    # Compute adaptive initial radii based on spacing
    initial_shrink = 0.9
    radii = compute_max_radii(centers) * initial_shrink

    # 5. Small random perturbations to break symmetry
    centers += np.random.uniform(-perturb_scale, perturb_scale, centers.shape)
    centers = np.clip(centers, 0.01, 0.99)

    # 6. Adaptive local optimization
    prev_sum = 0.0
    for it in range(adaptive_iters):
        # Recompute radii to maximize size without overlap or boundary violation
        radii = compute_max_radii(centers)
        curr_sum = np.sum(radii)

        # Early stopping if improvement is negligible
        if abs(curr_sum - prev_sum) < 1e-5:
            break
        prev_sum = curr_sum

        # Calculate total overlap to consider early stopping
        total_overlap = 0.0
        for i in range(n):
            for j in range(i+1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                overlap = max(0.0, radii[i] + radii[j] - dist)
                total_overlap += overlap
        if total_overlap < 1e-4:
            break

        # Nudge centers away from overlaps and boundaries
        overlaps_per_circle = np.zeros(n)
        for i in range(n):
            grad = np.zeros(2)
            # Boundary repulsion
            for d in range(2):
                if centers[i, d] - radii[i] < 0.0:
                    grad[d] += (0.01 - (centers[i, d] - radii[i])) * 0.5
                if centers[i, d] + radii[i] > 1.0:
                    grad[d] -= ((centers[i, d] + radii[i]) - 0.99) * 0.5
            # Overlap repulsion
            for j in range(n):
                if i == j:
                    continue
                dist = np.linalg.norm(centers[i] - centers[j])
                min_dist = radii[i] + radii[j]
                if dist < min_dist - 1e-6:
                    overlaps_per_circle[i] += 1
                    if dist > 1e-8:
                        grad += (centers[i] - centers[j]) / dist * (min_dist - dist) * 0.15
                    else:
                        grad += np.random.uniform(-1, 1, 2) * 0.01
            # Apply small step
            centers[i] += grad * 0.25
        # Clip to square
        centers = np.clip(centers, 0.01, 0.99)

        # Adaptive per-circle shrink factor based on overlaps count
        for i in range(n):
            if overlaps_per_circle[i] > 0:
                factor = shrink_factor ** overlaps_per_circle[i]
                radii[i] *= factor

    # Final radii computation
    radii = compute_max_radii(centers)

    # --- Global random shake-up step ---
    # Randomly select 3 circles, reposition, and re-optimize locally
    n_shake = 3
    shake_indices = np.random.choice(n, n_shake, replace=False)
    for idx in shake_indices:
        # Randomly reposition within feasible region (avoid borders)
        centers[idx] = np.random.uniform(0.08, 0.92, 2)
    # Brief local optimization after shake-up
    shake_iters = 6
    for it in range(shake_iters):
        radii = compute_max_radii(centers)
        for i in range(n):
            grad = np.zeros(2)
            for d in range(2):
                if centers[i, d] - radii[i] < 0.0:
                    grad[d] += (0.01 - (centers[i, d] - radii[i])) * 0.5
                if centers[i, d] + radii[i] > 1.0:
                    grad[d] -= ((centers[i, d] + radii[i]) - 0.99) * 0.5
            for j in range(n):
                if i == j:
                    continue
                dist = np.linalg.norm(centers[i] - centers[j])
                min_dist = radii[i] + radii[j]
                if dist < min_dist - 1e-6:
                    if dist > 1e-8:
                        grad += (centers[i] - centers[j]) / dist * (min_dist - dist) * 0.15
                    else:
                        grad += np.random.uniform(-1, 1, 2) * 0.01
            centers[i] += grad * 0.25
        centers = np.clip(centers, 0.01, 0.99)
        # Shrink radii if overlaps
        for i in range(n):
            for j in range(i+1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                if dist < radii[i] + radii[j] - 1e-6:
                    radii[i] *= shrink_factor
                    radii[j] *= shrink_factor

    # Final radii computation after shake-up
    radii = compute_max_radii(centers)
    return centers, radii

def compute_max_radii(centers):
    """
    Compute the maximum possible radii for each circle position
    such that they don't overlap and stay within the unit square.
    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates
    Returns:
        np.array of shape (n) with radius of each circle
    """
    n = centers.shape[0]
    radii = np.ones(n)
    # Limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)
    # Limit by distance to other circles
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.linalg.norm(centers[i] - centers[j])
            if dist < 1e-8:
                continue
            max_r = dist / 2.0
            if radii[i] > max_r:
                radii[i] = max_r
            if radii[j] > max_r:
                radii[j] = max_r
    return radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii