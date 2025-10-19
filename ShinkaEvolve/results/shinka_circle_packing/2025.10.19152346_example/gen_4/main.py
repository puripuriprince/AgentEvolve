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

    # Place 4 circles at the corners
    centers[0] = [0.01, 0.01]
    centers[1] = [0.99, 0.01]
    centers[2] = [0.99, 0.99]
    centers[3] = [0.01, 0.99]

    # Place 8 circles at the midpoints of the edges
    centers[4] = [0.5, 0.01]
    centers[5] = [0.99, 0.5]
    centers[6] = [0.5, 0.99]
    centers[7] = [0.01, 0.5]
    centers[8] = [0.25, 0.01]
    centers[9] = [0.75, 0.01]
    centers[10] = [0.99, 0.25]
    centers[11] = [0.99, 0.75]
    centers[12] = [0.75, 0.99]
    centers[13] = [0.25, 0.99]
    centers[14] = [0.01, 0.75]
    centers[15] = [0.01, 0.25]

    # Place 1 large circle in the center
    centers[16] = [0.5, 0.5]

    # Place 4 circles in an inner ring around the center
    for i in range(4):
        angle = 2 * np.pi * i / 4 + np.pi/4
        centers[17 + i] = [0.5 + 0.21 * np.cos(angle), 0.5 + 0.21 * np.sin(angle)]

    # Place 5 circles in a slightly larger ring
    for i in range(5):
        angle = 2 * np.pi * i / 5
        centers[21 + i] = [0.5 + 0.34 * np.cos(angle), 0.5 + 0.34 * np.sin(angle)]

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