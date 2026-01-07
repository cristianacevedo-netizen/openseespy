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
import re

def leer_archivo_sismico(ruta_archivo):
    """
    Lee un archivo con un encabezado de 4 filas. De la cuarta fila obtiene el númeor correspondiente a NTPS y DT
    La funcion devuelve un vector columna con los datos desde la fila 5 y la variale NTPS y DT de la cuarta fila
    """
    
    npts=0
    dt=0.0
    datos_aceleracion_lista=[]
    with open(ruta_archivo, 'r') as f:
        
        #Saltar las primeras 3 líneas
        f.readline()
        f.readline()
        f.readline()
        
        #Leer la 4 línea
        linea_metadatos = f.readline()
        
        #Encontrar valores
        match_npts=re.search(r'NPTS=\s*(\d+)', linea_metadatos)
        match_dt=re.search(r'DT=\s*([\d\.]+)', linea_metadatos)
        
        #Guardo las variables
        npts=int(match_npts.group(1))
        dt=float(match_dt.group(1))
        
        #Leer el resto del archivo
        datos_completos_str = f.read()
        
        #Obtengo todos los valores de aceleración en una lista
        lista_valores_str = datos_completos_str.split()
        
        #Convierto los datos a float y los guardo
        datos_aceleracion_lista = [float(valor) for valor in lista_valores_str]

        #Conierto la lista en un array
        aceleraciones_vector = np.array(datos_aceleracion_lista, dtype=float)

    return npts, dt, aceleraciones_vector
#Fin de la funcion

# OPENSEES LIBRERIES:
model('basic', '-ndm', 1, '-ndf', 1) # Carga las funciones de OpenSees para construir el modelo

	
# DEFINITIONS:

# CONSTANTS VALUES:
g = 9810; # Aceleración de la gravedad en mm/s^2
pi = np.acos(-1.0);
M = 2;
# Unidades T (masa), N(fuerza) , mm(distancia), s (tiempo)

# Conjunto de periodos, y valor max de desplazamientos, velocidades y aceleraciones para cada periodo :
T = np.arange(0.01, 3.03, 0.03)
MaxU = np.zeros(len(T))
MaxV = np.zeros(len(T))
MaxA = np.zeros(len(T))


for j in range(len(T)):
    
    wipe() # Limpia los objetos y archivos de salida del interprete
    
    # MATERIALS LIBRERIES:
    matTag=1
    K = M*(2*pi/T[j])**2
    uniaxialMaterial('Elastic', matTag, K)
    
    # SECTIONS LIBRERIES:
    
    # TIME SERIES:
    tagTS=1
    filePath='RSN1100_KOBE_ABN000.AT2'
    
    (Nsteps, dt, aceleraciones_vector) = leer_archivo_sismico(filePath)
    timeSeries('Path', 1, '-dt', dt, '-values', *aceleraciones_vector, '-factor', g)
    
    
    # NODE COORDENATES:
    node(1, 0)
    node(2, 0,'-mass', 2)
    
    # BOUNDARY CONDITIONS:
    fix(1, 1)
    fix(2, 0)
     
    # ELEMENTS:
    eleTag=1
    element('zeroLength', eleTag, 1,2, '-mat', matTag, '-dir', 1,'-doRayleigh', 1)
    
    # OUTPUTS
    recorder('Node', '-file', "Ux.txt",  '-time',  '-node',2, '-dof', 1, 'disp')
    	 
    # ANALYSIS
    accelSeriesTag=tagTS
    pattern('UniformExcitation', 1, 1, '-accel', accelSeriesTag)
    
    # MODELO DE AMORTIGUAMIENTO
    
    Damping=0.05
    Lambda=eigen('-fullGenLapack', 1)
    LambdaI=Lambda[0]
    
    omegaI=np.sqrt(LambdaI)
    
    alphaM=0
    betaK=2*Damping/omegaI
    betaKinit=0
    betaKcomm=0
    rayleigh(alphaM, betaK, betaKinit, betaKcomm)
    
    # create SOE
    system('UmfPack')
    
    # create DOF number
    numberer("RCM")
    
    # create constraint handler
    constraints('Transformation')
    
    # create algorithm
    algorithm("Linear")
    
    # perform the analysis
    
    ustep=np.zeros(Nsteps)
    vstep=np.zeros(Nsteps)
    astep=np.zeros(Nsteps)
    #tstep=np.zeros(Nsteps)
    
    for i in range(Nsteps):
        
        integrator('Newmark', 0.5, 0.25)
        # create analysis object
        analysis('Transient')
        analyze(1,dt)
        ustep[i]=nodeDisp(2, 1)
        vstep[i]=nodeVel(2, 1)
        astep[i]=nodeAccel(2, 1)
        #tstep[i]=getTime()
        
    MaxU[j] = np.max(np.abs(ustep))
    MaxV[j] = np.max(np.abs(vstep))
    MaxA[j] = np.max(np.abs(astep))
    

plt.plot(T,MaxU)
plt.title('Espectro (desplazamiento)')
plt.xlabel('Periodo [s]')
plt.ylabel('Desplazamiento max [s]')
plt.show()

plt.plot(T,MaxV)
plt.title('Espectro (velocidad)')
plt.xlabel('Periodo [s]')
plt.ylabel('Velocidad max [m/s]')
plt.show()  
    
plt.plot(T,MaxA)
plt.title('Espectro (aceleracion)')
plt.xlabel('Periodo [s]')
plt.ylabel('Aceleracion max [m/s**2]')
plt.show()  


