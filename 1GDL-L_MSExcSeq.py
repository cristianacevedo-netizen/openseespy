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
Nsteps1, dt1, ugNS1 = leer_registro_peer(ruta)
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.VT2'
Nsteps1, dt1, vgNS1 = leer_registro_peer(ruta)
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.AT2'
Nsteps1, dt1, agNS1 = leer_registro_peer(ruta)

ruta='Kobe/RSN1100_KOBE_ABN000.DT2'
Nsteps2, dt2, ugNS2 = leer_registro_peer(ruta)
ruta='Kobe/RSN1100_KOBE_ABN000.VT2'
Nsteps2, dt2, vgNS2 = leer_registro_peer(ruta)
ruta='Kobe/RSN1100_KOBE_ABN000.AT2'
Nsteps2, dt2, agNS2 = leer_registro_peer(ruta)

# ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC270.DT2'
# Nsteps, dt, ugEO = leer_registro_peer(ruta)
# ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC270.VT2'
# Nsteps, dt, vgEO = leer_registro_peer(ruta)
# ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC270.AT2'
# Nsteps, dt, agEO = leer_registro_peer(ruta)

Nsteps=int(1.05*(Nsteps1+Nsteps2))
dt=min(dt1,dt2)

dispSeriesTagNS1=1
timeSeries('Path', dispSeriesTagNS1, '-dt', dt, '-values', *ugNS1,'-factor', 10.0)
velSeriesTagNS1=2
timeSeries('Path', velSeriesTagNS1, '-dt', dt, '-values', *vgNS1,'-factor', 10.0)
accelSeriesTagNS1=3
timeSeries('Path', accelSeriesTagNS1, '-dt', dt, '-values', *agNS1,'-factor', g)

dispSeriesTagNS2=4
timeSeries('Path', dispSeriesTagNS2, '-dt', dt, '-values', *ugNS2,'-factor', 10.0,'-startTime', (Nsteps1+1)*dt1)
velSeriesTagNS2=5
timeSeries('Path', velSeriesTagNS2, '-dt', dt, '-values', *vgNS2,'-factor', 10.0,'-startTime', (Nsteps1+1)*dt1)
accelSeriesTagNS2=6
timeSeries('Path', accelSeriesTagNS2, '-dt', dt, '-values', *agNS2,'-factor', g,'-startTime', (Nsteps1+1)*dt1)

# NODE COORDENATES:
node(1, 0,0)
node(2, 0,0,'-mass', 2,2)

# BOUNDARY CONDITIONS:
fix(1, 1,1)
fix(2,0,1)
 
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
groundMotion(2, 'Plain', '-disp', dispSeriesTagNS2, '-vel', velSeriesTagNS2, '-accel', accelSeriesTagNS2, '-fact', 1.0)
groundMotion(3, 'Interpolated', 1,2, '-fact', 1,1)
imposedMotion(1, 1, 3)

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
    


plt.plot(tstep,u2stepNS)
plt.title('Disp.')
plt.show()



    
    


