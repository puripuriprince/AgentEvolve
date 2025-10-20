# EVOLVE-BLOCK-START
"""Radial spiral gradient packing with local relaxation for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Construct an arrangement of 26 circles in a unit square using a spiral gradient
    and a local relaxation step to maximize the sum of radii.
    Returns:
        centers: np.array (26, 2)
        radii: np.array (26,)
    """
    n = 26
    centers = np.zeros((n, 2))

    # --- 1. Strategic fixed placements: center, corners, edge centers ---
    centers[0] = [0.5, 0.5]  # center
    corners = [
        [0.06, 0.06], [0.94, 0.06], [0.94, 0.94], [0.06, 0.94]
    ]
    for i in range(4):
        centers[1+i] = corners[i]
    edge_centers = [
        [0.5, 0.045], [0.955, 0.5], [0.5, 0.955], [0.045, 0.5]
    ]
    for i in range(4):
        centers[5+i] = edge_centers[i]

    # --- 2. Place remaining 17 circles along an Archimedean spiral ---
    spiral_n = n - 9
    theta0 = np.pi/8  # avoid overlap with axes
    # Spiral goes from r_min (near center) to r_max (nearly to edges)
    r_min = 0.19
    r_max = 0.43
    for i in range(spiral_n):
        frac = i / (spiral_n - 1)
        theta = theta0 + 2.5 * np.pi * frac  # about 1.25 turns
        r = r_min + frac**1.15 * (r_max - r_min)  # gentle outward gradient
        # Slight inward pull on a few points to avoid edge collisions
        x = 0.5 + r * np.cos(theta)
        y = 0.5 + r * np.sin(theta)
        # For very last spiral points, bias radially inward to avoid sharp corners
        if frac > 0.85:
            x = 0.5 + 0.98 * (x - 0.5)
            y = 0.5 + 0.98 * (y - 0.5)
        centers[9+i] = [x, y]

    # --- 3. Local relaxation for spiral points ---
    movable = np.zeros(n, dtype=bool)
    movable[9:] = True  # only spiral points move; center/corners/edges fixed

    for relax_iter in range(13):  # a few rounds of jitter/repulse
        for i in range(n):
            if not movable[i]:
                continue
            dxy = np.zeros(2)
            # Random small jitter to escape local minima
            dxy += np.random.uniform(-0.004, 0.004, size=2)
            # Repulsion from all other circles (stronger if closer)
            for j in range(n):
                if i == j: continue
                delta = centers[i] - centers[j]
                dist = np.linalg.norm(delta)
                if dist < 1e-8:
                    dxy += np.random.randn(2) * 0.001
                elif dist < 0.08:
                    dxy += 0.012 * delta / (dist + 1e-8)
                elif dist < 0.18:
                    dxy += 0.005 * delta / dist
            # Stay inside square
            for d in range(2):
                if centers[i][d] < 0.013:
                    dxy[d] += 0.01
                if centers[i][d] > 0.987:
                    dxy[d] -= 0.01
            centers[i] += dxy
            centers[i] = np.clip(centers[i], 0.013, 0.987)

    # --- 4. Compute maximal radii with iterative tightening ---
    radii = compute_max_radii_iterative(centers, max_iters=55, tol=1e-8)

    return centers, radii

def compute_max_radii_iterative(centers, max_iters=55, tol=1e-8):
    """
    Iteratively compute maximal radii so circles don't overlap or exit the unit square.
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
                dist = np.linalg.norm(centers[i] - centers[j])
                if dist < 1e-8:
                    radii[i] = min(radii[i], 1e-4)
                    radii[j] = min(radii[j], 1e-4)
                elif radii[i] + radii[j] > dist:
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