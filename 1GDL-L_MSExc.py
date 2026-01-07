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
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.DT2'
Nsteps, dt, ug = leer_registro_peer(ruta)
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.VT2'
Nsteps, dt, vg = leer_registro_peer(ruta)
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.AT2'
Nsteps, dt, ag = leer_registro_peer(ruta)

dispSeriesTag=1
velSeriesTag=2
accelSeriesTag=3

timeSeries('Path', dispSeriesTag, '-dt', dt, '-values', *ug,'-factor', 10)
timeSeries('Path', velSeriesTag, '-dt', dt, '-values', *vg,'-factor', 10)
timeSeries('Path', accelSeriesTag, '-dt', dt, '-values', *ag,'-factor', g)

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
recorder('Node', '-file', "Ux.txt",  '-time',  '-node',1, '-dof', 1, 'disp')

# MODELO DE AMORTIGUAMIENTO

Damping=0.01
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
gmTag=1
groundMotion(gmTag, 'Plain', '-disp', dispSeriesTag, '-vel', velSeriesTag, '-accel', accelSeriesTag)

nodeTag=1
dof=1
imposedMotion(nodeTag, dof, gmTag)


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

u1step=np.zeros(Nsteps)
u2step=np.zeros(Nsteps)
vstep=np.zeros(Nsteps)
astep=np.zeros(Nsteps)
Lstep=np.zeros(Nsteps)
nstep=np.zeros(Nsteps)
tstep=np.zeros(Nsteps)
Rstep=np.zeros(Nsteps)
Fstep=np.zeros(Nsteps)

for i in range(Nsteps):
    analyze(1,dt)
    u1step[i]=nodeDisp(1, 1)
    u2step[i]=nodeDisp(2, 1)
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

plt.plot(nstep,u2step-u1step)
plt.title('Disp.')
plt.show()

# plt.plot(nstep,Rstep)
# plt.title('Reaction')
# plt.show()
    
    
    


