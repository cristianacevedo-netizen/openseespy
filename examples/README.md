# OpenSeesPy Examples

Esta carpeta contiene ejemplos de código OpenSeesPy organizados por nivel de complejidad.

## 📚 Estructura

### 📁 basic/
Ejemplos fundamentales para principiantes:
- Armaduras simples
- Vigas en voladizo
- Marcos básicos

**Requisitos previos**: Conocimientos básicos de Python y mecánica estructural

### 📁 intermediate/
Ejemplos para usuarios con experiencia básica:
- Análisis dinámicos
- Materiales no lineales
- Estructuras de múltiples pisos

**Requisitos previos**: Completar ejemplos básicos, entender análisis estático

### 📁 advanced/
Ejemplos complejos para usuarios experimentados:
- Secciones de fibra
- Análisis pushover
- Análisis sísmico de historia temporal

**Requisitos previos**: Experiencia con análisis no lineal y dinámica estructural

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
pip install -r ../requirements.txt

# Ejecutar ejemplo básico
python basic/01_simple_truss.py

# Ejecutar ejemplo intermedio
python intermediate/01_dynamic_analysis.py

# Ejecutar ejemplo avanzado
python advanced/01_pushover_fiber_section.py
```

## 📖 Guía de Aprendizaje

### Ruta Recomendada

1. **Semana 1-2: Básicos**
   - Leer `docs/getting_started.md`
   - Ejecutar todos los ejemplos en `basic/`
   - Modificar parámetros y observar cambios

2. **Semana 3-4: Intermedios**
   - Repasar `docs/command_reference.md`
   - Trabajar con ejemplos en `intermediate/`
   - Crear variaciones propias

3. **Semana 5+: Avanzados**
   - Estudiar teoría de análisis no lineal
   - Ejecutar ejemplos en `advanced/`
   - Desarrollar proyectos propios

## 🎯 Por Tipo de Análisis

### Análisis Estático
- `basic/01_simple_truss.py`
- `basic/02_cantilever_beam.py`
- `basic/03_frame_structure.py`
- `intermediate/03_multistory_frame.py`

### Análisis Dinámico
- `intermediate/01_dynamic_analysis.py`
- `advanced/02_earthquake_analysis.py`

### Análisis No Lineal
- `intermediate/02_nonlinear_material.py`
- `advanced/01_pushover_fiber_section.py`

## 💡 Consejos para Aprender

### Para Principiantes
1. **Empieza simple**: No te saltes los ejemplos básicos
2. **Entiende cada línea**: Lee los comentarios cuidadosamente
3. **Experimenta**: Cambia valores y observa resultados
4. **Valida**: Compara con soluciones conocidas cuando sea posible

### Para Usuarios Intermedios
1. **Combina conceptos**: Mezcla elementos de diferentes ejemplos
2. **Lee la documentación**: Consulta la referencia oficial
3. **Verifica convergencia**: Entiende por qué análisis fallan
4. **Optimiza**: Aprende a elegir algoritmos apropiados

### Para Usuarios Avanzados
1. **Valida modelos**: Compara con software comercial
2. **Considera física**: Asegura comportamiento realista
3. **Optimiza rendimiento**: Usa técnicas eficientes
4. **Contribuye**: Comparte tus propios ejemplos

## 🛠 Herramientas Útiles

### Visualización
```python
import matplotlib.pyplot as plt
# Los ejemplos intermedios y avanzados incluyen visualización
```

### Debugging
```python
ops.printModel()  # Ver estructura del modelo
ops.printModel('-file', 'model.txt')  # Guardar a archivo
```

### Verificación
```python
# Verificar equilibrio
ops.nodeReaction(nodeTag)
# Verificar deformaciones
ops.eleResponse(eleTag, 'section', 1, 'strain')
```

## 📊 Resultados

### Archivos de Salida
Los ejemplos generan:
- Salida en consola con resultados numéricos
- Archivos PNG con gráficos (en `/tmp/` para ejemplos intermedios/avanzados)
- Archivos `.out` con historias temporales (si se usan recorders)

### Interpretar Resultados
- **Desplazamientos**: Verifiquen ser razonables para la carga aplicada
- **Fuerzas**: Deben equilibrar las cargas aplicadas
- **Convergencia**: Mensajes de error indican problemas de análisis

## ⚠️ Problemas Comunes

### ImportError: No module named 'openseespy'
```bash
pip install openseespy
```

### Analysis failed to converge
- Reduce el paso de carga
- Cambia el algoritmo
- Verifica el modelo

### Resultados poco realistas
- Revisa unidades
- Verifica propiedades de materiales
- Comprueba condiciones de frontera

## 📚 Referencias por Tema

### Elementos
- Truss: `basic/01_simple_truss.py`
- Beam-Column: `basic/02_cantilever_beam.py`, `basic/03_frame_structure.py`
- Fibra: `advanced/01_pushover_fiber_section.py`

### Materiales
- Elastic: Todos los ejemplos básicos
- Steel02: `intermediate/02_nonlinear_material.py`, `advanced/01_pushover_fiber_section.py`
- Concrete02: `advanced/01_pushover_fiber_section.py`

### Análisis
- Static: Ejemplos básicos
- Transient: `intermediate/01_dynamic_analysis.py`, `advanced/02_earthquake_analysis.py`
- Pushover: `intermediate/02_nonlinear_material.py`, `advanced/01_pushover_fiber_section.py`
- Modal: `advanced/02_earthquake_analysis.py`

## 🔗 Enlaces Útiles

- [Documentación OpenSeesPy](https://openseespydoc.readthedocs.io/)
- [OpenSees Wiki](https://opensees.berkeley.edu/wiki/)
- [GitHub OpenSeesPy](https://github.com/zhuminjie/OpenSeesPy)

## 📝 Notas

- Todos los ejemplos usan el sistema de unidades kip-inch-second
- Los archivos temporales se guardan en `/tmp/`
- Las gráficas requieren matplotlib
- Algunos análisis pueden tardar varios minutos

---

**¿Nuevo en OpenSeesPy?** Comienza leyendo `../docs/getting_started.md`

**¿Buscas un comando específico?** Consulta `../docs/command_reference.md`
