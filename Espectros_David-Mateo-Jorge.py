# -*- coding: utf-8 -*-
"""
Created on Thu Nov  6 10:02:33 2025

@author: David
"""

##################################################################
##
## PRÁCTICA EN CLASE – ESPECTROS ELÁSTICOS 1GDL
## (Desplazamiento, Velocidad, Aceleración y Energía)
##
## Curso: Máster Universitario en Ingeniería Sísmica 2025-26
## Fecha: 04/11/2025
## Autor: David Macias, Mateo Molina y Jorge Chumbi
##################################################################
print("=========================================================")
print("Cálculo de espectros elásticos con OpenSeesPy")
print("=========================================================")
# ===== LIBRERÍAS =====
from openseespy.opensees import *
import numpy as np
import matplotlib.pyplot as plt
import os
# ===== CONSTANTES =====
g = 9810.0 # mm/s^2
pi = np.pi
M = 2.0 # masa del sistema
xi = 0.05 # amortiguamiento (5%)
# ===== FUNCIONES AUXILIARES =====
def leer_registro_peer(filepath):
    """Lee un archivo PEER .AT2 y devuelve un array con aceleraciones en g."""
    vals = []
    with open(filepath, 'r') as f:
        for line in f:
            try:
                nums = [float(x) for x in line.strip().split()]
                vals.extend(nums)
            except:
                continue
    return np.array(vals, dtype=float)

# ===== CONFIGURACIÓN DEL REGISTRO =====
filePath = 'RSN1100_KOBE_ABN000.AT2'
if not os.path.isfile(filePath):
    raise FileNotFoundError(" No se encontró el archivo del sismo en el directorio actual.")
# Leer aceleraciones del terreno
ag_g = leer_registro_peer(filePath) # en g
dt = 0.005 # paso de tiempo del registro (según el encabezado)
ag = ag_g * g # convertir a mm/s²
N = len(ag)
t = np.arange(0, N * dt, dt)
# ===== LISTAS PARA RESULTADOS =====
T_vals = np.arange(0.01, 3.03, 0.03)
Sd, Sv, Sa, Ein, VEin = [], [], [], [], []
# ===== FUNCIÓN PARA CADA PERIODO =====
1
def analizar_periodo(T, dt, ag):
    """
    Ejecuta el análisis dinámico para un periodo T dado.
    Devuelve u(t), v(t), a_rel(t), a_abs(t)
    """
    wipe()
    model('basic', '-ndm', 1, '-ndf', 1)
    # Nodos y masas
    node(1, 0.0)
    node(2, 0.0, '-mass', M)
    fix(1, 1)
    fix(2, 0)
    # Rigidez variable según el periodo
    omega = 2 * np.pi / T
    K = M * omega ** 2
    # Material elástico y elemento
    matTag = 1
    uniaxialMaterial('Elastic', matTag, K)
    element('zeroLength', 1, 1, 2, '-mat', matTag, '-dir', 1, '-doRayleigh', 1)
    # Amortiguamiento Rayleigh
    alphaM = 0.0
    betaK = 2 * xi / omega
    rayleigh(alphaM, betaK, 0.0, 0.0)
    # Excitación sísmica
    tsTag = 1
    timeSeries('Path', tsTag, '-dt', dt, '-values', *ag)
    pattern('UniformExcitation', 1, 1, '-accel', tsTag)
    # Análisis transitorio
    system('UmfPack')
    numberer('RCM')
    constraints('Transformation')
    test('NormDispIncr', 1.0e-8, 20, 0)
    algorithm('Linear')
    integrator('Newmark', 0.5, 0.25)
    analysis('Transient')
    # Vectores de respuesta
    u = np.zeros(len(ag))
    v = np.zeros(len(ag))
    a_rel = np.zeros(len(ag))
    a_abs = np.zeros(len(ag))
    for i in range(len(ag)):
        analyze(1, dt)
        u[i] = nodeDisp(2, 1)
        v[i] = nodeVel(2, 1)
        a_rel[i] = nodeAccel(2, 1)
        a_abs[i] = a_rel[i] + ag[i]
    return u, v, a_rel, a_abs

# ===== BUCLE PRINCIPAL =====
for T in T_vals:
    u, v, a_rel, a_abs = analizar_periodo(T, dt, ag)
    # Guardar máximos
    Sd.append(np.max(np.abs(u)))
    Sv.append(np.max(np.abs(v)))
    Sa.append(np.max(np.abs(a_rel)))
    # Input de energía: E = ∫ M * üg * u̇ dt
    E = np.trapz(M * ag * v, dx=dt)
    Ein.append(np.abs(E))
    VEin.append(np.abs(np.sqrt(2.0*Ein[-1]/M)))

# ===== GRÁFICAS =====
plt.figure(figsize=(7,5))
plt.plot(T_vals, Sd, 'b', linewidth=1.8)
plt.title('Espectro de Desplazamiento')
plt.xlabel('Periodo (s)')
plt.ylabel('Desplazamiento máximo (mm)')
plt.grid(True)
plt.figure(figsize=(7,5))
plt.plot(T_vals, Sv, 'g', linewidth=1.8)
plt.title('Espectro de Velocidad')
plt.xlabel('Periodo (s)')
plt.ylabel('Velocidad máxima (mm/s)')
plt.grid(True)
plt.figure(figsize=(7,5))
plt.plot(T_vals, Sa, 'r', linewidth=1.8)
plt.title('Espectro de Aceleración Absoluta')
plt.xlabel('Periodo (s)')
plt.ylabel('Aceleración máxima (mm/s²)')
plt.grid(True)
plt.figure(figsize=(7,5))
plt.plot(T_vals, VEin, 'm', linewidth=1.8)
plt.title('Espectro de Input de Energía')
plt.xlabel('Periodo (s)')
plt.ylabel('Input de Energía V_E (mm/s)')
plt.grid(True)
plt.show()
