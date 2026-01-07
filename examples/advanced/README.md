# README - Advanced Examples

Esta carpeta contiene ejemplos avanzados de OpenSeesPy para usuarios experimentados.

## Ejemplos Incluidos

### 01_pushover_fiber_section.py
**Descripción**: Análisis pushover no lineal de columna de concreto reforzado usando secciones de fibra detalladas.

**Conceptos cubiertos**:
- Secciones de fibra avanzadas
- Materiales Concrete02 (confinado y no confinado)
- Materiales Steel02 para refuerzo
- Análisis pushover
- Control por desplazamiento
- Transformación P-Delta
- Carga axial constante

**Salida**:
- Curva pushover (fuerza vs desplazamiento)
- Desplazamiento de fluencia aproximado
- Capacidad máxima

**Requisitos**: matplotlib, numpy

**Complejidad**: Alta - requiere comprensión de:
- Diseño de concreto reforzado
- Modelado de secciones de fibra
- Análisis no lineal

**Tiempo estimado**: 30-40 minutos

---

### 02_earthquake_analysis.py
**Descripción**: Análisis completo de historia temporal sísmica de edificio de 3 pisos con movimiento del suelo sintético.

**Conceptos cubiertos**:
- Análisis modal (eigenvalores)
- Cálculo de periodos naturales
- Amortiguamiento de Rayleigh
- Historia temporal de respuesta
- Movimiento del suelo sintético
- Análisis transitorio completo
- Registro de múltiples respuestas

**Salida**:
- Gráficos de:
  - Aceleración del suelo
  - Desplazamiento del techo
  - Cortante basal
- Estadísticas de respuesta máxima
- Razón de deriva máxima

**Requisitos**: matplotlib, numpy

**Complejidad**: Alta - requiere comprensión de:
- Dinámica estructural
- Análisis modal
- Análisis sísmico
- Amortiguamiento de Rayleigh

**Tiempo estimado**: 40-60 minutos

---

## Cómo Ejecutar

```bash
# Desde la raíz del repositorio
python examples/advanced/01_pushover_fiber_section.py
python examples/advanced/02_earthquake_analysis.py
```

## Requisitos del Sistema

- Python 3.7+
- openseespy
- numpy
- matplotlib
- Memoria: Mínimo 2GB RAM
- Procesador: Se recomienda multinúcleo

## Instalación de Dependencias

```bash
pip install -r requirements.txt
```

## Progresión Sugerida

1. **Revisar ejemplos intermedios primero** - Asegúrate de entender análisis dinámico y materiales no lineales
2. **01_pushover_fiber_section.py** - Modelado detallado de concreto
3. **02_earthquake_analysis.py** - Análisis sísmico completo

## Consideraciones Importantes

### Tiempo de Cómputo
- Los análisis avanzados pueden tardar varios minutos
- El análisis pushover con fibras es intensivo computacionalmente
- El análisis de historia temporal procesa muchos pasos de tiempo

### Convergencia
- Los análisis no lineales pueden no converger
- Ajusta parámetros si encuentras problemas:
  - Reduce incremento de desplazamiento
  - Cambia algoritmo de solución
  - Ajusta tolerancias

### Validación
- Compara resultados con soluciones conocidas
- Verifica comportamiento físico razonable
- Revisa advertencias de convergencia

## Modificaciones Avanzadas

Para usuarios expertos:

### Pushover Analysis
- Modifica parámetros de confinamiento
- Cambia distribución de refuerzo
- Aplica diferentes historias de carga
- Agrega degradación de rigidez

### Earthquake Analysis
- Usa registros sísmicos reales
- Modifica características del edificio
- Implementa aislamiento sísmico
- Agrega disipadores de energía

## Recursos Adicionales

### Teoría de Concreto Reforzado
- ACI 318 Building Code
- Paulay & Priestley (1992)
- Park & Paulay (1975)

### Dinámica Estructural
- Chopra (2017) - Dynamics of Structures
- Clough & Penzien (2003)

### Análisis Sísmico
- ASCE 7 Seismic Provisions
- FEMA P-695 (2009)
- Eurocode 8

## Problemas Comunes

### "Analysis failed to converge"
**Solución**:
```python
# Reducir paso de carga
ops.integrator('DisplacementControl', 2, 1, 0.01)  # más pequeño

# Cambia algoritmo
ops.algorithm('NewtonLineSearch')

# Aumenta iteraciones máximas
ops.test('NormDispIncr', 1.0e-6, 200)
```

### "Singular system matrix"
**Solución**:
- Verifica condiciones de frontera
- Revisa conectividad de elementos
- Asegura que no hay nodos libres no restringidos

### Resultados no físicos
**Solución**:
- Verifica unidades consistentes
- Revisa propiedades de materiales
- Valida geometría del modelo

## Notas de Rendimiento

- Los análisis pueden usar múltiples cores
- Considera paralelización para modelos grandes
- Monitorea uso de memoria para análisis extensos
- Guarda resultados intermedios para análisis largos

---

**Advertencia**: Estos ejemplos son para propósitos educativos. Para aplicaciones de diseño real, consulta códigos y estándares aplicables y verifica resultados con ingenieros calificados.
