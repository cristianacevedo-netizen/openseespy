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

# TIME SERIES:
filePath='RSN1100_KOBE_ABN000L.AT2'
Nsteps=14000
dt=0.01
timeSeries('Path', 9, '-dt', dt, '-filePath', filePath,'-factor', g)

# NODE COORDENATES:
node(1, 0)
node(2, 0,'-mass',10)

# BOUNDARY CONDITIONS:
fix(1, 1)
fix(2, 0)
 
# ELEMENTS:
eleTag=1
element('zeroLength', eleTag, 1,2, '-mat', matTag, '-dir', 1)

# OUTPUTS
recorder('Node', '-file', "Ux.txt",  '-time',  '-node',2, '-dof', 1, 'disp')
	 
# ANALYSIS
# create a plain load pattern
# pattern("Plain", 1, tagTS)
pattern('UniformExcitation', 2, 1, '-accel',9)

# Create the nodal load - command: load nodeID xForce yForce
# load(2, 1.0)
# sp(2, 1, 1.0)


# MODELO DE AMORTIGUAMIENTO
numEigenvalues=1
Damping=0.05
Lambda=eigen('-fullGenLapack', numEigenvalues)
LambdaI=Lambda[0]
omegaI=np.sqrt(LambdaI)

alphaM=2*Damping*omegaI
betaK=0
betaKinit=0
betaKcomm=0
rayleigh(alphaM, betaK, betaKinit, betaKcomm)

# create SOE
# system("BandSPD")
system('UmfPack')

# create DOF number
numberer("RCM")

# create constraint handler
# constraints("Plain")
constraints("Transformation")

# create integrator
# integrator("LoadControl", L)
integrator('Newmark', 0.5, 0.25)

# create algorithm
algorithm("Linear")

# create analysis object
# analysis("Static")
analysis("Transient")

# perform the analysis
# analyze(int(1/L))
# Nsteps=int(tEnd/L)

ustep=np.zeros(Nsteps)
Lstep=np.zeros(Nsteps)
Rstep=np.zeros(Nsteps)
Fstep=np.zeros(Nsteps)
nstep=np.zeros(Nsteps)
tstep=np.zeros(Nsteps)
for i in range(Nsteps):

    analyze(1,dt)
    
    ustep[i]=nodeDisp(2, 1)
    Lstep[i]=getLoadFactor(2)
    reactions()
    Rstep[i]=nodeReaction(1, 1)
    Fstep[i]=eleForce(1, 1)
    nstep[i]=i+1
    tstep[i]=getTime()
    


plt.plot(tstep,ustep)
plt.title('Disp.')
plt.show()

plt.plot(ustep,-Rstep)
plt.title('F-Disp.')
plt.show()


    
    
    


