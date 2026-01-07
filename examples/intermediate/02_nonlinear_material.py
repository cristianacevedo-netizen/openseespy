"""
Nonlinear Material Analysis
=============================
This example demonstrates the use of nonlinear materials in OpenSeesPy.
A cantilever column is subjected to cyclic loading with Steel02 material.

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
L = 120.0  # Column height (in)
ops.node(1, 0.0, 0.0)
ops.node(2, 0.0, L)

# Fix base node
ops.fix(1, 1, 1, 1)

# Define material - Steel02 (Giuffre-Menegotto-Pinto model)
Fy = 60.0       # Yield stress (ksi)
E = 29000.0     # Young's modulus (ksi)
b = 0.02        # Strain hardening ratio
R0 = 18.0       # Parameter for transition from elastic to plastic
cR1 = 0.925     # Parameter for transition
cR2 = 0.15      # Parameter for transition

ops.uniaxialMaterial('Steel02', 1, Fy, E, b, R0, cR1, cR2)

# Define geometric transformation
ops.geomTransf('PDelta', 1)

# Define section (fiber section)
d = 18.0        # Section depth (in)
bf = 12.0       # Flange width (in)
tf = 1.0        # Flange thickness (in)
tw = 0.5        # Web thickness (in)

ops.section('Fiber', 1)
# Define fibers for a simplified I-section
nf = 20
for i in range(nf):
    yLoc = -d/2 + (d/nf)*(i+0.5)
    if abs(yLoc) > (d/2 - tf):
        area = bf * (d/nf)
    else:
        area = tw * (d/nf)
    ops.fiber(yLoc, 0.0, area, 1)

# Define element
nIP = 5  # Number of integration points
ops.element('forceBeamColumn', 1, 1, 2, nIP, 1, 1)

# Define cyclic loading pattern
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, 1.0, 0.0, 0.0)  # Reference load

# Analysis setup
ops.system('BandGeneral')
ops.numberer('Plain')
ops.constraints('Plain')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.algorithm('Newton')
ops.integrator('DisplacementControl', 2, 1, 0.1)
ops.analysis('Static')

# Define loading protocol (cyclic)
displacements = [1, -2, 2, -3, 3, -4, 4, -3, 3, -2, 2, -1, 1, 0]
disp_history = []
force_history = []

print("Starting cyclic pushover analysis...")

for target_disp in displacements:
    current_disp = ops.nodeDisp(2, 1)
    disp_incr = target_disp - current_disp
    num_steps = max(int(abs(disp_incr) / 0.1), 1)
    
    for step in range(num_steps):
        ops.analyze(1)
        disp = ops.nodeDisp(2, 1)
        force = ops.eleForce(1)
        disp_history.append(disp)
        force_history.append(force[0])

# Plot hysteresis curve
plt.figure(figsize=(10, 6))
plt.plot(disp_history, force_history, 'b-', linewidth=1.5)
plt.xlabel('Displacement (in)')
plt.ylabel('Base Shear (kip)')
plt.title('Cyclic Pushover Analysis - Hysteresis Curve')
plt.grid(True)
plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
plt.axvline(x=0, color='k', linestyle='-', linewidth=0.5)
plt.tight_layout()
plt.savefig('/tmp/nonlinear_hysteresis.png', dpi=150)
print("Hysteresis curve saved to /tmp/nonlinear_hysteresis.png")

# Print summary
print("=" * 60)
print("Nonlinear Material Analysis Results")
print("=" * 60)
print(f"Maximum displacement: {max(disp_history):.4f} in")
print(f"Maximum force: {max(force_history):.4f} kip")
print(f"Energy dissipated (area under curve): {np.trapz(force_history, disp_history):.2f} kip-in")
print("=" * 60)

# Clean up
ops.wipe()
