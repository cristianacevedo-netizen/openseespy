# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 12:13:08 2025

@author: David
"""

import numpy as np
import matplotlib.pyplot as plt

import numpy as np

M=1

data = np.load("ImperialValley_EspectroL.npz")
amax1   = data["amax"]
vmax1   = data["vmax"]
umax1   = data["umax"]
Emax1   = data["Emax"]
Fmax1   = data["Fmax"]
T1  = data["T"]

data = np.load("ImperialValley_EspectroNL.npz")
amax2   = data["amax"]
vmax2   = data["vmax"]
umax2   = data["umax"]
Emax2   = data["Emax"]
Fmax2   = data["Fmax"]
T2  = data["T"]

plt.plot(T1,amax1, label='L')
plt.plot(T2,amax2, label='NL')
plt.title('Espectro Elástico - Aceleración')
plt.xlabel('T [s]')
plt.ylabel(r'$S_a$ [mm/s$^2$]')
plt.legend()  # aquí se muestra la leyenda
plt.show()

plt.plot(T1,vmax1, label='L')
plt.plot(T2,vmax2, label='NL')
plt.title('Espectro Elástico - Velocidad')
plt.xlabel('T [s]')
plt.ylabel(r'$S_v$ [mm/s]')
plt.legend()  # aquí se muestra la leyenda
plt.show()

plt.plot(T1,umax1, label='L')
plt.plot(T2,umax2, label='NL')
plt.title('Espectro Elástico - Desplazamiento')
plt.xlabel('T [s]')
plt.ylabel(r'$S_d$ [mm]')
plt.legend()  # aquí se muestra la leyenda
plt.show()

plt.plot(T1,np.sqrt(2*Emax1/M), label='L')
plt.plot(T2,np.sqrt(2*Emax2/M), label='NL')
plt.title('Espectro Elástico - energy Input')
plt.xlabel('T [s]')
plt.ylabel(r'$S_(v_E)$ [mm/s]')
plt.legend()  # aquí se muestra la leyenda
plt.show()

plt.plot(T1,Fmax1, label='L')
plt.plot(T2,Fmax2, label='L')
plt.title('Espectro Elástico - Fuerza')
plt.xlabel('T [s]')
plt.ylabel(r'$S_F$ [N]')
plt.show()