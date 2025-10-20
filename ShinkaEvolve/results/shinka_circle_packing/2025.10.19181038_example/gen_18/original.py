# EVOLVE-BLOCK-START
"""Layered adaptive grid for improved 26-circle packing in a unit square."""

import numpy as np

def construct_packing():
    """
    Construct an arrangement of 26 circles in a unit square
    maximizing the sum of their radii, using a layered adaptive hybrid grid.

    Returns:
        Tuple of (centers, radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26) with radius of each circle
    """
    n = 26
    centers = np.zeros((n, 2))
    idx = 0

    # 1. Place circles at corners and edge centers (8 circles)
    # Corners
    corner_eps = 0.015
    corners = [
        [corner_eps, corner_eps],
        [1 - corner_eps, corner_eps],
        [1 - corner_eps, 1 - corner_eps],
        [corner_eps, 1 - corner_eps]
    ]
    for c in corners:
        centers[idx] = c
        idx += 1
    # Edge centers
    edge_eps = 0.025
    edge_centers = [
        [0.5, edge_eps],
        [1 - edge_eps, 0.5],
        [0.5, 1 - edge_eps],
        [edge_eps, 0.5]
    ]
    for c in edge_centers:
        centers[idx] = c
        idx += 1

    # 2. Central 3x3 adaptive grid (9 circles)
    grid_N = 3
    grid_start = 0.32
    grid_stop = 0.68
    grid_pts = np.linspace(grid_start, grid_stop, grid_N)
    center_grid = []
    for i in range(grid_N):
        for j in range(grid_N):
            # Slightly jitter grid points to break symmetry and allow better radii
            jitter = 0.012 * np.array([np.random.uniform(-1,1), np.random.uniform(-1,1)])
            pt = [grid_pts[i], grid_pts[j]]
            pt_jit = np.clip(np.array(pt) + jitter, 0.1, 0.9)
            center_grid.append(pt_jit)
    # Place these 9
    for pt in center_grid:
        centers[idx] = pt
        idx += 1

    # 3. Adaptive non-uniform outer ring (9 circles)
    # Distribute with variable radius and angle to avoid edge/corner crowding
    ring_radii = np.linspace(0.38, 0.46, 9)  # Variable radius for slight spreading
    ring_angles = np.linspace(0, 2 * np.pi, 9, endpoint=False)
    for i in range(9):
        r = ring_radii[i]
        angle = ring_angles[i] + 0.13 * np.sin(i)
        # Squeeze away from corners by a factor depending on angle
        x = 0.5 + r * np.cos(angle)
        y = 0.5 + r * np.sin(angle)
        # Perturb slightly to break symmetry
        x += 0.02 * np.sin(2*angle)
        y += 0.02 * np.cos(3*angle)
        x = np.clip(x, 0.09, 0.91)
        y = np.clip(y, 0.09, 0.91)
        centers[idx] = [x, y]
        idx += 1

    assert idx == n

    # Compute maximum valid radii for this configuration
    radii = compute_max_radii_greedy(centers)
    return centers, radii


def compute_max_radii_greedy(centers, passes=3):
    """
    Compute the maximum possible radii for each circle position
    using a greedy pass with repeated overlap resolution.

    Args:
        centers: np.array of shape (n, 2) with (x, y) coordinates
        passes: how many times to sweep through all pairs to resolve conflicts

    Returns:
        np.array of shape (n) with radius of each circle
    """
    n = centers.shape[0]
    radii = np.ones(n)

    # Initial: limit by distance to borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)

    # Iteratively resolve pairwise overlaps (greedy, a few passes)
    for _ in range(passes):
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if radii[i] + radii[j] > d:
                    # Shrink both proportionally so sum = d
                    if d > 1e-12:
                        scale = d / (radii[i] + radii[j])
                        radii[i] *= scale
                        radii[j] *= scale
                    else:
                        # Coincident centers: set both radii to zero
                        radii[i] = 0
                        radii[j] = 0

    # Final: local radius boost (try to maximize each circle individually)
    for i in range(n):
        # Find min distance to border
        x, y = centers[i]
        border = min(x, y, 1 - x, 1 - y)
        # Find min distance to any other center minus that circle's radius
        min_dist = border
        for j in range(n):
            if i == j: continue
            d = np.linalg.norm(centers[i] - centers[j]) - radii[j]
            min_dist = min(min_dist, d)
        radii[i] = max(0, min_dist)
    return radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii