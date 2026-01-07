##################################################################
## 
##                      Modelo de 1-GDL
## 
##  
##
## Autor - Nombre y apellidos.
## Fecha - XX/XX/2025
##################################################################

print("=========================================================")
print("Modelo de 1-GDL")

# PYTHON LIBRERIES:
from openseespy.opensees import *

import numpy as np
import matplotlib.pyplot as plt

# OPENSEES LIBRERIES:
model('basic', '-ndm', 1, '-ndf', 1) # Carga las funciones de OpenSees para construir el modelo
wipe() # Limpia los objetos y archivos de salida del interprete
	
# DEFINITIONS:

# CONSTANTS VALUES:
g = 9810; # Aceleración de la gravedad en mm/s^2
pi = np.acos(-1.0);
# Unidades T (masa), N(fuerza) , mm(distancia), s (tiempo)

# MATERIALS LIBRERIES:
matTag=1
E=2e5
uniaxialMaterial('Elastic', matTag, E)

matTag2=2
matTag = 1
mu     = 0.30      # coef. fricción
N      = 200.0     # kN de normal (ejemplo)
F_fric = mu * N    # kN
K_tan  = 1e3       # kN/m, por ejemplo

uniaxialMaterial('CoulombDamper', matTag2, K_tan, F_fric,'-tol', 1e-8, '-numFlipped', 3,'-reduceFc', '-dampOutTangent', 0.0)

# SECTIONS LIBRERIES:
from DEF_leer_registro_peer import leer_registro_peer

# TIME SERIES:

timeSeries('Trig', 1, 0.0, 0.6, 0.2, '-factor', 3.0e-3)
timeSeries('Trig', 2, 0.6, 1.2, 0.2, '-factor', 6.0e-3)
timeSeries('Trig', 3, 1.2, 1.8, 0.2, '-factor', 9.0e-3)

timeSeries('Trig', 4, 0.0, 0.6, 0.2, '-factor', 3.0e-3, '-shift', pi/2.0)
timeSeries('Trig', 5, 0.6, 1.2, 0.2, '-factor', 6.0e-3, '-shift', pi/2.0)
timeSeries('Trig', 6, 1.2, 1.8, 0.2, '-factor', 9.0e-3, '-shift', pi/2.0)

timeSeries('Trig', 7, 0.0, 0.6, 0.2, '-factor', 3.0e-3, '-shift', pi)
timeSeries('Trig', 8, 0.6, 1.2, 0.2, '-factor', 6.0e-3, '-shift', pi)
timeSeries('Trig', 9, 1.2, 1.8, 0.2, '-factor', 9.0e-3, '-shift', pi)


# NODE COORDENATES:
node(1, 0)
node(2, 0,'-mass', 2)

# BOUNDARY CONDITIONS:
fix(1, 1)
 
# ELEMENTS:
eleTag=1
element('zeroLength', eleTag, 1,2, '-mat', matTag2, '-dir', 1,'-doRayleigh', 1)

# OUTPUTS
recorder('Node', '-file', "Ux.txt",  '-time',  '-node',1, '-dof', 1, 'disp')

# MODELO DE AMORTIGUAMIENTO

Damping=0.05
Lambda=eigen('-fullGenLapack', 1)
LambdaI=Lambda[0]

omegaI=np.sqrt(LambdaI)

alphaM=0
betaK=2*Damping/omegaI
betaKinit=0
betaKcomm=0
rayleigh(alphaM, betaK, betaKinit, betaKcomm)
	 
# ANALYSIS
# create a plain load pattern
# accelSeriesTag=tagTS
# pattern('UniformExcitation', 1, 1, '-accel', accelSeriesTag)
pattern('MultipleSupport', 1)
groundMotion(1, 'Plain', '-disp', 1, '-vel', 4, '-accel', 7)
groundMotion(2, 'Plain', '-disp', 2, '-vel', 5, '-accel', 8)
groundMotion(3, 'Plain', '-disp', 3, '-vel', 6, '-accel', 9)
groundMotion(4, 'Interpolated', 1,2,3, '-fact', 1,1,1)

nodeTag=2
dof=1
imposedMotion(nodeTag, dof, 4)

dt=0.001; #Paso en el pseudotiempo
Nsteps=int(1.8/dt)


# create SOE
system('UmfPack')

# create DOF number
numberer("RCM")

# create constraint handler
constraints('Transformation')

# create algorithm
algorithm("Newton")
tol=1e-8
Iter=50
pFlag=0
nType=2
test('NormDispIncr', tol, Iter, pFlag, nType)

integrator('Newmark', 0.5, 0.25)
 # create analysis object
analysis('Transient')

ustep=np.zeros(Nsteps)
vstep=np.zeros(Nsteps)
astep=np.zeros(Nsteps)
Lstep=np.zeros(Nsteps)
nstep=np.zeros(Nsteps)
tstep=np.zeros(Nsteps)
Rstep=np.zeros(Nsteps)
Fstep=np.zeros(Nsteps)

for i in range(Nsteps):
    analyze(1,dt)
    ustep[i]=nodeDisp(2, 1)
    vstep[i]=nodeVel(2, 1)
    astep[i]=nodeAccel(2, 1)
    Lstep[i]=getLoadFactor(1)
    reactions()
    Rstep[i]=nodeReaction(1, 1)
    Fstep[i]=eleForce(1, 1)
    nstep[i]=i+1
    tstep[i]=getTime()
    
# plt.plot(nstep,Lstep)
# plt.title('LoadFactor')
# plt.show()

plt.plot(tstep,ustep)
plt.title('Disp.')
plt.show()

plt.plot(tstep,vstep)
plt.title('Vel.')
plt.show()

plt.plot(tstep,astep)
plt.title('Accel.')
plt.show()

plt.plot(ustep,-Fstep)
plt.title('F-Desp')
plt.show()

# plt.plot(nstep,Rstep)
# plt.title('Reaction')
# plt.show()
    
    
    


