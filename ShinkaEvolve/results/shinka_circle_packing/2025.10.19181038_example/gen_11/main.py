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
    corner_pos = [
        [0.01, 0.01],
        [0.99, 0.01],
        [0.99, 0.99],
        [0.01, 0.99]
    ]
    for i in range(4):
        centers[i] = corner_pos[i]

    # Place 4 circles at the edge centers
    edge_centers = [
        [0.5, 0.01],
        [0.99, 0.5],
        [0.5, 0.99],
        [0.01, 0.5]
    ]
    for i in range(4):
        centers[4 + i] = edge_centers[i]

    # Place 1 large at the center
    centers[8] = [0.5, 0.5]

    # Place 6 in a "hex" ring around the center (radius ~0.26)
    for i in range(6):
        angle = 2 * np.pi * i / 6
        r = 0.26
        centers[9 + i] = [0.5 + r * np.cos(angle), 0.5 + r * np.sin(angle)]

    # Place 12 in a larger ring (radius ~0.425), with an angular offset to avoid grid alignment
    outer_ring_n = 12
    outer_ring_r = 0.425
    outer_offset = np.pi / outer_ring_n  # 15 deg offset
    for i in range(outer_ring_n):
        angle = 2 * np.pi * i / outer_ring_n + outer_offset
        x = 0.5 + outer_ring_r * np.cos(angle)
        y = 0.5 + outer_ring_r * np.sin(angle)
        centers[15 + i] = [x, y]

    # Local repulsion step for outer ring points only (indices 15..26)
    outer_idx = np.arange(15, 27)
    for repulse_iter in range(8):
        for i in outer_idx:
            dxy = np.zeros(2)
            for j in outer_idx:
                if i == j:
                    continue
                delta = centers[i] - centers[j]
                dist = np.linalg.norm(delta)
                if dist < 1e-8:
                    dxy += np.random.randn(2) * 1e-3
                elif dist < 0.13:
                    dxy += delta / (dist + 1e-5) * 0.014
                elif dist < 0.22:
                    dxy += delta / dist * 0.003
            # Bias to stay in the square (gentle)
            for d in range(2):
                if centers[i][d] < 0.019: dxy[d] += 0.013
                if centers[i][d] > 0.981: dxy[d] -= 0.013
            centers[i] += dxy
        # Clamp outer ring to square
        centers[outer_idx] = np.clip(centers[outer_idx], 0.018, 0.982)

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