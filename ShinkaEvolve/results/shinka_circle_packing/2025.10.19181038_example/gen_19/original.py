# EVOLVE-BLOCK-START
"""Hybrid arrangement with center-edge-corner gradient for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Improved: Hybrid arrangement for 26 circles using center, edge/corner, a jittered inner grid,
    and an adaptive elliptical outer ring to break symmetry and local crowding.

    Returns:
        Tuple of (centers, radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26) with radius of each circle
    """
    n = 26
    centers = np.zeros((n, 2))
    idx = 0

    # 0: Main center
    centers[idx] = [0.5, 0.5]
    idx += 1

    # 1-4: edge centers (midpoints of edges)
    edge_eps = 0.035
    centers[idx] = [0.5, edge_eps]
    idx += 1
    centers[idx] = [1 - edge_eps, 0.5]
    idx += 1
    centers[idx] = [0.5, 1 - edge_eps]
    idx += 1
    centers[idx] = [edge_eps, 0.5]
    idx += 1

    # 5-8: corners (inset)
    crn = 0.035
    centers[idx] = [crn, crn]
    idx += 1
    centers[idx] = [1 - crn, crn]
    idx += 1
    centers[idx] = [1 - crn, 1 - crn]
    idx += 1
    centers[idx] = [crn, 1 - crn]
    idx += 1

    # 9-17 (9): jittered 3x3 grid (excluding center) for the inner region
    grid_N = 3
    grid_lo = 0.28
    grid_hi = 0.72
    grid_pts = np.linspace(grid_lo, grid_hi, grid_N)
    for i in range(grid_N):
        for j in range(grid_N):
            if i == 1 and j == 1:
                continue  # center already placed
            # Small jitter per point to break symmetry and help radii
            dx = 0.012 * np.sin(i + 2.3 * j)
            dy = 0.012 * np.cos(j + 1.7 * i)
            pt = [grid_pts[i] + dx, grid_pts[j] + dy]
            centers[idx] = pt
            idx += 1

    # 18-25 (8): adaptive outer elliptical ring (longer along diagonal)
    ring_N = n - idx
    outer_a = 0.435
    outer_b = 0.395
    angle_jitter = 0.16
    for i in range(ring_N):
        theta = 2 * np.pi * i / ring_N + 0.13 * np.sin(1.8*i)
        r = outer_a * outer_b / np.sqrt((outer_b * np.cos(theta))**2 + (outer_a * np.sin(theta))**2)
        r *= 1.0 + 0.022 * np.sin(2 * theta + 2.1 * i)
        x = 0.5 + r * np.cos(theta)
        y = 0.5 + r * np.sin(theta)
        # Slightly repel from corners and edges if too close
        for cpt in ([ [crn, crn], [1-crn, crn], [1-crn,1-crn], [crn,1-crn],
                      [0.5, edge_eps], [1-edge_eps,0.5], [0.5,1-edge_eps], [edge_eps,0.5] ]):
            vec = np.array([x,y]) - np.array(cpt)
            dist = np.linalg.norm(vec)
            if dist < 0.17:
                f = 0.012 * (0.17-dist)/0.17
                x += vec[0] * f
                y += vec[1] * f
        # Extra angular jitter to break symmetry
        x += 0.008 * np.sin(2 * i + 0.9)
        y += 0.008 * np.cos(2 * i + 1.7)
        x = np.clip(x, 0.018, 0.982)
        y = np.clip(y, 0.018, 0.982)
        centers[idx] = [x, y]
        idx += 1

    assert idx == n

    # Compute maximal radii
    radii = compute_max_radii_iterative(centers)
    return centers, radii

def compute_max_radii_iterative(centers, max_iters=50, tol=1e-8):
    """
    Iteratively compute maximal radii so that circles don't overlap or exit the unit square.
    Uses a pairwise min procedure and iterative tightening.

    Args:
        centers: np.array (n, 2)
        max_iters: int, number of iterations for tightening
        tol: convergence tolerance

    Returns:
        radii: np.array (n,)
    """
    n = centers.shape[0]
    radii = np.ones(n)
    # Border constraint
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1-x, 1-y)
    # Iterative tightening for overlaps
    for _ in range(max_iters):
        prev = radii.copy()
        for i in range(n):
            for j in range(i+1, n):
                dist = np.linalg.norm(centers[i]-centers[j])
                if dist < 1e-8:
                    # If two centers are coincident, force radii to nearly zero
                    radii[i] = min(radii[i], 1e-4)
                    radii[j] = min(radii[j], 1e-4)
                elif radii[i] + radii[j] > dist:
                    # Reduce both radii proportionally to avoid overlap
                    excess = (radii[i] + radii[j]) - dist
                    share = 0.5 * excess
                    radii[i] -= share
                    radii[j] -= share
                    radii[i] = max(radii[i], 1e-6)
                    radii[j] = max(radii[j], 1e-6)
        if np.max(np.abs(radii - prev)) < tol:
            break
    return radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii