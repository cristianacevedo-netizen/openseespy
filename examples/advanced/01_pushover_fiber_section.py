"""
Pushover Analysis with Fiber Section
=====================================
This example demonstrates a nonlinear pushover analysis of a reinforced concrete column
using fiber sections in OpenSeesPy.

Reference: https://openseespydoc.readthedocs.io/en/stable/index.html
"""

import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt

# Initialize
ops.wipe()

# Model dimensions: 2D model with 3 DOF per node
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Define nodes
L = 180.0  # Column height (in)
ops.node(1, 0.0, 0.0)
ops.node(2, 0.0, L)

# Fix base node
ops.fix(1, 1, 1, 1)

# Define axial load
P = 500.0  # kip
ops.load(2, 0.0, -P, 0.0)

# Define materials for RC section
# Concrete (confined and unconfined)
fc = -4.0      # Concrete compressive strength (ksi, negative)
Ec = 57*np.sqrt(-fc*1000)  # Concrete elastic modulus (ksi)

# Confined concrete (core)
fcc = 1.3 * fc  # Confined strength
epsc0 = 2*fcc/Ec
epscu = 0.02
ops.uniaxialMaterial('Concrete02', 1, fcc, epsc0, fc*0.2, epscu, 0.1, fcc, epsc0)

# Unconfined concrete (cover)
ops.uniaxialMaterial('Concrete02', 2, fc, -0.002, fc*0.2, -0.006, 0.1, fc, -0.002)

# Steel
fy = 60.0       # Steel yield strength (ksi)
Es = 29000.0    # Steel elastic modulus (ksi)
b = 0.02        # Strain hardening ratio
ops.uniaxialMaterial('Steel02', 3, fy, Es, b, 20, 0.925, 0.15)

# Define RC section (20"x20" column)
col_width = 20.0   # in
col_depth = 20.0   # in
cover = 2.0        # in
core_width = col_width - 2*cover
core_depth = col_depth - 2*cover

# Number of fibers
nf_core_y = 10
nf_core_z = 10
nf_cover_y = 10
nf_cover_z = 2

ops.section('Fiber', 1)

# Core concrete
y_core = [-core_depth/2 + (core_depth/nf_core_y)*(i+0.5) for i in range(nf_core_y)]
z_core = [-core_width/2 + (core_width/nf_core_z)*(i+0.5) for i in range(nf_core_z)]

for y in y_core:
    for z in z_core:
        area = (core_depth/nf_core_y) * (core_width/nf_core_z)
        ops.fiber(y, z, area, 1)

# Cover concrete (top and bottom)
y_cover_tb = []
for i in range(nf_cover_y):
    y_cover_tb.append(-col_depth/2 + (cover/nf_cover_z)*(i+0.5))
    y_cover_tb.append(col_depth/2 - (cover/nf_cover_z)*(i+0.5))

for y in y_cover_tb:
    for i in range(nf_cover_y):
        z = -col_width/2 + (col_width/nf_cover_y)*(i+0.5)
        area = (col_width/nf_cover_y) * (cover/nf_cover_z)
        ops.fiber(y, z, area, 2)

# Cover concrete (left and right)
z_cover_lr = [-col_width/2 + (cover/nf_cover_z)*(i+0.5) for i in range(nf_cover_z)]
z_cover_lr.extend([col_width/2 - (cover/nf_cover_z)*(i+0.5) for i in range(nf_cover_z)])

for z in z_cover_lr:
    for i in range(nf_core_y):
        y = -core_depth/2 + (core_depth/nf_core_y)*(i+0.5)
        area = (core_depth/nf_core_y) * (cover/nf_cover_z)
        ops.fiber(y, z, area, 2)

# Reinforcing steel (8 #9 bars)
bar_area = 1.0  # in^2
bar_positions = [
    (-core_depth/2, -core_width/2),
    (-core_depth/2, 0.0),
    (-core_depth/2, core_width/2),
    (0.0, -core_width/2),
    (0.0, core_width/2),
    (core_depth/2, -core_width/2),
    (core_depth/2, 0.0),
    (core_depth/2, core_width/2),
]

for y, z in bar_positions:
    ops.fiber(y, z, bar_area, 3)

# Define geometric transformation
ops.geomTransf('PDelta', 1)

# Define element
nIP = 5
ops.element('forceBeamColumn', 1, 1, 2, nIP, 1, 1)

# Gravity analysis
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, 0.0, -P, 0.0)

ops.system('BandGeneral')
ops.numberer('Plain')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Newton')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.analysis('Static')
ops.analyze(1)

# Maintain constant axial load
ops.loadConst('-time', 0.0)

# Lateral pushover analysis
ops.timeSeries('Linear', 2)
ops.pattern('Plain', 2, 2)
ops.load(2, 1.0, 0.0, 0.0)

# Change to displacement control
target_disp = 10.0
disp_incr = 0.05
num_steps = int(target_disp / disp_incr)

ops.integrator('DisplacementControl', 2, 1, disp_incr)

# Perform pushover analysis
disp_history = []
force_history = []

print("Performing pushover analysis...")
for i in range(num_steps):
    ok = ops.analyze(1)
    if ok != 0:
        print(f"Analysis failed at step {i}")
        break
    
    disp = ops.nodeDisp(2, 1)
    force = ops.eleForce(1)
    disp_history.append(disp)
    force_history.append(-force[0])  # Base shear

# Plot pushover curve
plt.figure(figsize=(10, 6))
plt.plot(disp_history, force_history, 'b-', linewidth=2)
plt.xlabel('Roof Displacement (in)')
plt.ylabel('Base Shear (kip)')
plt.title('RC Column Pushover Curve')
plt.grid(True)
plt.tight_layout()
plt.savefig('/tmp/pushover_curve.png', dpi=150)
print("Pushover curve saved to /tmp/pushover_curve.png")

# Print summary
print("=" * 60)
print("Pushover Analysis Results")
print("=" * 60)
print(f"Maximum displacement reached: {max(disp_history):.4f} in")
print(f"Maximum base shear: {max(force_history):.4f} kip")
# Note: Yield displacement calculation is approximate and should be
# determined by more sophisticated methods in practice (e.g., bilinear fit)
print("=" * 60)

# Clean up
ops.wipe()
