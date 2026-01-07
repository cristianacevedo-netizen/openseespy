"""
Cantilever Beam Example
========================
This example demonstrates a cantilever beam analysis using OpenSeesPy.
The beam is modeled with elastic beam-column elements and subjected to a point load.

Reference: https://openseespydoc.readthedocs.io/en/stable/index.html
"""

import openseespy.opensees as ops

# Initialize
ops.wipe()

# Model dimensions: 2D model with 3 DOF per node (2 translations + 1 rotation)
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Define nodes
# node(nodeTag, x, y)
ops.node(1, 0.0, 0.0)
ops.node(2, 144.0, 0.0)

# Fix node 1 (cantilever support - all DOF fixed)
# fix(nodeTag, dx, dy, rz)
ops.fix(1, 1, 1, 1)

# Define geometric transformation
ops.geomTransf('Linear', 1)

# Define material properties
E = 29000.0  # Young's modulus (ksi)
A = 20.0     # Cross-sectional area (in^2)
I = 1400.0   # Moment of inertia (in^4)

# Define element
# element(eleType, eleTag, iNode, jNode, A, E, I, transfTag)
ops.element('elasticBeamColumn', 1, 1, 2, A, E, I, 1)

# Define load pattern
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply vertical load at free end (node 2)
# load(nodeTag, Fx, Fy, Mz)
ops.load(2, 0.0, -10.0, 0.0)

# Analysis setup
ops.system('BandGeneral')
ops.numberer('Plain')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

# Perform analysis
ops.analyze(1)

# Get results
disp_x = ops.nodeDisp(2, 1)
disp_y = ops.nodeDisp(2, 2)
rotation = ops.nodeDisp(2, 3)
forces = ops.eleForce(1)

# Print results
print("=" * 60)
print("Cantilever Beam Analysis Results")
print("=" * 60)
print(f"Displacement at free end (node 2):")
print(f"  Horizontal: {disp_x:.6e} in")
print(f"  Vertical: {disp_y:.6e} in")
print(f"  Rotation: {rotation:.6e} rad")
print(f"\nElement forces at node 1:")
print(f"  Axial: {forces[0]:.6f} kip")
print(f"  Shear: {forces[1]:.6f} kip")
print(f"  Moment: {forces[2]:.6f} kip-in")
print("=" * 60)

# Clean up
ops.wipe()
