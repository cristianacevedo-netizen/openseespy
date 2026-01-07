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
tagTS=3
Fsc=1.0 # Factor de escala

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
elif tagTS==3:
    step=0.01
    Nsteps=int(1/step)
    dt=step
    timeSeries('Linear', tagTS)

# NODE COORDENATES:
node(1, 0,0,0)
node(2, 0,0,1000)
node(3, 0,0,2000)
node(4, 0,0,3000)
node(5, 0,0,4000)

# BOUNDARY CONDITIONS:
fix(1, 1,1,1,1,1,1)

 
# ELEMENTS:
transfTag=1
vecxz=[0,1,0]
geomTransf('Linear', transfTag, *vecxz)
# element('forceBeamColumn', eleTag, *eleNodes, transfTag, integrationTag, '-iter', maxIter=10, tol=1e-12, '-mass', mass=0.0)
integrationTag=1
N=3 # Nº de Puntos de Gauss
beamIntegration('Lobatto', integrationTag, secTag, N)
element('forceBeamColumn', 1, 1,2, transfTag, integrationTag)
element('forceBeamColumn', 2, 2,3, transfTag, integrationTag)
element('forceBeamColumn', 3,3,4, transfTag, integrationTag)
element('forceBeamColumn', 4, 4,5, transfTag, integrationTag)


# OUTPUTS
# Tensión-Deformación de Fibras en puntos de Gauss
# recorder Element -file $Outputs/Fibras/StressStrain.out -ele 1 section fiber 0 -150 stressStrain; 

# args="forces"
# arg="localForce"
# arg="basicForce"
# arg='section 1 force'   #arg='section $sectionNumber $arg1 $arg2'
# arg='section 1 deformation'   #arg='section $sectionNumber $arg1 $arg2'
# arg='section 1 fiber 0 -150 stressStrain'   #arg='section $sectionNumber $arg1 $arg2'
# arg='basicDeformation'
# arg='plasticDeformation'
# arg='inflectionPoint'
# arg='tangentDrift'
# arg='integrationPoints'
# arg='integrationWeights'

# Ruta de la carpeta que quieres crear
ruta_carpeta = "Outputs"
os.makedirs(ruta_carpeta, exist_ok=True)
recorder('Node', '-file', "Outputs/Ux.txt",  '-time',  '-node',2, '-dof', 1, 'disp')
recorder('Element', '-file', "Ele1Force.out",'-ele', 1, "section",1,"force")
recorder('Element', '-file', "Ele1localForce.out",'-ele', 1, "localForce")
recorder('Element', '-file', "Ele1stressStrain.out",'-ele', 1, "section",1, "fiber", 0, -150, "stressStrain")

ruta_carpeta = "Outputs/PVD"
os.makedirs(ruta_carpeta, exist_ok=True)
recorder("PVD", ruta_carpeta, "disp")
	 
# ANALYSIS
# create a plain load pattern
pattern("Plain", 1, tagTS)
Wy=0.0
Wz=-11.0
eleLoad('-ele', 3,4, '-type', '-beamUniform', Wy, Wz)

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
    
    ustep[i]=nodeDisp(5, 2)
    Lstep[i]=getLoadFactor(1)
    reactions()
    Rstep[i]=nodeReaction(1, 1)
    Fstep[i]=eleForce(1, 4)
    nstep[i]=i+1

    
# plt.plot(nstep,Lstep)
# plt.title('LoadFactor')
# plt.show()

# plt.plot(nstep,ustep)
# plt.title('Disp.')
# plt.show()

# plt.plot(nstep,Rstep)
# plt.title('Reaction')
# plt.show()

plt.plot(-ustep,-Fstep)
plt.title('M-u')
plt.show()




    
