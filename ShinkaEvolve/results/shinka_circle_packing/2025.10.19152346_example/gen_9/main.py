# EVOLVE-BLOCK-START
# EVOLVE-BLOCK-START
"""Enhanced hybrid variable-sized circle packing for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Construct a hybrid arrangement of 26 circles in a unit square,
    optimizing the sum of radii by strategic placement and sizing.
    """
    n = 26
    centers = np.zeros((n, 2))
    radii = np.zeros(n)

    # Place central large circle
    centers[0] = [0.5, 0.5]
    radii[0] = 0.2  # large center circle

    # Define concentric rings with decreasing radii
    rings = [
        {'radius': 0.4, 'count': 8, 'radius_scale': 0.1},
        {'radius': 0.6, 'count': 8, 'radius_scale': 0.05},
        {'radius': 0.8, 'count': 8, 'radius_scale': 0.03}
    ]

    index = 1
    for ring in rings:
        r_center = ring['radius']
        r_circle = ring['radius_scale']
        for i in range(ring['count']):
            angle = 2 * np.pi * i / ring['count']
            centers[index] = [
                0.5 + r_center * np.cos(angle),
                0.5 + r_center * np.sin(angle)
            ]
            radii[index] = r_circle
            index += 1

    # Place corner and edge circles with smaller sizes
    corner_positions = [
        [0.1, 0.1], [0.9, 0.1], [0.1, 0.9], [0.9, 0.9],
        [0.5, 0.05], [0.95, 0.5], [0.5, 0.95], [0.05, 0.5]
    ]
    corner_radii = [0.03, 0.03, 0.03, 0.03, 0.02, 0.02, 0.02, 0.02]

    for i, pos in enumerate(corner_positions):
        centers[index] = pos
        radii[index] = corner_radii[i]
        index += 1

    # Clip centers to stay within bounds
    centers = np.clip(centers, 0.01, 0.99)

    # Compute maximum radii considering overlaps
    radii = compute_max_radii(centers, radii)
    return centers, radii

def compute_max_radii(centers, initial_radii):
    """
    Adjust radii to prevent overlaps and stay within the square.
    """
    n = centers.shape[0]
    radii = initial_radii.copy()

    # Limit by distance to borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(radii[i], x, y, 1 - x, 1 - y)

    # Iteratively refine radii to avoid overlaps
    for _ in range(3):  # multiple passes for better packing
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                if dist < radii[i] + radii[j]:
                    # Reduce radii proportionally
                    overlap = radii[i] + radii[j]
                    scale = dist / overlap
                    radii[i] *= scale
                    radii[j] *= scale
                    # Ensure radii do not become too small
                    radii[i] = max(radii[i], 0.005)
                    radii[j] = max(radii[j], 0.005)
    return radii

# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii
# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii