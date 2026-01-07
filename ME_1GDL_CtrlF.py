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

filePath='RSN1100_KOBE_ABN000.DT2'
Nsteps=14000
dt=0.01
timeSeries('Path', 9, '-dt', dt, '-filePath', filePath)
f=np.zeros(Nsteps)

datos=np.loadtxt(filePath)
d=np.zeros(datos.shape[0]*datos.shape[1])
c=-1
for i in range(datos.shape[0]):
    for j in range(datos.shape[1]):
        c+=1
        d[c]=datos[i,j]
        
timeSeries('Path', 8, '-dt', 0.01, '-values', *d)

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
# load(2, 1.0)
sp(2, 1, 1.0)

# create SOE
# system("BandSPD")
system('UmfPack')

# create DOF number
numberer("RCM")

# create constraint handler
# constraints("Plain")
constraints("Transformation")

# create integrator
L=dt
integrator("LoadControl", L)
# incr=L/E
# integrator('DisplacementControl', 2, 1, incr)

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
    # i+=1
    # incr=d[i]-d[i-1]
    # integrator('DisplacementControl', 2, 1, incr)
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
    
    
    


