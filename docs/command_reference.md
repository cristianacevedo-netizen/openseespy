# OpenSeesPy Command Reference

Este documento proporciona una referencia rápida de los comandos más utilizados en OpenSeesPy.

Referencia completa: https://openseespydoc.readthedocs.io/en/stable/index.html

## Comandos Básicos

### Model Setup

```python
import openseespy.opensees as ops

# Limpiar modelo existente
ops.wipe()

# Definir modelo
# -ndm: dimensiones (2 o 3)
# -ndf: grados de libertad por nodo
ops.model('basic', '-ndm', 2, '-ndf', 3)
```

### Nodes

```python
# Crear nodo
# node(nodeTag, x, y, [z])
ops.node(1, 0.0, 0.0)
ops.node(2, 120.0, 0.0)

# Fijar nodo (boundary conditions)
# fix(nodeTag, dx, dy, [dz], [rx], [ry], [rz])
ops.fix(1, 1, 1, 1)  # Todos los DOF fijos
ops.fix(2, 0, 1, 0)  # Solo Y fijo

# Asignar masa
# mass(nodeTag, mx, my, [mz])
ops.mass(2, 100.0, 100.0)
```

### Materials

```python
# Material uniaxial elástico
# uniaxialMaterial(matType, matTag, E)
ops.uniaxialMaterial('Elastic', 1, 29000.0)

# Material Steel01
# uniaxialMaterial('Steel01', matTag, Fy, E0, b)
ops.uniaxialMaterial('Steel01', 2, 60.0, 29000.0, 0.02)

# Material Steel02 (Giuffre-Menegotto-Pinto)
# uniaxialMaterial('Steel02', matTag, Fy, E0, b, R0, cR1, cR2)
ops.uniaxialMaterial('Steel02', 3, 60.0, 29000.0, 0.02, 18.0, 0.925, 0.15)

# Material Concrete01
# uniaxialMaterial('Concrete01', matTag, fpc, epsc0, fpcu, epscu)
ops.uniaxialMaterial('Concrete01', 4, -4.0, -0.002, -0.8, -0.006)

# Material Concrete02
# uniaxialMaterial('Concrete02', matTag, fpc, epsc0, fpcu, epscu, lambda, ft, Ets)
ops.uniaxialMaterial('Concrete02', 5, -4.0, -0.002, -0.8, -0.006, 0.1, 0.4, 0.4)
```

### Elements

```python
# Transformación geométrica
ops.geomTransf('Linear', 1)
ops.geomTransf('PDelta', 2)
ops.geomTransf('Corotational', 3)

# Elemento Truss
# element('Truss', eleTag, iNode, jNode, A, matTag)
ops.element('Truss', 1, 1, 2, 10.0, 1)

# Elemento elasticBeamColumn
# element('elasticBeamColumn', eleTag, iNode, jNode, A, E, I, transfTag)
ops.element('elasticBeamColumn', 1, 1, 2, 20.0, 29000.0, 1400.0, 1)

# Elemento forceBeamColumn (nonlinear)
# element('forceBeamColumn', eleTag, iNode, jNode, numIntgrPts, secTag, transfTag)
ops.element('forceBeamColumn', 1, 1, 2, 5, 1, 1)

# Elemento zeroLength
# element('zeroLength', eleTag, iNode, jNode, '-mat', matTag, '-dir', dir)
ops.element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 1)
```

### Sections

```python
# Sección Fiber
ops.section('Fiber', 1)

# Agregar fibras
# fiber(yLoc, zLoc, A, matTag)
ops.fiber(0.0, 0.0, 10.0, 1)

# Sección Elastic
# section('Elastic', secTag, E, A, Iz, [Iy], [G], [J])
ops.section('Elastic', 1, 29000.0, 20.0, 1400.0)
```

## Cargas y Patrones

```python
# Time Series
ops.timeSeries('Linear', 1)
ops.timeSeries('Constant', 2)
ops.timeSeries('Path', 3, '-dt', 0.01, '-filePath', 'motion.txt', '-factor', 1.0)

# Pattern
ops.pattern('Plain', 1, 1)

# Carga nodal
# load(nodeTag, Fx, Fy, [Fz], [Mx], [My], [Mz])
ops.load(2, 100.0, -50.0, 0.0)

# Uniform Excitation (earthquake)
ops.pattern('UniformExcitation', 1, 1, '-accel', 1)

# Mantener cargas constantes
ops.loadConst('-time', 0.0)
```

## Análisis

### Static Analysis

```python
# System
ops.system('BandGeneral')
ops.system('BandSPD')
ops.system('ProfileSPD')
ops.system('FullGeneral')

# Numberer
ops.numberer('Plain')
ops.numberer('RCM')

# Constraints
ops.constraints('Plain')
ops.constraints('Transformation')
ops.constraints('Penalty', 1e15, 1e15)

# Integrator
ops.integrator('LoadControl', 0.1)
ops.integrator('DisplacementControl', nodeTag, dof, incr)

# Algorithm
ops.algorithm('Linear')
ops.algorithm('Newton')
ops.algorithm('NewtonLineSearch')
ops.algorithm('ModifiedNewton')

# Test
ops.test('NormDispIncr', 1.0e-6, 100)
ops.test('NormUnbalance', 1.0e-6, 100)

# Analysis
ops.analysis('Static')

# Analyze
ops.analyze(numSteps)
```

### Dynamic Analysis

```python
# Integrator
ops.integrator('Newmark', 0.5, 0.25)
ops.integrator('HHT', 0.9)

# Analysis
ops.analysis('Transient')

# Analyze
ops.analyze(numSteps, dt)

# Damping (Rayleigh)
# rayleigh(alphaM, betaK, betaKinit, betaKcomm)
ops.rayleigh(a0, 0.0, 0.0, a1)
```

### Modal Analysis

```python
# Eigen analysis
# eigen(numModes)
eigenValues = ops.eigen(3)

# Calculate periods
import numpy as np
periods = [2*np.pi/np.sqrt(ev) for ev in eigenValues]
```

## Resultados

```python
# Desplazamiento nodal
# nodeDisp(nodeTag, dof)
disp = ops.nodeDisp(2, 1)

# Reacción nodal
# nodeReaction(nodeTag)
reaction = ops.nodeReaction(1)

# Fuerzas en elemento
# eleForce(eleTag)
forces = ops.eleForce(1)

# Deformaciones en elemento
# eleResponse(eleTag, 'section', sectionNum, responseType)
strains = ops.eleResponse(1, 'section', 1, 'strain')
```

## Recorders

```python
# Recorder de nodo
# recorder('Node', '-file', fileName, '-time', '-node', nodeTag, '-dof', dof, respType)
ops.recorder('Node', '-file', 'disp.out', '-time', '-node', 2, '-dof', 1, 'disp')

# Recorder de elemento
# recorder('Element', '-file', fileName, '-time', '-ele', eleTag, responseType)
ops.recorder('Element', '-file', 'force.out', '-time', '-ele', 1, 'force')
```

## Utilidades

```python
# Limpiar análisis
ops.wipeAnalysis()

# Limpiar modelo completo
ops.wipe()

# Print model info
ops.printModel()
ops.printModel('-file', 'model.txt')

# Get node coordinates
coords = ops.nodeCoord(nodeTag)

# Get element nodes
nodes = ops.eleNodes(eleTag)
```

## Referencias

- Documentación oficial: https://openseespydoc.readthedocs.io/en/stable/
- GitHub OpenSeesPy: https://github.com/zhuminjie/OpenSeesPy
- Teoría OpenSees: https://opensees.berkeley.edu/
