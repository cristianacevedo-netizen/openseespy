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
E=200
uniaxialMaterial('Elastic', matTag, E)

# SECTIONS LIBRERIES:
from DEF_leer_registro_peer import leer_registro_peer

# TIME SERIES:

# Ruta al registro PEER
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.AT2'
Nsteps, dt, ag = leer_registro_peer(ruta)
ag=ag*g

tagTS=1
timeSeries('Path', tagTS, '-dt', dt, '-values', *ag)

# NODE COORDENATES:
node(1, 0)
node(2, 0,'-mass', 2)

# BOUNDARY CONDITIONS:
fix(1, 1)
fix(2, 0)
 
# ELEMENTS:
eleTag=1
element('zeroLength', eleTag, 1,2, '-mat', matTag, '-dir', 1,'-doRayleigh', 1)

# OUTPUTS
recorder('Node', '-file', "Ux.txt",  '-time',  '-node',2, '-dof', 1, 'disp')

# MODELO DE AMORTIGUAMIENTO

Damping=0.05
Lambda=eigen('-fullGenLapack', 1)
LambdaI=Lambda[0]

omegaI=np.sqrt(LambdaI)

alphaM=2*Damping*omegaI
betaK=0
betaKinit=0
betaKcomm=0
rayleigh(alphaM, betaK, betaKinit, betaKcomm)
	 
# ANALYSIS
# create a plain load pattern
accelSeriesTag=tagTS
pattern('UniformExcitation', 1, 1, '-accel', accelSeriesTag)

# create SOE
system('UmfPack')

# create DOF number
numberer("RCM")

# create constraint handler
constraints('Transformation')

# create algorithm
algorithm("Linear")

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

plt.plot(nstep,ustep)
plt.title('Disp.')
plt.show()

# plt.plot(nstep,Rstep)
# plt.title('Reaction')
# plt.show()
    
    
    


