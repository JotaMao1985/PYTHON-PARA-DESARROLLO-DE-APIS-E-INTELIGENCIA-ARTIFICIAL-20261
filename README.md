# Python para Desarrollo de APIs e Inteligencia Artificial

> Universidad Santo Tomás · Pregrado en Estadística · 2026-I

Materiales del curso *Python para Desarrollo de APIs e Inteligencia Artificial*.
El objetivo del curso es que los estudiantes transiten del análisis estadístico
en notebooks al diseño y despliegue de servicios web reales con FastAPI,
incorporando validación de datos, persistencia, contenedores, CI/CD y
modelos de machine learning en producción.

---

## Cómo navegar el material

- **En línea** — abre [`index.html`](index.html) directamente en el navegador
  (clonar el repo o, si está habilitado, vía GitHub Pages).
- **Localmente** — clona el repositorio y abre `index.html` en tu navegador.

```bash
git clone https://github.com/JotaMao1985/PYTHON-PARA-DESARROLLO-DE-APIS-E-INTELIGENCIA-ARTIFICIAL-20261.git
cd PYTHON-PARA-DESARROLLO-DE-APIS-E-INTELIGENCIA-ARTIFICIAL-20261
open index.html      # macOS
xdg-open index.html  # Linux
start index.html     # Windows
```

---

## Índice de módulos

| #  | Módulo                                                                                            | Tema                                  |
| -- | ------------------------------------------------------------------------------------------------- | ------------------------------------- |
| 0  | [Syllabus del curso](0_Syllabus_P_A_IA.html)                                                      | Plan general, objetivos y evaluación  |
| 1  | [Introducción a Python para APIs e IA](1_Python_para_APIS_IA.html)                                | Encuadre y herramientas               |
| 2  | [Protocolo HTTP](2_Python_para_APIS_IA_HTTP.html)                                                 | Verbos, estados y diseño REST         |
| 3  | [POO y clases en Python](3_Python_para_APIS_IA_POO_Clases.html)                                   | Programación orientada a objetos      |
| 4  | [Pydantic — Estudio autónomo](4_Python_para_APIS_IA_Pydantic.html)                                | Validación declarativa de datos       |
| 5  | [Del modelo estadístico al servicio web](5_Python_para_APIS_Del_Modelo_al_Servicio_Web.html)      | Del análisis al servicio HTTP         |
| 6  | [FastAPI — De script a servicio](6_Python_para_APIS_IA_Fast_API.html)                             | Routers, modelos y OpenAPI            |
| 7  | [Validación de datos en Python](7_Python_para_APIS_IA_Data_Validation.html)                       | Patrones de validación robustos       |
| 8  | [Inyección de dependencias y configuración](8_Python_para_APIS_IA_DI_Configuracion.html)          | DI y settings en FastAPI              |
| 9  | [SQLAlchemy y bases de datos](9_Python_para_APIS_IA_SQLAlchemy_BD.html)                           | Persistencia con SQLAlchemy           |
| 10 | [Testing y reproducibilidad](10_Python_para_APIS_IA_Testing_y_Reproducibilidad.html)              | Pruebas automatizadas y entornos      |
| 11 | [Contenedores y Docker](11_Python_para_APIS_IA_Contenedores_y_Docker.html)                        | Imágenes reproducibles                |
| 12 | [Despliegue, PaaS y CI/CD](12_Python_para_APIS_IA_Despliegue_PaaS_y_CI_CD.html)                   | Publicación automatizada              |
| 13 | [Modelos de ML en producción](13_Python_para_APIS_IA_Modelos_ML_en_Produccion.html)               | Serialización y patrón Singleton      |

### Proyecto integrador — Teoría del Riesgo

- [Clase II — Planteamiento y bases del modelo](Proyecto_Integrador_Riesgo_Python_CII.html)
- [Clase III — Profundización y articulación con la API](Proyecto_Integrador_Riesgo_Python_CIII.html)

---

## Stack del curso

`Python` · `FastAPI` · `Pydantic` · `SQLAlchemy` · `Scikit-Learn` · `Docker` · `GitHub Actions`

## Estructura del repositorio

```text
.
├── index.html                  # Portada con navegación a los módulos
├── 0_Syllabus_P_A_IA.html      # Syllabus
├── 1_…  …  13_…                # Materiales numerados por sesión
├── Proyecto_I/                 # Plantilla del proyecto integrador
├── app/                        # Ejemplos de aplicación FastAPI
├── data/                       # Datasets de apoyo
└── *.ipynb / *.py              # Notebooks y scripts complementarios
```

## Docente

**Javier Mauricio Sierra** — Universidad Santo Tomás

## Uso académico

Material elaborado con fines educativos para la asignatura.
Cualquier reutilización fuera del contexto del curso debe citar la fuente.
