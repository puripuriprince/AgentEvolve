# EVOLVE-BLOCK-START
"""Hierarchical honeycomb with privileged edge/corner and adaptive repulsion for 26-circle packing."""

import numpy as np

def construct_packing():
    """
    Construct an arrangement of 26 circles in a unit square maximizing the sum of radii.
    Returns:
        centers: np.array of shape (26, 2)
        radii: np.array of shape (26,)
    """
    n = 26
    centers = np.zeros((n, 2))
    idx = 0

    # 1. Place 4 corners and 4 edge centers — these will be larger
    margin = 0.016
    edge_margin = 0.032
    corners = [
        [margin, margin],
        [1 - margin, margin],
        [1 - margin, 1 - margin],
        [margin, 1 - margin]
    ]
    for c in corners:
        centers[idx] = c
        idx += 1
    edges = [
        [0.5, edge_margin],
        [1 - edge_margin, 0.5],
        [0.5, 1 - edge_margin],
        [edge_margin, 0.5]
    ]
    for c in edges:
        centers[idx] = c
        idx += 1

    # 2. Place a central circle
    centers[idx] = [0.5, 0.5]
    idx += 1

    # 3. Place a 3x4 adaptive grid in the central region (12 circles)
    # The grid will be slightly compressed toward the center to avoid edge crowding
    grid_rows, grid_cols = 3, 4
    grid_x = np.linspace(0.28, 0.72, grid_cols)
    grid_y = np.linspace(0.28, 0.72, grid_rows)
    grid_jitter = 0.012
    center_pt = [0.5, 0.5]
    grid_pts = []
    for i, y in enumerate(grid_y):
        for j, x in enumerate(grid_x):
            # Small random jitter to avoid perfect alignment and promote larger radii
            dx = grid_jitter * np.sin(i + 2.1 * j)
            dy = grid_jitter * np.cos(j + 1.5 * i)
            pt = [x + dx, y + dy]
            # Avoid the precise center (already placed)
            if np.linalg.norm(np.array(pt) - center_pt) < 0.08:
                continue
            grid_pts.append(pt)
    for pt in grid_pts:
        centers[idx] = pt
        idx += 1

    # 4. Place remaining circles (6) in an adaptive outer ring
    num_outer = n - idx
    ring_base_r = 0.41
    ring_spread = 0.04
    ring_theta = np.linspace(0, 2*np.pi, num_outer, endpoint=False)
    for ii in range(num_outer):
        # Vary radius so that points are not all equidistant from center
        r = ring_base_r + ring_spread * np.sin(2 * ring_theta[ii] + ii)
        theta = ring_theta[ii] + 0.18 * np.cos(3 * ii)
        x = 0.5 + r * np.cos(theta)
        y = 0.5 + r * np.sin(theta)
        # Repulsion from corners and edge-centers
        repulse = np.zeros(2)
        for c in corners + edges:
            vec = np.array([x, y]) - np.array(c)
            dist = np.linalg.norm(vec)
            if dist < 0.20:
                repulse += (vec / (dist + 1e-10)) * (0.022 / (dist + 0.022))
        x += repulse[0]
        y += repulse[1]
        # Angular jitter to break symmetry and avoid repeats
        x += 0.014 * np.sin(2 * ii + 0.5)
        y += 0.014 * np.cos(2 * ii + 0.9)
        x = np.clip(x, 0.07, 0.93)
        y = np.clip(y, 0.07, 0.93)
        centers[idx] = [x, y]
        idx += 1

    assert idx == n

    # 5. Local adaptive repulsion for interior grid points from corners/edges
    # (push away if too close)
    grid_start = 8
    grid_end = 8 + len(grid_pts)
    interior_idx = list(range(grid_start, grid_end))
    special_idx = list(range(0,8))
    for k in interior_idx:
        for j in special_idx:
            d = np.linalg.norm(centers[k] - centers[j])
            if d < 0.18:
                push_vec = (centers[k] - centers[j])
                if np.linalg.norm(push_vec) > 0:
                    push_vec = push_vec / np.linalg.norm(push_vec)
                    centers[k] += 0.016 * push_vec

    # 6. Iterative max-min radii update
    radii = maximize_radii_iterative(centers, passes=6)
    return centers, radii

def maximize_radii_iterative(centers, passes=5):
    """
    Iteratively maximize each circle's radius given others' positions and radii.
    Each pass, maximize for each circle in turn.
    """
    n = centers.shape[0]
    radii = np.ones(n)
    # Initial: border-limited
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)
    for _ in range(passes):
        for i in range(n):
            # For each other circle, the distance minus its radius is a limit
            min_r = min(centers[i][0], centers[i][1], 1 - centers[i][0], 1 - centers[i][1])
            for j in range(n):
                if i == j: continue
                d = np.linalg.norm(centers[i] - centers[j])
                min_r = min(min_r, d - radii[j])
            radii[i] = max(min_r, 0)
    return radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii