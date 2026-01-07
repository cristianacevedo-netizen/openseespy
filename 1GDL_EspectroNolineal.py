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
print("Espectro Elástico")

# PYTHON LIBRERIES:
from openseespy.opensees import *

import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.integrate import cumulative_trapezoid

tic = time.time()     # empieza el cronómetro
	
# DEFINITIONS:
from DEF_leer_registro_peer import leer_registro_peer

# CONSTANTS VALUES:
g = 9810; # Aceleración de la gravedad en mm/s^2
pi = np.acos(-1.0);
# Unidades T (masa), N(fuerza) , mm(distancia), s (tiempo)

T=np.arange(0.01, 3.03, 0.01)
M=1 # Mass [T]

# Ruta al registro PEER
ruta='Imperial Valley/RSN4_IMPVALL.BG_B-ELC000.AT2'
Nsteps, dt, ag = leer_registro_peer(ruta)
ag=ag*g

umax=np.zeros(len(T))
vmax=np.zeros(len(T))
amax=np.zeros(len(T))
Emax=np.zeros(len(T))
Fmax=np.zeros(len(T))

for j in range(len(T)):
    
    # OPENSEES LIBRERIES:
    model('basic', '-ndm', 1, '-ndf', 1) # Carga las funciones de OpenSees para construir el modelo
    wipe() # Limpia los objetos y archivos de salida del interprete

    # MATERIALS LIBRERIES:
    matTag=1
    K=(2*pi/T[j])**2
    uniaxialMaterial('Elastic', matTag, K)
    
    matTag2=2
    K=(2*pi/T[j])**2
    Fy=300.0
    dy=Fy/K
    pinchX=0.8
    pinchY=0.2
    p1=[Fy, dy]
    p2=[Fy, 2*dy]
    p3=[Fy, 3*dy]
    n1=[-Fy, -dy]
    n2=[-Fy, -dy*2]
    n3=[-Fy, -dy*3]
    uniaxialMaterial('Hysteretic', matTag2, *p1, *p2, *p3, *n1, *n2, *n3, pinchX, pinchY, 0, 0, 0)
    
    # SECTIONS LIBRERIES:
    
    # TIME SERIES:
    tagTS=1
    timeSeries('Path', tagTS, '-dt', dt, '-values', *ag)
   
    # NODE COORDENATES:
    node(1, 0)
    node(2, 0,'-mass', M)
    
    # BOUNDARY CONDITIONS:
    fix(1, 1)
    fix(2, 0)
     
    # ELEMENTS:
    eleTag=1
    element('zeroLength', eleTag, 1,2, '-mat', matTag2, '-dir', 1,'-doRayleigh', 1)
    
    
    # DAMPING MODEL    
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
    accelSeriesTag=tagTS
    pattern('UniformExcitation', 1, 1, '-accel', accelSeriesTag)
    
    system('UmfPack')
    numberer("RCM")
    constraints('Transformation')
    algorithm("Newton")
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')

    # SAVE RESULTS
    ustep=np.zeros(Nsteps)
    vstep=np.zeros(Nsteps)
    astep=np.zeros(Nsteps)
    Estep=np.zeros(Nsteps)
    Lstep=np.zeros(Nsteps)
    Fstep=np.zeros(Nsteps)
    nstep=np.zeros(Nsteps)
    tstep=np.zeros(Nsteps)
    for i in range(Nsteps):
        
        analyze(1,dt)
        
        ustep[i]=nodeDisp(2, 1)
        vstep[i]=nodeVel(2, 1)
        astep[i]=nodeAccel(2, 1)
        
        Lstep[i]=getLoadFactor(1)
        Fstep[i]=eleForce(1, 1)
        nstep[i]=i+1
        tstep[i]=getTime()
        
    du = np.gradient(ustep, dt)
    Estep = cumulative_trapezoid(-ag * M * vstep, dx=dt, initial=0.0)
    
    # FIGURE
    umax[j]=np.max(np.abs(ustep))
    vmax[j]=np.max(np.abs(vstep))
    amax[j]=np.max(np.abs(astep))
    Fmax[j]=np.max(np.abs(Fstep))
    Emax[j]=np.max(Estep)
        
plt.plot(T,amax)
plt.title('Espectro Elástico - Aceleración')
plt.xlabel('T [s]')
plt.ylabel(r'$S_a$ [mm/s$^2$]')
plt.show()

plt.plot(T,vmax, label='v')
plt.plot(T,np.sqrt(2*Emax/M), label='V_E')
plt.title('Espectro Elástico - Velocidad')
plt.xlabel('T [s]')
plt.ylabel(r'$S_v$ [mm/s]')
plt.legend()  # aquí se muestra la leyenda
plt.show()

plt.plot(T,umax)
plt.title('Espectro Elástico - Desplazamiento')
plt.xlabel('T [s]')
plt.ylabel(r'$S_d$ [mm]')
plt.show()

plt.plot(T,np.sqrt(Emax))
plt.title('Espectro Elástico - energy Input')
plt.xlabel('T [s]')
plt.ylabel(r'$S(E)$ [mm/s]')
plt.show()

plt.plot(T,Fmax)
plt.title('Espectro Elástico - Fuerza')
plt.xlabel('T [s]')
plt.ylabel(r'$S_F$ [N]')
plt.show()

toc = time.time()     # termina el cronómetro
print("Tiempo transcurrido: {:.4f} s".format(toc - tic))

    
 # Guardar todo en un solo archivo
np.savez("ImperialValley_EspectroNL.npz", T=T,amax=amax,vmax=vmax,umax=umax,Emax=Emax,Fmax=Fmax)   
    


