# EVOLVE-BLOCK-START
"""Constructor-based circle packing for n=26 circles"""

import numpy as np


def construct_packing():
    """
    Construct a specific arrangement of 26 circles in a unit square
    that attempts to maximize the sum of their radii.

    Returns:
        Tuple of (centers, radii, sum_of_radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26) with radius of each circle
        sum_of_radii: Sum of all radii
    """
    # Initialize arrays for 26 circles
    n = 26
    centers = np.zeros((n, 2))
    # RNG for deterministic jitter in ring placements
    rng = np.random.RandomState(42)

    # Place circles in a structured pattern
    # This is a simple pattern - evolution will improve this

    # Define radii for a centered large circle and smaller surrounding circles
    radii_pattern = np.array([
        0.2,  # Center large circle
        0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,  # 8 smaller circles around center
        0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05,  # 8 even smaller at outer ring
        0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03, 0.03  # 8 smallest at outermost ring
    ])

    # Assign centers based on radii, positioning larger at center
    centers[0] = [0.5, 0.5]

    # Parameter sweep for three concentric rings
    best_sum = 0.0
    best_centers = None
    for ring1 in [0.38, 0.40, 0.42]:
        for ring2 in [0.58, 0.60, 0.62]:
            for ring3 in [0.78, 0.80, 0.82]:
                temp_centers = np.zeros((n, 2))
                temp_centers[0] = [0.5, 0.5]
                # inner ring
                for i in range(8):
                    a = 2 * np.pi * i / 8
                    temp_centers[i + 1] = [0.5 + ring1 * np.cos(a), 0.5 + ring1 * np.sin(a)]
                # middle ring with offset
                for i in range(8):
                    a = 2 * np.pi * i / 8 + np.pi / 8
                    temp_centers[i + 9] = [0.5 + ring2 * np.cos(a), 0.5 + ring2 * np.sin(a)]
                # outer ring with another offset
                for i in range(8):
                    a = 2 * np.pi * i / 8 + np.pi / 4
                    temp_centers[i + 17] = [0.5 + ring3 * np.cos(a), 0.5 + ring3 * np.sin(a)]
                temp_centers = np.clip(temp_centers, 0.01, 0.99)
                temp_radii = compute_max_radii(temp_centers)
                s = np.sum(temp_radii)
                if s > best_sum:
                    best_sum = s
                    best_centers = temp_centers
    # Adopt the best configuration found
    centers = best_centers
    # Ensure still within unit square
    centers = np.clip(centers, 0.01, 0.99)

    # Compute maximum valid radii for this configuration
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

    # First, limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        # Distance to borders
        radii[i] = min(x, y, 1 - x, 1 - y)

    # Then, iteratively limit by distance to other circles
    # Perform multiple passes for more accurate radii
    max_iter = 5
    for _ in range(max_iter):
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
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