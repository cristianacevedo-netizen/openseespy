import numpy as np
import matplotlib.pyplot as plt

# ------------------------------
# Ejmeplos de programación en Python
# -----------------------------

# ATAJOS DE PROGRAMACIÓN
# Ctrl+1 (Comenta/Descomentar)
# F5 Ejecutar
# Ctrl+F5 Ejecutar en modo depuración
# Ctrl+F1 Depuración línea a línea


# VARIABLES (escalares)
A = 4.0
E = 29000.0
alpha = 0.05

# Operaciones
AE= A*E # multiplicación
print(AE)

A2= A**2; # Cuadrado
print(AE)

a = np.sqrt(5)
print(a)  # 2.23606797749979


# VARIABLES (vectores/matrices)
valores = [10, 20, 30] # Lista 

vector_fila = np.array([10, 20, 30])      # vector fila
vector_columna = np.array([[10], [20], [30]])  # vector columna

A = np.array([[1, 2, 3], [2, 5, 6]])
print(A)

B=A[0,1] # De A coge fila 0 y columna 1 (en Python se empieza en cero)
print(B)

C=A[:,1]
print(C)

D=A.T # Traspuesta
print(D)

E = A[:, -1]   # -1 indica la última columna
print(E)


Nsteps=100
data = np.zeros((Nsteps+1,2))



t= np.arange(1, 10.1, 0.1)
n=len(t)

s1=range(n)
print(s1.stop)

s2=range(0, 91, 2) #☻ solo funciona con numeros enteros
print(s2)

# ESTRUCTURAS IF
# Nota: Necesitan tabulación (Indentación)
x = 5

if x > 5:
    print("x > 5")
elif x == 5:
    print("x es igual a 5")
else:
    print("x < 5")

# ESTRUCTURAS FOR
# Nota: Necesitan tabulación (Indentación)

for j in range(n): # Ejecuta el bucle una vez por cada número desde 0 hasta n - 1.
    print(j)

for i in range(A.shape[0]):      # nº de filas
    for j in range(A.shape[1]):  # nº de columnas
        print(A[i, j])
print(A.shape[0])

print(A)

# ESTRUCTURAS WHILE
# Nota: Necesitan tabulación (Indentación)
# CASO 1:
x = 0

while x < 5:
    print(x)
    x += 1  # equivalente a x = x + 1
    
# CASO 2:
x = 0

while True:        # bucle infinito
    print(x)
    x += 1
    if x == 5:
        break      # salir del bucle cuando x = 5
        
# CASO 3:
x = 0

while x < 5:
    x += 1
    if x == 3:
        continue  # salta el print cuando x = 3
    print(x)   

# FUNCIONES
def divmod_custom(a, b):
    s = a // b      # división entera
    r = a % b       # resto
    return s, r

q, r = divmod_custom(7, 3)
print(q, r)  # 2 1


A = np.array([[2, 1],
              [1, 3]])
B = np.array([8, 13])

X = np.linalg.solve(A, B)
print(X)  # [3. 4.]

# GRÁFICAS
t= np.arange(1, 10.1, 0.1).reshape(1, -1) # ajusta las filas para que tengan un columna
t= np.arange(1, 10.1, 0.1)
s=np.sin(t);
print(t.shape)
plt.plot(t, s)
plt.xlabel('Horizontal Displacement')
plt.ylabel('Horizontal Load')
plt.show()


