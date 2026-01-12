# OpenSeesPy - Repositorio de Referencias y Ejemplos

Repositorio completo de códigos de referencia, ejemplos y documentación para OpenSeesPy, la interfaz Python para OpenSees (Open System for Earthquake Engineering Simulation).

## 📋 Descripción

Este repositorio contiene una colección organizada de ejemplos y referencias de código que demuestran el uso de OpenSeesPy para análisis estructural y de ingeniería sísmica. Los ejemplos están basados en la documentación oficial y mejores prácticas del framework.

**Referencia oficial**: https://openseespydoc.readthedocs.io/en/stable/index.html

## 🎯 Objetivo

Proporcionar recursos de código bien documentados que:
- Sirvan como referencia para crear nuevos análisis
- Demuestren las capacidades de OpenSeesPy
- Faciliten el aprendizaje del framework
- Muestren implementaciones prácticas de conceptos teóricos

## 📁 Estructura del Repositorio

```
openseespy/
├── README.md                    # Este archivo
├── requirements.txt             # Dependencias Python
├── examples/                    # Ejemplos de código
│   ├── basic/                  # Ejemplos básicos
│   │   ├── 01_simple_truss.py
│   │   ├── 02_cantilever_beam.py
│   │   └── 03_frame_structure.py
│   ├── intermediate/           # Ejemplos intermedios
│   │   ├── 01_dynamic_analysis.py
│   │   ├── 02_nonlinear_material.py
│   │   └── 03_multistory_frame.py
│   └── advanced/               # Ejemplos avanzados
│       ├── 01_pushover_fiber_section.py
│       └── 02_earthquake_analysis.py
└── docs/                       # Documentación
    ├── getting_started.md      # Guía de inicio
    └── command_reference.md    # Referencia de comandos
```

## 🚀 Instalación

### Requisitos Previos
- Python 3.7 o superior
- pip

### Instalar Dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install openseespy numpy matplotlib
```

## 📚 Ejemplos Incluidos

### Nivel Básico

#### 1. Simple Truss (`01_simple_truss.py`)
- Análisis estático de armadura 2D
- Conceptos: nodos, elementos, cargas básicas
- **Aprenderás**: estructura básica de un modelo OpenSeesPy

#### 2. Cantilever Beam (`02_cantilever_beam.py`)
- Viga en voladizo con elementos beam-column
- Conceptos: elementos viga, transformación geométrica
- **Aprenderás**: modelado de vigas y obtención de resultados

#### 3. Frame Structure (`03_frame_structure.py`)
- Marco portal 2D
- Conceptos: estructuras aporticadas, múltiples elementos
- **Aprenderás**: ensamblaje de estructuras complejas

### Nivel Intermedio

#### 4. Dynamic Analysis (`01_dynamic_analysis.py`)
- Análisis dinámico de sistema SDOF
- Conceptos: análisis temporal, movimiento del suelo
- **Aprenderás**: análisis dinámico y registro de historia temporal

#### 5. Nonlinear Material (`02_nonlinear_material.py`)
- Análisis con material Steel02 no lineal
- Conceptos: comportamiento inelástico, curvas histeréticas
- **Aprenderás**: materiales no lineales y análisis cíclico

#### 6. Multi-Story Frame (`03_multistory_frame.py`)
- Edificio de múltiples pisos
- Conceptos: estructuras complejas, distribución de cargas
- **Aprenderás**: modelado de edificios completos

### Nivel Avanzado

#### 7. Pushover with Fiber Section (`01_pushover_fiber_section.py`)
- Análisis pushover de columna de concreto reforzado
- Conceptos: secciones de fibra, análisis pushover
- **Aprenderás**: modelado detallado de elementos de concreto

#### 8. Earthquake Time History (`02_earthquake_analysis.py`)
- Análisis de historia temporal sísmica completo
- Conceptos: análisis modal, amortiguamiento de Rayleigh
- **Aprenderás**: análisis sísmico completo de edificios

## 🎓 Guías y Documentación

### [Guía de Inicio](docs/getting_started.md)
Introducción completa a OpenSeesPy con:
- Instalación paso a paso
- Tu primer programa
- Estructura de un análisis
- Consejos y mejores prácticas

### [Referencia de Comandos](docs/command_reference.md)
Guía rápida de comandos OpenSeesPy incluyendo:
- Model setup
- Definición de nodos y elementos
- Materiales
- Análisis estático y dinámico
- Obtención de resultados

## 💻 Uso

### Ejecutar un Ejemplo

```bash
# Ejemplo básico
python examples/basic/01_simple_truss.py

# Ejemplo intermedio con visualización
python examples/intermediate/01_dynamic_analysis.py

# Ejemplo avanzado
python examples/advanced/01_pushover_fiber_section.py
```

### Ejemplo de Código Rápido

```python
import openseespy.opensees as ops

# Inicializar
ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

# Crear nodos
ops.node(1, 0.0, 0.0)
ops.node(2, 120.0, 0.0)

# Condiciones de frontera
ops.fix(1, 1, 1, 1)

# Definir elemento
ops.geomTransf('Linear', 1)
ops.element('elasticBeamColumn', 1, 1, 2, 20.0, 29000.0, 1400.0, 1)

# Cargas
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
ops.load(2, 0.0, -10.0, 0.0)

# Análisis
ops.system('BandGeneral')
ops.numberer('Plain')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)

# Resultados
disp = ops.nodeDisp(2, 2)
print(f"Desplazamiento vertical: {disp} in")

ops.wipe()
```

## 🔧 Tipos de Análisis Soportados

- ✅ **Análisis Estático**: Cargas gravitacionales, cargas laterales
- ✅ **Análisis Dinámico**: Historia temporal, respuesta sísmica
- ✅ **Análisis Modal**: Frecuencias y modos de vibración
- ✅ **Análisis Pushover**: Capacidad estructural no lineal
- ✅ **Análisis Cíclico**: Comportamiento histerético

## 📖 Recursos Adicionales

### Documentación Oficial
- [OpenSeesPy Documentation](https://openseespydoc.readthedocs.io/en/stable/)
- [OpenSees Wiki](https://opensees.berkeley.edu/wiki/)
- [OpenSees Command Language](https://opensees.berkeley.edu/wiki/index.php/Command_Manual)

### Repositorios y Comunidad
- [OpenSeesPy GitHub](https://github.com/zhuminjie/OpenSeesPy)
- [OpenSees GitHub](https://github.com/OpenSees/OpenSees)

### Tutoriales y Videos
- [OpenSees YouTube Channel](https://www.youtube.com/c/OpenSees)
- [DesignSafe-CI Tutorials](https://www.designsafe-ci.org/learning-center/)

## 🤝 Contribución

Este repositorio sirve como referencia de código. Los ejemplos están basados en:
- Documentación oficial de OpenSeesPy
- Mejores prácticas de ingeniería estructural
- Ejemplos verificados y validados

## 📝 Convenciones de Código

- **Idioma**: Comentarios en español, código en inglés
- **Estilo**: PEP 8 para código Python
- **Documentación**: Docstrings al inicio de cada ejemplo
- **Unidades**: Especificadas claramente en comentarios

## ⚙️ Sistemas de Unidades

### Kip-Inch-Second (usado en ejemplos)
- Fuerza: kip (1 kip = 1000 lb)
- Longitud: inch (in)
- Tiempo: second (sec)
- Masa: kip-sec²/in
- Esfuerzo: ksi (kip/in²)

### SI (alternativa)
- Fuerza: Newton (N)
- Longitud: metro (m)
- Tiempo: segundo (s)
- Masa: kilogramo (kg)
- Esfuerzo: Pascal (Pa)

## 🐛 Solución de Problemas

### Error común: "Model not built"
```python
# Solución: Siempre definir el modelo antes de agregar elementos
ops.model('basic', '-ndm', 2, '-ndf', 3)
```

### Análisis no converge
```python
# Reducir paso de carga
ops.integrator('LoadControl', 0.01)  # En lugar de 0.1

# O usar algoritmo más robusto
ops.algorithm('NewtonLineSearch')
```

## 📄 Licencia

Este repositorio contiene ejemplos educativos basados en OpenSeesPy, que es software de código abierto.

## 👥 Autores

Repositorio creado como referencia para la comunidad de OpenSeesPy.

## 🙏 Agradecimientos

- UC Berkeley Pacific Earthquake Engineering Research Center (PEER)
- Desarrolladores de OpenSees y OpenSeesPy
- Comunidad de ingeniería estructural

---

**Nota**: Este repositorio está en desarrollo continuo. Se agregan nuevos ejemplos y mejoras regularmente.

Para preguntas o sugerencias, consulta la [documentación oficial](https://openseespydoc.readthedocs.io/en/stable/) o el [repositorio oficial de OpenSeesPy](https://github.com/zhuminjie/OpenSeesPy).
