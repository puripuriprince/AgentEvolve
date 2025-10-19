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
    # This is a simple pattern - evolution will improve this

    # First, place a large circle in the center
    centers[0] = [0.5, 0.5]

    # Parameter sweep for inner and outer ring radii
    best_sum = 0
    best_centers = None
    best_radii = None
    for ring1 in [0.26, 0.28, 0.30]:
        for ring2 in [0.63, 0.65, 0.67]:
            temp_centers = np.zeros((n, 2))
            temp_centers[0] = [0.5, 0.5]
            for i in range(8):
                angle = 2 * np.pi * i / 8
                temp_centers[i + 1] = [0.5 + ring1 * np.cos(angle), 0.5 + ring1 * np.sin(angle)]
            for i in range(17):
                angle = 2 * np.pi * i / 17
                temp_centers[i + 9] = [0.5 + ring2 * np.cos(angle), 0.5 + ring2 * np.sin(angle)]
            temp_centers = np.clip(temp_centers, 0.01, 0.99)
            temp_radii = compute_max_radii(temp_centers)
            sum_radii = np.sum(temp_radii)
            if sum_radii > best_sum:
                best_sum = sum_radii
                best_centers = temp_centers
                best_radii = temp_radii
    return best_centers, best_radii


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