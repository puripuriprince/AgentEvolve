# EVOLVE-BLOCK-START
"""Layered forced-symmetry gradient circle packing for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Construct a maximized sum-of-radii packing of 26 circles in a unit square
    using layered, symmetry-forced, gradient and local repulsion ideas.

    Returns:
        centers: np.array of shape (26, 2)
        radii: np.array of shape (26,)
    """
    n = 26
    centers = np.zeros((n, 2))

    # Layer assignment:
    # 0: Center
    # 1-6: Inner hexagon ring (6)
    # 7-18: Outer dodecagon ring (12)
    # 19-22: Edge-centers (4)
    # 23-26: Corners (4)

    # --- Central circle ---
    centers[0] = [0.5, 0.5]

    # --- Inner ring (hexagon, radius r1) ---
    # r1 = 0.23 ensures separation from center and outer
    r1 = 0.23
    for i in range(6):
        angle = 2*np.pi*i/6
        centers[1+i] = [0.5 + r1*np.cos(angle), 0.5 + r1*np.sin(angle)]

    # --- Outer ring (dodecagon, radius r2) ---
    r2 = 0.42
    outer_angle_offset = np.pi/12  # slight rotation for better edge coverage
    for i in range(12):
        angle = 2*np.pi*i/12 + outer_angle_offset
        centers[7+i] = [0.5 + r2*np.cos(angle), 0.5 + r2*np.sin(angle)]

    # --- Edge-centers (inset slightly to allow larger radii) ---
    edge_inset = 0.062
    centers[19] = [0.5, edge_inset]
    centers[20] = [1-edge_inset, 0.5]
    centers[21] = [0.5, 1-edge_inset]
    centers[22] = [edge_inset, 0.5]

    # --- Corners (inset for larger radii) ---
    corner_inset = 0.061
    centers[23] = [corner_inset, corner_inset]
    centers[24] = [1-corner_inset, corner_inset]
    centers[25] = [1-corner_inset, 1-corner_inset]
    centers[26-1] = [corner_inset, 1-corner_inset]

    # --- Local repulsion refinement (mini-optimization) ---
    # Only nudge outer, edge, and corner circles, not the center or inner ring (structural backbone)
    movable = np.array([False]*7 + [True]*12 + [True]*4 + [True]*4)
    repulse_iters = 8
    repulse_eps = 1e-3
    for _ in range(repulse_iters):
        for i in range(n):
            if not movable[i]:
                continue
            dxy = np.zeros(2)
            for j in range(n):
                if i == j:
                    continue
                delta = centers[i] - centers[j]
                dist = np.linalg.norm(delta)
                if dist < 1e-8:
                    dxy += np.random.randn(2)*1e-3
                elif dist < 0.07:
                    # Strong repulsion for near-coincident
                    dxy += delta / (dist+1e-6) * 0.013
                elif dist < 0.18:
                    # Moderate repulsion
                    dxy += delta / dist * 0.004
            # Bias to stay in the square
            for d in range(2):
                if centers[i][d] < 0.015:
                    dxy[d] += 0.01
                if centers[i][d] > 0.985:
                    dxy[d] -= 0.01
            centers[i] += dxy
        # Clamp to square (with inset)
        centers = np.clip(centers, 0.013, 0.987)

    # --- Compute radii gradient ---
    # Center gets largest, inner ring next, outer ring/edges/corners smallest (but not too small)
    radii = np.zeros(n)
    # Borders: stay within square
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1-x, 1-y)
    # Pairwise overlap constraint: iteratively shrink if needed
    for _ in range(38):
        prev = radii.copy()
        for i in range(n):
            for j in range(i+1, n):
                dist = np.linalg.norm(centers[i]-centers[j])
                if dist < 1e-8:
                    radii[i] = min(radii[i], 1e-4)
                    radii[j] = min(radii[j], 1e-4)
                elif radii[i] + radii[j] > dist:
                    excess = (radii[i] + radii[j]) - dist
                    share = 0.5*excess
                    radii[i] -= share
                    radii[j] -= share
                    radii[i] = max(radii[i], 1e-6)
                    radii[j] = max(radii[j], 1e-6)
        if np.max(np.abs(radii-prev)) < 1e-8:
            break

    return centers, radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii