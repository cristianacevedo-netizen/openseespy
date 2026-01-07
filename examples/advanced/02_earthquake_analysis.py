"""
Earthquake Time History Analysis
=================================
This example demonstrates a complete earthquake time history analysis of a multi-story
building using OpenSeesPy with recorded ground motion.

Reference: https://openseespydoc.readthedocs.io/en/stable/index.html
"""

import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt

# Initialize
ops.wipe()

# Model dimensions: 2D model with 3 DOF per node
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Building parameters
num_stories = 3
story_height = 144.0  # in
bay_width = 240.0     # in

# Define nodes
for i in range(num_stories + 1):
    ops.node(2*i + 1, 0.0, i * story_height)
    ops.node(2*i + 2, bay_width, i * story_height)

# Fix base nodes
ops.fix(1, 1, 1, 1)
ops.fix(2, 1, 1, 1)

# Define geometric transformation
ops.geomTransf('PDelta', 1)

# Material properties
E = 29000.0  # ksi

# Define sections and elements
A_col = 20.0
I_col = 800.0
A_beam = 15.0
I_beam = 600.0

# Columns
for i in range(num_stories):
    ops.element('elasticBeamColumn', 2*i + 1, 2*i + 1, 2*i + 3, A_col, E, I_col, 1)
    ops.element('elasticBeamColumn', 2*i + 2, 2*i + 2, 2*i + 4, A_col, E, I_col, 1)

# Beams
for i in range(1, num_stories + 1):
    ops.element('elasticBeamColumn', 2*num_stories + i, 2*i + 1, 2*i + 2, A_beam, E, I_beam, 1)

# Define masses
masses = [10.0, 10.0, 8.0]  # kip-sec^2/in
for i in range(num_stories):
    ops.mass(2*i + 3, masses[i], masses[i], 0.0)
    ops.mass(2*i + 4, masses[i], masses[i], 0.0)

# Modal analysis to get periods
num_modes = 3
eigenValues = ops.eigen(num_modes)
periods = [2*np.pi/np.sqrt(ev) for ev in eigenValues]

print("=" * 60)
print("Modal Analysis Results")
print("=" * 60)
for i, T in enumerate(periods):
    print(f"Mode {i+1}: T = {T:.4f} sec, f = {1/T:.4f} Hz")
print("=" * 60)

# Define damping (Rayleigh)
dampRatio = 0.05
omega1 = 2*np.pi/periods[0]
omega2 = 2*np.pi/periods[1]
a0 = dampRatio * 2 * omega1 * omega2 / (omega1 + omega2)
a1 = dampRatio * 2 / (omega1 + omega2)
ops.rayleigh(a0, 0.0, 0.0, a1)

# Generate synthetic earthquake record
dt = 0.01  # sec
duration = 20.0  # sec
npts = int(duration / dt)
time = np.linspace(0, duration, npts)

# Create a synthetic ground motion (modulated sine wave)
freq_content = [1.0, 2.5, 4.0]  # Hz
amplitudes = [0.2, 0.15, 0.1]  # g
accel = np.zeros(npts)

for freq, amp in zip(freq_content, amplitudes):
    accel += amp * np.sin(2*np.pi*freq*time)

# Apply envelope function
envelope = np.exp(-0.3*time) * (1 - np.exp(-2*time))
accel = accel * envelope

# Write to file
gm_file = '/tmp/earthquake.txt'
with open(gm_file, 'w') as f:
    for a in accel:
        f.write(f"{a}\n")

# Define time series for earthquake
ops.timeSeries('Path', 1, '-dt', dt, '-filePath', gm_file, '-factor', 386.4)

# Define uniform excitation pattern
ops.pattern('UniformExcitation', 1, 1, '-accel', 1)

# Analysis setup
ops.wipeAnalysis()
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Transformation')
ops.integrator('Newmark', 0.5, 0.25)
ops.algorithm('Newton')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.analysis('Transient')

# Perform time history analysis
print("\nPerforming earthquake time history analysis...")
roof_disp = []
base_shear = []
time_history = []

for i in range(npts):
    ok = ops.analyze(1, dt)
    if ok != 0:
        print(f"Analysis failed at time {i*dt:.2f} sec")
        break
    
    # Record roof displacement (top left node)
    disp = ops.nodeDisp(2*num_stories + 1, 1)
    roof_disp.append(disp)
    
    # Calculate base shear
    shear = 0.0
    for j in range(1, 3):  # Base nodes
        reaction = ops.nodeReaction(j)
        shear += reaction[0]
    base_shear.append(shear)
    
    time_history.append(i*dt)
    
    if i % 500 == 0:
        print(f"  Time: {i*dt:.2f} sec")

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Ground motion
axes[0].plot(time_history, accel[:len(time_history)], 'k-', linewidth=0.8)
axes[0].set_ylabel('Acceleration (g)')
axes[0].set_title('Ground Motion')
axes[0].grid(True)

# Roof displacement
axes[1].plot(time_history, roof_disp, 'b-', linewidth=1)
axes[1].set_ylabel('Displacement (in)')
axes[1].set_title('Roof Displacement Time History')
axes[1].grid(True)

# Base shear
axes[2].plot(time_history, base_shear, 'r-', linewidth=1)
axes[2].set_xlabel('Time (sec)')
axes[2].set_ylabel('Base Shear (kip)')
axes[2].set_title('Base Shear Time History')
axes[2].grid(True)

plt.tight_layout()
plt.savefig('/tmp/earthquake_analysis.png', dpi=150)
print("\nResults saved to /tmp/earthquake_analysis.png")

# Print summary
print("=" * 60)
print("Earthquake Analysis Summary")
print("=" * 60)
print(f"Peak ground acceleration: {max(abs(accel)):.4f} g")
print(f"Maximum roof displacement: {max(np.abs(roof_disp)):.4f} in")
print(f"Maximum base shear: {max(np.abs(base_shear)):.4f} kip")
print(f"Maximum story drift ratio: {max(np.abs(roof_disp))/(num_stories*story_height):.6f}")
print("=" * 60)

# Clean up
ops.wipe()
