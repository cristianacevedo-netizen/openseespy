"""
Simple Truss Example
=====================
This example demonstrates a basic 2D truss analysis using OpenSeesPy.
The truss consists of two nodes connected by a single element.

Reference: https://openseespydoc.readthedocs.io/en/stable/index.html
"""

import openseespy.opensees as ops
import numpy as np

# Initialize
ops.wipe()

# Model dimensions: 2D model with 2 degrees of freedom (DOF) per node
ops.model('basic', '-ndm', 2, '-ndf', 2)

# Define nodes
# node(nodeTag, x, y)
ops.node(1, 0.0, 0.0)
ops.node(2, 120.0, 0.0)

# Fix node 1 (support) - both DOF fixed
# fix(nodeTag, dx, dy)
ops.fix(1, 1, 1)

# Fix node 2 in Y direction only (roller support)
ops.fix(2, 0, 1)

# Define material
# uniaxialMaterial(matType, matTag, E)
E = 3000.0  # Young's modulus (ksi)
ops.uniaxialMaterial('Elastic', 1, E)

# Define element
# element(eleType, eleTag, iNode, jNode, A, matTag)
A = 10.0  # Cross-sectional area (in^2)
ops.element('Truss', 1, 1, 2, A, 1)

# Define load pattern
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply load at node 2
# load(nodeTag, Fx, Fy)
ops.load(2, 100.0, 0.0)  # Only horizontal load since Y is fixed

# Analysis setup
ops.system('BandSPD')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

# Perform analysis
ops.analyze(1)

# Get results
disp_x = ops.nodeDisp(2, 1)
disp_y = ops.nodeDisp(2, 2)
force = ops.eleForce(1)

# Print results
print("=" * 50)
print("Simple Truss Analysis Results")
print("=" * 50)
print(f"Displacement at node 2:")
print(f"  X-direction: {disp_x:.6f} in")
print(f"  Y-direction: {disp_y:.6f} in")
print(f"\nElement forces:")
print(f"  Axial force: {force[0]:.6f} kip")
print("=" * 50)

# Clean up
ops.wipe()
