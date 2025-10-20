# EVOLVE-BLOCK-START
"""Centered honeycomb gradient arrangement for n=26 circles"""

import numpy as np

def construct_packing():
    """
    Construct an optimized arrangement of 26 circles in a unit square,
    using a honeycomb-inspired hybrid placement: big center, two hexagonal rings,
    and edge/corner/interstitial circles placed strategically.

    Returns:
        Tuple of (centers, radii)
        centers: np.array of shape (26, 2) with (x, y) coordinates
        radii: np.array of shape (26,) with radius of each circle
    """
    n = 26
    centers = np.zeros((n, 2))

    # 0: Center (largest)
    centers[0] = [0.5, 0.5]

    # 1-6: First tight hexagon ring (radius ~0.22)
    r1 = 0.22
    for i in range(6):
        angle = 2*np.pi*i/6
        centers[1+i] = [0.5 + r1*np.cos(angle), 0.5 + r1*np.sin(angle)]

    # 7-18: Staggered outer hexagon ring (radius ~0.41, offset)
    r2 = 0.41
    ring_offset = np.pi/12
    for i in range(12):
        angle = 2*np.pi*i/12 + ring_offset
        centers[7+i] = [0.5 + r2*np.cos(angle), 0.5 + r2*np.sin(angle)]

    # 19-22: Edge centers (inset for larger radius)
    edge_inset = 0.057
    centers[19] = [0.5, edge_inset]
    centers[20] = [1-edge_inset, 0.5]
    centers[21] = [0.5, 1-edge_inset]
    centers[22] = [edge_inset, 0.5]

    # 23-26: Corners (inset for larger radius)
    corner_inset = 0.055
    centers[23] = [corner_inset, corner_inset]
    centers[24] = [1-corner_inset, corner_inset]
    centers[25] = [1-corner_inset, 1-corner_inset]
    centers[26-1] = [corner_inset, 1-corner_inset]

    # Slightly move points inside if at the border (safety)
    centers = np.clip(centers, 0.012, 0.988)

    # Compute maximal radii with iterative tightening
    radii = compute_max_radii_iterative(centers)
    return centers, radii

def compute_max_radii_iterative(centers, max_iters=60, tol=1e-8):
    """
    Iteratively compute maximal radii so that circles don't overlap or exit the unit square.
    Uses a pairwise min procedure and iterative tightening.

    Args:
        centers: np.array (n, 2)
        max_iters: int, number of iterations for tightening
        tol: convergence tolerance

    Returns:
        radii: np.array (n,)
    """
    n = centers.shape[0]
    radii = np.ones(n)
    # Border constraint
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1-x, 1-y)
    # Iterative tightening for overlaps
    for _ in range(max_iters):
        prev = radii.copy()
        for i in range(n):
            for j in range(i+1, n):
                dist = np.linalg.norm(centers[i]-centers[j])
                if dist < 1e-8:
                    # If two centers are coincident, force radii to nearly zero
                    radii[i] = min(radii[i], 1e-4)
                    radii[j] = min(radii[j], 1e-4)
                elif radii[i] + radii[j] > dist:
                    # Reduce both radii proportionally to avoid overlap
                    excess = (radii[i] + radii[j]) - dist
                    share = 0.5 * excess
                    radii[i] -= share
                    radii[j] -= share
                    radii[i] = max(radii[i], 1e-6)
                    radii[j] = max(radii[j], 1e-6)
        if np.max(np.abs(radii - prev)) < tol:
            break
    return radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii