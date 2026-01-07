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
model('basic', '-ndm', 2, '-ndf', 2) # Carga las funciones de OpenSees para construir el modelo
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
Nsteps, dt1, ugNS = leer_registro_peer(ruta)
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.VT2'
Nsteps, dt1, vgNS = leer_registro_peer(ruta)
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.AT2'
Nsteps, dt, agNS = leer_registro_peer(ruta)


ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC270.DT2'
Nsteps, dt, ugEO = leer_registro_peer(ruta)
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC270.VT2'
Nsteps, dt, vgEO = leer_registro_peer(ruta)
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC270.AT2'
Nsteps, dt, agEO = leer_registro_peer(ruta)

Nsteps=int(1.2*(Nsteps))
dt=dt1

dispSeriesTagNS1=1
timeSeries('Path', dispSeriesTagNS1, '-dt', dt, '-values', *ugNS,'-factor', 10.0)
velSeriesTagNS1=2
timeSeries('Path', velSeriesTagNS1, '-dt', dt, '-values', *vgNS,'-factor', 10.0)
accelSeriesTagNS1=3
timeSeries('Path', accelSeriesTagNS1, '-dt', dt, '-values', *agNS,'-factor', g)

dispSeriesTagEO=4
timeSeries('Path', dispSeriesTagEO, '-dt', dt, '-values', *ugEO,'-factor', 10.0)
velSeriesTagEO=5
timeSeries('Path', velSeriesTagEO, '-dt', dt, '-values', *vgEO,'-factor', 10.0)
accelSeriesTagEO=6
timeSeries('Path', accelSeriesTagEO, '-dt', dt, '-values', *agEO,'-factor', g)

# NODE COORDENATES:
node(1, 0,0)
node(2, 0,0,'-mass', 2,2)

# BOUNDARY CONDITIONS:
fix(1, 1,1)

 
# ELEMENTS:
eleTag=1
element('zeroLength', eleTag, 1,2, '-mat', matTag, matTag, '-dir', 1, 2,'-doRayleigh', 1)

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

# pattern('UniformExcitation', 1, 1, '-accel', accelSeriesTag)

pattern('MultipleSupport', 1)

groundMotion(1, 'Plain', '-disp', dispSeriesTagNS1, '-vel', velSeriesTagNS1, '-accel', accelSeriesTagNS1, '-fact', 1.0)
imposedMotion(1, 1, 1)
groundMotion(2, 'Plain', '-disp', dispSeriesTagEO, '-vel', velSeriesTagEO, '-accel', accelSeriesTagEO, '-fact', 1.0)
imposedMotion(1, 2, 2)

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
u2stepNS=np.zeros(Nsteps)
u2stepEO=np.zeros(Nsteps)
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
    u2stepNS[i]=nodeDisp(2, 1)
    u2stepEO[i]=nodeDisp(2, 2)
    vstep[i]=nodeVel(2, 1)
    astep[i]=nodeAccel(2, 1)
    Lstep[i]=getLoadFactor(1)
    reactions()
    Rstep[i]=nodeReaction(1, 1)
    Fstep[i]=eleForce(1, 1)
    nstep[i]=i+1
    tstep[i]=getTime()
    
plt.plot(nstep,u2stepEO)
plt.title('Disp.')
plt.show()

plt.plot(nstep,u2stepNS)
plt.title('Disp.')
plt.show()

plt.plot(u2stepEO,u2stepNS)
plt.title('Disp.')
plt.show()

    


