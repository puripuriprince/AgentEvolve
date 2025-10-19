# EVOLVE-BLOCK-START
"""Adaptive hybrid ring/corner/edge circle packing for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Construct an improved arrangement of 26 circles in a unit square
    that attempts to maximize the sum of their radii.

    Returns:
        Tuple of (centers, radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26) with radius of each circle
    """
    n = 26
    centers = np.zeros((n, 2))

    # 1. Place a large circle in the center
    centers[0] = [0.5, 0.5]

    # 2. Place 8 circles in an inner ring
    ring1 = 0.28
    for i in range(8):
        angle = 2 * np.pi * i / 8
        centers[1 + i] = [0.5 + ring1 * np.cos(angle), 0.5 + ring1 * np.sin(angle)]

    # 3. Place 12 circles in an outer ring
    ring2 = 0.65
    for i in range(12):
        angle = 2 * np.pi * i / 12
        centers[9 + i] = [0.5 + ring2 * np.cos(angle), 0.5 + ring2 * np.sin(angle)]

    # 4. Place 4 circles at the corners
    corners = np.array([[0.01, 0.01], [0.99, 0.01], [0.99, 0.99], [0.01, 0.99]])
    centers[21:25] = corners

    # 5. Place 1 circle at the center of a random edge (choose bottom edge for determinism)
    centers[25] = [0.5, 0.01]

    # Ensure all centers are within the unit square
    centers = np.clip(centers, 0.01, 0.99)

    # Compute adaptive initial radii
    radii = adaptive_max_radii(centers)

    # Local optimization: nudge circles away from overlaps and recompute radii
    for _ in range(4):
        centers = local_nudge(centers, radii)
        radii = adaptive_max_radii(centers)

    return centers, radii

def adaptive_max_radii(centers):
    """
    Compute the maximum possible radii for each circle position
    such that they don't overlap and stay within the unit square.
    Uses a more adaptive, iterative approach.
    """
    n = centers.shape[0]
    radii = np.ones(n)
    # Limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)
    # Limit by distance to other circles (with a small margin)
    for _ in range(2):  # Two passes for better convergence
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                if dist < 1e-8:
                    # Overlapping centers, shrink both
                    radii[i] *= 0.95
                    radii[j] *= 0.95
                elif radii[i] + radii[j] > dist - 1e-4:
                    # Shrink both radii slightly to avoid overlap
                    scale = (dist - 1e-4) / (radii[i] + radii[j])
                    scale = max(scale, 0.7)
                    radii[i] *= scale
                    radii[j] *= scale
    return radii

def local_nudge(centers, radii):
    """
    Nudge circles away from their nearest neighbor if overlap is detected.
    """
    n = centers.shape[0]
    new_centers = centers.copy()
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = np.linalg.norm(centers[i] - centers[j])
            min_dist = radii[i] + radii[j] + 1e-4
            if d < min_dist and d > 1e-8:
                # Move i away from j
                direction = (centers[i] - centers[j]) / d
                move_dist = (min_dist - d) * 0.55
                new_centers[i] += direction * move_dist
                # Keep within bounds
                new_centers[i] = np.clip(new_centers[i], 0.01, 0.99)
    return new_centers

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii