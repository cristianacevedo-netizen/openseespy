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
tagTS=8
timeSeries('Constant', 1, '-factor', 1.0)
timeSeries('Linear', 2, '-factor', 1.0)

tStart=0
tEnd=100
period=tEnd/5
timeSeries('Trig', 3, tStart, tEnd, period, '-factor', 1.0, '-shift', 0.0, '-zeroShift', 0.0)
timeSeries('Triangle', 4, tStart, tEnd, period, '-factor', 1.0, '-shift', 0.0, '-zeroShift', 0.0)
timeSeries('Rectangular', 5, tEnd/6, tEnd-tEnd/6, '-factor', 1.0)
timeSeries('Pulse', 6, tStart, tEnd, period, '-width', 0.5, '-shift', 0.0, '-factor', 1.0, '-zeroShift', 0.0)

Nsteps=1000
step=tEnd/Nsteps

t=np.arange(0,tEnd+step,step)

# t = np.arange(0.002, tend + 0.002, 0.002)  # +0.002 para incluir 10*pi
S = 1
f = np.zeros_like(t)  # inicializa el array de salida

for i in range(len(t)):
    if 0 <= t[i] <= 2*tEnd/3:
        f[i] = t[i]/(2*tEnd/3) * np.sin(t[i]) * S
    elif 2*tEnd/3 < t[i] <= tEnd:
        f[i] = (1 - (t[i] - 2*tEnd/3)/(tEnd/3)) * np.sin(t[i]) * S
    else:
        f[i] = 0

timeSeries('Path', 8, '-time', *t, '-values', *f)


# NODE COORDENATES:
node(1, 0)
node(2, 0)

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
pattern("Plain", 1, tagTS)

# Create the nodal load - command: load nodeID xForce yForce
load(2, 100.0)

# create SOE
system("BandSPD")

# create DOF number
numberer("RCM")

# create constraint handler
constraints("Plain")

# create integrator
integrator("LoadControl", step)

# create algorithm
algorithm("Linear")

# create analysis object
analysis("Static")

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
    analyze(1)
    ustep[i]=nodeDisp(2, 1)
    Lstep[i]=getLoadFactor(1)
    reactions()
    Rstep[i]=nodeReaction(1, 1)
    Fstep[i]=eleForce(1, 1)
    nstep[i]=i+1
    tstep[i]=getTime()
    
plt.plot(nstep,Lstep)
plt.title('LoadFactor')
plt.show()

plt.plot(nstep,ustep)
plt.title('Disp.')
plt.show()

plt.plot(nstep,Rstep)
plt.title('Reaction')
plt.show()
    
    
    


