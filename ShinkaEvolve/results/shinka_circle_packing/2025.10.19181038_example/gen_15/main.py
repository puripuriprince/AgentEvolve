# EVOLVE-BLOCK-START
"""Force-directed relaxation for optimal 26-circle packing in a unit square."""

import numpy as np

def construct_packing():
    """
    Place 26 circles in a unit square to maximize the sum of their radii.
    Uses a force-directed/relaxation approach with adaptive radii.
    Returns:
        centers: np.array, shape (26,2), positions of circle centers
        radii:   np.array, shape (26,), optimal radii for given centers
    """

    n = 26
    # --- 1. Initial layout: hybrid (corners, edge-centers, center, inner grid, outer ring) ---
    centers = np.zeros((n,2))
    idx = 0
    # Corners
    margin = 0.018
    for c in ([margin, margin], [1-margin, margin], [1-margin, 1-margin], [margin, 1-margin]):
        centers[idx] = c
        idx += 1
    # Edge-centers (slightly inset)
    emargin = 0.035
    for c in ([0.5, emargin], [1-emargin, 0.5], [0.5, 1-emargin], [emargin, 0.5]):
        centers[idx] = c
        idx += 1
    # Center
    centers[idx] = [0.5, 0.5]
    idx += 1
    # 3x3 jittered grid (excluding center)
    grid_N = 3
    grid_lo, grid_hi = 0.28, 0.72
    grid_pts = np.linspace(grid_lo, grid_hi, grid_N)
    for i in range(grid_N):
        for j in range(grid_N):
            if i==1 and j==1: continue
            jitter = 0.015*np.array([np.sin(i+2.3*j), np.cos(j+1.5*i)])
            pt = [grid_pts[i]+jitter[0], grid_pts[j]+jitter[1]]
            centers[idx] = pt
            idx += 1
    # Adaptive outer ring (remaining circles)
    n_ring = n-idx
    r_ring = 0.43
    for k in range(n_ring):
        theta = 2*np.pi*k/n_ring + 0.12*np.sin(1.9*k)
        r = r_ring*(1+0.025*np.sin(2*theta+2.1*k))
        x = 0.5+r*np.cos(theta)
        y = 0.5+r*np.sin(theta)
        # extra jitter to break symmetry
        x += 0.009*np.sin(2*k+0.6)
        y += 0.009*np.cos(2*k+1.1)
        # slightly repel from corners
        for cpt in ([margin,margin],[1-margin,margin],[1-margin,1-margin],[margin,1-margin]):
            vec = np.array([x,y]) - np.array(cpt)
            dist = np.linalg.norm(vec)
            if dist<0.15:
                f = 0.012*(0.15-dist)/0.15
                x += vec[0]*f
                y += vec[1]*f
        x = np.clip(x, margin+0.005, 1-margin-0.005)
        y = np.clip(y, margin+0.005, 1-margin-0.005)
        centers[idx] = [x, y]
        idx += 1

    assert idx == n

    # --- 2. Force-directed relaxation/annealing ---
    np.random.seed(42)
    iters = 120
    init_step = 0.018
    anneal = 0.82
    radii = compute_max_radii_iterative(centers, passes=4)
    for it in range(iters):
        forces = np.zeros_like(centers)
        # Pairwise repulsion if overlap (strong), soft if close
        for i in range(n):
            for j in range(i+1, n):
                v = centers[i]-centers[j]
                d = np.linalg.norm(v)
                min_dist = radii[i]+radii[j]+1e-7
                if d<min_dist:
                    push = 0.15*(min_dist-d)/(d+1e-8)
                elif d<min_dist+0.06:
                    push = 0.05*(min_dist+0.06-d)/(d+1e-8)
                else:
                    push = 0
                if push>0:
                    delta = v*push
                    forces[i] += delta
                    forces[j] -= delta
        # Mild attraction toward square center (for outer circles)
        for i in range(n):
            dcen = centers[i]-np.array([0.5,0.5])
            if np.linalg.norm(dcen)>0.34:
                forces[i] -= 0.014*dcen
        # Boundary forces: confine inside (0,1), with strong restoring if near edge
        for i in range(n):
            for d in [0,1]:
                for coord in range(2):
                    dist = abs(centers[i,coord]-d)
                    if dist<radii[i]+0.004:
                        sign = -1 if d==0 else 1
                        forces[i,coord] += sign*0.10*(radii[i]+0.004-dist)
        # Anneal step size
        step = init_step*(anneal**(it))
        # Random jitter (decaying)
        jitter = np.random.randn(*centers.shape)*0.003*(0.85**(it))
        # Update positions
        centers += step*forces + jitter
        # Ensure inside square
        centers = np.clip(centers, margin+1e-3, 1-margin-1e-3)
        # Update radii after each move
        radii = compute_max_radii_iterative(centers, passes=2)
    # Final: tighten radii with more iterations
    radii = compute_max_radii_iterative(centers, passes=12)
    return centers, radii

def compute_max_radii_iterative(centers, passes=5):
    """Compute maximal radii for given centers without overlap or boundary violation."""
    n = centers.shape[0]
    radii = np.ones(n)
    # Initial: border-limited
    for i in range(n):
        x, y = centers[i]
        radii[i] = min(x, y, 1-x, 1-y)
    for _ in range(passes):
        for i in range(n):
            min_r = min(centers[i][0], centers[i][1], 1 - centers[i][0], 1 - centers[i][1])
            for j in range(n):
                if i==j: continue
                d = np.linalg.norm(centers[i]-centers[j])
                min_r = min(min_r, d-radii[j])
            radii[i] = max(min_r, 1e-7)
    return radii

# EVOLVE-BLOCK-END


# This part remains fixed (not evolved)
def run_packing():
    """Run the circle packing constructor for n=26"""
    centers, radii = construct_packing()
    # Calculate the sum of radii
    sum_radii = np.sum(radii)
    return centers, radii, sum_radii