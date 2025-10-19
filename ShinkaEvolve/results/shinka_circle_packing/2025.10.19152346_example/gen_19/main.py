# EVOLVE-BLOCK-START
"""Hybrid circle packing for n=26 circles with improved optimization"""

import numpy as np

def construct_packing():
    """
    Construct an optimized arrangement of 26 circles in a unit square
    to maximize the sum of their radii using structured placement,
    local gradient refinement, and stochastic perturbations.
    """
    n = 26
    centers = np.zeros((n, 2))
    
    # Initial structured placement
    centers[0] = [0.5, 0.5]  # Center large circle
    for i in range(8):
        angle = 2 * np.pi * i / 8
        centers[i + 1] = [0.5 + 0.28 * np.cos(angle), 0.5 + 0.28 * np.sin(angle)]
    for i in range(16):
        angle = 2 * np.pi * i / 16
        centers[i + 9] = [0.5 + 0.65 * np.cos(angle), 0.5 + 0.65 * np.sin(angle)]
    centers = np.clip(centers, 0.01, 0.99)

    # Compute initial radii
    radii = compute_max_radii(centers)

    # Local gradient-based refinement
    for _ in range(100):
        radii, centers = gradient_refine(centers, radii, iterations=10)

    # Apply stochastic perturbations ("shake") to escape local minima
    best_sum = np.sum(radii)
    best_centers = centers.copy()
    best_radii = radii.copy()

    for _ in range(50):
        perturbed_centers = centers.copy()
        # Randomly select a subset of circles to perturb
        indices = np.random.choice(n, size=3, replace=False)
        for idx in indices:
            # Small random shift within a radius
            shift = 0.05 * (np.random.rand(2) - 0.5)
            perturbed_centers[idx] += shift
        # Clip to stay within bounds
        perturbed_centers = np.clip(perturbed_centers, 0.01, 0.99)
        # Recompute radii after perturbation
        new_radii = compute_max_radii(perturbed_centers)
        new_sum = np.sum(new_radii)
        if new_sum > best_sum:
            best_sum = new_sum
            best_centers = perturbed_centers.copy()
            best_radii = new_radii.copy()

    return best_centers, best_radii

def compute_max_radii(centers):
    """
    Compute maximum radii for each circle to avoid overlaps and stay within bounds.
    """
    n = centers.shape[0]
    radii = np.ones(n)

    # Limit by distance to square borders
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1 - x, 1 - y)

    # Limit by distance to other circles
    for i in range(n):
        for j in range(i + 1, n):
            dist = np.linalg.norm(centers[i] - centers[j])
            if radii[i] + radii[j] > dist:
                scale = dist / (radii[i] + radii[j])
                radii[i] *= scale
                radii[j] *= scale
    return radii

def gradient_refine(centers, radii, iterations=10):
    """
    Refine radii and centers via gradient descent to improve total radii sum.
    """
    n = centers.shape[0]
    for _ in range(iterations):
        # Compute overlaps and gradients
        overlaps = np.zeros(n)
        grad_centers = np.zeros_like(centers)
        for i in range(n):
            x_i, y_i = centers[i]
            r_i = radii[i]
            # Gradient w.r.t. radius
            overlap_sum = 0
            for j in range(n):
                if i == j:
                    continue
                x_j, y_j = centers[j]
                r_j = radii[j]
                d = np.linalg.norm(centers[i] - centers[j])
                if d < r_i + r_j:
                    overlap = r_i + r_j - d
                    overlap_sum += overlap
                    # Gradient w.r.t. radius
                    grad_r = -1 if r_i > 0 else 0
                    # Gradient w.r.t. center positions
                    direction = (centers[i] - centers[j]) / d if d != 0 else np.zeros(2)
                    grad_centers[i] += (overlap / d) * direction
            # Gradient w.r.t. radius (to increase radius if no overlap)
            radii[i] += 0.001 * (1 - overlap_sum)
            # Keep radii positive
            radii[i] = max(radii[i], 0.01)
        # Update centers based on gradients
        centers += 0.01 * grad_centers
        centers = np.clip(centers, 0.01, 0.99)
        # Recompute radii after updates
        radii = compute_max_radii(centers)
    return radii, centers

def run_packing():
    """Run the improved circle packing routine."""
    centers, radii = construct_packing()
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii
# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii