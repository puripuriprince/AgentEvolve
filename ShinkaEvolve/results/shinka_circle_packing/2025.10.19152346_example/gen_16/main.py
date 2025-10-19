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
    n = 26
    best_sum = 0
    best_centers = None
    best_radii = None

    # We'll try a sweep for the central ring radii as before
    for ring1 in [0.24, 0.26, 0.28]:
        for ring2 in [0.57, 0.60, 0.63, 0.66]:
            centers = np.zeros((n, 2))

            # 1. Four corners
            corners = np.array([
                [0.01, 0.01],
                [0.01, 0.99],
                [0.99, 0.01],
                [0.99, 0.99]
            ])
            centers[0:4] = corners

            # 2. Eight edge placements - 4 at center-points, 4 at quarter-points
            edge_points = np.array([
                [0.5, 0.01],   # bottom center
                [0.5, 0.99],   # top center
                [0.01, 0.5],   # left center
                [0.99, 0.5],   # right center
                [0.25, 0.01],  # bottom left quarter
                [0.75, 0.01],  # bottom right quarter
                [0.25, 0.99],  # top left quarter
                [0.75, 0.99],  # top right quarter
            ])
            centers[4:12] = edge_points

            # 3. Place a large circle at center
            centers[12] = [0.5, 0.5]

            # 4. 5-circle inner ring
            for i in range(5):
                angle = 2 * np.pi * i / 5 + (np.pi / 5)
                centers[13 + i] = [0.5 + ring1 * np.cos(angle), 0.5 + ring1 * np.sin(angle)]

            # 5. Remaining 9 circles in an outer ring
            for i in range(9):
                angle = 2 * np.pi * i / 9
                centers[18 + i] = [0.5 + ring2 * np.cos(angle), 0.5 + ring2 * np.sin(angle)]

            # 6. Adjust to ensure all points are within open square
            centers = np.clip(centers, 0.01, 0.99)

            # Estimate initial radii for better local density
            init_radii = np.zeros(n)
            for i in range(n):
                x, y = centers[i]
                # Corners
                if i < 4:
                    init_radii[i] = min(x, y, 1 - x, 1 - y)
                # Edge points
                elif i < 12:
                    edge_min = min(x, y, 1 - x, 1 - y)
                    # Minimum to neighbors on edge
                    min_edge_dist = 1.0
                    for j in range(4):
                        if i == 4 + j or i == 8 + j:
                            continue
                        d = np.linalg.norm(centers[i] - centers[j])
                        if d < min_edge_dist and d > 1e-8:
                            min_edge_dist = d
                    init_radii[i] = min(edge_min, 0.5 * min_edge_dist)
                else:
                    # Center and bulk: based on distance to border and other centers
                    dists = [np.sqrt(np.sum((centers[i] - centers[j]) ** 2)) for j in range(n) if i != j]
                    init_radii[i] = min([x, y, 1 - x, 1 - y] + [0.5 * d for d in dists])

            # Run iterative non-overlapping constraint, but start with init_radii
            temp_radii = compute_max_radii_with_init(centers, init_radii)
            sum_radii = np.sum(temp_radii)
            if sum_radii > best_sum:
                best_sum = sum_radii
                best_centers = np.copy(centers)
                best_radii = np.copy(temp_radii)
    return best_centers, best_radii

def compute_max_radii_with_init(centers, radii_init):
    """
    Like compute_max_radii but respects initial guesses for radii,
    then iteratively shrinks if needed to avoid overlap and borders.
    """
    n = centers.shape[0]
    radii = radii_init.copy()
    # Limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(radii[i], x, y, 1 - x, 1 - y)
    # Resolve overlap: repeat a few times for convergence
    for _ in range(6):
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.sqrt(np.sum((centers[i] - centers[j]) ** 2))
                if radii[i] + radii[j] > dist:
                    scale = dist / (radii[i] + radii[j])
                    radii[i] *= scale
                    radii[j] *= scale
    return radii


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