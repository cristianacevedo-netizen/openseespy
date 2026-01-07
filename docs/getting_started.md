# Guía de Inicio - OpenSeesPy

Esta guía te ayudará a comenzar con OpenSeesPy, desde la instalación hasta tu primer análisis.

## ¿Qué es OpenSeesPy?

OpenSeesPy es una interfaz Python para OpenSees (Open System for Earthquake Engineering Simulation), un framework de código abierto desarrollado en UC Berkeley para el modelado y análisis de sistemas estructurales sometidos a eventos sísmicos y otras cargas.

## Instalación

### Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalación de OpenSeesPy

```bash
pip install openseespy
```

### Paquetes Adicionales Recomendados

```bash
pip install numpy matplotlib
```

O instalar desde requirements.txt:

```bash
pip install -r requirements.txt
```

## Tu Primer Programa

Aquí está un ejemplo simple de un análisis de armadura:

```python
import openseespy.opensees as ops

# Limpiar modelo
ops.wipe()

# Crear modelo 2D con 2 DOF por nodo
ops.model('basic', '-ndm', 2, '-ndf', 2)

# Definir nodos
ops.node(1, 0.0, 0.0)
ops.node(2, 120.0, 0.0)

# Fijar primer nodo
ops.fix(1, 1, 1)

# Definir material
ops.uniaxialMaterial('Elastic', 1, 3000.0)

# Definir elemento
ops.element('Truss', 1, 1, 2, 10.0, 1)

# Crear patrón de carga
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, 100.0, -50.0)

# Configurar análisis
ops.system('BandSPD')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')

# Ejecutar análisis
ops.analyze(1)

# Obtener resultados
disp = ops.nodeDisp(2, 1)
print(f"Desplazamiento en X: {disp} in")

# Limpiar
ops.wipe()
```

## Estructura de un Análisis OpenSeesPy

Todo análisis en OpenSeesPy sigue estos pasos:

### 1. Inicialización

```python
import openseespy.opensees as ops
ops.wipe()
```

### 2. Definición del Modelo

```python
ops.model('basic', '-ndm', 2, '-ndf', 3)
```

- `-ndm`: número de dimensiones (2 o 3)
- `-ndf`: grados de libertad por nodo

### 3. Geometría (Nodos)

```python
ops.node(nodeTag, x, y, [z])
ops.fix(nodeTag, dx, dy, [dz])
```

### 4. Materiales

```python
ops.uniaxialMaterial('materialType', matTag, *args)
```

### 5. Elementos

```python
ops.element('elementType', eleTag, *nodes, *properties)
```

### 6. Cargas

```python
ops.timeSeries('seriesType', tag)
ops.pattern('patternType', patternTag, seriesTag)
ops.load(nodeTag, *forces)
```

### 7. Configuración del Análisis

```python
ops.system('systemType')
ops.numberer('numbererType')
ops.constraints('constraintType')
ops.integrator('integratorType', *args)
ops.algorithm('algorithmType')
ops.analysis('analysisType')
```

### 8. Ejecución

```python
ops.analyze(numSteps, [dt])
```

### 9. Resultados

```python
displacement = ops.nodeDisp(nodeTag, dof)
reaction = ops.nodeReaction(nodeTag)
forces = ops.eleForce(eleTag)
```

## Ejemplos Incluidos

Este repositorio incluye varios ejemplos organizados por nivel de complejidad:

### Básicos (`examples/basic/`)

1. **01_simple_truss.py** - Análisis simple de armadura
2. **02_cantilever_beam.py** - Viga en voladizo
3. **03_frame_structure.py** - Marco 2D simple

### Intermedios (`examples/intermediate/`)

1. **01_dynamic_analysis.py** - Análisis dinámico de un sistema SDOF
2. **02_nonlinear_material.py** - Análisis con materiales no lineales
3. **03_multistory_frame.py** - Marco de múltiples pisos

### Avanzados (`examples/advanced/`)

1. **01_pushover_fiber_section.py** - Análisis pushover con secciones de fibra
2. **02_earthquake_analysis.py** - Análisis de historia temporal sísmica

## Ejecutar los Ejemplos

```bash
# Ejemplo básico
python examples/basic/01_simple_truss.py

# Ejemplo intermedio
python examples/intermediate/01_dynamic_analysis.py

# Ejemplo avanzado
python examples/advanced/01_pushover_fiber_section.py
```

## Tipos de Análisis Comunes

### Análisis Estático

Para estructuras bajo cargas estáticas:

```python
ops.analysis('Static')
ops.analyze(numSteps)
```

### Análisis Dinámico

Para análisis de historia temporal:

```python
ops.analysis('Transient')
ops.analyze(numSteps, dt)
```

### Análisis Modal

Para obtener modos de vibración:

```python
eigenValues = ops.eigen(numModes)
```

## Consejos y Mejores Prácticas

1. **Siempre inicializa con `ops.wipe()`** para limpiar modelos previos
2. **Verifica unidades** - mantén consistencia (kip-in, N-mm, etc.)
3. **Usa `ops.wipeAnalysis()`** si solo quieres cambiar el análisis
4. **Guarda resultados** usando recorders o listas de Python
5. **Visualiza tus resultados** con matplotlib
6. **Valida el modelo** imprimiendo información con `ops.printModel()`

## Unidades Comunes

### Sistema Kip-Inch-Second

- Fuerza: kip (1 kip = 1000 lb)
- Longitud: inch
- Tiempo: second
- Masa: kip-sec²/in
- Esfuerzo: ksi (kip/in²)

### Sistema SI (N-m-s)

- Fuerza: Newton (N)
- Longitud: meter (m)
- Tiempo: second (s)
- Masa: kg
- Esfuerzo: Pa (N/m²)

## Recursos Adicionales

- **Documentación oficial**: https://openseespydoc.readthedocs.io/en/stable/
- **OpenSees Wiki**: https://opensees.berkeley.edu/wiki/
- **GitHub**: https://github.com/zhuminjie/OpenSeesPy
- **Foro de usuarios**: https://github.com/zhuminjie/OpenSeesPy/discussions

## Problemas Comunes

### Error: Model not built

Solución: Asegúrate de definir el modelo con `ops.model()` antes de agregar nodos.

### Análisis no converge

Solución: 
- Reduce el tamaño del paso de carga
- Usa un algoritmo diferente (Newton, ModifiedNewton)
- Verifica las condiciones de frontera
- Revisa las propiedades de los materiales

### Importación falla

Solución: Verifica la instalación con `pip list | grep opensees`

## Próximos Pasos

1. Ejecuta los ejemplos básicos
2. Modifica los parámetros para entender el comportamiento
3. Crea tu propio modelo simple
4. Explora análisis más complejos
5. Lee la documentación oficial para comandos específicos

¡Buena suerte con tus análisis!
