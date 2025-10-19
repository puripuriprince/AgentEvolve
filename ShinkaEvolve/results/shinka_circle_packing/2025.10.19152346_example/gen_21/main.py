# EVOLVE-BLOCK-START
"""Hexagonal ring adaptive shrinking circle packing for n=26"""

import numpy as np

def construct_packing():
    n = 26
    centers = np.zeros((n, 2))
    radii = np.zeros(n)

    # --- Structured initial placement as concentric hexagonal rings ---

    # Center circle (largest)
    centers[0] = [0.5, 0.5]

    # First hex ring (6 circles) radius approx 0.18 from center
    r1 = 0.18
    for i in range(6):
        angle = np.pi/3 * i
        centers[1 + i] = 0.5 + r1 * np.array([np.cos(angle), np.sin(angle)])

    # Second hex ring (12 circles) radius approx 0.35 from center
    r2 = 0.35
    for i in range(12):
        angle = np.pi/6 + (np.pi/6) * i  # offset for even spacing of 12
        centers[7 + i] = 0.5 + r2 * np.array([np.cos(angle), np.sin(angle)])

    # Remaining 7 circles arranged near edges and corners, smaller radii expected
    edge_buffer = 0.08  # keep some margin from edges
    edge_spots = np.array([
        [edge_buffer, edge_buffer],
        [0.5, edge_buffer*0.9],
        [1 - edge_buffer, edge_buffer],
        [1 - edge_buffer, 0.5],
        [1 - edge_buffer, 1 - edge_buffer],
        [0.5, 1 - edge_buffer*0.9],
        [edge_buffer, 1 - edge_buffer]
    ])
    centers[19:] = edge_spots

    # Initial radii estimates: center largest, rings medium, edges smallest
    radii[:1] = 0.07
    radii[1:7] = 0.04
    radii[7:19] = 0.03
    radii[19:] = 0.015

    # Clip centers inside unit square margins
    centers = np.clip(centers, 0.01, 0.99)

    # --- Adaptive optimization parameters ---
    max_iters = 200
    tol = 1e-5
    step_pos = 0.01
    max_shrink = 0.993
    min_radius = 0.005

    # Per-circle shrink factors (dynamic)
    shrink_factors = np.ones(n)

    # Track improvement to implement early stopping
    prev_sum = 0
    no_improve_iters = 0
    max_no_improve = 20

    for iteration in range(max_iters):
        # Compute pairwise distances and overlaps
        diffs = centers[:, None, :] - centers[None, :, :]
        dists = np.linalg.norm(diffs, axis=2)
        np.fill_diagonal(dists, np.inf)

        # Compute maximum possible radii constrained by borders
        border_radii = np.minimum.reduce([centers[:,0], centers[:,1], 1-centers[:,0], 1-centers[:,1]])
        # Radii limited also by neighboring circles
        radii_max = border_radii.copy()

        for i in range(n):
            for j in range(i+1, n):
                dist = dists[i,j]
                if dist < np.inf:
                    max_r = dist / 2
                    if max_r < radii_max[i]:
                        radii_max[i] = max_r
                    if max_r < radii_max[j]:
                        radii_max[j] = max_r

        # Apply dynamic shrink factors to avoid sudden radius increase causing overlaps
        radii_new = np.minimum(radii_max, radii * shrink_factors)

        # Compute gradients: position and radius adjustment
        grad_positions = np.zeros_like(centers)
        radius_shrink_updates = np.ones(n)

        total_radius = np.sum(radii)
        total_radius_new = np.sum(radii_new)

        # Gradient for positions - repel overlapping circles and respect borders
        for i in range(n):
            grad = np.zeros(2)
            # Border repulsion
            for d in range(2):
                low_dist = centers[i,d] - radii_new[i] - 0.01
                if low_dist < 0:
                    grad[d] += -low_dist * 2  # repulsive force
                high_dist = centers[i,d] + radii_new[i] - 0.99
                if high_dist > 0:
                    grad[d] += -high_dist * 2
            # Overlap repulsion with neighbors
            for j in range(n):
                if i == j:
                    continue
                dist = dists[i,j]
                overlap = radii_new[i] + radii_new[j] - dist
                if overlap > 0:
                    if dist > 1e-10:
                        direction = (centers[i] - centers[j]) / dist
                    else:
                        direction = np.random.uniform(-1,1,2)
                        direction /= np.linalg.norm(direction)
                    grad += direction * overlap * 3  # weighted repulsion

                    # Encourage shrink if persistent overlap
                    radius_shrink_updates[i] *= max_shrink
                    radius_shrink_updates[j] *= max_shrink
            grad_positions[i] = grad

        # Normalize gradients to step_pos scale
        norms = np.linalg.norm(grad_positions, axis=1)
        norms[norms < 1e-12] = 1
        grad_positions = (grad_positions.T / norms * step_pos).T

        # Update centers
        centers += grad_positions
        centers = np.clip(centers, 0.01, 0.99)

        # Update shrink factors for radii per circle
        shrink_factors = np.minimum(shrink_factors, radius_shrink_updates)
        # Prevent shrinking below min radius fraction
        shrink_factors = np.maximum(shrink_factors, min_radius / (radii + 1e-10))

        # Set new radii
        radii = np.minimum(radii_new, radii * shrink_factors)
        radii = np.maximum(radii, min_radius)

        # Check improvement and early stop
        sum_radii = np.sum(radii)
        if sum_radii - prev_sum < tol:
            no_improve_iters += 1
            if no_improve_iters >= max_no_improve:
                break
        else:
            no_improve_iters = 0
            prev_sum = sum_radii

    # --- Small random shake step to escape local minima ---

    shake_trials = 15
    best_sum = np.sum(radii)
    best_centers = centers.copy()
    best_radii = radii.copy()

    for _ in range(shake_trials):
        trial_centers = centers.copy()
        trial_radii = radii.copy()
        selected = np.random.choice(n, 3, replace=False)
        for idx in selected:
            perturb = (np.random.rand(2) - 0.5) * 0.06
            trial_centers[idx] += perturb
        trial_centers = np.clip(trial_centers, 0.01, 0.99)

        # Run few adaptive steps after shake
        trial_radii, trial_centers = local_refine_after_shake(trial_centers, trial_radii,
                                                             max_steps=30,
                                                             step_pos=0.012,
                                                             min_radius=min_radius,
                                                             max_shrink=max_shrink)

        trial_sum = np.sum(trial_radii)
        if trial_sum > best_sum + 1e-5:
            best_sum = trial_sum
            best_centers = trial_centers.copy()
            best_radii = trial_radii.copy()

    return best_centers, best_radii


def local_refine_after_shake(centers, radii, max_steps=30, step_pos=0.01, min_radius=0.005, max_shrink=0.993):
    n = centers.shape[0]
    shrink_factors = np.ones(n)
    for _ in range(max_steps):
        diffs = centers[:, None, :] - centers[None, :, :]
        dists = np.linalg.norm(diffs, axis=2)
        np.fill_diagonal(dists, np.inf)
        border_radii = np.minimum.reduce([centers[:,0], centers[:,1], 1-centers[:,0], 1-centers[:,1]])
        radii_max = border_radii.copy()
        for i in range(n):
            for j in range(i+1, n):
                dist = dists[i,j]
                if dist < np.inf:
                    max_r = dist / 2
                    if max_r < radii_max[i]:
                        radii_max[i] = max_r
                    if max_r < radii_max[j]:
                        radii_max[j] = max_r

        radii_new = np.minimum(radii_max, radii * shrink_factors)

        grad_positions = np.zeros_like(centers)
        radius_shrink_updates = np.ones(n)
        for i in range(n):
            grad = np.zeros(2)
            for d in range(2):
                low_dist = centers[i,d] - radii_new[i] - 0.01
                if low_dist < 0:
                    grad[d] += -low_dist * 2
                high_dist = centers[i,d] + radii_new[i] - 0.99
                if high_dist > 0:
                    grad[d] += -high_dist * 2
            for j in range(n):
                if i == j:
                    continue
                dist = dists[i,j]
                overlap = radii_new[i] + radii_new[j] - dist
                if overlap > 0:
                    if dist > 1e-10:
                        direction = (centers[i] - centers[j]) / dist
                    else:
                        direction = np.random.uniform(-1,1,2)
                        direction /= np.linalg.norm(direction)
                    grad += direction * overlap * 3
                    radius_shrink_updates[i] *= max_shrink
                    radius_shrink_updates[j] *= max_shrink
            grad_positions[i] = grad

        norms = np.linalg.norm(grad_positions, axis=1)
        norms[norms < 1e-12] = 1
        grad_positions = (grad_positions.T / norms * step_pos).T
        centers += grad_positions
        centers = np.clip(centers, 0.01, 0.99)

        shrink_factors = np.minimum(shrink_factors, radius_shrink_updates)
        shrink_factors = np.maximum(shrink_factors, min_radius / (radii + 1e-10))

        radii = np.minimum(radii_new, radii * shrink_factors)
        radii = np.maximum(radii, min_radius)
    return radii, centers

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii