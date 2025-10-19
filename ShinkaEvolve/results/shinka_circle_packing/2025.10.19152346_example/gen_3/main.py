# EVOLVE-BLOCK-START
import numpy as np

def construct_packing():
    """Construct a hybrid circle packing in the unit square with improved total radii."""
    n = 26
    centers = []
    radii = []

    # Place large circles at key positions: center and corners
    large_radius = 0.2
    centers.append([0.5, 0.5])  # center
    radii.append(large_radius)

    corners = [
        [large_radius, large_radius],
        [1 - large_radius, large_radius],
        [large_radius, 1 - large_radius],
        [1 - large_radius, 1 - large_radius],
    ]
    for c in corners:
        centers.append(c)
        radii.append(large_radius)

    # Place intermediate circles along edges with decreasing radii
    edge_positions = []
    for i in range(1, 5):
        # Along bottom edge
        x = i / 5
        y = 0.1
        edge_positions.append([x, y])
        # Along top edge
        edge_positions.append([x, 1 - 0.1])
        # Along left edge
        y = i / 5
        x = 0.1
        edge_positions.append([x, y])
        # Along right edge
        x = 1 - 0.1
        edge_positions.append([x, y])

    # Assign radii decreasing towards corners
    for pos in edge_positions:
        # Distance from center for scaling radii
        dist_center = np.linalg.norm(np.array(pos) - [0.5, 0.5])
        # Radii inversely proportional to distance from center
        radius = max(0.05, 0.2 * (1 - dist_center))
        centers.append(pos)
        radii.append(radius)

    # Fill remaining positions with small circles in a grid to maximize packing
    grid_x = np.linspace(0.2, 0.8, 4)
    grid_y = np.linspace(0.2, 0.8, 4)
    for x in grid_x:
        for y in grid_y:
            # Avoid overlapping with existing large or medium circles
            candidate = np.array([x, y])
            # Check overlap with existing circles
            overlaps = False
            for c, r in zip(centers, radii):
                dist = np.linalg.norm(candidate - c)
                if dist < r + 0.02:
                    overlaps = True
                    break
            if not overlaps:
                # Assign small radius
                radius = 0.02
                centers.append([x, y])
                radii.append(radius)

    centers = np.array(centers[:n])
    radii = np.array(radii[:n])

    # Compute maximum radii for these centers considering overlaps
    radii = compute_max_radii(centers)
    return centers, radii

def compute_max_radii(centers):
    """Compute maximum radii so circles do not overlap and stay inside bounds."""
    n = len(centers)
    radii = np.zeros(n)
    for i in range(n):
        c = centers[i]
        # Distance to borders
        radii[i] = min(c[0], 1 - c[0], c[1], 1 - c[1])
    # Adjust radii to prevent overlaps
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(i + 1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                max_r = d / 2
                if radii[i] + radii[j] > d:
                    # Scale down to prevent overlap
                    scale = max_r / (radii[i] + radii[j])
                    if scale < 1:
                        radii[i] *= scale
                        radii[j] *= scale
                        changed = True
                        # Ensure radii do not exceed border constraints
                        for k in [i, j]:
                            c = centers[k]
                            radii[k] = min(radii[k], min(c[0], 1 - c[0], c[1], 1 - c[1]))
    return radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii
