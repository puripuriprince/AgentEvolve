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

    # Place 8 circles around the center with slight random jitter
    for i in range(8):
        angle = 2 * np.pi * i / 8
        radius_dist = 0.4 + rng.uniform(-0.01, 0.01)  # perturbed distance to break symmetry
        centers[i + 1] = [0.5 + radius_dist * np.cos(angle), 0.5 + radius_dist * np.sin(angle)]

    # Place 8 more circles in a middle ring with jitter
    for i in range(8):
        angle = 2 * np.pi * i / 8
        radius_dist = 0.6 + rng.uniform(-0.015, 0.015)
        centers[i + 9] = [0.5 + radius_dist * np.cos(angle), 0.5 + radius_dist * np.sin(angle)]

    # Place 8 smallest circles at the outermost ring with jitter
    for i in range(8):
        angle = 2 * np.pi * i / 8
        radius_dist = 0.8 + rng.uniform(-0.02, 0.02)
        centers[i + 17] = [0.5 + radius_dist * np.cos(angle), 0.5 + radius_dist * np.sin(angle)]

    # Additional positioning adjustment to make sure all circles
    # are inside the square and don't overlap
    # Clip to ensure everything is inside the unit square
    centers = np.clip(centers, 0.01, 0.99)

    # Compute maximum valid radii for this configuration
    radii = compute_max_radii(centers)
    return centers, radii


def compute_max_radii(centers):
    """
    Compute the maximum possible radii for each circle position
    such that they don't overlap and stay within the unit square.
    Uses iterative refinement over sorted circle pairs for tighter packings.
    """
    n = centers.shape[0]
    radii = np.ones(n)

    # 1) Limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)

    # 2) Precompute all circle pairs with their center distances
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            d = np.hypot(*(centers[i] - centers[j]))
            pairs.append((d, i, j))
    # Sort by proximity: closest circles first
    pairs.sort(key=lambda t: t[0])

    # 3) Iteratively refine radii to resolve overlaps
    max_iter = 10
    for _ in range(max_iter):
        for d, i, j in pairs:
            if radii[i] + radii[j] > d:
                scale = d / (radii[i] + radii[j])
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