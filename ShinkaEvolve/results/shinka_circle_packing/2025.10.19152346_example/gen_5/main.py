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

    # Place circles in a structured pattern
    # Hybrid approach: large center circle, two rings, and corner circles

    # Large center circle
    centers[0] = [0.5, 0.5]

    # Tunable ring distances for flexible configuration
    ring1 = 0.25  # inner ring radius (slightly smaller to allow bigger center)
    ring2 = 0.62  # outer ring radius (adjusted for better packing)

    # Place 8 circles around it in an inner ring
    for i in range(8):
        angle = 2 * np.pi * i / 8
        centers[i + 1] = [0.5 + ring1 * np.cos(angle), 0.5 + ring1 * np.sin(angle)]

    # Place 14 circles in an outer ring (reduced from 17 to allocate corners)
    for i in range(14):
        angle = 2 * np.pi * i / 14
        centers[i + 9] = [0.5 + ring2 * np.cos(angle), 0.5 + ring2 * np.sin(angle)]

    # Place 4 smaller circles in the corners to better use edges
    corner_offset = 0.07
    corners = np.array([
        [corner_offset, corner_offset],
        [1 - corner_offset, corner_offset],
        [corner_offset, 1 - corner_offset],
        [1 - corner_offset, 1 - corner_offset],
    ])
    centers[23:27] = corners[:4]

    # Clip to ensure everything is inside the unit square
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

    # Then, limit by distance to other circles
    # Each pair of circles with centers at distance d can have
    # sum of radii at most d to avoid overlap
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))

            # If current radii would cause overlap
            if radii[i] + radii[j] > dist:
                # Scale both radii proportionally
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