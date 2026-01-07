##################################################################
##                     Modelo de 1-GDL – Análisis Dinámico
## Autor - Pauline Dehon
## Fecha - 04/11/2025
##################################################################

print("=========================================================")
print("Análisis Dinámico - 1 GDL")

from openseespy.opensees import *
import numpy as np
import matplotlib.pyplot as plt
import re


# Definición del modelo: 1 dimensión (x), 1 GDL por nodo (desplazamiento)
model('basic', '-ndm', 1, '-ndf', 1)

# --- CONSTANTES Y UNIDADES (T - N - mm - s) ---
g = 9810.0  # aceleración gravedad en mm/s²
E = 200.0   # módulo elástico (N/mm)
m = 2.0     # masa en toneladas


# ----- EXCITACIÓN SÍSMICA -----
filePath = 'RSN1100_KOBE_ABN000.AT2'  # archivo de aceleración


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
 
# Cargar el registro sísmico desde el archivo .AT2
Nsteps, dt, acel = leer_archivo_sismico(filePath)


dp=0.03
T=np.arange(0.01,3+dp,dp)
K=np.zeros(len(T))

U = np.zeros(len(T))
V = np.zeros(len(T))
A = np.zeros(len(T))

for j in range(len(T)):
    K[j]=m*(2*np.pi/T[j])**2


    # --- MATERIAL (Elástico uniaxial) ---
    
    wipe()
    uniaxialMaterial('Elastic', 1, K[j])
    
    # --- NODOS ---
    node(1, 0.0)
    node(2, 0.0, '-mass', m)  # masa asociada al nodo libre
    
    # --- CONDICIONES DE APOYO ---
    fix(1, 1)  # nodo 1 fijo
    fix(2, 0)  # nodo 2 libre
    
    # --- ELEMENTO DE 1 GDL ---
    element('zeroLength', 1, 1, 2, '-mat', 1, '-dir', 1,'-doRayleigh', 1)
    
   
    
    
    # Crear el TimeSeries con datos directamente
    timeSeries('Path', 1, '-dt', dt, '-values', *acel, '-factor', g)
    
    
    # UniformExcitation aplica la aceleración en los apoyos (entrada sísmica)
    # 1 → eje X
    pattern('UniformExcitation', 1, 1, '-accel', 1)
    
    
    
    
    # --- AMORTIGUAMIENTO DE RAYLEIGH (ζ = 1%) ---
    Lambda=eigen('-fullGenLapack', 1)
    omega = np.sqrt(Lambda[0])
    zeta = 0.05
    alphaM = 0.0
    betaK = 2*zeta/omega
    rayleigh(alphaM, betaK, 0, 0)
    
    # --- REGISTRO DEL DESPLAZAMIENTO DEL NODO 2 ---
    recorder('Node', '-file', 'Ux.txt', '-time', '-node', 2, '-dof', 1, 'disp')
    
    # --- DEFINICIÓN DEL ANÁLISIS ---
    system('UmfPack')
    numberer('RCM')
    constraints('Transformation')
    algorithm('Linear')
    integrator('Newmark', 0.5, 0.25)  # esquema de integración
    analysis('Transient')
    
    # --- BUCLE DE INTEGRACIÓN EN EL TIEMPO ---
    u = np.zeros(Nsteps)
    v = np.zeros(Nsteps)
    a = np.zeros(Nsteps)
    t = np.zeros(Nsteps)
    nstep=np.zeros(Nsteps)
    
    for i in range(Nsteps):
        analyze(1, dt)
        u[i] = nodeDisp(2, 1)
        v[i] = nodeVel(2, 1)
        a[i] = nodeAccel(2, 1)
        t[i] = getTime()
        nstep[i]=i+1
    
    U[j]=max(u)
    V[j]=max(v)
    A[j]=max(a)
    
# --- GRÁFICA DEL RESULTADO ---

plt.plot(T, U)
plt.xlabel('Periodo [s]')
plt.ylabel('max(Desp)')
plt.grid()
plt.show()

plt.plot(T, V)
plt.xlabel('Periodo [s]')
plt.ylabel('max(Vel)')
plt.grid()
plt.show()

plt.plot(T, A)
plt.xlabel('Periodo [s]')
plt.ylabel('max(Acel)')
plt.grid()
plt.show()




