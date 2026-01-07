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
import os
import numpy as np
import matplotlib.pyplot as plt

# OPENSEES LIBRERIES:
model('basic', '-ndm', 1, '-ndf', 1) # Carga las funciones de OpenSees para construir el modelo
wipe() # Limpia los objetos y archivos de salida del interprete
	
# DEFINITIONS:
from DEF_leer_registro_peer import leer_registro_peer

# CONSTANTS VALUES:
g = 9810; # Aceleración de la gravedad en mm/s^2
pi = np.acos(-1.0);
# Unidades T (masa), N(fuerza) , mm(distancia), s (tiempo)

# MATERIALS LIBRERIES:
matTag1=1
E=2e5
uniaxialMaterial('Elastic', matTag1, E)

matTag2=2
E0=E
Fy=300.0
b=0.01
a2=1.0
a1=a2*(Fy/E)
a4=1.0
a3=a4*(Fy/E)

uniaxialMaterial('Steel01', matTag2, Fy, E0, b, a1, a2, a3, a4)

# SECTIONS LIBRERIES:

    
# TIME SERIES:
tagTS=1
Fsc=0.004 # Factor de escala

if tagTS==1:
    # Ruta al registro PEER
    ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.DT2'
    ruta='Kobe/RSN1100_KOBE_ABN000.DT2'
    ruta='Northridge/RSN942_NORTHR_ALH090.DT2'
    
    Nsteps, dt, ug = leer_registro_peer(ruta)
    ug=ug*Fsc
    timeSeries('Path', tagTS, '-dt', dt, '-values', *ug)


elif tagTS==2:
    tEnd=100.0
    step=0.1
    t=np.arange(0,tEnd+step,step)
    S = 1
    f = np.zeros_like(t)  # inicializa el array de salida
    
    for i in range(len(t)):
        if 0 <= t[i] <= 2*tEnd/3:
            f[i] = t[i]/(2*tEnd/3) * np.sin(t[i]) * S
        elif 2*tEnd/3 < t[i] <= tEnd:
            f[i] = (1 - (t[i] - 2*tEnd/3)/(tEnd/3)) * np.sin(t[i]) * S
        else:
            f[i] = 0
    
    Nsteps=len(t)
    dt=step
    timeSeries('Path', tagTS, '-time', *t, '-values', *f,'-factor', Fsc)

# NODE COORDENATES:
node(1, 0)
node(2, 0)

# BOUNDARY CONDITIONS:
fix(1, 1)
fix(2, 0)
 
# ELEMENTS:
eleTag=1
element('zeroLength', eleTag, 1,2, '-mat', matTag2, '-dir', 1)

# OUTPUTS


# Ruta de la carpeta que quieres crear
ruta_carpeta = "Outputs"
os.makedirs(ruta_carpeta, exist_ok=True)
recorder('Node', '-file', "Outputs/Ux.txt",  '-time',  '-node',2, '-dof', 1, 'disp')
	 
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
algorithm("Newton")
tol=1e-8
Iter=50
pFlag=0
nType=2
test('NormDispIncr', tol, Iter, pFlag, nType)

# create analysis object
analysis("Static")

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

plt.plot(ustep,-Rstep)
plt.title('F-Desp')
plt.show()
    
    
    


