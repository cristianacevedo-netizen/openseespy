"""
Multi-Story Frame Analysis
===========================
This example demonstrates the analysis of a multi-story frame building using OpenSeesPy.
The structure is subjected to gravity and lateral loads.

Reference: https://openseespydoc.readthedocs.io/en/stable/index.html
"""

import openseespy.opensees as ops
import numpy as np

# Initialize
ops.wipe()

# Model dimensions: 2D model with 3 DOF per node
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Building geometry
num_stories = 4
story_height = 144.0  # in (12 ft)
bay_width = 240.0     # in (20 ft)
num_bays = 3

# Define nodes
node_tag = 1
for floor in range(num_stories + 1):
    for bay in range(num_bays + 1):
        x = bay * bay_width
        y = floor * story_height
        ops.node(node_tag, x, y)
        
        # Fix base nodes
        if floor == 0:
            ops.fix(node_tag, 1, 1, 1)
        
        node_tag += 1

# Define geometric transformation
ops.geomTransf('PDelta', 1)

# Define material properties
E = 29000.0    # ksi

# Column properties (W14x90)
A_col = 26.5   # in^2
I_col = 999.0  # in^4

# Beam properties (W18x50)
A_beam = 14.7  # in^2
I_beam = 800.0 # in^4

# Define elements
elem_tag = 1

# Columns
for floor in range(num_stories):
    for bay in range(num_bays + 1):
        node_i = floor * (num_bays + 1) + bay + 1
        node_j = (floor + 1) * (num_bays + 1) + bay + 1
        ops.element('elasticBeamColumn', elem_tag, node_i, node_j, 
                    A_col, E, I_col, 1)
        elem_tag += 1

# Beams
for floor in range(1, num_stories + 1):
    for bay in range(num_bays):
        node_i = floor * (num_bays + 1) + bay + 1
        node_j = floor * (num_bays + 1) + bay + 2
        ops.element('elasticBeamColumn', elem_tag, node_i, node_j, 
                    A_beam, E, I_beam, 1)
        elem_tag += 1

# Define masses (for dynamic analysis, if needed later)
mass_per_node = 5.0  # kip-sec^2/in
for floor in range(1, num_stories + 1):
    for bay in range(num_bays + 1):
        node_num = floor * (num_bays + 1) + bay + 1
        ops.mass(node_num, mass_per_node, mass_per_node, 0.0)

# Define load patterns
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply gravity loads on beams
gravity_load = -5.0  # kip (distributed load represented as nodal loads)
for floor in range(1, num_stories + 1):
    for bay in range(1, num_bays):
        node_num = floor * (num_bays + 1) + bay + 1
        ops.load(node_num, 0.0, gravity_load, 0.0)
    
    # Corner loads (half)
    node_left = floor * (num_bays + 1) + 1
    node_right = floor * (num_bays + 1) + num_bays + 1
    ops.load(node_left, 0.0, gravity_load/2, 0.0)
    ops.load(node_right, 0.0, gravity_load/2, 0.0)

# Apply lateral loads (wind/seismic)
ops.timeSeries('Linear', 2)
ops.pattern('Plain', 2, 2)

lateral_loads = [30.0, 25.0, 20.0, 15.0]  # kip at each floor
for floor in range(1, num_stories + 1):
    node_left = floor * (num_bays + 1) + 1
    lateral_load = lateral_loads[floor - 1]
    ops.load(node_left, lateral_load, 0.0, 0.0)

# Analysis setup
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 0.1)
ops.algorithm('Newton')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.analysis('Static')

# Perform analysis
num_steps = 10
ops.analyze(num_steps)

# Get and print results
print("=" * 70)
print("Multi-Story Frame Analysis Results")
print("=" * 70)
print(f"\nLateral Displacements at each floor (left column):")
for floor in range(1, num_stories + 1):
    node_num = floor * (num_bays + 1) + 1
    disp = ops.nodeDisp(node_num, 1)
    print(f"  Floor {floor}: {disp:.6f} in")

print(f"\nStory Drift Ratios:")
prev_disp = 0.0
for floor in range(1, num_stories + 1):
    node_num = floor * (num_bays + 1) + 1
    disp = ops.nodeDisp(node_num, 1)
    drift = (disp - prev_disp) / story_height
    print(f"  Story {floor}: {drift:.6e} (or {drift*100:.4f}%)")
    prev_disp = disp

# Check maximum base reactions
print(f"\nBase Reactions:")
total_h_reaction = 0.0
total_v_reaction = 0.0
for bay in range(num_bays + 1):
    node_num = bay + 1
    reaction = ops.nodeReaction(node_num)
    total_h_reaction += reaction[0]
    total_v_reaction += reaction[1]
    print(f"  Base node {node_num}: Fx={reaction[0]:.2f} kip, Fy={reaction[1]:.2f} kip")

print(f"\nTotal Base Reactions:")
print(f"  Horizontal: {total_h_reaction:.2f} kip")
print(f"  Vertical: {total_v_reaction:.2f} kip")
print("=" * 70)

# Clean up
ops.wipe()
