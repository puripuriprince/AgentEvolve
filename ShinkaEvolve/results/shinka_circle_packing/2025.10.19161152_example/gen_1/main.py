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

    # Hybrid geometric placement:
    # 0: Center
    centers[0] = [0.5, 0.5]
    # 1-4: Corners
    centers[1] = [0.01, 0.01]
    centers[2] = [0.99, 0.01]
    centers[3] = [0.99, 0.99]
    centers[4] = [0.01, 0.99]
    # 5-8: Edge centers
    centers[5] = [0.5, 0.01]
    centers[6] = [0.99, 0.5]
    centers[7] = [0.5, 0.99]
    centers[8] = [0.01, 0.5]

    # 9-16: First ring (inner, octagon-like)
    ring1_r = 0.24  # radius for inner ring, adjustable
    for i in range(8):
        angle = np.pi/8 + 2 * np.pi * i / 8  # slight offset to avoid alignment with edge centers
        centers[9 + i] = [0.5 + ring1_r * np.cos(angle), 0.5 + ring1_r * np.sin(angle)]

    # 17-25: Outer ring (toward sides, just inside corners/edges)
    ring2_r = 0.47  # radius for outer ring, not all the way to edge
    for i in range(9):
        angle = 2 * np.pi * i / 9
        cx = 0.5 + ring2_r * np.cos(angle)
        cy = 0.5 + ring2_r * np.sin(angle)
        # Clamp to keep inside [0.01, 0.99]
        centers[17 + i] = [min(max(cx, 0.01), 0.99), min(max(cy, 0.01), 0.99)]

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