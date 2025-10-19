# EVOLVE-BLOCK-START
"""Hybrid density-based init + local optimization for n=26 circle packing"""

import numpy as np

def construct_packing():
    """
    Construct a hybrid arrangement of 26 circles in a unit square
    that attempts to maximize the sum of their radii.

    Returns:
        Tuple of (centers, radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26) with radius of each circle
    """
    n = 26
    centers = np.zeros((n, 2))

    # 1. Strategic placement: center, corners, edge-centers, and two staggered rings
    idx = 0
    # Center
    centers[idx] = [0.5, 0.5]; idx += 1
    # Corners
    pad = 0.04
    for x in [pad, 1-pad]:
        for y in [pad, 1-pad]:
            centers[idx] = [x, y]; idx += 1
    # Edge centers
    edge_pad = 0.04
    for x, y in [(0.5, edge_pad), (0.5, 1-edge_pad), (edge_pad, 0.5), (1-edge_pad, 0.5)]:
        centers[idx] = [x, y]; idx += 1
    # First ring (8 points, radius ~0.28)
    r1 = 0.28
    for i in range(8):
        angle = 2 * np.pi * i / 8
        centers[idx] = [0.5 + r1 * np.cos(angle), 0.5 + r1 * np.sin(angle)]
        idx += 1
    # Second ring (8 points, radius ~0.62, offset for staggering)
    r2 = 0.62
    for i in range(8):
        angle = 2 * np.pi * (i + 0.5) / 8
        centers[idx] = [0.5 + r2 * np.cos(angle), 0.5 + r2 * np.sin(angle)]
        idx += 1
    assert idx == n

    # 2. Estimate local available space for each circle (nearest neighbor, border)
    dists = np.full(n, np.inf)
    for i in range(n):
        # Distance to border
        x, y = centers[i]
        border_dist = min(x, y, 1-x, 1-y)
        # Distance to nearest other center
        for j in range(n):
            if i == j: continue
            d = np.linalg.norm(centers[i] - centers[j])
            if d < dists[i]:
                dists[i] = d
        dists[i] = min(dists[i], 2*border_dist)
    # Assign initial radii as a fraction of local available space
    radii = 0.49 * dists

    # 3. Local greedy optimization: try to move circles to maximize their radii
    np.random.seed(42)
    for step in range(40):
        order = np.random.permutation(n)
        for i in order:
            best_center = centers[i].copy()
            best_radius = compute_one_max_radius(i, centers, radii)
            # Try small moves in 8 directions
            for dtheta in np.linspace(0, 2*np.pi, 8, endpoint=False):
                delta = 0.015 * np.array([np.cos(dtheta), np.sin(dtheta)])
                new_center = centers[i] + delta
                # Stay inside square
                if not (0.01 <= new_center[0] <= 0.99 and 0.01 <= new_center[1] <= 0.99):
                    continue
                centers[i] = new_center
                r = compute_one_max_radius(i, centers, radii)
                if r > best_radius:
                    best_center = new_center.copy()
                    best_radius = r
            centers[i] = best_center
            radii[i] = best_radius

    # Final adjustment: ensure all radii are valid for the final config
    radii = compute_max_radii(centers)
    return centers, radii

def compute_one_max_radius(i, centers, radii):
    """Compute the largest possible radius for circle i given others and the square."""
    x, y = centers[i]
    # Border
    r = min(x, y, 1-x, 1-y)
    # Other circles
    for j in range(centers.shape[0]):
        if i == j:
            continue
        d = np.linalg.norm(centers[i] - centers[j])
        r = min(r, d - radii[j] if d > radii[j] else 0)
    return max(r, 0.0)

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
        radii[i] = min(x, y, 1-x, 1-y)
    # Limit by distance to other circles
    for i in range(n):
        for j in range(i+1, n):
            dist = np.linalg.norm(centers[i] - centers[j])
            if radii[i] + radii[j] > dist:
                scale = dist / (radii[i] + radii[j])
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