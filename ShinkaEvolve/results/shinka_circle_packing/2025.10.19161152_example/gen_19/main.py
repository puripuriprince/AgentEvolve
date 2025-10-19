# EVOLVE-BLOCK-START
"""Force-relaxation, meta-hexagonal circle packing for n=26 in a unit square."""

import numpy as np

def hex_lattice_positions(n_layers, center=(0.5, 0.5), d=0.16, jitter=0.05):
    """
    Generate a hexagonal (or meta-hexagonal) grid of points for up to N circles,
    starting from the center. Returns up to 26 points.
    n_layers: number of hexagonal rings (including center, e.g. 3 or 4)
    d: distance between rings
    jitter: random perturbation for diversity
    """
    cx, cy = center
    positions = [[cx, cy]]
    if n_layers < 2:
        return np.array(positions)
    # Layer by layer
    for layer in range(1, n_layers):
        n_pts = 6 * layer
        for k in range(n_pts):
            theta = 2 * np.pi * k / n_pts
            r = d * layer
            px = cx + r * np.cos(theta)
            py = cy + r * np.sin(theta)
            # Add slight noise for symmetry breaking
            px += np.random.uniform(-jitter, jitter)
            py += np.random.uniform(-jitter, jitter)
            positions.append([px, py])
    return np.array(positions)

def fill_to_26(pts, square_pad=0.10):
    """
    If less than 26 points, fill out with edge/corner points in the square (with padding)
    """
    needed = 26 - pts.shape[0]
    result = list(pts)
    # Place extra on edges and corners, inset for more room
    if needed > 0:
        # Corners:
        for x in [square_pad, 1-square_pad]:
            for y in [square_pad, 1-square_pad]:
                if needed == 0: break
                result.append([x, y])
                needed -= 1
            if needed == 0: break
        # Edges:
        edge_pts = [
            [0.5, square_pad], [0.5, 1-square_pad],
            [square_pad, 0.5], [1-square_pad, 0.5]
        ]
        for ep in edge_pts:
            if needed == 0: break
            result.append(ep)
            needed -= 1
    # If still not 26, fill randomly inside square, but in a ring
    while len(result) < 26:
        angle = np.random.uniform(0, 2*np.pi)
        r = np.random.uniform(0.32, 0.47)
        px = 0.5 + r * np.cos(angle)
        py = 0.5 + r * np.sin(angle)
        result.append([px, py])
    return np.array(result[:26])

def clip_to_square(centers, pad=0.008):
    return np.clip(centers, pad, 1-pad)

def compute_max_radii_adaptive(centers, min_radius=0.01):
    """
    Compute the maximal radii for each circle: inside unit square, no overlap.
    """
    n = centers.shape[0]
    radii = np.array([min(x, y, 1-x, 1-y) for x, y in centers])
    # Pairwise overlaps: iterative tightening
    for _ in range(3):
        for i in range(n):
            for j in range(i+1, n):
                d = np.linalg.norm(centers[i] - centers[j])
                if d < 1e-10:
                    # Degenerate
                    radii[i] = radii[j] = 0
                elif radii[i] + radii[j] > d:
                    scale = d / (radii[i] + radii[j])
                    radii[i] *= scale
                    radii[j] *= scale
    # Don't let any circle vanish
    radii = np.maximum(radii, min_radius)
    return radii

def force_relaxation(centers, n_iter=60, alpha=0.14, centering=0.08, border_repulse=0.09, ideal_layer_radii=None):
    """
    Simulate a few rounds of force-based relaxation. Each circle repels others if overlapping,
    is attracted to its ideal ring radius, and is gently pulled toward the center.
    All updates are clipped to keep within the square.
    """
    n = centers.shape[0]
    for it in range(n_iter):
        deltas = np.zeros_like(centers)
        # Repulsion between circles (if too close)
        for i in range(n):
            for j in range(i+1, n):
                vec = centers[i] - centers[j]
                dist = np.linalg.norm(vec)
                if dist < 1e-10:
                    # Random nudge for degenerate
                    vec = np.random.uniform(-1, 1, 2)
                    dist = 1e-3
                overlap = 0.17 - dist  # treat 0.17 as "target" min spacing
                if overlap > 0:
                    # Strong repulsion
                    force = overlap * 0.55 / (dist+1e-4)
                    deltas[i] += force * vec
                    deltas[j] -= force * vec
        # Centering force (pull toward assigned ring radius if available)
        if ideal_layer_radii is not None:
            cxy = np.array([0.5, 0.5])
            for i in range(n):
                vec = centers[i] - cxy
                r_now = np.linalg.norm(vec)
                r_ideal = ideal_layer_radii[i]
                if r_ideal > 0:
                    diff = r_ideal - r_now
                    deltas[i] += centering * diff * (vec / (r_now + 1e-4))
                else:
                    # Pull toward center for center circle
                    deltas[i] += -centering * vec
        else:
            # All: weak pull toward center
            cxy = np.array([0.5, 0.5])
            for i in range(n):
                deltas[i] += -centering * (centers[i] - cxy)
        # Wall repulsion (boost for near walls)
        for i in range(n):
            x, y = centers[i]
            for b in [x, 1-x, y, 1-y]:
                if b < border_repulse:
                    sign = -1 if b in [x, y] else 1
                    axis = 0 if b in [x, 1-x] else 1
                    deltas[i, axis] += sign * (border_repulse - b) * 0.29
        # Step update
        centers += alpha * deltas
        centers = clip_to_square(centers)
    return centers

def assign_ideal_layers(centers):
    """
    Assign each circle to an ideal ring radius for relaxation.
    Tries to mimic a central, inner, mid, and outer layer pattern.
    """
    n = centers.shape[0]
    ideal_radii = np.zeros(n)
    # Sort by distance to center, assign layers
    cxy = np.array([0.5, 0.5])
    dists = np.linalg.norm(centers - cxy, axis=1)
    # Empirically chosen radii for 26: 1 center, 6 inner, 7 mid, 8 outer, 4 corners/edges
    idxs = np.argsort(dists)
    # Layer assignments:
    # 0: center
    ideal_radii[idxs[0]] = 0.0
    # 1-6: inner
    for i in idxs[1:7]:
        ideal_radii[i] = 0.21
    # 7-13: mid
    for i in idxs[7:14]:
        ideal_radii[i] = 0.31
    # 14-21: outer
    for i in idxs[14:22]:
        ideal_radii[i] = 0.43
    # 22+: corners/edges
    for i in idxs[22:]:
        ideal_radii[i] = 0.49
    return ideal_radii

def construct_packing():
    """
    Force-based meta-hexagonal packing for 26 circles in a unit square.
    Returns:
        centers: np.array (26,2)
        radii:   np.array (26,)
    """
    # Step 1: Meta-hexagonal grid + fill to 26
    np.random.seed(4)  # For reproducibility; adjust or randomize for further exploration
    pts = hex_lattice_positions(n_layers=3, d=0.162, jitter=0.016)
    centers = fill_to_26(pts, square_pad=0.10)
    centers = clip_to_square(centers)
    # Step 2: Assign target ring (layer) radii for each circle
    ideal_radii = assign_ideal_layers(centers)
    # Step 3: Force relaxation
    centers = force_relaxation(centers, n_iter=70, alpha=0.17, centering=0.07, border_repulse=0.09, ideal_layer_radii=ideal_radii)
    centers = clip_to_square(centers)
    # Step 4: Compute maximal radii
    radii = compute_max_radii_adaptive(centers)
    return centers, radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii