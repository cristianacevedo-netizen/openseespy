"""
2D Frame Structure Example
===========================
This example demonstrates a simple 2D frame analysis using OpenSeesPy.
The frame consists of a portal frame with horizontal and vertical members.

Reference: https://openseespydoc.readthedocs.io/en/stable/index.html
"""

import openseespy.opensees as ops

# Initialize
ops.wipe()

# Model dimensions: 2D model with 3 DOF per node
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Define nodes
# Corner nodes of the frame
ops.node(1, 0.0, 0.0)      # Bottom left
ops.node(2, 0.0, 120.0)    # Top left
ops.node(3, 240.0, 120.0)  # Top right
ops.node(4, 240.0, 0.0)    # Bottom right

# Fix base nodes (pinned supports)
ops.fix(1, 1, 1, 0)
ops.fix(4, 1, 1, 0)

# Define geometric transformation
ops.geomTransf('Linear', 1)

# Define material properties
E = 29000.0   # Young's modulus (ksi)
A = 15.0      # Cross-sectional area (in^2)
I = 800.0     # Moment of inertia (in^4)

# Define elements
# Columns
ops.element('elasticBeamColumn', 1, 1, 2, A, E, I, 1)  # Left column
ops.element('elasticBeamColumn', 2, 4, 3, A, E, I, 1)  # Right column

# Beam
ops.element('elasticBeamColumn', 3, 2, 3, A, E, I, 1)  # Top beam

# Define load pattern
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply loads
# Horizontal load at top left node (wind load)
ops.load(2, 50.0, 0.0, 0.0)

# Vertical load on beam (gravity load)
ops.load(3, 0.0, -100.0, 0.0)

# Analysis setup
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

# Perform analysis
ops.analyze(1)

# Get results
print("=" * 60)
print("2D Frame Structure Analysis Results")
print("=" * 60)
print(f"\nNode Displacements:")
for node in [1, 2, 3, 4]:
    disp_x = ops.nodeDisp(node, 1)
    disp_y = ops.nodeDisp(node, 2)
    rotation = ops.nodeDisp(node, 3)
    print(f"  Node {node}:")
    print(f"    X: {disp_x:.6e} in")
    print(f"    Y: {disp_y:.6e} in")
    print(f"    Rotation: {rotation:.6e} rad")

print(f"\nElement Forces:")
for elem in [1, 2, 3]:
    forces = ops.eleForce(elem)
    print(f"  Element {elem}:")
    print(f"    Node i - Axial: {forces[0]:.4f}, Shear: {forces[1]:.4f}, Moment: {forces[2]:.4f}")
    print(f"    Node j - Axial: {forces[3]:.4f}, Shear: {forces[4]:.4f}, Moment: {forces[5]:.4f}")

print("=" * 60)

# Clean up
ops.wipe()
