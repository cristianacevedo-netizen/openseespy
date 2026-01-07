# README - Intermediate Examples

Esta carpeta contiene ejemplos intermedios de OpenSeesPy para usuarios con conocimientos básicos.

## Ejemplos Incluidos

### 01_dynamic_analysis.py
**Descripción**: Análisis dinámico de un sistema de un grado de libertad (SDOF) sometido a movimiento del suelo.

**Conceptos cubiertos**:
- Análisis transitorio
- Asignación de masas
- Movimiento del suelo sintético
- Integración de Newmark
- Amortiguamiento
- Historia temporal de respuesta

**Salida**: 
- Gráficos de aceleración y desplazamiento vs tiempo
- Archivo PNG con resultados

**Requisitos**: matplotlib para visualización

**Tiempo estimado**: 15-20 minutos

---

### 02_nonlinear_material.py
**Descripción**: Análisis cíclico de columna con material Steel02 no lineal.

**Conceptos cubiertos**:
- Materiales no lineales (Steel02)
- Secciones de fibra
- Análisis pushover cíclico
- Control por desplazamiento
- Curvas de histéresis

**Salida**:
- Curva de histéresis fuerza-desplazamiento
- Cálculo de energía disipada
- Archivo PNG con resultados

**Requisitos**: matplotlib, numpy

**Tiempo estimado**: 20 minutos

---

### 03_multistory_frame.py
**Descripción**: Edificio de múltiples pisos (4 pisos, 3 bahías) bajo cargas de gravedad y laterales.

**Conceptos cubiertos**:
- Estructuras complejas
- Múltiples pisos y bahías
- Cargas distribuidas
- Análisis de deriva de piso
- Reacciones en la base

**Salida**:
- Desplazamientos laterales por piso
- Razones de deriva de piso
- Reacciones en la base

**Tiempo estimado**: 20-25 minutos

---

## Cómo Ejecutar

```bash
# Desde la raíz del repositorio
python examples/intermediate/01_dynamic_analysis.py
python examples/intermediate/02_nonlinear_material.py
python examples/intermediate/03_multistory_frame.py
```

## Requisitos Adicionales

Asegúrate de tener instaladas las dependencias de visualización:

```bash
pip install matplotlib numpy
```

## Progresión Sugerida

1. `01_dynamic_analysis.py` - Introduce análisis dinámico
2. `02_nonlinear_material.py` - Materiales no lineales e histéresis
3. `03_multistory_frame.py` - Estructuras realistas complejas

## Modificaciones Sugeridas

Experimenta con:
- Diferentes parámetros de movimiento del suelo
- Varios modelos de materiales
- Número de pisos y geometría del edificio
- Cargas sísmicas o de viento
- Amortiguamiento estructural

## Notas Importantes

- Los archivos temporales se guardan en `/tmp/`
- Las gráficas se generan automáticamente
- Algunos análisis pueden tardar varios segundos
