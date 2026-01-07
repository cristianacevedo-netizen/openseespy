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

# secTag=1
# section('Aggregator', secTag, *mats, '-section', sectionTag)


# ACTIVAR LINEA 78 A 87, CANCELANDO DESDE LÍNEA 66 A 74
# fib_sec_1 = [['section', 'Fiber', secTag, '-GJ', GJ],
#              ['patch', 'rect', matTag2, numSubdivY, numSubdivZ, -b/2,h/2-tf, b/2,h/2], 
#              ['patch', 'rect', matTag2, numSubdivZ, numSubdivY*2, -tw/2,-h/2+tf, tw/2,h/2-tf],  
#              ['patch', 'rect',matTag2, numSubdivY, numSubdivZ, -b/2,-h/2, b/2,-h/2+tf]  
#              ]
# opsv.fib_sec_list_to_cmds(fib_sec_1)
# matcolor = ['r', 'lightgrey', 'gold', 'w', 'w', 'w']
# opsv.plot_fiber_section(fib_sec_1, matcolor=matcolor)
# plt.axis('equal')
# plt.show()

   
# TIME SERIES:
tagTS=1
Fsc=1.2 # Factor de escala


# Ruta al registro PEER
ruta='Imperial Valley/RSN6_IMPVALL.I_I-ELC180.AT2'
# ruta='Kobe/RSN1100_KOBE_ABN000.AT2'
# ruta='Northridge/RSN942_NORTHR_ALH090.AT2'

Nsteps, dt, ag = leer_registro_peer(ruta)
ag=ag*g*Fsc
timeSeries('Path', tagTS, '-dt', dt, '-values', *ag)

# NODE COORDENATES:
node( 1, 0,0,0)
node( 2, 0,0,1000)
node( 3, 0,0,2000,"-mass",1,1,0,0,0,0)
node( 4, 0,0,3000)
node( 5, 0,0,4000,"-mass",1,1,0,0,0,0)

node( 6, 5000,0,0)
node( 7, 5000,0,1000)
node( 8, 5000,0,2000,"-mass",1,1,0,0,0,0)
node( 9, 5000,0,3000)
node(10, 5000,0,4000,"-mass",1,1,0,0,0,0)

node(11, 1250,0,4000)
node(12, 2500,0,4000,"-mass",1,1,0,0,0,0)
node(13, 3750,0,4000)

node( 14, 0,4000,0)
node( 15, 0,4000,1000)
node( 16, 0,4000,2000,"-mass",1,1,0,0,0,0)
node( 17, 0,4000,3000)
node( 18, 0,4000,4000,"-mass",1,1,0,0,0,0)

node( 19, 5000,4000,0)
node( 20, 5000,4000,1000)
node( 21, 5000,4000,2000,"-mass",1,1,0,0,0,0)
node( 22, 5000,4000,3000)
node(23, 5000,4000,4000,"-mass",1,1,0,0,0,0)

node(24, 1250,4000,4000)
node(25, 2500,4000,4000,"-mass",1,1,0,0,0,0)
node(26, 3750,4000,4000)


node( 28, 0,0,1000+4000)
node( 29, 0,0,2000+4000,"-mass",1,1,0,0,0,0)
node( 30, 0,0,3000+4000)
node( 31, 0,0,4000+4000,"-mass",1,1,0,0,0,0)

node( 33, 5000,0,1000+4000)
node( 34, 5000,0,2000+4000,"-mass",1,1,0,0,0,0)
node( 35, 5000,0,3000+4000)
node( 36, 5000,0,4000+4000,"-mass",1,1,0,0,0,0)

node(37, 1250,0,4000+4000)
node(38, 2500,0,4000+4000,"-mass",1,1,0,0,0,0)
node(39, 3750,0,4000+4000)

node( 41, 0,4000,1000+4000)
node( 42, 0,4000,2000+4000,"-mass",1,1,0,0,0,0)
node( 43, 0,4000,3000+4000)
node( 44, 0,4000,4000+4000,"-mass",1,1,0,0,0,0)

node( 46, 5000,4000,1000+4000)
node( 47, 5000,4000,2000+4000,"-mass",1,1,0,0,0,0)
node( 48, 5000,4000,3000+4000)
node( 49, 5000,4000,4000+4000,"-mass",1,1,0,0,0,0)

node(50, 1250,4000,4000+4000)
node(51, 2500,4000,4000+4000,"-mass",1,1,0,0,0,0)
node(52, 3750,4000,4000+4000)


Nodes=getNodeTags()
NodeEnd=Nodes[-1]
print("Total de nudos:",NodeEnd)

# BOUNDARY CONDITIONS:
fix(1, 1,1,1,1,1,1)
fix(6, 1,1,1,1,1,1)
fix(14, 1,1,1,1,1,1)
fix(19, 1,1,1,1,1,1)

# node(NodeEnd+1, 2500,2000,4000)#,"-mass",1,1,0,0,0,0)
# fix(NodeEnd+1, 0,0,1,1,1,0)
# perpDirn=3
# rNodeTag=NodeEnd+1
# cNodeTags=[5,10,11,12,13,18,23,24,25,26]
# rigidDiaphragm(perpDirn, rNodeTag, *cNodeTags)

# node(NodeEnd+2, 2500,2000,4000+4000)#,"-mass",1,1,0,0,0,0)
# fix(NodeEnd+2, 0,0,1,1,1,0)
# perpDirn=3
# rNodeTag=NodeEnd+2
# cNodeTags=[5+26,10+26,11+26,12+26,13+26,18+26,23+26,24+26,25+26,26+26]
# rigidDiaphragm(perpDirn, rNodeTag, *cNodeTags)

# ELEMENTS:
transfTag1=1
vecxz=[0,0,1]
geomTransf('Linear', transfTag1, *vecxz)

transfTag2=2
vecxz=[1,0,0]
geomTransf('Linear', transfTag2, *vecxz)
# element('forceBeamColumn', eleTag, *eleNodes, transfTag, integrationTag, '-iter', maxIter=10, tol=1e-12, '-mass', mass=0.0)
integrationTag=1
N=3 # Nº de Puntos de Gauss
beamIntegration('Lobatto', integrationTag, secTag, N)
element('forceBeamColumn', 1, 1,2, transfTag2, integrationTag)
element('forceBeamColumn', 2, 2,3, transfTag2, integrationTag)
element('forceBeamColumn', 3, 3,4, transfTag2, integrationTag)
element('forceBeamColumn', 4, 4,5, transfTag2, integrationTag)

element('forceBeamColumn', 5, 6,7, transfTag2, integrationTag)
element('forceBeamColumn', 6, 7,8, transfTag2, integrationTag)
element('forceBeamColumn', 7, 8,9, transfTag2, integrationTag)
element('forceBeamColumn', 8, 9,10, transfTag2, integrationTag)

element('forceBeamColumn', 9,   5,11, transfTag1, integrationTag)
element('forceBeamColumn', 10, 11,12, transfTag1, integrationTag)
element('forceBeamColumn', 11, 12,13, transfTag1, integrationTag)
element('forceBeamColumn', 12, 13,10, transfTag1, integrationTag)


element('forceBeamColumn', 13, 1+13,2+13, transfTag2, integrationTag)
element('forceBeamColumn', 14, 2+13,3+13, transfTag2, integrationTag)
element('forceBeamColumn', 15, 3+13,4+13, transfTag2, integrationTag)
element('forceBeamColumn', 16, 4+13,5+13, transfTag2, integrationTag)

element('forceBeamColumn', 17, 6+13,7+13, transfTag2, integrationTag)
element('forceBeamColumn', 18, 7+13,8+13, transfTag2, integrationTag)
element('forceBeamColumn', 19, 8+13,9+13, transfTag2, integrationTag)
element('forceBeamColumn', 20, 9+13,10+13, transfTag2, integrationTag)

element('forceBeamColumn', 21,   5+13,11+13, transfTag1, integrationTag)
element('forceBeamColumn', 22, 11+13,12+13, transfTag1, integrationTag)
element('forceBeamColumn', 23, 12+13,13+13, transfTag1, integrationTag)
element('forceBeamColumn', 24, 13+13,10+13, transfTag1, integrationTag)

element('forceBeamColumn', 25,  5, 18, transfTag1, integrationTag)
element('forceBeamColumn', 26, 10, 23, transfTag1, integrationTag)


element('forceBeamColumn', 27, 5,2+26, transfTag2, integrationTag)
element('forceBeamColumn', 28, 2+26,3+26, transfTag2, integrationTag)
element('forceBeamColumn', 29, 3+26,4+26, transfTag2, integrationTag)
element('forceBeamColumn', 30, 4+26,5+26, transfTag2, integrationTag)

element('forceBeamColumn', 31, 10,7+26, transfTag2, integrationTag)
element('forceBeamColumn', 32, 7+26,8+26, transfTag2, integrationTag)
element('forceBeamColumn', 33, 8+26,9+26, transfTag2, integrationTag)
element('forceBeamColumn', 34, 9+26,10+26, transfTag2, integrationTag)

element('forceBeamColumn', 35,   5+26,11+26, transfTag1, integrationTag)
element('forceBeamColumn', 36, 11+26,12+26, transfTag1, integrationTag)
element('forceBeamColumn', 37, 12+26,13+26, transfTag1, integrationTag)
element('forceBeamColumn', 38, 13+26,10+26, transfTag1, integrationTag)


element('forceBeamColumn', 39, 18,2+13+26, transfTag2, integrationTag)
element('forceBeamColumn', 40, 2+13+26,3+13+26, transfTag2, integrationTag)
element('forceBeamColumn', 41, 3+13+26,4+13+26, transfTag2, integrationTag)
element('forceBeamColumn', 42, 4+13+26,5+13+26, transfTag2, integrationTag)

element('forceBeamColumn', 43, 23,7+13+26, transfTag2, integrationTag)
element('forceBeamColumn', 44, 7+13+26,8+13+26, transfTag2, integrationTag)
element('forceBeamColumn', 45, 8+13+26,9+13+26, transfTag2, integrationTag)
element('forceBeamColumn', 46, 9+13+26,10+13+26, transfTag2, integrationTag)

element('forceBeamColumn', 47,   5+13+26,11+13+26, transfTag1, integrationTag)
element('forceBeamColumn', 48, 11+13+26,12+13+26, transfTag1, integrationTag)
element('forceBeamColumn', 49, 12+13+26,13+13+26, transfTag1, integrationTag)
element('forceBeamColumn', 50, 13+13+26,10+13+26, transfTag1, integrationTag)

element('forceBeamColumn', 51,  5+26, 18+26, transfTag1, integrationTag)
element('forceBeamColumn', 52, 10+26, 23+26, transfTag1, integrationTag)

# OUTPUTS
numEigenvalues=6
os.makedirs("Outputs", exist_ok=True)
ruta_pvd = "Outputs/PVD"
os.makedirs(ruta_pvd, exist_ok=True)
recorder("PVD", ruta_pvd, 'eigen',numEigenvalues)

# MODAL PROPERTIES
Lambda=eigen(numEigenvalues)
# modalProperties('-file', "reportFileName.out")
os.makedirs("Outputs/modalProperties", exist_ok=True)
MP=modalProperties('-file', "Outputs/modalProperties/ModalPropertiesReport.out",'-return')
record() # Graba los recorder en un step concreto definido en la ejecición de recorder()

print("Periodos:",MP['eigenPeriod'])

wipe()




    
