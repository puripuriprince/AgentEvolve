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
    # Improved: 1 center, 4 corners, 10 edges, 6+5 in two rings (twisted)
    n = 26
    centers = np.zeros((n, 2))

    # 0: Central circle
    centers[0] = [0.5, 0.5]

    # 1-4: Corners, closer to corners
    corner_inset = 0.09
    centers[1] = [corner_inset, corner_inset]
    centers[2] = [1 - corner_inset, corner_inset]
    centers[3] = [1 - corner_inset, 1 - corner_inset]
    centers[4] = [corner_inset, 1 - corner_inset]

    # 5-14: Edges, distribute 3 on each long edge (excluding corners), 2 on short edges
    edge_inset = 0.085
    edge_positions = [0.23, 0.5, 0.77]  # points along the edge (excluding corners)
    # Left edge (x fixed, y varies)
    centers[5] = [edge_inset, edge_positions[0]]
    centers[6] = [edge_inset, edge_positions[1]]
    centers[7] = [edge_inset, edge_positions[2]]
    # Right edge
    centers[8] = [1 - edge_inset, edge_positions[0]]
    centers[9] = [1 - edge_inset, edge_positions[1]]
    centers[10] = [1 - edge_inset, edge_positions[2]]
    # Bottom edge (y fixed, x varies)
    centers[11] = [edge_positions[0], edge_inset]
    centers[12] = [edge_positions[2], edge_inset]
    # Top edge
    centers[13] = [edge_positions[0], 1 - edge_inset]
    centers[14] = [edge_positions[2], 1 - edge_inset]

    # 15-20: Inner ring 1 (radius r1, 6 circles)
    r1 = 0.23
    for k in range(6):
        theta = 2 * np.pi * k / 6 + np.pi/12  # slight twist
        centers[15 + k] = [0.5 + r1 * np.cos(theta), 0.5 + r1 * np.sin(theta)]

    # 21-25: Inner ring 2 (radius r2, 5 circles, offset from previous)
    r2 = 0.355
    for k in range(5):
        theta = 2 * np.pi * k / 5 + np.pi/6
        centers[21 + k] = [0.5 + r2 * np.cos(theta), 0.5 + r2 * np.sin(theta)]

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