# README - Basic Examples

Esta carpeta contiene ejemplos básicos de OpenSeesPy para usuarios principiantes.

## Ejemplos Incluidos

### 01_simple_truss.py
**Descripción**: Análisis estático simple de una armadura 2D con dos nodos.

**Conceptos cubiertos**:
- Inicialización del modelo
- Definición de nodos
- Condiciones de frontera
- Material elástico
- Elemento tipo Truss
- Carga estática
- Análisis lineal

**Salida**: Desplazamientos nodales y fuerzas en elementos

**Tiempo estimado**: 5 minutos

---

### 02_cantilever_beam.py
**Descripción**: Viga en voladizo con carga puntual en el extremo libre.

**Conceptos cubiertos**:
- Modelo 2D con 3 DOF por nodo
- Transformación geométrica
- Elemento elasticBeamColumn
- Propiedades de sección (A, I, E)
- Resultados de momento y cortante

**Salida**: Desplazamientos, rotaciones y fuerzas en elementos

**Tiempo estimado**: 5-10 minutos

---

### 03_frame_structure.py
**Descripción**: Marco portal 2D con columnas y viga.

**Conceptos cubiertos**:
- Estructuras aporticadas
- Múltiples elementos conectados
- Distribución de cargas
- Análisis de estructura completa

**Salida**: Desplazamientos en todos los nodos y fuerzas en todos los elementos

**Tiempo estimado**: 10 minutos

---

## Cómo Ejecutar

```bash
# Desde la raíz del repositorio
python examples/basic/01_simple_truss.py
python examples/basic/02_cantilever_beam.py
python examples/basic/03_frame_structure.py
```

## Progresión Sugerida

1. Empieza con `01_simple_truss.py` para entender la estructura básica
2. Continúa con `02_cantilever_beam.py` para elementos de viga
3. Finaliza con `03_frame_structure.py` para estructuras completas

## Modificaciones Sugeridas

Para practicar, intenta:
- Cambiar las dimensiones de los elementos
- Modificar las propiedades de los materiales
- Agregar más nodos y elementos
- Aplicar diferentes tipos de cargas
