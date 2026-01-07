"""
Dynamic Analysis - SDOF System
================================
This example demonstrates a dynamic analysis of a Single Degree of Freedom (SDOF) system
subjected to earthquake ground motion using OpenSeesPy.

Reference: https://openseespydoc.readthedocs.io/en/stable/index.html
"""

import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt

# Initialize
ops.wipe()

# Model dimensions: 2D model with 2 DOF per node
ops.model('basic', '-ndm', 2, '-ndf', 2)

# Define nodes
ops.node(1, 0.0, 0.0)
ops.node(2, 0.0, 0.0)

# Fix base node
ops.fix(1, 1, 1)

# Define mass at node 2
mass = 100.0  # kip-sec^2/in (mass)
ops.mass(2, mass, mass)

# Define material (bilinear with hardening)
K = 100.0      # Initial stiffness (kip/in)
Fy = 50.0      # Yield strength (kip)
b = 0.05       # Hardening ratio
ops.uniaxialMaterial('Steel01', 1, Fy, K, b)

# Define zero-length element
ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 1)

# Define time series and load pattern for earthquake
dt = 0.01      # Time step (sec)
npts = 1000    # Number of points

# Create synthetic ground motion (sine wave)
time = np.linspace(0, dt*npts, npts)
accel = 0.3 * np.sin(2*np.pi*2.0*time) * np.exp(-0.5*time)

# Write ground motion to file
with open('/tmp/ground_motion.txt', 'w') as f:
    for a in accel:
        f.write(f"{a}\n")

# Define time series
ops.timeSeries('Path', 1, '-dt', dt, '-filePath', '/tmp/ground_motion.txt', '-factor', 386.4)

# Define uniform excitation (earthquake)
ops.pattern('UniformExcitation', 1, 1, '-accel', 1)

# Define damping
omega = np.sqrt(K/mass)
freq = omega / (2*np.pi)
dampRatio = 0.05
ops.rayleigh(0.0, 0.0, 0.0, 2*dampRatio/omega)

# Analysis setup
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('Newmark', 0.5, 0.25)
ops.algorithm('Linear')
ops.analysis('Transient')

# Perform analysis and record results
disp_history = []
time_history = []

for i in range(npts):
    ops.analyze(1, dt)
    disp = ops.nodeDisp(2, 1)
    disp_history.append(disp)
    time_history.append(i*dt)

# Plot results
plt.figure(figsize=(12, 8))

plt.subplot(2, 1, 1)
plt.plot(time_history, accel[:len(time_history)])
plt.xlabel('Time (sec)')
plt.ylabel('Acceleration (g)')
plt.title('Ground Motion Acceleration')
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(time_history, disp_history)
plt.xlabel('Time (sec)')
plt.ylabel('Displacement (in)')
plt.title('SDOF System Response')
plt.grid(True)

plt.tight_layout()
plt.savefig('/tmp/dynamic_analysis_results.png', dpi=150)
print("Results saved to /tmp/dynamic_analysis_results.png")

# Print summary
print("=" * 60)
print("Dynamic Analysis Results - SDOF System")
print("=" * 60)
print(f"Natural frequency: {freq:.4f} Hz")
print(f"Period: {1/freq:.4f} sec")
print(f"Maximum displacement: {max(disp_history):.6f} in")
print(f"Minimum displacement: {min(disp_history):.6f} in")
print("=" * 60)

# Clean up
ops.wipe()
