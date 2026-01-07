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
import opsvis as opsv

# OPENSEES LIBRERIES:
model('basic', '-ndm', 3, '-ndf', 6) # Carga las funciones de OpenSees para construir el modelo
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
Fy=275.0
b=0.01
a2=1.0
a1=a2*(Fy/E)
a4=1.0
a3=a4*(Fy/E)

R0=12
cR1=0.925
cR2=0.15
sigInit=0.0

uniaxialMaterial('Steel02', matTag2, Fy, E0, b, R0,cR1,cR2, a1, a2, a3, a4, sigInit)

# SECTIONS LIBRERIES:
    # IPE200 - https://www.staticstools.eu/es/profile-ipe/IPE200/mm/show
GJ=1e12
secTag=1
numSubdivY=20
numSubdivZ=2
b=100
h=200
tw=5.6
tf=8.5
r=12
A=((2*r)**2-pi*r**2)/4
section('Fiber', secTag, '-GJ', GJ)
patch('rect', matTag2, numSubdivY, numSubdivZ, -b/2,h/2-tf, b/2,h/2) # Ala sup
patch('rect', matTag2, numSubdivZ, numSubdivY*2, -tw/2,-h/2+tf, tw/2,h/2-tf) # Alma
patch('rect', matTag2, numSubdivY, numSubdivZ, -b/2,-h/2, b/2,-h/2+tf) # Ala inf

fiber(tw/2+r/3, h/2-tf-r/3, A, matTag2)
fiber(-(tw/2+r/3), h/2-tf-r/3, A, matTag2)
fiber(tw/2+r/3, -(h/2-tf-r/3), A, matTag2)
fiber(-(tw/2+r/3),-(h/2-tf-r/3), A, matTag2)

# TIME SERIES:
tagTS=3

step=0.01
Nsteps=int(1/step)
dt=step
timeSeries('Linear', tagTS)

# NODE COORDENATES:
nelem=20
L=5000 
    
for i in range(nelem-int(nelem/2)+1):
    node(i+1, i*L/nelem,0,0)
    print('parte1',i+1,i*L/nelem)

Nodes=getNodeTags()
NodeEnd1=Nodes[-1]

    
for i in range(int(nelem/2), nelem+1):
    node(i+2, i*L/nelem,0,0)
    print('parte2',i+2,i*L/nelem)


# BOUNDARY CONDITIONS:
fix(1, 1,1,1,1,1,1)
fix(nelem+1, 1,1,1,1,1,1)

# ELEMENTS:
transfTag1=1
vecxz=[0,0,1]
geomTransf('Linear', transfTag1, *vecxz)

integrationTag=1
N=3 # Nº de Puntos de Gauss
beamIntegration('Lobatto', integrationTag, secTag, N)

for i in range(nelem-int(nelem/2)):
    element('forceBeamColumn', i+1, i+1,i+2, transfTag1, integrationTag)
    print(i+1, i+1,i+2)


for i in range(int(nelem/2), nelem):
    print(i+1, i+2,i+3)
    element('forceBeamColumn', i+1, i+2,i+3, transfTag1, integrationTag)
    
    
equalDOF(NodeEnd1,NodeEnd1+1,1,2,3)

# OUTPUTS
os.makedirs("Outputs", exist_ok=True)

ruta_pvd = "Outputs/PVD"
os.makedirs(ruta_pvd, exist_ok=True)
recorder("PVD", ruta_pvd, "disp")


# ANALYSIS
# create a plain load pattern
pattern("Plain", 1, tagTS)
Wy=0.0
Wz=-15.0
eleLoad( '-range', 1, nelem,'-type', '-beamUniform', Wy, Wz)

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


for i in range(Nsteps):
    analyze(1)
    




    
