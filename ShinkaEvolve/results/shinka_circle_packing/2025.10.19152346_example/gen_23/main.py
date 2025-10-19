# EVOLVE-BLOCK-START
"""Modular hybrid circle packing n=26 with adaptive shrink, early stopping, and shake-enhanced swaps"""

import numpy as np

def construct_packing():
    n = 26

    centers = initial_placement(n)
    radii = compute_max_radii(centers)

    centers, radii = local_gradient_optimization(
        centers, radii,
        max_iters=300,
        tolerance=1e-6,
        overlap_tol=1e-6,
        step_pos=0.007,
        shrink_init=0.995,
        shrink_min=0.006
    )

    centers, radii = hybrid_swap_optimization(
        centers, radii,
        swaps=150,
        step_pos=0.007,
        shrink_init=0.995,
        shrink_min=0.006
    )

    return centers, radii


def initial_placement(n):
    centers = np.zeros((n, 2))

    # Center circle - largest
    centers[0] = [0.5, 0.5]

    # Inner ring of 8 circles around center (octagonal)
    inner_ring_radius = 0.27
    for i in range(8):
        angle = 2 * np.pi * i / 8
        centers[i + 1] = [0.5 + inner_ring_radius * np.cos(angle),
                          0.5 + inner_ring_radius * np.sin(angle)]

    # Place 4 corner circles larger spacing
    corners = np.array([[0.05, 0.05], [0.05, 0.95], [0.95, 0.05], [0.95, 0.95]])
    centers[9:13] = corners

    # Remaining 13 circles placed on edges between corners with even spacing
    edge_positions = []
    bottom_xs = np.linspace(0.15, 0.85, 4)
    for x in bottom_xs:
        edge_positions.append([x, 0.05])
    top_xs = np.linspace(0.15, 0.85, 4)
    for x in top_xs:
        edge_positions.append([x, 0.95])
    left_ys = np.linspace(0.15, 0.85, 2)
    for y in left_ys:
        edge_positions.append([0.05, y])
    right_ys = np.linspace(0.15, 0.85, 3)
    for y in right_ys:
        edge_positions.append([0.95, y])
    centers[13:26] = np.array(edge_positions)

    return centers


def compute_max_radii(centers):
    n = centers.shape[0]
    radii = np.zeros(n)

    # Distances to borders
    dist_borders = np.minimum.reduce(
        [centers[:, 0], centers[:, 1], 1 - centers[:, 0], 1 - centers[:, 1]]
    )
    radii[:] = dist_borders

    # Iterative adjustment to avoid overlaps
    for _ in range(100):
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                dist = np.linalg.norm(centers[i] - centers[j])
                if dist < 1e-14:
                    continue
                if radii[i] + radii[j] > dist:
                    scale = dist / (radii[i] + radii[j])
                    if scale < 1:
                        new_i = radii[i] * scale
                        new_j = radii[j] * scale
                        if new_i < radii[i]:
                            radii[i] = new_i
                            changed = True
                        if new_j < radii[j]:
                            radii[j] = new_j
                            changed = True
        if not changed:
            break
    return radii


def local_gradient_optimization(centers, radii, max_iters=300, tolerance=1e-6,
                                overlap_tol=1e-6, step_pos=0.007,
                                shrink_init=0.995, shrink_min=0.006):
    n = centers.shape[0]
    margin = 1e-3
    shrink_factors = np.ones(n) * shrink_init

    prev_sum = np.sum(radii)
    no_improve_count = 0
    max_no_improve = 30

    for iteration in range(max_iters):
        diffs = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
        dists = np.linalg.norm(diffs, axis=2)
        np.fill_diagonal(dists, np.inf)

        move_vecs = np.zeros_like(centers)
        radius_shrink_updates = np.ones(n)

        max_overlap = 0.0

        for i in range(n):
            grad = np.zeros(2)
            # Boundary repulsion
            for d in range(2):
                low_dist = centers[i, d] - radii[i] - margin
                if low_dist < 0:
                    grad[d] += -low_dist * 3
                high_dist = centers[i, d] + radii[i] - (1 - margin)
                if high_dist > 0:
                    grad[d] += -high_dist * 3

            for j in range(n):
                if i == j:
                    continue
                dist = dists[i, j]
                overlap = radii[i] + radii[j] - dist
                if overlap > overlap_tol:
                    max_overlap = max(max_overlap, overlap)
                    if dist > 1e-12:
                        direction = diffs[i, j] / dist
                    else:
                        # Random unit vector
                        direction = np.random.randn(2)
                        direction /= np.linalg.norm(direction)
                    grad += direction * overlap * 4
                    radius_shrink_updates[i] = min(radius_shrink_updates[i], shrink_init)
                    radius_shrink_updates[j] = min(radius_shrink_updates[j], shrink_init)
            move_vecs[i] = grad

        # Normalize and scale moves
        norms = np.linalg.norm(move_vecs, axis=1, keepdims=True)
        norms[norms < 1e-12] = 1
        moves = (move_vecs / norms) * step_pos

        centers_new = centers + moves
        centers_new = np.clip(centers_new, margin, 1 - margin)

        radii_new = compute_max_radii(centers_new)

        sum_prev = np.sum(radii)
        sum_new = np.sum(radii_new)
        max_move_dist = np.max(np.linalg.norm(centers_new - centers, axis=1))

        # Accept new if improvement in sum or significant move to escape local minima
        if sum_new >= sum_prev or max_move_dist > tolerance:
            centers = centers_new
            radii = radii_new
            shrink_factors = np.minimum(shrink_factors, radius_shrink_updates)
            no_improve_count = 0 if sum_new > sum_prev + 1e-8 else no_improve_count + 1
            prev_sum = sum_new
        else:
            # Shrink radii if stuck
            radii = np.maximum(radii * shrink_factors, shrink_min)
            no_improve_count += 1

        if max_overlap < overlap_tol and no_improve_count >= max_no_improve:
            break

    return centers, radii


def hybrid_swap_optimization(centers, radii, swaps=150, step_pos=0.007,
                             shrink_init=0.995, shrink_min=0.006):
    n = centers.shape[0]
    best_centers = centers.copy()
    best_radii = radii.copy()
    best_sum = np.sum(radii)

    dists = np.linalg.norm(centers[:, np.newaxis, :] - centers[np.newaxis, :, :], axis=2)
    np.fill_diagonal(dists, np.inf)
    k = 5
    nearest_neighbors = np.argsort(dists, axis=1)[:, :k]

    for _ in range(swaps):
        i = np.random.randint(n)
        j = np.random.choice(nearest_neighbors[i])
        if i == j:
            continue

        swapped_centers = centers.copy()
        swapped_centers[i], swapped_centers[j] = centers[j], centers[i]

        swapped_radii = compute_max_radii(swapped_centers)

        # Run a brief refinement after swap to relax
        swapped_centers, swapped_radii = local_gradient_optimization(
            swapped_centers,
            swapped_radii,
            max_iters=30,
            tolerance=5e-6,
            overlap_tol=1e-5,
            step_pos=step_pos,
            shrink_init=shrink_init,
            shrink_min=shrink_min
        )

        swapped_sum = np.sum(swapped_radii)

        if swapped_sum > best_sum + 1e-5:
            best_sum = swapped_sum
            best_centers = swapped_centers.copy()
            best_radii = swapped_radii.copy()
            centers = best_centers.copy()
            radii = best_radii.copy()

            dists = np.linalg.norm(centers[:, np.newaxis, :] - centers[np.newaxis, :, :], axis=2)
            np.fill_diagonal(dists, np.inf)
            nearest_neighbors = np.argsort(dists, axis=1)[:, :k]

    return best_centers, best_radii


# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii