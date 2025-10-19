# EVOLVE-BLOCK-START
"""Progressive force-relaxation hybrid circle packing for n=26 in a unit square."""

import numpy as np

def construct_packing():
    """
    Hybrid + force-relaxed arrangement for 26 circles in a unit square.
    Returns:
        centers: np.array (26,2)
        radii: np.array (26,)
    """
    n = 26
    centers = np.zeros((n, 2))

    # 0: Center circle
    centers[0] = [0.5, 0.5]

    # 1-4: Corners, with tight inset for maximal radius
    corner_inset = 0.06
    centers[1] = [corner_inset, corner_inset]
    centers[2] = [1-corner_inset, corner_inset]
    centers[3] = [1-corner_inset, 1-corner_inset]
    centers[4] = [corner_inset, 1-corner_inset]

    # 5-16: Edges, 3 per edge, not including corners
    edge_inset = 0.085
    edge_pos = [0.25, 0.5, 0.75]
    # Bottom edge (y fixed)
    centers[5] = [edge_pos[0], edge_inset]
    centers[6] = [edge_pos[1], edge_inset]
    centers[7] = [edge_pos[2], edge_inset]
    # Right edge (x fixed)
    centers[8]  = [1-edge_inset, edge_pos[0]]
    centers[9]  = [1-edge_inset, edge_pos[1]]
    centers[10] = [1-edge_inset, edge_pos[2]]
    # Top edge (y fixed)
    centers[11] = [edge_pos[0], 1-edge_inset]
    centers[12] = [edge_pos[1], 1-edge_inset]
    centers[13] = [edge_pos[2], 1-edge_inset]
    # Left edge (x fixed)
    centers[14] = [edge_inset, edge_pos[0]]
    centers[15] = [edge_inset, edge_pos[1]]
    centers[16] = [edge_inset, edge_pos[2]]

    # 17-20: Inner ring 1, 4 circles (diamond), radius r1, offset for maximal room
    r1 = 0.215
    for k in range(4):
        theta = np.pi/4 + np.pi/2 * k
        centers[17+k] = [0.5 + r1 * np.cos(theta), 0.5 + r1 * np.sin(theta)]
    # 21-26: Inner ring 2, 6 circles (hexagon), radius r2, offset for symmetry
    r2 = 0.336
    rng = np.random.default_rng(seed=123)
    for k in range(6):
        theta = 2*np.pi*k/6 + np.pi/12
        # Mild random perturbation to break symmetry
        perturb = rng.uniform(-0.012, 0.012, 2)
        centers[21+k] = [
            np.clip(0.5 + r2 * np.cos(theta) + perturb[0], 0.01, 0.99),
            np.clip(0.5 + r2 * np.sin(theta) + perturb[1], 0.01, 0.99),
        ]

    # Also perturb the inner ring 1 (diamond) slightly to help symmetry breaking
    for k in range(4):
        perturb = rng.uniform(-0.01, 0.01, 2)
        centers[17+k] = np.clip(centers[17+k] + perturb, 0.01, 0.99)

    # Now, iteratively relax the interior (indices 0, 17-26) for a few more steps
    # while freezing corners/edges (indices 1-16)
    fixed = np.zeros(n, dtype=bool)
    fixed[1:17] = True # center and two inner rings are movable

    for relax_step in range(12):
        radii = compute_max_radii_relax(centers)
        grad = np.zeros_like(centers)

        # For each movable circle, compute small repulsive force from overlaps, gentle push to center if near boundary
        for i in range(n):
            if fixed[i]:
                continue
            # Repulsion from other circles (if overlap/close)
            for j in range(n):
                if i == j:
                    continue
                # Only repel from circles that are "too close"
                delta = centers[i] - centers[j]
                dist = np.linalg.norm(delta)
                min_dist = radii[i] + radii[j] + 1e-8
                if dist < min_dist and dist > 1e-8:
                    # Repulsive force, scaled by overlap amount
                    force = (min_dist - dist) * (delta / (dist + 1e-8))
                    grad[i] += force * 0.18  # 0.18 is a slightly stronger step
            # Gentle push toward center if near square walls
            cx, cy = centers[i]
            if cx < radii[i]+0.01:
                grad[i,0] += (radii[i]+0.01-cx)*0.13
            if cy < radii[i]+0.01:
                grad[i,1] += (radii[i]+0.01-cy)*0.13
            if cx > 1-(radii[i]+0.01):
                grad[i,0] -= (cx-(1-(radii[i]+0.01)))*0.13
            if cy > 1-(radii[i]+0.01):
                grad[i,1] -= (cy-(1-(radii[i]+0.01)))*0.13
        # Update positions (small step), but keep inside [0,1]
        centers[~fixed] += grad[~fixed]
        centers = np.clip(centers, 0.01, 0.99)

    # Final radii computation after relaxation
    radii = compute_max_radii_relax(centers)
    return centers, radii

def compute_max_radii_relax(centers):
    """
    Compute max radii for centers (no overlap, all inside square), multiple passes for fairness.
    """
    n = centers.shape[0]
    radii = np.array([min(x, y, 1-x, 1-y) for x, y in centers])

    # Two passes for better fairness
    for _ in range(2):
        for i in range(n):
            for j in range(i+1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if d <= 1e-12:
                    radii[i] = radii[j] = 0
                elif radii[i] + radii[j] > d:
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