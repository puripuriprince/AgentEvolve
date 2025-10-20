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
    # 1-6: First ring (hexagon, 6)
    # 7-14: Second ring (octagon, 8)
    # 15-22: Third ring (octagon, 8)
    # 23-24: Edge centers (2)
    # 25: One corner (1)  (remaining corners omitted for less crowding)

    # --- Central circle ---
    centers[0] = [0.5, 0.5]

    # --- First ring (hexagon, radius r1) ---
    r1 = 0.185
    for i in range(6):
        angle = 2*np.pi*i/6 + np.pi/12
        centers[1+i] = [0.5 + r1*np.cos(angle), 0.5 + r1*np.sin(angle)]

    # --- Second ring (octagon, radius r2, angular offset) ---
    r2 = 0.295
    for i in range(8):
        angle = 2*np.pi*i/8
        centers[7+i] = [0.5 + r2*np.cos(angle), 0.5 + r2*np.sin(angle)]

    # --- Third ring (octagon, radius r3, staggered offset) ---
    r3 = 0.41
    angle_offset3 = np.pi/8
    for i in range(8):
        angle = 2*np.pi*i/8 + angle_offset3
        centers[15+i] = [0.5 + r3*np.cos(angle), 0.5 + r3*np.sin(angle)]

    # --- Edge-centers (inset for larger radii) ---
    edge_inset = 0.08
    centers[23] = [0.5, edge_inset]
    centers[24] = [0.5, 1-edge_inset]

    # --- Single corner (most favorable) ---
    corner_inset = 0.07
    centers[25] = [corner_inset, corner_inset]

    # --- Local repulsion refinement (mini-optimization) ---
    # Only nudge outer two rings, edge, and corner circles, not the center or first ring (structural backbone)
    movable = np.array([False]*7 + [True]*8 + [True]*8 + [True]*2 + [True])
    repulse_iters = 18
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
                elif dist < 0.06:
                    # Strong repulsion for near-coincident
                    dxy += delta / (dist+1e-6) * 0.016
                elif dist < 0.16:
                    # Moderate repulsion
                    dxy += delta / dist * 0.007
            # Bias to stay in the square
            for d in range(2):
                if centers[i][d] < 0.012:
                    dxy[d] += 0.014
                if centers[i][d] > 0.988:
                    dxy[d] -= 0.014
            centers[i] += dxy
        # Clamp to square (with inset)
        centers = np.clip(centers, 0.012, 0.988)

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